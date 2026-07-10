"""Zentrale Konfiguration (pydantic-settings, Env-Prefix AIOS_)."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AIOS_", env_file=".env", extra="ignore")

    app_name: str = "AI-OS Backend"
    version: str = "0.1.0"

    # LLM-Anbindung (Ollama lokal, LiteLLM als OpenAI-kompatibler Fallback)
    ollama_url: str = "http://localhost:11434"
    litellm_url: str = "http://localhost:4000/v1"
    chat_model: str = "llama3"
    embedding_model: str = "nomic-embed-text"

    # RAG-Parameter
    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k: int = 4

    # Vector Store: "json" (Datei, kein Server noetig) oder "qdrant" (Docker :6333)
    vector_backend: Literal["json", "qdrant"] = "json"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "aios"

    # Persistenz
    data_dir: Path = Path(__file__).resolve().parents[2] / "data"


@lru_cache
def get_settings() -> Settings:
    return Settings()
