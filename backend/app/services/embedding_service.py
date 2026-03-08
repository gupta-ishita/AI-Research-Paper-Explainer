"""Embedding and vector store operations."""
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from openai import OpenAI

from app.config import settings


def get_embedding_client() -> OpenAI:
    """OpenAI client for embeddings."""
    return OpenAI(api_key=settings.openai_api_key)


def get_embedding(text: str, client: OpenAI) -> list[float]:
    """Get embedding for a single text using OpenAI."""
    resp = client.embeddings.create(
        model=settings.embedding_model,
        input=text[:8000],
    )
    return resp.data[0].embedding


def get_embeddings(texts: list[str], client: OpenAI) -> list[list[float]]:
    """Batch embed texts (OpenAI accepts batch input)."""
    if not texts:
        return []
    # Truncate long texts
    inputs = [t[:8000] for t in texts]
    resp = client.embeddings.create(
        model=settings.embedding_model,
        input=inputs,
    )
    # Preserve order by index
    ordered = [None] * len(resp.data)
    for d in resp.data:
        ordered[d.index] = d.embedding
    return ordered


def get_chroma_collection(paper_id: str):
    """Get or create a Chroma collection for a paper. Persists to disk."""
    persist_dir = Path(settings.chroma_persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(persist_dir),
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    # Collection name safe for Chroma (alphanumeric + _)
    name = f"paper_{paper_id.replace('-', '_')}"
    return client.get_or_create_collection(
        name=name,
        metadata={"description": f"Chunks for paper {paper_id}"},
    )


def add_chunks_to_paper(paper_id: str, chunks: list[str], client: OpenAI) -> None:
    """Embed chunks and add to the paper's vector store."""
    if not chunks:
        return
    coll = get_chroma_collection(paper_id)
    embeddings = get_embeddings(chunks, client)
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    coll.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
    )


def search_paper(paper_id: str, query: str, client: OpenAI, top_k: int | None = None) -> list[str]:
    """Return top-k most relevant chunks for the query."""
    k = top_k or settings.top_k_retrieve
    coll = get_chroma_collection(paper_id)
    query_embedding = get_embedding(query, client)
    results = coll.query(
        query_embeddings=[query_embedding],
        n_results=min(k, coll.count() or 1),
        include=["documents"],
    )
    docs = results.get("documents") or [[]]
    return list(docs[0]) if docs else []
