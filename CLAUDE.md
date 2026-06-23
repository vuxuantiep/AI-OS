# CLAUDE.md - Systemanweisungen für mein AI Operating System V2

## Überblick
Dies ist meine **KI-Fabrik V2** - ein vollständiges Multi-Agent-System mit Workflow-Engine, RAG-Pipeline und Monitoring. Es verbindet:
- **Ollama** (lokale KI-Modelle) als KI-Engine
- **7 spezialisierte KI-Agenten** (Orchestrator, Research, Code, Writer, Analysis, Planner, Memory)
- **Workflow Engine** für DAG-basierte Aufgaben-Pipelines
- **API Gateway** als zentraler Einstiegspunkt
- **RAG Pipeline** mit Vektorsuche über die Wissensdatenbank
- **Monitoring** mit Health-Checks, Metriken und Logging
- **Web Dashboard** (Flask) als Benutzeroberfläche
- **MCP Server** für AI-Clients (Claude Desktop, etc.)

## Architektur (6 Schichten)

```
┌─────────────────────────────────────────────────────────────┐
│                    🌐 Interface Layer                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   Dashboard  │  │  API Gateway │  │  MCP Server V2   │   │
│  │   (Port 5000)│  │  (Port 5100) │  │  (Port 5001)     │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘   │
├─────────┼────────────────┼───────────────────┼─────────────┤
│         │    🔄 Orchestration Layer           │             │
│  ┌──────┴──────────────────┴───────────────────┴────────┐  │
│  │              Workflow Engine (Port 5200)              │  │
│  │  ┌─────────────────┐  ┌──────────────────────────┐   │  │
│  │  │ Task Orchestrator│  │  Pipeline Manager        │   │  │
│  │  └────────┬────────┘  └───────────┬──────────────┘   │  │
│  └───────────┼───────────────────────┼──────────────────┘  │
├──────────────┼───────────────────────┼────────────────────┤
│              │    🤖 Agent Layer     │                     │
│  ┌───────────┴───────────────────────┴──────────────────┐ │
│  │              Multi-Agent System (Port 5300)           │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │ │
│  │  │Orchestr. │ │ Research │ │  Code    │ │ Writer │  │ │
│  │  │ Agent    │ │ Agent    │ │  Agent   │ │ Agent  │  │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘  │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐     │ │
│  │  │Analysis  │ │ Planner  │ │  Memory Agent    │     │ │
│  │  │ Agent    │ │ Agent    │ │  (Context Mgr)   │     │ │
│  │  └──────────┘ └──────────┘ └──────────────────┘     │ │
│  └─────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────┤
│                    📚 RAG Pipeline (Port 5002)            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │Ingestion │ │ Chunking │ │Embedding │ │  Hybrid    │  │
│  │ Pipeline │ │ Strategy │ │  Service │ │  Search    │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │
├──────────────────────────────────────────────────────────┤
│                    📊 Monitoring Layer                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ Metrics  │ │ Logging  │ │ Health   │ │  Tracing   │  │
│  │ Collector│ │ Service  │ │ Checks   │ │  Service   │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │
├──────────────────────────────────────────────────────────┤
│                    ⚙️ Infrastructure Layer                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │  Ollama  │ │ Vector DB│ │ File Sys │ │  Queue     │  │
│  │(Port 11434)│(JSON/Chroma)│(Knowledge)│ │  (In-Mem) │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Lokale KI-Komponenten

### Verfügbare KI-Modelle (Ollama)
| Modell | Größe | Verwendung |
|--------|-------|------------|
| llama3 | 4.7 GB | Allgemeine Aufgaben, Chat |
| mistral | 4.4 GB | Chat, Textgenerierung |
| deepseek-coder | 776 MB | Code-Generierung |
| qwen2.5-coder | 4.7 GB | Code & Entwicklung |
| gemma4 | 9.6 GB | Fortgeschrittene Aufgaben |
| qwen3.6 | 23 GB | Große Modelle, komplexe Analyse |
| llama2 | 3.8 GB | Backup-Modell |

### System starten
**Einfach (empfohlen):**
```bash
# Dashboard starten (automatisch im Browser öffnen)
python 04_System/Scripts/ai_os_dashboard.py
```

**Alle Komponenten:**
```bash
python 04_System/Scripts/start_ai_os.py
```

**Windows:** Doppelklick auf `04_System/Scripts/start_ai_os.bat`

### Ports & URLs (KI-Fabrik V2)
| Komponente | Port | URL |
|-----------|------|-----|
| Dashboard | 5000 | http://localhost:5000 |
| MCP Server | 5001 | http://localhost:5001 |
| RAG Pipeline | 5002 | http://localhost:5002 |
| **API Gateway** | **5100** | **http://localhost:5100** |
| **Workflow Engine** | **5200** | **http://localhost:5200** |
| **Agent System** | **5300** | **http://localhost:5300** |
| **Monitoring** | **5400** | **http://localhost:5400/status** |
| Ollama API | 11434 | http://localhost:11434 |

## Meine Identität & Arbeitsweise

### Über mich
- Name: [HIER EINTRAGEN]
- Rolle/Beruf: [HIER EINTRAGEN]
- Hauptfokus: [HIER EINTRAGEN]
- Arbeitsstil: [HIER EINTRAGEN - z.B. strukturiert, kreativ, schnell, gründlich]

### Sprache & Kommunikation
- Primärsprache: Deutsch
- Sekundärsprache: [HIER EINTRAGEN falls vorhanden]
- Schreibstil: [HIER EINTRAGEN - z.B. professionell, locker, prägnant, ausführlich]

## Wichtige Arbeitsregeln

### 1. Git-Synchronisation (KRITISCH)
**Vor JEDER Arbeit:**
```bash
git pull
```
**Nach JEDER Arbeit:**
```bash
git add .
git commit -m "[beschreibende Nachricht]"
git push
```

### 2. Dateiorganisation
- Neue Notizen in `00_Knowledge/03_Work_In_Progress/Active/`
- Fertige Projekte nach `00_Knowledge/02_Business/Projects/`
- Archiviertes nach `00_Knowledge/05_Archive/`

### 3. Links & Verknüpfungen
- Nutze Obsidian-Links `[[Dateiname]]` für interne Verbindungen
- Tagge wichtige Dateien mit #wichtig #urgent #idee

### 4. Secrets & Sicherheit
- API-Keys und Passwörter NIE direkt in Dateien speichern
- Stattdessen in `01_Connections/APIs/Secrets/` (wird nicht versioniert)
- Oder Umgebungsvariablen verwenden

## Verbindungen & Tools

### Aktive Verbindungen (KI-Fabrik V2)
- [x] **Ollama** (lokale KI-Modelle) - Port 11434
- [x] **AI-OS Dashboard** (Web-UI) - Port 5000
- [x] **AI-OS MCP Server** (für AI-Clients) - Port 5001
- [x] **RAG Pipeline** (Vektorsuche) - Port 5002
- [x] **API Gateway** (zentraler Einstieg) - Port 5100
- [x] **Workflow Engine** (DAG-Pipelines) - Port 5200
- [x] **Agent System** (7 KI-Agenten) - Port 5300
- [x] **Monitoring** (Health/Metriken) - Port 5400
- [x] GitHub (CLI installiert)
- [ ] Google Workspace (Gmail, Calendar, Drive)

### MCP Server
- [x] **AI-OS eigener MCP Server** (http://localhost:5001/mcp)

## Skill-Nutzung

Wenn ich einen Skill aufrufe, erwarte ich:
1. Klare Bestätigung, welcher Skill genutzt wird
2. Schritt-für-Schritt Ausführung
3. Bei Fehlern: Sofortige Rückmeldung und Alternativvorschläge
4. Am Ende: Zusammenfassung der Ergebnisse

## Routinen & Automatisierung

### Lokale Routinen (laufen auf diesem PC)
- [x] **AI-OS Dashboard starten** → `03_Routines/Local/ROUTINE_start_ai_os.md`
- [ ] [HIER EINTRAGEN]

### Remote Routinen (laufen auf Server)
- [ ] [HIER EINTRAGEN]

## MCP Kommandos (für AI-Clients)

Der MCP-Server unter Port 5001 bietet diese Tools:
- `chat` - Chat mit lokaler KI
- `generate` - Text generieren
- `summarize` - Texte zusammenfassen
- `search_knowledge` - Wissensdatenbank durchsuchen
- `list_models` - Verfügbare Modelle auflisten

## Dateinamenskonventionen

- Meetings: `YYYY-MM-DD_Meeting_[Thema].md`
- Projekte: `Project_[Name].md`
- Notizen: `YYYY-MM-DD_[Stichwort].md`
- Skills: `SKILL_[Name].md`
- Routinen: `ROUTINE_[Name].md`

## Wichtige Orte im Vault

- Tagesnotizen: `00_Knowledge/03_Work_In_Progress/Active/`
- Projekte: `00_Knowledge/02_Business/Projects/`
- Aktive Skills: `02_Skills/Active/`
- Templates: `04_System/Templates/`
- Skripte: `04_System/Scripts/`
- Wiki/Referenzen: `00_Knowledge/04_Reference/Wiki/`
- Vektordatenbank: `04_System/Data/vector_store.json`

---

*Letzte Aktualisierung: 19.06.2026*
*Diese Datei wird regelmäßig aktualisiert, um die Arbeitsweise zu verbessern*
