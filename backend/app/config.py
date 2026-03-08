"""Application configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings loaded from environment."""

    openai_api_key: str = ""
    chroma_persist_dir: str = "./data/chroma"
    max_pdf_pages: int = 200
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_retrieve: int = 8

    # Model selection (override via env for cost/quality tradeoff)
    summarization_model: str = "gpt-4o"
    qa_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-large"

    # Summarization: max chars to send (GPT-4o has 128k context; ~50k chars ≈ safe margin)
    summarization_max_chars: int = 50_000

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
