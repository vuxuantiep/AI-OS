# ROUTINE: AI-OS Starten
# Beschreibung: Startet alle Komponenten des lokalen KI-Betriebssystems
# Intervall: Manuell (bei Systemstart)
# Typ: Lokal

## Ausführung

### Option 1: Dashboard (empfohlen)
```bash
cd /AI-OS
python 04_System/Scripts/ai_os_dashboard.py
```
Öffne dann http://localhost:5000 im Browser.

### Option 2: Alle Komponenten (Launcher)
```bash
cd /AI-OS
python 04_System/Scripts/start_ai_os.py
```
Startet Dashboard, MCP-Server und Knowledge Agent.

### Option 3: Einzelne Komponenten
```bash
# Dashboard (Web-UI)
python 04_System/Scripts/ai_os_dashboard.py

# MCP-Server (für Claude Desktop und andere Clients)
python 04_System/Scripts/mcp_server.py

# Knowledge Agent (RAG / Vektorsuche)
python 04_System/Scripts/knowledge_agent.py
```

## Voraussetzungen
- Ollama muss installiert und laufen: `ollama serve`
- Python-Abhängigkeiten: `pip install flask psutil`
- Mindestens ein KI-Modell: `ollama pull llama3`

## Windows Autostart
1. Erstelle eine `start_ai_os.bat`:
```batch
@echo off
cd /d C:\Users\vuxua\Documents\Github_Projekte\AI-OS
python 04_System\Scripts\ai_os_dashboard.py
```
2. Leg die .bat-Datei in `shell:startup` ab.

## Ports
| Komponente | Port | URL |
|-----------|------|-----|
| Dashboard | 5000 | http://localhost:5000 |
| MCP Server | 5001 | http://localhost:5001 |
| Knowledge Agent | 5002 | http://localhost:5002 |
| Ollama | 11434 | http://localhost:11434 |