# 🏭 KI-Fabrik V2 - Architektur

## Übersicht
Die KI-Fabrik V2 ist ein modulares Multi-Agent-System, das auf dem bestehenden AI-OS aufbaut und es zu einer vollständigen KI-Produktionsumgebung erweitert.

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

## Komponenten

### 1. Multi-Agent System (Port 5300)
- **Orchestrator Agent**: Koordiniert alle Agenten, verteilt Aufgaben
- **Research Agent**: Durchsucht Wissen, sammelt Informationen
- **Code Agent**: Generiert und analysiert Code
- **Writer Agent**: Erstellt Content, Dokumentation
- **Analysis Agent**: Analysiert Daten, erstellt Reports
- **Planner Agent**: Erstellt Ausführungspläne
- **Memory Agent**: Verwaltet Kontext und Gedächtnis

### 2. Workflow Engine (Port 5200)
- DAG-basierte Workflow-Definition
- Parallele und sequentielle Ausführung
- Bedingte Verzweigungen
- Retry- und Fehlerbehandlung
- Pipeline-Manager für komplexe Abläufe

### 3. Task Orchestrator (Teil der Workflow Engine)
- Prioritäts-Warteschlange
- Task-Dependency-Management
- Parallele Ausführung mit Thread-Pool
- Status-Tracking und Benachrichtigungen

### 4. RAG Pipeline (Port 5002, erweitert)
- Verbesserte Chunking-Strategien
- Hybrid Search (Semantisch + Keyword)
- Re-Ranking der Ergebnisse
- Kontext-Fenster-Management
- Automatische Neu-Indizierung

### 5. API Gateway (Port 5100)
- Einheitlicher API-Einstiegspunkt
- Routen zu allen Diensten
- Request-Validierung
- CORS-Management

### 6. Monitoring (Port 5400)
- Metrik-Erfassung (CPU, RAM, Requests, Latenz)
- Log-Aggregation
- Health-Checks für alle Dienste
- Performance-Tracing
- Alerting

## Datenflüsse

```
User Request → API Gateway → Orchestrator Agent → Workflow Engine
                                 ↓
                    ┌────────────────────────────┐
                    │  Task Queue & Orchestration │
                    └──────────┬─────────────────┘
                               ↓
              ┌────────────────┼────────────────┐
              ↓                ↓                ↓
        Research Agent    Code Agent      Writer Agent
              ↓                ↓                ↓
              └────────────────┼────────────────┘
                               ↓
                        RAG Pipeline
                        (Knowledge Base)
                               ↓
                        Ergebnis → User
```

## Port-Übersicht

| Komponente | Port | Beschreibung |
|-----------|------|-------------|
| Dashboard | 5000 | Web UI |
| MCP Server | 5001 | AI-Client Interface |
| RAG Pipeline | 5002 | Knowledge Agent |
| API Gateway | 5100 | Unified API |
| Workflow Engine | 5200 | Workflow & Tasks |
| Agent System | 5300 | Multi-Agent System |
| Monitoring | 5400 | Observability |
| Ollama | 11434 | Lokale KI-Modelle |