"""Question-answering over paper chunks (RAG)."""
from openai import OpenAI

from app.config import settings


def answer_question(
    paper_id: str,
    question: str,
    client: OpenAI,
    context_chunks: list[str],
) -> str:
    """
    Answer the user question given retrieved context chunks.
    Uses a stronger model and citation-focused prompting for accuracy.
    """
    if not context_chunks:
        return (
            "No relevant passages were found in this paper for your question. "
            "Try rephrasing or asking about the main findings or methodology."
        )

    context = "\n\n---\n\n".join(context_chunks)

    system = """You are an expert assistant that answers questions about academic research papers with precision and rigor.

Rules:
1. Use ONLY the provided excerpts from the paper. Do not infer or invent information.
2. When the excerpts support an answer, quote or paraphrase the paper's language directly.
3. If the excerpts are insufficient, say so clearly and suggest what might be missing.
4. Be specific: cite numbers, methods, and findings when they appear in the excerpts.
5. If the question is ambiguous, address the most likely interpretation and note alternatives.
6. Keep answers focused and concise, but complete enough to be useful."""

    user = f"""Relevant excerpts from the paper:

{context}

Question: {question}

Answer based only on the excerpts above. Quote the paper when it strengthens your answer."""

    resp = client.chat.completions.create(
        model=settings.qa_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=800,
    )
    return (resp.choices[0].message.content or "").strip()
