"""API routes for upload and Q&A."""
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile
from openai import APIError, RateLimitError

from app.config import settings
from app.models import QuestionRequest, QuestionResponse, UploadResponse
from app.services.embedding_service import (
    add_chunks_to_paper,
    get_embedding_client,
    search_paper,
)
from app.services.pdf_service import (
    chunk_text,
    extract_text_from_pdf,
    generate_paper_id,
)
from app.services.qa_service import answer_question
from app.services.summarization_service import summarize_paper

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/upload", response_model=UploadResponse)
async def upload_paper(file: UploadFile = File(...)):
    """Upload a PDF, extract text, summarize, and index for Q&A."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed.")

    if not settings.openai_api_key:
        raise HTTPException(
            500,
            "OpenAI API key not configured. Set OPENAI_API_KEY in .env.",
        )

    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)
    except Exception as e:
        raise HTTPException(500, f"Failed to save upload: {e}") from e

    try:
        text, num_pages = extract_text_from_pdf(tmp_path)
    except Exception as e:
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Failed to read PDF: {e}") from e
    finally:
        tmp_path.unlink(missing_ok=True)

    if not text or len(text.strip()) < 100:
        raise HTTPException(
            400,
            "Could not extract enough text from the PDF. It may be scanned or empty.",
        )

    paper_id = generate_paper_id()
    client = get_embedding_client()

    try:
        summary = summarize_paper(text, client)
        chunks = chunk_text(text)
        add_chunks_to_paper(paper_id, chunks, client)
    except RateLimitError as e:
        err = e.response.json() if e.response else {}
        msg = err.get("error", {}).get("message", str(e))
        if "quota" in msg.lower() or "insufficient_quota" in str(err).lower():
            raise HTTPException(
                402,
                "OpenAI quota exceeded. Add a payment method or check usage at "
                "https://platform.openai.com/account/billing",
            ) from e
        raise HTTPException(429, f"OpenAI rate limit: {msg}") from e
    except APIError as e:
        raise HTTPException(502, f"OpenAI API error: {e.message or str(e)}") from e

    return UploadResponse(
        paper_id=paper_id,
        filename=file.filename or "document.pdf",
        summary=summary,
        num_pages=num_pages,
    )


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(req: QuestionRequest):
    """Answer a question about a previously uploaded paper (vector search + LLM)."""
    if not settings.openai_api_key:
        raise HTTPException(
            500,
            "OpenAI API key not configured. Set OPENAI_API_KEY in .env.",
        )

    client = get_embedding_client()
    try:
        chunks = search_paper(req.paper_id, req.question, client)
        answer = answer_question(req.paper_id, req.question, client, chunks)
    except RateLimitError as e:
        err = e.response.json() if e.response else {}
        if "quota" in str(err).lower():
            raise HTTPException(
                402,
                "OpenAI quota exceeded. Add a payment method or check usage at "
                "https://platform.openai.com/account/billing",
            ) from e
        raise HTTPException(429, "OpenAI rate limit exceeded. Try again in a moment.") from e
    except APIError as e:
        raise HTTPException(502, f"OpenAI API error: {e.message or str(e)}") from e
    return QuestionResponse(answer=answer, sources=chunks[:3])
