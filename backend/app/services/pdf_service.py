"""PDF text extraction."""
import uuid
from pathlib import Path

from pypdf import PdfReader

from app.config import settings


def extract_text_from_pdf(file_path: Path) -> tuple[str, int]:
    """
    Extract text from a PDF file.
    Returns (full_text, num_pages).
    """
    reader = PdfReader(str(file_path))
    num_pages = min(len(reader.pages), settings.max_pdf_pages)
    chunks = []
    for i in range(num_pages):
        page = reader.pages[i]
        text = page.extract_text() or ""
        chunks.append(text)
    full_text = "\n\n".join(chunks).strip()
    return full_text, num_pages


def chunk_text(text: str) -> list[str]:
    """
    Split text into overlapping chunks, preferring paragraph boundaries.
    Keeps semantic units intact for better retrieval quality.
    """
    size = settings.chunk_size
    overlap = settings.chunk_overlap
    if not text or size <= 0:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        # Prefer breaking at paragraph boundary when possible
        if end < len(text):
            last_para = chunk.rfind("\n\n")
            if last_para > size // 2:
                chunk = chunk[: last_para + 2]
                end = start + len(chunk)
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def generate_paper_id() -> str:
    """Generate a unique paper ID."""
    return str(uuid.uuid4())
