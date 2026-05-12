# Legal Document Simplifier Backend (Flask)

This backend handles document parsing, embedding + retrieval, and Gemini-powered legal tasks.

## Project Structure

```text
legal_document_simplifier_backend_google-main/
	app/
		main.py
		config/
			settings.py
		routes/
			legal.py
		services/
			parser.py
			chunker.py
			embeddings.py
			database.py
			retrieval.py
			gemini_client.py
			legal_tasks.py
	requirements.txt
	.env.example
```

## Prerequisites

- Python 3.10+ (recommended)
- A Pinecone index key + region
- A Gemini API key

## Local Setup

1. Create and activate a virtual environment.

```powershell
cd legal_document_simplifier_backend_google-main
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Create your environment file.

```powershell
Copy-Item .env.example .env
```

4. Edit `.env` with your real keys.

```env
GEMINI_API_KEY=...
PINECONE_API_KEY=...
PINECONE_ENV=...
GEMINI_MODEL=models/gemini-1.5-flash
```

5. Run the backend.

```powershell
python -m app.main
```

The backend will be available at `http://localhost:5000`.

## Health Check

- `GET http://localhost:5000/ping` -> `{ "message": "pong" }`

## API Notes

- `POST /api/legal/ingest` accepts either:
	- `multipart/form-data` with `file` and optional `doc_id`, or
	- JSON with `path` and optional `doc_id`
- `POST /api/legal/summarise_document` accepts:
	- `multipart/form-data` with `file`, or
	- form/JSON `text`, or
	- JSON `path`
