#!/usr/bin/env python3
"""
LangGraph-Engine für die KI-Fabrik (Port 5500).

Bildet die Scrum-Pipeline der KI-Fabrik als LangGraph-Zustandsgraph ab:

    planen ──▶ entwickeln ──▶ qualitaet ──▶ [BESTANDEN?] ──▶ ENDE
                    ▲                            │
                    └──── Nachbesserung (max. 1) ┘

Jeder Knoten ruft das LLM über den AI-OS LLM-Router auf (Ollama zuerst,
dann LM Studio / Pi-Gateway / Online-Fallbacks) — die Engine erbt damit
die komplette Ausfallsicherheit des KI-Gateways.

Endpunkte:
  GET  /health       – schneller Health-Check für Dashboard & Monitoring
  GET  /agent/info   – Beschreibung & Fähigkeiten
  GET  /graph        – Graph-Struktur als Mermaid-Diagramm (Text)
  POST /run          – {"briefing": "...", "model": "llama3"} führt den Graphen aus
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import TypedDict

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

AI_OS_ROOT = Path(os.environ.get("AI_OS_ROOT", Path(__file__).parent.parent))
sys.path.insert(0, str(AI_OS_ROOT / "04_Infrastruktur" / "Gateway"))
from llm_router import LLM_ROUTER  # noqa: E402

from fastapi import FastAPI  # noqa: E402
from pydantic import BaseModel  # noqa: E402
from langgraph.graph import StateGraph, START, END  # noqa: E402

PORT = int(os.environ.get("LANGGRAPH_PORT", 5500))
MAX_REWORK = 1


# ---------- Graph-Definition ----------

class FactoryState(TypedDict, total=False):
    briefing: str
    model: str
    plan: str
    concept: str
    review: str
    passed: bool
    rework_count: int
    path: list      # besuchte Knoten in Reihenfolge
    engines: dict   # Knoten -> genutzter Provider


def _llm(state, system, prompt, num_predict=700):
    text, provider = LLM_ROUTER.generate(
        system, prompt, model=state.get("model", "llama3"),
        temperature=0.4, num_predict=num_predict, timeout=300)
    return text, provider


def node_planen(state: FactoryState):
    text, provider = _llm(
        state,
        "Du bist der PLANNER AGENT der KI-Fabrik. Erstelle strukturierte, realistische "
        "Umsetzungspläne. Antworte auf Deutsch in Markdown.",
        "Erstelle einen kompakten Umsetzungsplan (Ziel, 3-5 Arbeitspakete, Risiken, "
        "grobe Zeitschätzung) für:\n\n" + state["briefing"])
    return {"plan": text, "path": state.get("path", []) + ["planen"],
            "engines": {**state.get("engines", {}), "planen": provider}}


def node_entwickeln(state: FactoryState):
    rework = state.get("rework_count", 0)
    extra = ""
    if state.get("review"):
        extra = ("\n\nNACHBESSERUNG: Die QA hat das letzte Konzept NICHT bestanden. "
                 "Behebe die genannten Punkte:\n" + state["review"][:1500])
    text, provider = _llm(
        state,
        "Du bist der CODE/DEV AGENT der KI-Fabrik. Erstelle technische Konzepte und "
        "Architektur-Vorschläge. Antworte auf Deutsch in Markdown.",
        "Erstelle auf Basis von Briefing und Plan ein kompaktes technisches Konzept "
        "(Architektur, Komponenten, Tech-Stack, MVP-Umfang):\n\nBRIEFING:\n"
        + state["briefing"] + "\n\nPLAN:\n" + state.get("plan", "")[:2500] + extra,
        num_predict=900)
    return {"concept": text, "path": state.get("path", []) + ["entwickeln"],
            "engines": {**state.get("engines", {}), "entwickeln": provider}}


def node_qualitaet(state: FactoryState):
    text, provider = _llm(
        state,
        "Du bist der ANALYSIS/QA AGENT der KI-Fabrik. Prüfe Konzepte kritisch auf Lücken "
        "und Risiken. Beginne deine Antwort zwingend mit genau einer Zeile "
        "'URTEIL: BESTANDEN' oder 'URTEIL: NICHT BESTANDEN'. Antworte auf Deutsch, kurz.",
        "Prüfe das folgende Konzept kritisch: Stärken, Top-3-Risiken, Verbesserungen, "
        "Gesamturteil. Erste Zeile: URTEIL wie vorgegeben.\n\nBRIEFING:\n"
        + state["briefing"] + "\n\nKONZEPT:\n" + state.get("concept", "")[:3000],
        num_predict=500)
    passed = "NICHT BESTANDEN" not in text[:80].upper()
    return {"review": text, "passed": passed,
            "rework_count": state.get("rework_count", 0) + (0 if passed else 1),
            "path": state.get("path", []) + ["qualitaet"],
            "engines": {**state.get("engines", {}), "qualitaet": provider}}


def route_qa(state: FactoryState):
    """QA-Schleife: nicht bestanden -> einmal zurück in die Entwicklung, dann Ende."""
    if not state.get("passed", True) and state.get("rework_count", 0) <= MAX_REWORK:
        return "entwickeln"
    return END


def build_graph():
    g = StateGraph(FactoryState)
    g.add_node("planen", node_planen)
    g.add_node("entwickeln", node_entwickeln)
    g.add_node("qualitaet", node_qualitaet)
    g.add_edge(START, "planen")
    g.add_edge("planen", "entwickeln")
    g.add_edge("entwickeln", "qualitaet")
    g.add_conditional_edges("qualitaet", route_qa, {"entwickeln": "entwickeln", END: END})
    return g.compile()


GRAPH = build_graph()

# ---------- FastAPI-Dienst ----------

app = FastAPI(title="AI-OS LangGraph Engine", version="1.0.0")


class RunRequest(BaseModel):
    briefing: str
    model: str = "llama3"


@app.get("/health")
async def health():
    return {"status": "ok", "service": "🕸️ LangGraph Engine", "version": "1.0.0",
            "graph_nodes": ["planen", "entwickeln", "qualitaet"],
            "timestamp": datetime.now().isoformat()}


@app.get("/agent/info")
async def agent_info():
    return {
        "id": "langgraph-engine",
        "name": "🕸️ LangGraph Engine",
        "description": "Führt die KI-Fabrik-Pipeline (Planung → Entwicklung → QA mit "
                       "Nachbesserungs-Schleife) als LangGraph-Zustandsgraph aus.",
        "capabilities": ["stategraph", "factory-pipeline", "qa-loop", "llm-router-fallback"],
        "endpoints": ["GET /health", "GET /agent/info", "GET /graph", "POST /run"],
    }


@app.get("/graph")
async def graph_diagram():
    return {"mermaid": GRAPH.get_graph().draw_mermaid()}


@app.post("/run")
async def run(req: RunRequest):
    if not req.briefing.strip():
        return {"success": False, "error": "Kein Briefing angegeben."}
    try:
        result = GRAPH.invoke({"briefing": req.briefing.strip()[:4000],
                               "model": req.model, "rework_count": 0,
                               "path": [], "engines": {}},
                              config={"recursion_limit": 12})
        return {
            "success": True,
            "passed": result.get("passed"),
            "rework_count": result.get("rework_count", 0),
            "path": result.get("path", []),
            "engines": result.get("engines", {}),
            "plan": result.get("plan", ""),
            "concept": result.get("concept", ""),
            "review": result.get("review", ""),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    print(f"🕸️ LangGraph Engine startet auf http://localhost:{PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
