"""Test-Fixtures: Fake-LLM (deterministisch, ohne Netzwerk) + App mit Test-Services."""

import hashlib
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.agents.pipeline import AgentPipeline
from app.main import create_app
from app.rag.service import RagService
from app.rag.vector_store import JsonVectorStore


class FakeLLMClient:
    """Deterministischer Ersatz für Ollama: Hash-basierte Embeddings, Echo-Chat."""

    chat_model = "fake-model"

    async def chat(self, prompt: str, system: str | None = None, model: str | None = None) -> str:
        return f"ANTWORT auf: {prompt[:80]}"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    @staticmethod
    def _vector(text: str) -> list[float]:
        # Wort-Hash-Histogramm: gleiche Wörter → ähnliche Vektoren
        vector = [0.0] * 64
        for word in text.lower().split():
            digest = hashlib.sha256(word.encode()).digest()
            vector[digest[0] % 64] += 1.0
        return vector


@pytest.fixture
def fake_llm() -> FakeLLMClient:
    return FakeLLMClient()


@pytest.fixture
def client(tmp_path: Path, fake_llm: FakeLLMClient) -> Iterator[TestClient]:
    app = create_app()
    with TestClient(app) as test_client:
        store = JsonVectorStore(tmp_path / "vector_store.json")
        app.state.llm = fake_llm
        app.state.rag = RagService(llm=fake_llm, store=store, chunk_size=200, chunk_overlap=40)
        app.state.pipeline = AgentPipeline(llm=fake_llm)
        yield test_client
