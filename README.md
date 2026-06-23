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

## System starten

**Alle Komponenten starten:**
```bash
python 04_System/Scripts/start_ai_os.py
```

**Oder einzeln:**
```bash
python 04_System/Scripts/ai_os_dashboard.py   # Dashboard (Port 5000)
python 04_System/Scripts/api_gateway.py        # API Gateway (Port 5100)
python 04_System/Scripts/agent_system.py       # Agent System (Port 5300)
python 04_System/Scripts/workflow_engine.py    # Workflow Engine (Port 5200)
python 04_System/Scripts/monitoring_service.py # Monitoring (Port 5400)
```

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

Der einfachste Weg, mit der KI-Fabrik zu interagieren:

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

## Monitoring

Das Monitoring ist unter http://localhost:5400/status erreichbar und zeigt:
- Health-Status aller 7 Dienste + Ollama
- Latenz und Uptime
- Logs und Traces
- System-Metriken

## Ordnerstruktur

| Ordner | Inhalt | Zweck |
|--------|--------|-------|
| `00_Knowledge/` | Persönliches Wissen, Projekte, Referenzen, Wiki | Wissensdatenbank für RAG |
| `01_Connections/` | MCP, CLI und API Konfigurationen | Verbindungen zu externen Tools |
| `02_Skills/` | Wiederverwendbare Arbeitsanleitungen | Prozesse einmal erklärt, immer nutzbar |
| `03_Routines/` | Automatisierte Abläufe | Zeitgesteuerte Aufgaben |
| `04_System/` | Skripte, Logs, Templates | Systemdateien und Hilfsmittel |
| `06_KI-Gedächtnis/` | Architektur-Dokumentation | KI-Fabrik Design |

## Schnellstart

### Als Obsidian Vault öffnen
1. Obsidian starten
2. "Open folder as vault" wählen
3. Diesen Ordner (`AI-OS`) auswählen
4. Fertig!

### Mit Claude Desktop nutzen
1. Claude Desktop öffnen
2. Auf "Select Project" / "Projekt auswählen" klicken
3. Diesen Ordner wählen
4. Claude hat jetzt Zugriff auf alles

### Per SSH auf Server
```bash
ssh root@[SERVER-IP]
cd /AI-OS
claude
```

## Wichtige Dateien

| Datei | Zweck |
|-------|-------|
| `CLAUDE.md` | Zentrale Systemanweisungen für Claude - **Immer aktuell halten!** |
| `README.md` | Diese Datei - Übersicht des Systems |
| `.gitignore` | Dateien, die nicht ins Repository gehören |

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

## Skills verwenden

Skills findest du in `02_Skills/Active/`. Um einen Skill zu nutzen:

1. In Claude: "Nutze den Skill [Name] für [Aufgabe]"
2. Oder direkt den Inhalt des Skills referenzieren

## Routinen einrichten

Lokale Routinen werden in `03_Routines/Local/` definiert und über Cronjobs ausgeführt.

Remote Routinen laufen auf dem Server und werden über GitHub Actions oder Server-Cronjobs gesteuert.

## Verbindungen hinzufügen

Neue Tool-Verbindungen werden in `01_Connections/` konfiguriert.

## Sicherheit

- **API-Keys und Secrets** gehören NIE ins Git-Repository
- Sie werden in `01_Connections/APIs/Secrets/` gespeichert (`.gitignore` schützt diese)
- Alternativ: Umgebungsvariablen nutzen

---

*Erstellt mit ♥ und Claude*
