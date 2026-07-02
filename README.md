# 🏭 KI-Fabrik V2 - Multi-Agent System

Willkommen in meiner **KI-Fabrik V2** – einem vollständigen Multi-Agent-System mit Workflow-Engine, RAG-Pipeline und Monitoring.

## Was ist das?

Die KI-Fabrik V2 ist ein **6-schichtiges Multi-Agent-System**, das auf Ollama (lokale KI-Modelle) aufbaut:

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
│  └──────────────────────────────────────────────────────┘  │
├───────────────────────────────────────────────────────────┤
│              🤖 Agent Layer (Port 5300)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│  │Orchestr. │ │ Research │ │  Code    │ │ Writer/Plan/ │ │
│  │ Agent    │ │ Agent    │ │  Agent   │ │ Memory/Analy │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘ │
├───────────────────────────────────────────────────────────┤
│              📚 RAG Pipeline (Port 5002)                   │
├───────────────────────────────────────────────────────────┤
│              📊 Monitoring Layer (Port 5400)               │
├───────────────────────────────────────────────────────────┤
│              ⚙️ Infrastructure (Ollama Port 11434)         │
└───────────────────────────────────────────────────────────┘
```

## Schnellstart

### 🚀 Erste Schritte

1. **System starten:**
   ```bash
   python 04_Infrastruktur/Runtime/start_ai_os.py
   ```

2. **CLAUDE.md ausfüllen:**
   Öffne `CLAUDE.md` und trag deinen Namen, deine Rolle und deinen Arbeitsstil ein.

3. **Obsidian Vault öffnen:**
   - Obsidian starten
   - "Open folder as vault" wählen
   - Diesen Ordner (`AI-OS`) auswählen

4. **Git initialisieren (bei Bedarf):**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

### Einzelne Komponenten starten
```bash
python 04_Infrastruktur/Gateway/ai_os_dashboard.py   # Dashboard (Port 5000)
python 04_Infrastruktur/Gateway/api_gateway.py       # API Gateway (Port 5100)
python 05_Agenten/agent_system.py                    # Agent System (Port 5300)
python 05_Agenten/workflow_engine.py                 # Workflow Engine (Port 5200)
python 08_Monitoring/monitoring_service.py           # Monitoring (Port 5400)
```

### Mit Claude Desktop nutzen
1. Claude Desktop öffnen
2. Auf "Select Project" / "Projekt auswählen" klicken
3. Diesen Ordner wählen
4. Fertig!

## Architektur

| Schicht | Komponente | Port | Beschreibung |
|---------|-----------|------|-------------|
| 🌐 Interface | Dashboard | 5000 | Web UI |
| 🌐 Interface | MCP Server | 5001 | AI-Client Interface |
| 🌐 Interface | **API Gateway** | **5100** | **Zentraler Einstiegspunkt** |
| 🔄 Orchestrierung | **Workflow Engine** | **5200** | **DAG-basierte Pipelines** |
| 🤖 Agenten | **Agent System** | **5300** | **7 KI-Agenten** |
| 📚 Wissen | RAG Pipeline | 5002 | Vektorsuche |
| 📊 Monitoring | **Monitoring** | **5400** | **Health/Metriken** |
| ⚙️ Infrastruktur | Ollama | 11434 | Lokale KI-Modelle |

## 7 KI-Agenten

| Agent | Aufgabe | Modell |
|-------|---------|--------|
| **Orchestrator** | Koordiniert alle Agenten | llama3 |
| **Research** | Informationssuche & Recherche | llama3 |
| **Code** | Code-Generierung & Analyse | qwen2.5-coder |
| **Writer** | Texterstellung & Dokumentation | llama3 |
| **Analysis** | Datenanalyse & Reports | llama3 |
| **Planner** | Planung & Strategie | llama3 |
| **Memory** | Kontext- & Gedächtnisverwaltung | llama3 |

## API Gateway (Zentraler Einstieg)

```bash
# Chat mit Orchestrator
curl -X POST http://localhost:5100/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Erstelle einen Bericht über KI-Trends"}'

# Task mit bestimmtem Agenten
curl -X POST http://localhost:5100/execute \
  -H "Content-Type: application/json" \
  -d '{"agent": "code", "task": "Schreibe ein Python-Skript"}'

# Orchestrierte Ausführung (mehrere Agenten)
curl -X POST http://localhost:5100/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"task": "Analysiere und dokumentiere das Projekt"}'

# Workflow starten
curl -X POST http://localhost:5100/workflow/run \
  -H "Content-Type: application/json" \
  -d '{"name": "Mein Workflow", "tasks": [{"name": "Recherche", "agent": "research", "prompt": "..."}]}'

# RAG Query
curl -X POST http://localhost:5100/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Was ist in meiner Wissensdatenbank zu KI?"}'
```

## Ordnerstruktur

```
AI-OS/
├── 00_Wissen/              ← Wissensdatenbank für RAG (Obsidian Vault)
│   ├── 01_Persönlich/      ← Infos, Ziele, Vorlieben
│   ├── 02_Projekte/        ← Kunden, Produkte, abgeschlossene Projekte
│   ├── 03_Aktuelles/       ← Aktuelle Arbeiten, Tagesnotizen, Backlog
│   ├── 04_Referenzen/      ← Recherche, Notizen, Wiki-Dokumente
│   ├── 05_Archiv/          ← Alte Notizen, abgeschlossenes
│   └── 06_Transkripte/     ← Gesprächsaufzeichnungen
├── 01_Verbindungen/        ← MCP, CLI und API Konfigurationen
├── 02_Fähigkeiten/         ← Wiederverwendbare Arbeitsanleitungen (inkl. Vorlagen)
├── 03_Abläufe/             ← Automatisierte Routinen
├── 04_Infrastruktur/       ← Gateway, Runtime, Config, Architektur-Dokumentation
├── 05_Agenten/             ← Agentenlayer (Agent-System, Workflow-Engine)
├── 06_Gedächtnis/          ← Memory-Layer (RAG-Indexer, Wissenskategorien)
├── 07_Sicherheit/          ← Security, Compliance
├── 08_Monitoring/          ← Health-Checks, Metriken, Logs
├── 09_Backup-Recovery/     ← Backup-Strategie, Disaster Recovery
├── 10_Business/            ← Geschäftsprojekte
└── README.md               ← Diese Datei
    AGENTS.md               ← Claude-Systemanweisungen (Ordner-Kontext)
    CLAUDE.md               ← Zentrale Systemanweisungen
    AI-OS.code-workspace    ← VS Code Workspace
```

## Wissen aufbauen

So startest du mit deinem persönlichen Wissensspeicher:

1. **Profil anlegen:** `00_Wissen/01_Persönlich/`
2. **Projekt starten:** `00_Wissen/02_Projekte/`
3. **Tagesnotiz:** `00_Wissen/03_Aktuelles/Aktiv/`
4. **Referenz speichern:** `00_Wissen/04_Referenzen/`

Nutze immer die Vorlagen aus `02_Fähigkeiten/Vorlagen/` für neue Notizen und Projekte.

## Fähigkeiten (Skills)

Skills findest du in `02_Fähigkeiten/Aktiv/`. Um einen Skill zu nutzen:
1. In Claude: "Nutze den Skill [Name] für [Aufgabe]"
2. Oder direkt den Inhalt des Skills referenzieren

## Abläufe (Routines)

- **Lokale Routinen:** `03_Abläufe/Lokal/` – werden auf diesem PC ausgeführt
- **Remote Routinen:** `03_Abläufe/Remote/` – laufen auf dem Server

## Verbindungen

Neue Tool-Verbindungen werden in `01_Verbindungen/` konfiguriert:
- **APIs:** Externe API-Zugänge
- **CLI:** Kommandozeilen-Tools
- **MCP:** MCP-Server-Verbindungen

## Git-Workflow

**Vor Arbeit beginnen:**
```bash
git pull
```

**Nach Arbeit beenden:**
```bash
git add .
git commit -m "Beschreibung der Änderung"
git push
```

## Wichtige Dateien

| Datei | Zweck |
|-------|-------|
| `CLAUDE.md` | Zentrale Systemanweisungen für Claude |
| `AGENTS.md` | Ordner-spezifische Anweisungen für KI-Agenten |
| `README.md` | Diese Datei – Übersicht des Systems |
| `.gitignore` | Ausgeschlossene Dateien für Git |

## Sicherheit

- **API-Keys und Secrets** gehören NIE ins Git-Repository
- Sie werden in `01_Verbindungen/APIs/Geheimnisse/` gespeichert (`.gitignore` schützt diese)
- Alternativ: Umgebungsvariablen nutzen

---

*Erstellt mit ♥ und Claude*