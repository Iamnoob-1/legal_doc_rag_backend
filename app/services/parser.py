from pypdf import PdfReader
import docx
import os

def parse_pdf(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join([page.extract_text() or "" for page in reader.pages])

def parse_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def parse_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def parse_document(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        return parse_pdf(path)
    elif ext == ".docx":
        return parse_docx(path)
    elif ext == ".txt":
        return parse_text(path)
    else:
        raise ValueError("Unsupported file format. Use PDF, DOCX, or TXT.")
