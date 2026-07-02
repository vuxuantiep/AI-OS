# AI-OS Architektur: Getrennte Ebenen

> Status: ✅ **Umgesetzt** (2026-07-02). Migration per `git mv` durchgeführt (Historie erhalten, außer bei
> `05_Produkte/` und `06_AI-Fabrik/` — die waren nie committed, daher reines Verschieben ohne History).
> Offene Punkte wurden mit den ⭐-Vorschlägen entschieden: n8n → `03_Abläufe/Remote/`,
> Vorlagen → `02_Fähigkeiten/Vorlagen/`.

## Warum

`04_System/Skripte/` vermischt aktuell mehrere Ebenen in einem Ordner: Agent-Code
(`agent_system.py`, `workflow_engine.py`), Infrastruktur/Gateway (`ai_os_dashboard.py`,
`api_gateway.py`, `mcp_server.py`), Memory (`knowledge_agent.py`) und Monitoring
(`monitoring_service.py`) liegen alle nebeneinander. `05_Produkte/` und `06_AI-Fabrik/` sind zwei
getrennte Business-Ordner ohne gemeinsamen Oberbegriff.

## Vorgeschlagene Struktur

```
AI-OS/
├── 00_Wissen/            Obsidian Vault — Rohwissen, Notizen (unverändert)
├── 01_Verbindungen/      APIs, CLI, MCP-Client-Configs (unverändert)
├── 02_Fähigkeiten/       Skills (unverändert)
├── 03_Abläufe/           Routinen/Automatisierung (unverändert)
│
├── 04_Infrastruktur/     Betriebssystem-Ebene: Gateway, Config, Bootstrap, Deployment
│   ├── Config/
│   ├── Gateway/          ai_os_dashboard.py, api_gateway.py, mcp_server.py
│   ├── Runtime/          start_ai_os.py, start_ai_os.bat, requirements.txt
│   └── Dokumentation/    Architektur-Docs, Git-Workflow
│
├── 05_Agenten/           Agentenlayer — klar getrennt von Infrastruktur
│   ├── agent_system.py
│   ├── workflow_engine.py
│   └── Rollen/           (künftig: CEO/CTO/Developer/... Configs)
│
├── 06_Gedächtnis/        Memory-Layer (RAG/Indexer — NICHT der Vault selbst!)
│   ├── knowledge_agent.py
│   ├── Business-Knowledge/    Produkte, Kunden, Strategien
│   ├── Technical-Knowledge/   APIs, Docker, FastAPI, Python
│   ├── Agent-Knowledge/       Rollen, Fähigkeiten, Grenzen
│   ├── Project-Knowledge/     Entscheidungen, ADRs, Architektur
│   ├── Memory/
│   │   ├── Short-Memory/      Kurzfristiger Session-Kontext
│   │   ├── Long-Memory/       Dauerhaftes, konsolidiertes Wissen
│   │   └── Episodic-Memory/   Konkrete vergangene Ereignisse
│   ├── Prompt-Library/
│   ├── SOP-Library/
│   └── Vector-Database/       vector_store.json (bewusst getrennt pro Kategorie einzubetten,
│                               statt alles in einem Index zu vermischen)
│
├── 07_Sicherheit/        Security, Vault/Secrets-Policies, Compliance (DSGVO/AI Act)
│                         (aktuell leer — Geheimnisse liegen weiter in
│                          01_Verbindungen/APIs/Geheimnisse/)
│
├── 08_Monitoring/        Health-Checks, Metriken
│   ├── monitoring_service.py
│   └── Logs/
│
├── 09_Backup-Recovery/   Backup-Strategie + Disaster-Recovery-Playbooks (aktuell leer)
│
└── 10_Business/          Alle Geschäftsprojekte an einem Ort
    ├── Lokal-Private-LLM-App/   ← aus 05_Produkte/
    └── CEO-Dashboard/            ← aus 06_AI-Fabrik/ (Backend+Frontend)
```

## Migrations-Tabelle (jede Datei bekommt einen konkreten neuen Platz)

| Aktuell | Neu | Begründung |
|---|---|---|
| `04_System/Config/` | `04_Infrastruktur/Config/` | Infra-Konfiguration |
| `04_System/Skripte/ai_os_dashboard.py` | `04_Infrastruktur/Gateway/` | Interface Layer |
| `04_System/Skripte/api_gateway.py` | `04_Infrastruktur/Gateway/` | Interface Layer |
| `04_System/Skripte/mcp_server.py` | `04_Infrastruktur/Gateway/` | Interface Layer |
| `04_System/Skripte/start_ai_os.py` / `.bat` | `04_Infrastruktur/Runtime/` | Bootstrap |
| `04_System/Skripte/requirements.txt` | `04_Infrastruktur/Runtime/` | Bootstrap |
| `04_System/Dokumentation/` | `04_Infrastruktur/Dokumentation/` | System-Doku |
| `04_System/Skripte/agent_system.py` | `05_Agenten/` | Agentenlayer |
| `04_System/Skripte/workflow_engine.py` | `05_Agenten/` | Orchestriert Agenten |
| `04_System/Skripte/knowledge_agent.py` | `06_Gedächtnis/` | Memory/RAG-Indexer |
| `04_System/Skripte/monitoring_service.py` | `08_Monitoring/` | Monitoring |
| `04_System/Logs/` | `08_Monitoring/Logs/` | Monitoring |
| `05_Produkte/Lokal_Private_LLM_App/` | `10_Business/Lokal-Private-LLM-App/` | Business |
| `06_AI-Fabrik/` | `10_Business/CEO-Dashboard/` | Business |

## Entscheidungen (vormals offene Punkte)

1. **`n8n-Lead-Funnel.json`** → `03_Abläufe/Remote/n8n-Lead-Funnel.json`
2. **Vorlagen** (Daily Note, Project, Routine Templates) → `02_Fähigkeiten/Vorlagen/`

## Nach der Migration angepasst

- **Pfad-Tiefe in Skripten:** `AI_OS_ROOT = Path(__file__).parent.parent.parent` ging von einer festen
  2-Ebenen-Tiefe (`04_System/Skripte/`) aus. Nach dem Split liegen `agent_system.py`, `workflow_engine.py`
  (`05_Agenten/`) und `knowledge_agent.py` (`06_Gedächtnis/`) nur noch 1 Ebene tief — dort auf
  `.parent.parent` korrigiert. `ai_os_dashboard.py`, `api_gateway.py`, `mcp_server.py` blieben 2 Ebenen tief
  (`04_Infrastruktur/Gateway/`) und brauchten keine Anpassung.
- **`VECTOR_DB_PATH`** in `knowledge_agent.py` zeigte hart codiert auf das nie existierende
  `04_System/Data/vector_store.json` — jetzt auf `06_Gedächtnis/Vector-Database/vector_store.json`.
- `CLAUDE.md` wurde auf alle neuen Pfade aktualisiert (Start-Befehle, "Wichtige Orte im Vault").
- `05_Produkte/` und `06_AI-Fabrik/` waren nie committed (git zeigte sie als `??`) — daher per einfachem
  `mv` statt `git mv` verschoben; es gibt keine Git-Historie zu erhalten.
