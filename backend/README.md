# AI-OS Backend — AI Engineering Platform

Das neue Backend des AI-OS nach dem Konzept "AI Engineering Platform":
FastAPI + Pydantic v2 + asyncio, verwaltet mit **uv**, geprüft mit **Ruff, MyPy (strict) und pytest**.

## Quickstart

```bash
cd backend
uv sync                                          # Dependencies installieren
uv run uvicorn app.main:app --reload --port 8000 # Server starten
```

API-Dokumentation (Swagger): http://localhost:8000/docs

## Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/health` | Status des Backends |
| GET | `/health/ollama` | Erreichbarkeit von Ollama |
| POST | `/api/chat` | Chat mit lokalem LLM (Ollama) |
| POST | `/api/documents/upload` | Dokument hochladen (PDF, DOCX, TXT, MD) → Parse → Chunk → Embed → Vector Store |
| GET | `/api/documents` | Ingestierte Dokumente auflisten |
| POST | `/api/rag/query` | RAG-Frage: Vektorsuche + LLM-Antwort mit Quellen |
| POST | `/api/agents/run` | Multi-Agent-Pipeline (Planner → Developer → Reviewer) |

## Voraussetzungen

- **Ollama** auf Port 11434 mit einem Chat-Modell (Standard: `llama3`)
- Embedding-Modell: `ollama pull nomic-embed-text`
- Konfiguration über Env-Variablen mit Prefix `AIOS_` (z.B. `AIOS_CHAT_MODEL=mistral`) oder `.env`

## Vector Store: JSON oder Qdrant

Standard ist der dependency-freie JSON-Store (`backend/data/vector_store.json`).
Für Qdrant (Roadmap Phase 3b):

```bash
docker compose up -d qdrant          # startet Qdrant auf Port 6333
AIOS_VECTOR_BACKEND=qdrant uv run uvicorn app.main:app --port 8000
```

Beide Implementierungen erfüllen denselben `VectorStore`-Vertrag
(`app/rag/vector_store.py`) und laufen durch dieselbe Test-Suite.

## Qualität (Phase 8 des Konzepts — von Anfang an dabei)

```bash
uv run ruff check .    # Linting
uv run ruff format .   # Formatierung
uv run mypy            # Statische Typprüfung (strict)
uv run pytest          # Tests (ohne Netzwerk, Fake-LLM)
```

## Struktur

```
backend/
├── app/
│   ├── main.py          # FastAPI-App + Lifespan (Service-Wiring)
│   ├── api/             # Routen + Dependencies
│   ├── core/            # Konfiguration (pydantic-settings)
│   ├── models/          # Pydantic-v2-Schemas
│   ├── services/        # LLM-Client (Ollama, async httpx)
│   ├── rag/             # Parser, Chunker, Vector Store, RAG-Service
│   └── agents/          # Multi-Agent-Pipeline (Vorstufe zu LangGraph)
└── tests/               # pytest + pytest-asyncio, Fake-LLM ohne Netzwerk
```

Die komplette Lernroadmap (8 Phasen) steht in [../docs/AI-Engineering-Roadmap.md](../docs/AI-Engineering-Roadmap.md).
