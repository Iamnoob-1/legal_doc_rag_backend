from flask import Blueprint, request, jsonify
from app.services.legal_tasks import simplify_clause, query_for_answer, risk_check, ingest_document, summarize_document
import os
import tempfile
from werkzeug.utils import secure_filename


legal_bp = Blueprint("legal", __name__)

@legal_bp.route("/simplify", methods=["POST"])
def simplify():
    data = request.json
    clause = data.get("clause", "")
    simplified = simplify_clause(clause)
    return jsonify({"simplified": simplified})

@legal_bp.route("/query", methods=["POST"])
def query():
    data = request.json
    question = data.get("question", "")
    answer = query_for_answer(question)
    return jsonify({"answer": answer})

@legal_bp.route("/risk", methods=["POST"])
def risk():
    data = request.get_json(silent=True) or {}
    query = data.get("query") or data.get("text") or "potential risks or penalties"
    risks = risk_check(query=query)
    return jsonify({"risks": risks})



@legal_bp.route("/ingest", methods=["POST"])
def ingest():
    """Accept multipart upload (`file`) or JSON body (`path`) and ingest into vector index."""
    data = request.get_json(silent=True) or {}
    file = request.files.get("file")
    path = data.get("path") or request.form.get("path")
    doc_id = data.get("doc_id") or request.form.get("doc_id") or "default_doc"

    temp_path = None
    try:
        if file:
            filename = secure_filename(file.filename or "uploaded_document.txt")
            suffix = os.path.splitext(filename)[1] or ".txt"

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                file.save(tmp.name)
                temp_path = tmp.name

            ingest_result = ingest_document(temp_path, doc_id)

            return jsonify(
                {
                    "message": (
                        f"Document {doc_id} ingested successfully."
                        if ingest_result.get("vector_indexed")
                        else f"Document {doc_id} text extracted successfully; vector indexing was skipped."
                    ),
                    "doc_id": doc_id,
                    "filename": filename,
                    "text_content": ingest_result.get("text", ""),
                    "vector_indexed": ingest_result.get("vector_indexed", False),
                    "warning": ingest_result.get("warning"),
                }
            )

        if path:
            ingest_result = ingest_document(path, doc_id)
            return jsonify(
                {
                    "message": (
                        f"Document {doc_id} ingested successfully."
                        if ingest_result.get("vector_indexed")
                        else f"Document {doc_id} text extracted successfully; vector indexing was skipped."
                    ),
                    "doc_id": doc_id,
                    "filename": os.path.basename(path),
                    "text_content": ingest_result.get("text", ""),
                    "vector_indexed": ingest_result.get("vector_indexed", False),
                    "warning": ingest_result.get("warning"),
                }
            )

        return jsonify({"error": "Provide either 'file' (multipart) or 'path' in request body"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
    

@legal_bp.route("/summarise_document",methods=["POST"])
def summarise_document_route():
    """Accept multipart upload (`file`), raw `text`, or JSON `path` and return section-wise summary."""
    data = request.get_json(silent=True) or {}
    file = request.files.get("file")
    path = data.get("path") or request.form.get("path")
    text = data.get("text") or request.form.get("text")

    temp_path = None
    try:
        if file:
            filename = secure_filename(file.filename or "uploaded_document.txt")
            suffix = os.path.splitext(filename)[1] or ".txt"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                file.save(tmp.name)
                temp_path = tmp.name
            summary = summarize_document(temp_path)
            return jsonify({"Summary": summary})

        if text:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
                tmp.write(text)
                temp_path = tmp.name
            summary = summarize_document(temp_path)
            return jsonify({"Summary": summary})

        if path:
            summary = summarize_document(path)
            return jsonify({"Summary": summary})

        return jsonify({"error": "Provide either 'file', 'text', or 'path'"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)