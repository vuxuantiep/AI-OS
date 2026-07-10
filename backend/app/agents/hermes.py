"""Hermes — der autonome Mitarbeiter des AI-OS.

Hermes kombiniert drei Fähigkeiten zu einem "Mitarbeiter":

1. learn():  liest die Projekt-Dokumente (CLAUDE.md, Roadmap, Architektur ...)
             in die RAG-Wissensbasis ein — er kennt Ziele und bisherige Arbeit.
2. ask():    beantwortet Fragen über das Projekt aus diesem Wissen.
3. work():   erledigt Aufträge autonom: holt sich Projektkontext per Vektorsuche,
             arbeitet ihn durch die Agenten-Pipeline (Planner → Developer →
             Reviewer) ab und schreibt das Ergebnis als Journal-Eintrag zurück
             in die Wissensbasis — Hermes lernt aus seiner eigenen Arbeit.
"""

from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from app.agents.pipeline import AgentPipeline, AgentStep
from app.models.rag import RagAnswer, RetrievedChunk
from app.rag.service import RagService

JOURNAL_PREFIX = "hermes_journal"


class HermesLearnReport(BaseModel):
    learned: list[str]
    skipped: list[str]
    missing: list[str]


class HermesWorkResult(BaseModel):
    briefing: str
    context_sources: list[RetrievedChunk]
    steps: list[AgentStep]
    final: str
    journal_filename: str


class HermesStatus(BaseModel):
    name: str = "Hermes"
    role: str = "Autonomer Mitarbeiter des AI-OS"
    known_documents: list[str]
    journal_entries: int


class HermesAgent:
    def __init__(
        self,
        rag: RagService,
        pipeline: AgentPipeline,
        project_root: Path,
        knowledge_files: list[str],
    ) -> None:
        self._rag = rag
        self._pipeline = pipeline
        self._project_root = project_root
        self._knowledge_files = knowledge_files

    async def learn(self) -> HermesLearnReport:
        """Projekt-Dokumente in die Wissensbasis einlesen (idempotent)."""
        known = {doc.filename for doc in self._rag.list_documents()}
        learned: list[str] = []
        skipped: list[str] = []
        missing: list[str] = []

        for relative in self._knowledge_files:
            path = self._project_root / relative
            if not path.is_file():
                missing.append(relative)
                continue
            if relative in known:
                skipped.append(relative)
                continue
            await self._rag.ingest(
                filename=relative, data=path.read_bytes(), media_type="text/markdown"
            )
            learned.append(relative)

        return HermesLearnReport(learned=learned, skipped=skipped, missing=missing)

    async def ask(self, question: str, top_k: int = 4) -> RagAnswer:
        """Frage zum Projekt beantworten — aus Zielen, Roadmap und Journal."""
        return await self._rag.query(question, top_k)

    async def work(self, briefing: str, top_k: int = 4) -> HermesWorkResult:
        """Einen Auftrag autonom erledigen und das Ergebnis ins Journal lernen."""
        sources = await self._rag.retrieve(briefing, top_k)
        context = "\n\n".join(f"[{source.filename}]\n{source.text}" for source in sources)
        briefing_with_context = (
            f"Projektkontext aus der Wissensbasis:\n{context}\n\nAuftrag: {briefing}"
            if sources
            else briefing
        )
        result = await self._pipeline.run(briefing_with_context)

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        journal_filename = f"{JOURNAL_PREFIX}_{timestamp}.md"
        journal = (
            f"# Hermes-Journal: {briefing}\n\n"
            f"Erledigt am {datetime.now(UTC).isoformat()}\n\n"
            + "\n\n".join(f"## {step.role}\n\n{step.output}" for step in result.steps)
        )
        await self._rag.ingest(
            filename=journal_filename,
            data=journal.encode("utf-8"),
            media_type="text/markdown",
        )

        return HermesWorkResult(
            briefing=briefing,
            context_sources=sources,
            steps=result.steps,
            final=result.final,
            journal_filename=journal_filename,
        )

    def status(self) -> HermesStatus:
        documents = [doc.filename for doc in self._rag.list_documents()]
        return HermesStatus(
            known_documents=documents,
            journal_entries=sum(1 for name in documents if name.startswith(JOURNAL_PREFIX)),
        )
