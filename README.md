# 🏭 KI-Fabrik V2 - Multi-Agent System

Willkommen in meiner **KI-Fabrik V2** – einem vollständigen Multi-Agent-System mit Workflow-Engine, RAG-Pipeline und Monitoring.

## 🎯 Was ist das?

Die KI-Fabrik V2 ist ein **lokales KI-Betriebssystem** mit 7 spezialisierten Agenten, das auf Ollama aufbaut und volle Kontrolle über deine KI-Workflows gibt.

## ⚡ Schnellstart

### 🚀 Ein-Klick-Start (empfohlen)
```bash
python 04_Infrastruktur/Runtime/start_ai_os.py
```

### 🎨 Dashboard starten
```bash
python 04_Infrastruktur/Gateway/ai_os_dashboard.py
```
Öffne dann: http://localhost:5000

### 🖥️ Einzelne Komponenten starten
```bash
python 04_Infrastruktur/Gateway/ai_os_dashboard.py   # Dashboard (Port 5000)
python 04_Infrastruktur/Gateway/mcp_server.py        # MCP Server (Port 5001)
python 06_Gedächtnis/knowledge_agent.py              # RAG/Gedächtnis (Port 5002)
python 04_Infrastruktur/Gateway/api_gateway.py       # API Gateway (Port 5100)
python 05_Agenten/workflow_engine.py                 # Workflow Engine (Port 5200)
python 05_Agenten/agent_system.py                    # Agent System (Port 5300)
python 08_Monitoring/monitoring_service.py           # Monitoring (Port 5400)
```

## 🏗️ Architektur

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
│  │           Multi-Agent System (Port 5300)              │ │
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
│  │(Port11434)│(JSON/Chroma)│(Knowledge)│ │  (In-Mem) │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## 🤖 7 KI-Agenten

| Agent | Aufgabe | Modell |
|-------|---------|--------|
| **Orchestrator** | Koordiniert alle Agenten | llama3 |
| **Research** | Informationssuche & Recherche | llama3 |
| **Code** | Code-Generierung & Analyse | qwen2.5-coder |
| **Writer** | Texterstellung & Dokumentation | llama3 |
| **Analysis** | Datenanalyse & Reports | llama3 |
| **Planner** | Planung & Strategie | llama3 |
| **Memory** | Kontext- & Gedächtnisverwaltung | llama3 |

## 🧠 Lernender Agent

Das System lernt aus deinen Chat-Interaktionen und passt sich automatisch an:
- **Episodic-Memory**: Speichert alle Interaktionen
- **Lernzyklus**: Konsolidiert Wissen ins Long-Memory
- **Personalisierung**: Passt Chat-Antworten basierend auf gelerntem Profil an
- **Auto-Lernen**: Automatischer Lernzyklus alle 10 Interaktionen

## 📦 Verfügbare Open-Source Modelle

Über das Dashboard können folgende Modelle heruntergeladen werden:
- **llama3** (4.7 GB) - Allgemeine Aufgaben
- **mistral** (4.4 GB) - Chat & Textgenerierung
- **deepseek-coder** (776 MB) - Code-Generierung
- **qwen2.5-coder** (4.7 GB) - Code & Entwicklung
- **gemma2** (9.6 GB) - Fortgeschrittene Aufgaben
- **llama2** (3.8 GB) - Backup-Modell

## 🎨 Dashboard Features

- **📊 Übersicht**: System-Status, Dienste, Statistiken
- **📰 KI-News**: Tägliche Tech-News mit KI-generiertem CEO-Brief
- **🧩 Dienste**: Verwaltung aller AI-OS Komponenten
- **💬 Chat**: Business-Ideen-Chat mit Wissensmodus (RAG)
- **📦 Modelle**: Herunterladen, löschen und verwalten von Ollama-Modellen
- **🧠 Gedächtnis**: Wissenskategorien und Vektorsuche
- **🎓 Lernen**: Lernender Agent mit Profilverwaltung
- **📂 Dateien**: Wissensspeicher-Explorer
- **🏛️ Architektur**: Live-Ansicht der Ebenen-Struktur

## 📂 Ordnerstruktur

```
AI-OS/
├── 00_Wissen/              ← Wissensdatenbank (Obsidian Vault)
│   ├── 01_Persönlich/      ← Profil, Ziele, Vorlieben
│   ├── 02_Projekte/        ← Kunden, Produkte, Projekte
│   ├── 03_Aktuelles/       ← Tagesnotizen, aktuelle Arbeit
│   ├── 04_Referenzen/      ← Wiki, Architektur-Doku
│   └── 05_Archiv/          ← Abgeschlossene Notizen
├── 01_Verbindungen/        ← APIs, CLI, MCP-Configs
├── 02_Fähigkeiten/         ← Skills & Vorlagen
├── 03_Abläufe/             ← Routinen & Automatisierung
├── 04_Infrastruktur/       ← Gateway, Runtime, Config, Doku
│   ├── Gateway/            ← Dashboard, MCP, API Gateway
│   ├── Runtime/            ← Start-Skripte
│   └── Dokumentation/      ← Architektur-Dokumente
├── 05_Agenten/             ← Agentenlayer
│   ├── agent_system.py     ← 7 KI-Agenten
│   ├── workflow_engine.py  ← DAG-Pipelines
│   └── Rollen/             ← Agent-Rollen-Konfigurationen
├── 06_Gedächtnis/          ← Memory-Layer (RAG)
│   ├── Knowledge/          ← Wissenskategorien
│   ├── Memory/             ← Short/Long/Episodic Memory
│   └── Vector-Database/    ← Vektor-Index
├── 07_Sicherheit/          ← Security & Compliance
├── 08_Monitoring/          ← Health-Checks, Metriken
├── 09_Backup-Recovery/     ← Backup & Disaster Recovery
├── 10_Business/            ← Geschäftsprojekte
├── README.md               ← Diese Datei
├── AGENTS.md               ← Claude-Systemanweisungen
├── CLAUDE.md               ← Zentrale Konfiguration
└── AI-OS.code-workspace    ← VS Code Workspace
```

## 🔌 MCP Server (Claude Desktop Integration)

Der MCP-Server ermöglicht die Nutzung des AI-OS aus Claude Desktop heraus:
- `chat` - Chat mit lokaler KI
- `generate` - Text generieren
- `summarize` - Texte zusammenfassen
- `search_knowledge` - Wissensdatenbank durchsuchen
- `list_models` - Verfügbare Modelle auflisten

**Ports & URLs:**
| Komponente | Port | URL |
|-----------|------|-----|
| Dashboard | 5000 | http://localhost:5000 |
| MCP Server | 5001 | http://localhost:5001 |
| RAG Pipeline | 5002 | http://localhost:5002 |
| API Gateway | 5100 | http://localhost:5100 |
| Workflow Engine | 5200 | http://localhost:5200 |
| Agent System | 5300 | http://localhost:5300 |
| Monitoring | 5400 | http://localhost:5400/status |
| Ollama API | 11434 | http://localhost:11434 |

## 🛠️ Technologien

- **Backend**: Python, Flask, Ollama
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Datenbank**: JSON, Vektordatenbank (JSON/Chroma)
- **KI-Modelle**: Llama 3, Mistral, Qwen 2.5, DeepSeek
- **RAG**: Vektorbasierte semantische Suche
- **Monitoring**: Health-Checks, Metriken, Logging

## 🔒 Sicherheit

- **API-Keys & Secrets** gehören NIE ins Git
- Speicherung in `01_Verbindungen/APIs/Geheimnisse/` (`.gitignore` schützt diese)
- Alternativ: Umgebungsvariablen nutzen
- Alle Dienste laufen lokal auf `127.0.0.1`

## 📝 Git-Workflow

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

## 🎓 Lernmodus

Das System lernt kontinuierlich aus Interaktionen:
1. Chatten im Dashboard
2. Lernzyklus starten (manuell oder automatisch)
3. Profil wird ins Long-Memory konsolidiert
4. Zukünftige Chats nutzen das gelernte Profil

## 📚 Wissensmanagement

**Wissen aufbauen:**
1. **Persönlich**: `00_Wissen/01_Persönlich/` - Dein Profil
2. **Projekte**: `00_Wissen/02_Projekte/` - Kunden & Produkte
3. **Aktuell**: `00_Wissen/03_Aktuelles/` - Tagesnotizen
4. **Referenzen**: `00_Wissen/04_Referenzen/` - Wiki & Docs

Nutze Vorlagen aus `02_Fähigkeiten/Vorlagen/` für neue Einträge.

## 🚀 Nächste Schritte

- [ ] Erweiterte Agenten-Rollen (CEO, CTO, Developer)
- [ ] Fine-Tuning für spezifische Branchen
- [ ] Plugin-System für externe Tools
- [ ] Multi-User-Support
- [ ] Cloud-Backup für Wissensdatenbank

## 📄 Lizenz

Privates Projekt - Alle Rechte vorbehalten.

---

*Erstellt mit ♥ und Claude*