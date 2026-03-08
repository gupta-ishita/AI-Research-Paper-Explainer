# AI Research Paper Explainer

Upload a research paper PDF, get an AI-generated summary, and ask questions about the paper. Uses vector search (RAG) for accurate, source-grounded answers.

## Quick start

1. **Backend** (from project root):
   ```bash
   cd backend
   cp ../.env.example .env
   # Edit .env and set OPENAI_API_KEY=sk-...
   python -m venv .venv
   source .venv/bin/activate   # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend** (new terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Open **http://localhost:5173**, upload a PDF, and use the summary and Q&A.

## Project structure

```
ai-research-paper-explainer/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app, CORS, health
│   │   ├── config.py         # Settings (OpenAI, Chroma, chunking)
│   │   ├── models/
│   │   │   └── schemas.py    # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── pdf_service.py         # PDF text extraction, chunking
│   │   │   ├── summarization_service.py # OpenAI summary
│   │   │   ├── embedding_service.py   # OpenAI embeddings + ChromaDB
│   │   │   └── qa_service.py          # RAG: retrieve + LLM answer
│   │   └── api/
│   │       └── routes.py    # POST /api/upload, POST /api/ask
│   ├── requirements.txt
│   └── .env                 # OPENAI_API_KEY (create from .env.example)
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # State: paper, upload, Q&A
│   │   ├── api.js           # uploadPdf(), askQuestion()
│   │   └── components/      # UploadZone, SummaryCard, QASection
│   ├── index.html
│   ├── vite.config.js       # Proxy /api to backend
│   └── package.json
├── .env.example
└── README.md
```

## Design choices

### Tech stack
- **Backend: Python + FastAPI** – Async API, automatic OpenAPI docs, simple to extend. Ideal for ML/AI pipelines.
- **PDF: pypdf** – Lightweight, pure Python, good text extraction for most academic PDFs.
- **LLM & embeddings: OpenAI** – Reliable, one API for summarization, embeddings, and Q&A. Easiest path to production quality.
- **Vector store: ChromaDB** – Persistent, file-based, no extra server. One collection per paper keeps queries scoped and simple.
- **Frontend: React + Vite** – Fast dev experience, minimal tooling. No global state library; component state is enough for this flow.

### Architecture
- **Modular backend**: `pdf_service` (extract + chunk), `summarization_service`, `embedding_service` (embed + Chroma), `qa_service` (retrieve + answer). Each has a single responsibility and can be tested or swapped (e.g. different embed model or vector DB).
- **Stateless API**: No session store. Upload returns a `paper_id`; the client sends it with every question. Index is stored on disk (Chroma), so server restarts don’t lose data.
- **RAG flow**: On upload, text is chunked (configurable size/overlap), embedded with OpenAI, and stored in a Chroma collection keyed by `paper_id`. On question, the query is embedded, top-k chunks are retrieved, and the LLM answers from that context only.

### Simplicity vs production
- **Simplicity**: Single repo, no Docker required to run, minimal dependencies. Frontend proxies to backend; no auth or multi-tenancy in this version.
- **Production-oriented**: Pydantic validation, structured error responses, config via env (e.g. `OPENAI_API_KEY`), chunk size/overlap and top-k in config, and a clear place to add rate limits, auth, or a proper vector DB later.

## Environment variables (backend)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for embeddings and chat. |
| `CHROMA_PERSIST_DIR` | No | Directory for ChromaDB (default: `./data/chroma`). |
| `MAX_PDF_PAGES` | No | Max pages to process (default: 200). |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | No | Chunking for RAG (defaults: 1000, 200). |
| `TOP_K_RETRIEVE` | No | Number of chunks to pass to the LLM (default: 8). |
| `SUMMARIZATION_MODEL` | No | Model for summarization (default: `gpt-4o`). |
| `QA_MODEL` | No | Model for question answering (default: `gpt-4o`). |
| `EMBEDDING_MODEL` | No | Model for embeddings (default: `text-embedding-3-large`). If you change this, delete `data/chroma` and re-upload papers. |

## API

- **POST /api/upload** – `multipart/form-data` with `file` (PDF). Returns `paper_id`, `summary`, `num_pages`, `filename`.
- **POST /api/ask** – JSON `{ "paper_id": "...", "question": "..." }`. Returns `{ "answer": "...", "sources": [...] }`.
- **GET /health** – Health check.
