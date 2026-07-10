from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse, RedirectResponse

from app.agents.hermes import (
    HermesAgent,
    HermesLearnReport,
    HermesStatus,
    HermesWorkResult,
)
from app.agents.pipeline import AgentPipeline, PipelineResult
from app.api.deps import get_hermes, get_llm, get_pipeline, get_rag
from app.core.config import get_settings
from app.models import ChatRequest, ChatResponse, DocumentMeta, RagAnswer, RagQuery
from app.rag.parser import UnsupportedFormatError
from app.rag.service import RagService
from app.services.llm_service import LLMClient, OllamaClient

router = APIRouter()

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


@router.get("/", include_in_schema=False)
async def index() -> RedirectResponse:
    return RedirectResponse(url="/ui")


@router.get("/ui", include_in_schema=False)
async def hermes_ui() -> FileResponse:
    """Hermes-Bedienoberfläche (Chat für Fragen und Aufträge)."""
    return FileResponse(STATIC_DIR / "hermes.html", media_type="text/html")


@router.get("/health")
async def health() -> dict[str, Any]:
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "version": settings.version}


@router.get("/health/ollama")
async def health_ollama(llm: Annotated[LLMClient, Depends(get_llm)]) -> dict[str, Any]:
    reachable = await llm.is_healthy() if isinstance(llm, OllamaClient) else True
    return {"ollama": "ok" if reachable else "unreachable"}


@router.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, llm: Annotated[LLMClient, Depends(get_llm)]) -> ChatResponse:
    answer = await llm.chat(body.message, system=body.system, model=body.model)
    return ChatResponse(answer=answer, model=body.model or llm.chat_model)


@router.post("/api/documents/upload", response_model=DocumentMeta)
async def upload_document(
    file: UploadFile, rag: Annotated[RagService, Depends(get_rag)]
) -> DocumentMeta:
    data = await file.read()
    try:
        return await rag.ingest(
            filename=file.filename or "upload.txt",
            data=data,
            media_type=file.content_type or "application/octet-stream",
        )
    except (UnsupportedFormatError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/api/documents", response_model=list[DocumentMeta])
async def list_documents(rag: Annotated[RagService, Depends(get_rag)]) -> list[DocumentMeta]:
    return rag.list_documents()


@router.post("/api/rag/query", response_model=RagAnswer)
async def rag_query(body: RagQuery, rag: Annotated[RagService, Depends(get_rag)]) -> RagAnswer:
    return await rag.query(body.question, body.top_k)


@router.post("/api/agents/run", response_model=PipelineResult)
async def run_pipeline(
    body: ChatRequest, pipeline: Annotated[AgentPipeline, Depends(get_pipeline)]
) -> PipelineResult:
    return await pipeline.run(body.message)


@router.post("/api/hermes/learn", response_model=HermesLearnReport)
async def hermes_learn(hermes: Annotated[HermesAgent, Depends(get_hermes)]) -> HermesLearnReport:
    """Hermes liest die Projekt-Dokumente (Ziele, Roadmap, bisherige Arbeit) ein."""
    return await hermes.learn()


@router.post("/api/hermes/ask", response_model=RagAnswer)
async def hermes_ask(
    body: RagQuery, hermes: Annotated[HermesAgent, Depends(get_hermes)]
) -> RagAnswer:
    """Frage an Hermes über Projekt, Ziele und bisherige Arbeit."""
    return await hermes.ask(body.question, body.top_k)


@router.post("/api/hermes/work", response_model=HermesWorkResult)
async def hermes_work(
    body: ChatRequest, hermes: Annotated[HermesAgent, Depends(get_hermes)]
) -> HermesWorkResult:
    """Auftrag an Hermes: kontextbewusst erledigen + Ergebnis ins Journal lernen."""
    return await hermes.work(body.message)


@router.get("/api/hermes/status", response_model=HermesStatus)
async def hermes_status(hermes: Annotated[HermesAgent, Depends(get_hermes)]) -> HermesStatus:
    return hermes.status()
