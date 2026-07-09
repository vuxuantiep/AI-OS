"""FastAPI-Einstiegspunkt des AI-OS Backends.

Start:  uv run uvicorn app.main:app --reload --port 8000
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agents.pipeline import AgentPipeline
from app.api.routes import router
from app.core.config import get_settings
from app.rag.service import RagService
from app.rag.vector_store import JsonVectorStore
from app.services.llm_service import OllamaClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    llm = OllamaClient(
        base_url=settings.ollama_url,
        chat_model=settings.chat_model,
        embedding_model=settings.embedding_model,
    )
    store = JsonVectorStore(settings.data_dir / "vector_store.json")
    app.state.llm = llm
    app.state.rag = RagService(
        llm=llm,
        store=store,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    app.state.pipeline = AgentPipeline(llm=llm)
    try:
        yield
    finally:
        await llm.aclose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.version, lifespan=lifespan)
    app.include_router(router)
    return app


app = create_app()
