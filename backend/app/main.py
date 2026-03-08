"""FastAPI application entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings

# CORS: localhost for dev + any ALLOWED_ORIGINS from env for production
def _get_cors_origins() -> list[str]:
    origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
    if settings.allowed_origins:
        origins.extend(o.strip() for o in settings.allowed_origins.split(",") if o.strip())
    return origins


app = FastAPI(
    title="AI Research Paper Explainer",
    description="Upload PDFs, get summaries, and ask questions about papers.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
