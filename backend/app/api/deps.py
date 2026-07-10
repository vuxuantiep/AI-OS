"""FastAPI-Dependencies: greifen auf die in app.state registrierten Services zu."""

from fastapi import Request

from app.agents.hermes import HermesAgent
from app.agents.pipeline import AgentPipeline
from app.rag.service import RagService
from app.services.llm_service import LLMClient


def get_llm(request: Request) -> LLMClient:
    llm: LLMClient = request.app.state.llm
    return llm


def get_rag(request: Request) -> RagService:
    rag: RagService = request.app.state.rag
    return rag


def get_pipeline(request: Request) -> AgentPipeline:
    pipeline: AgentPipeline = request.app.state.pipeline
    return pipeline


def get_hermes(request: Request) -> HermesAgent:
    hermes: HermesAgent = request.app.state.hermes
    return hermes
