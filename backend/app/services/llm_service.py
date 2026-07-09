"""Async-Client für Ollama (Chat + Embeddings).

Bewusst als Protocol + Implementierung getrennt, damit Tests einen
Fake-Client injizieren können, ohne dass Netzwerk nötig ist.
"""

from typing import Any, Protocol

import httpx


class LLMClient(Protocol):
    async def chat(
        self, prompt: str, system: str | None = None, model: str | None = None
    ) -> str: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...

    @property
    def chat_model(self) -> str: ...


class OllamaClient:
    """Spricht die native Ollama-API (Port 11434)."""

    def __init__(
        self,
        base_url: str,
        chat_model: str,
        embedding_model: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._chat_model = chat_model
        self._embedding_model = embedding_model
        self._client = client or httpx.AsyncClient(timeout=120.0)

    @property
    def chat_model(self) -> str:
        return self._chat_model

    async def chat(self, prompt: str, system: str | None = None, model: str | None = None) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": model or self._chat_model,
            "messages": messages,
            "stream": False,
        }
        response = await self._client.post(f"{self._base_url}/api/chat", json=payload)
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return str(data.get("message", {}).get("content", ""))

    async def embed(self, texts: list[str]) -> list[list[float]]:
        payload = {"model": self._embedding_model, "input": texts}
        response = await self._client.post(f"{self._base_url}/api/embed", json=payload)
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        embeddings: list[list[float]] = data.get("embeddings", [])
        return embeddings

    async def is_healthy(self) -> bool:
        try:
            response = await self._client.get(f"{self._base_url}/api/tags", timeout=3.0)
        except httpx.HTTPError:
            return False
        return response.status_code == 200

    async def aclose(self) -> None:
        await self._client.aclose()
