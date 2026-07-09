# AI-OS → AI Engineering Platform: Roadmap

Umsetzung des Lernkonzepts (Stellenprofil AI Engineer / Platform Engineer) direkt im AI-OS.
Jede Phase liefert ein echtes Feature **und** vermittelt genau die Technologien aus dem Anforderungsprofil.

Stand: 09.07.2026

## Phasen-Überblick

| Phase | Thema | Status | Ort im Repo |
|-------|-------|--------|-------------|
| 1 | Fundament: FastAPI, Pydantic v2, uv, Ruff, MyPy, pytest, asyncio | ✅ umgesetzt | `backend/` |
| 2 | Dokumentenplattform: Upload → Parsing → Chunking → Embeddings | ✅ umgesetzt (PDF, DOCX, TXT/MD) | `backend/app/rag/` |
| 3 | Vektordatenbank: JSON-Store mit Kosinus-Suche → Migration auf **Qdrant** | 🟡 JSON-Store fertig, Qdrant offen | `backend/app/rag/vector_store.py` |
| 4 | LangGraph: Multi-Agent-Workflow (CEO → Planner → Developer → Reviewer → Tester) | 🟡 sequenzielle Pipeline fertig, LangGraph-Migration offen | `backend/app/agents/pipeline.py`, bestehend: `05_Agenten/langgraph_engine.py` |
| 5 | Coding Agent: Tool Calling / Function Calling (read_file, write_file, run_python …) | ⬜ offen | `backend/app/agents/` |
| 6 | Knowledge Graph: Neo4j, Entitäten-/Beziehungsextraktion, Hybrid Search | ⬜ offen (bewusst später) | — |
| 7 | Cloud: Docker, GitHub Actions, AWS S3/Lambda/Bedrock, Terraform | ⬜ offen | `docker/`, `terraform/` (geplant) |
| 8 | Qualität: pytest, RAG-Evaluation (Relevanz/Treue), CI/CD | 🟡 pytest+MyPy+Ruff von Anfang an aktiv, Evaluation & CI offen | `backend/tests/` |

## Was Phase 1–3 bereits abdeckt (09.07.2026)

- **FastAPI + Pydantic v2 + asyncio**: komplettes async Backend (`backend/app/`), Settings über pydantic-settings (`AIOS_`-Env-Prefix)
- **uv**: Paketverwaltung (`backend/pyproject.toml`, `uv sync`)
- **Ruff + MyPy strict**: konfiguriert und fehlerfrei
- **pytest + pytest-asyncio**: 13 Tests, komplett ohne Netzwerk (Fake-LLM mit deterministischen Embeddings)
- **RAG-Pipeline**: `POST /api/documents/upload` (PDF/DOCX/TXT/MD → Chunking mit Überlappung → Ollama-Embeddings → Vector Store), `POST /api/rag/query` (Vektorsuche + Antwort mit Quellenangaben)
- **Multi-Agent-Grundlage**: `POST /api/agents/run` — Planner → Developer → Reviewer (LEGO-Rollen der KI-Fabrik)

## Nächste Schritte (Reihenfolge nach Konzept-Priorität)

1. **Qdrant** als zweite `VectorStore`-Implementierung (Docker-Service in `docker-compose.yml`), Interface ist schon dafür geschnitten
2. **LangGraph-Migration** der Agent-Pipeline: State Machine mit QA-Schleife und Human Approval — die bestehende `05_Agenten/langgraph_engine.py` als Vorbild, aber im neuen typisierten Backend
3. **Tool Calling** für den Developer-Agent (read_file, write_file, run_python, search_docs)
4. **Evaluation-Modul**: pro RAG-Antwort Frage/Chunks/Antwort/Score protokollieren (Relevanz, Treue, Latenz)
5. **Security Guardrails**: Prompt-Injection-Erkennung + PII-Filter vor jedem LLM-Aufruf
6. **Docker + GitHub Actions**: Backend containerisieren, CI mit ruff/mypy/pytest
7. **Terraform + AWS** (S3 für Dokumente, Bedrock als optionaler LLM-Provider über LiteLLM)
8. **Neo4j Knowledge Graph** als Erweiterung der Suche (Hybrid: Vektor + Graph)

## Verhältnis zum bestehenden System

Das neue `backend/` ersetzt das alte System nicht sofort — es ist die saubere Zielarchitektur.
Bestehende Dienste (Dashboard :5000, Gateway :5100, Agent-System :5300, LiteLLM :4000) laufen weiter;
das Backend läuft auf **Port 8000** und übernimmt Funktionen Schritt für Schritt.
Integration: Dashboard kann die neuen Endpunkte (`/api/rag/query`, `/api/agents/run`) direkt aufrufen.
