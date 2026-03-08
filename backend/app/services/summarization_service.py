"""Paper summarization using OpenAI."""
from openai import OpenAI

from app.config import settings


def summarize_paper(text: str, client: OpenAI) -> str:
    """
    Generate a concise, high-quality summary of the research paper.
    Uses a larger context window for full-paper understanding.
    """
    max_chars = settings.summarization_max_chars
    truncated = text[:max_chars].strip()
    if not truncated:
        return "No text could be extracted from this PDF."

    system = """You are an expert at summarizing academic research papers for both specialists and general audiences.

Provide a clear, well-structured summary that includes:

1. **Title & Topic** – Paper title (if evident) and main subject area
2. **Research Question / Objective** – What the authors set out to investigate or achieve
3. **Methodology** – Approach, data, methods, and key design choices (be specific)
4. **Main Findings** – Core results, with numbers or outcomes when available
5. **Conclusions & Implications** – Takeaways, limitations, and suggested future work

Guidelines:
- Use plain language; avoid unnecessary jargon
- Be precise: cite specific findings, metrics, or claims when relevant
- Aim for 250–450 words
- Preserve important terminology (e.g., model names, datasets)"""

    resp = client.chat.completions.create(
        model=settings.summarization_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Summarize this research paper:\n\n{truncated}"},
        ],
        max_tokens=1000,
    )
    return (resp.choices[0].message.content or "").strip()
