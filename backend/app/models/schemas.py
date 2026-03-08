"""API request/response schemas."""
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response after PDF upload and processing."""

    paper_id: str
    filename: str
    summary: str
    num_pages: int
    message: str = "Paper processed successfully. You can now ask questions."


class QuestionRequest(BaseModel):
    """Request to ask a question about a paper."""

    paper_id: str
    question: str = Field(..., min_length=1, max_length=2000)


class QuestionResponse(BaseModel):
    """Answer to a user question with optional sources."""

    answer: str
    sources: list[str] = Field(default_factory=list)
