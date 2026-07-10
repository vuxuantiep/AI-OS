"""FastAPI-Einstiegspunkt des AI-OS Backends.

Start:  uv run uvicorn app.main:app --reload --port 8000
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agents.hermes import HermesAgent
from app.agents.pipeline import AgentPipeline
from app.api.routes import router
from app.core.config import Settings, get_settings
from app.rag.qdrant_store import QdrantVectorStore
from app.rag.service import RagService
from app.rag.vector_store import JsonVectorStore, VectorStore
from app.services.llm_service import OllamaClient


def build_vector_store(settings: Settings) -> VectorStore:
    """Composition Root für den Vector Store: AIOS_VECTOR_BACKEND entscheidet."""
    if settings.vector_backend == "qdrant":
        return QdrantVectorStore(settings.qdrant_url, settings.qdrant_collection)
    return JsonVectorStore(settings.data_dir / "vector_store.json")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    llm = OllamaClient(
        base_url=settings.ollama_url,
        chat_model=settings.chat_model,
        embedding_model=settings.embedding_model,
    )
    store = build_vector_store(settings)
    rag = RagService(
        llm=llm,
        store=store,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    pipeline = AgentPipeline(llm=llm)
    app.state.llm = llm
    app.state.rag = rag
    app.state.pipeline = pipeline
    app.state.hermes = HermesAgent(
        rag=rag,
        pipeline=pipeline,
        project_root=settings.project_root,
        knowledge_files=settings.hermes_knowledge_files,
    )
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
