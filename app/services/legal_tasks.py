from app.services.parser import parse_document
from app.services.chunker import chunk_text
from app.services.embeddings import get_embedding_model
from app.services.database import collection
from app.services.retrieval import retrieve_and_rerank
from app.services.gemini_client import generate_response
from app.config.settings import GEMINI_MODEL_NAME

from typing import List, Dict, Any
import re


def ingest_document(path: str, doc_id: str):
    text = parse_document(path)
    if not text or not text.strip():
        raise ValueError("No extractable text found in the uploaded document. If this is a scanned PDF, run OCR first.")

    chunks = chunk_text(text)
    chunks = [chunk for chunk in chunks if chunk.strip()]
    if not chunks:
        raise ValueError("Document text extraction returned empty content, so ingestion was skipped.")

    embedding_model = get_embedding_model()
    embeddings = embedding_model.encode(chunks).tolist()

    vectors = [
        {
            "id": f"{doc_id}_{i}",
            "values": emb,
            "metadata": {"text": chunk}
        }
        for i, (emb, chunk) in enumerate(zip(embeddings, chunks))
    ]

    try:
        # Try to clear old data first (namespace may not exist on first upload — that's fine)
        try:
            collection.delete(delete_all=True, namespace="legal-docs")
            print(f"Cleared previous vectors in 'legal-docs' namespace.")
        except Exception as del_err:
            print(f"Could not clear namespace (likely first upload): {del_err}")

        # Always upsert the new vectors
        collection.upsert(vectors=vectors, namespace="legal-docs")
        print(f"Document {doc_id} ingested with {len(chunks)} chunks.")
        return {"text": text, "vector_indexed": True, "warning": None}
    except RuntimeError as e:
        warning = str(e)
        print(f"Vector indexing skipped for {doc_id}: {warning}")
        return {"text": text, "vector_indexed": False, "warning": warning}
    except Exception as e:
        warning = str(e)
        print(f"Unexpected error during vector indexing for {doc_id}: {warning}")
        return {"text": text, "vector_indexed": False, "warning": warning}


def simplify_clause(clause_query: str, doc_type: str = "contract") -> str:
    retrieved_chunks = retrieve_and_rerank(clause_query)
    context = "\n".join(retrieved_chunks)

    prompt = f"""
    You are a legal simplifier. The user provided a {doc_type}.
    Clause/query: {clause_query}

    Relevant context from the document:
    {context}

    Simplify this clause into plain English so a non-lawyer can understand.
    """
    return generate_response(prompt)


def query_for_answer(question: str, doc_type: str = "contract") -> str:
    retrieved_chunks = retrieve_and_rerank(question)
    context = "\n".join(retrieved_chunks)

    prompt = f"""
    You are assisting with understanding a {doc_type}.
    Question: {question}

    Relevant context from the document:
    {context}

    Answer the question in plain English, clearly and concisely.
    """
    return generate_response(prompt)


def risk_check(query: str = "potential risks or penalties", doc_type: str = "contract") -> str:
    retrieved_chunks = retrieve_and_rerank(query, top_k=8)
    context = "\n".join(retrieved_chunks)

    prompt = f"""
    You are a legal risk detector. The user uploaded a {doc_type}.
    Relevant document context:
    {context}

    Identify any clauses that may be risky or unfavorable (penalties, hidden fees, unilateral rights, etc.).
    Return a short checklist in plain English.
    If no risks are found, say: "No significant risks detected."
    """
    return generate_response(prompt)


def split_by_headings(text: str) -> Dict[str, str]:
    """
    Split document text into sections based on headings.
    Headings are assumed to be lines in ALL CAPS or numbered like 1., 2.1, etc.
    """
    sections = {}
    current_heading = "Introduction"
    buffer = []

    lines = text.splitlines()
    for line in lines:
        line_stripped = line.strip()
        # Detect headings (very simple heuristic)
        if re.match(r"^(\d+(\.\d+)*)\s", line_stripped) or line_stripped.isupper():
            # Save previous section
            if buffer:
                sections[current_heading] = "\n".join(buffer).strip()
                buffer = []
            current_heading = line_stripped
        else:
            buffer.append(line_stripped)

    # Add last section
    if buffer:
        sections[current_heading] = "\n".join(buffer).strip()

    return sections


def simplify_summarize_section(title: str, text: str) -> str:
    """
    Summarize one section into bullet points (simplified, easy to understand).
    Skips if section is empty or trivial.
    """
    if not text.strip() or len(text.split()) < 20:  # skip too short sections
        return ""

    prompt = f"""
    You are an assistant that explains documents in simple language.
    Summarize the following section into 3–5 short, clear bullet points.

    Rules:
    - Use plain English (avoid jargon or legalese).
    - Write as if explaining to someone with no legal/technical background.
    - Keep sentences short and direct.
    - If the section has no meaningful information, output "No important points."

    Section Title: "{title}"

    Section Text:
    {text}

    Output format:
    - simple point 1
    - simple point 2
    ...
    """

    response = generate_response(prompt)
    return response


def summarize_section(title: str, text: str) -> str:
    """
    Summarize one section into bullet points (if relevant).
    Skips if section is empty or trivial.
    """
    if not text.strip() or len(text.split()) < 20:  # skip too short sections
        return ""

    prompt = f"""
    You are a legal assistant. Summarize the following section into 3–5 clear bullet points.
    Do not invent a title, use the given one: "{title}".
    If no meaningful points exist, return "No important points."

    Section Text:
    {text}

    Output format:
    - point 1
    - point 2
    ...
    """

    response = generate_response(prompt)
    return response


def summarize_document(path: str) -> Dict[str, str]:
    """
    Parse document and generate ONE combined summary request
    to reduce Gemini API quota usage.
    """

    text = parse_document(path)

    if not text or not text.strip():
        return {
            "Error": "No text could be extracted from document."
        }

    # Limit size to avoid token overflow
    text = text[:12000]

    prompt = f"""
    You are a legal assistant.

    Summarize the following legal/technical document in simple English.

    Requirements:
    - Use headings
    - Use bullet points
    - Keep explanations short
    - Highlight important clauses, penalties, responsibilities, risks, and deadlines
    - Make it easy for a normal person to understand

    Document:
    {text}
    """

    response = generate_response(prompt)

    return {
        "AI Summary": response
    }