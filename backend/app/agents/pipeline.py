"""Sequenzielle Multi-Agent-Pipeline (Planner → Developer → Reviewer).

Bewusst schlank gehalten: Das ist die Vorstufe zu LangGraph (Roadmap Phase 4).
Die Rollen entsprechen den LEGO-Figuren der KI-Fabrik; jeder Schritt erhält
das Ergebnis des vorherigen als Input.
"""

from pydantic import BaseModel

from app.services.llm_service import LLMClient


class AgentStep(BaseModel):
    role: str
    output: str


class PipelineResult(BaseModel):
    briefing: str
    steps: list[AgentStep]
    final: str


ROLES: list[tuple[str, str]] = [
    (
        "Planner",
        "Du bist der Planner-Agent der KI-Fabrik. Zerlege das Briefing in einen "
        "kurzen, nummerierten Umsetzungsplan (max. 5 Schritte). Antworte auf Deutsch.",
    ),
    (
        "Developer",
        "Du bist der Developer-Agent. Setze den Plan konkret um: liefere Code oder "
        "die inhaltliche Lösung, knapp und lauffähig. Antworte auf Deutsch.",
    ),
    (
        "Reviewer",
        "Du bist der Reviewer-Agent. Prüfe das Ergebnis auf Fehler und Lücken, "
        "verbessere es und liefere die finale Fassung. Antworte auf Deutsch.",
    ),
]


class AgentPipeline:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    async def run(self, briefing: str) -> PipelineResult:
        steps: list[AgentStep] = []
        previous = briefing
        for role, system in ROLES:
            prompt = (
                f"Briefing: {briefing}\n\nErgebnis des vorherigen Schritts:\n{previous}"
                if steps
                else briefing
            )
            output = await self._llm.chat(prompt, system=system)
            steps.append(AgentStep(role=role, output=output))
            previous = output
        return PipelineResult(briefing=briefing, steps=steps, final=previous)
