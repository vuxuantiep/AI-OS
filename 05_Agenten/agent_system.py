#!/usr/bin/env python3
"""
AI-OS Multi-Agent System (Port 5300)
Koordiniert spezialisierte KI-Agenten für verschiedene Aufgaben.
"""

import json
import os
import sys
import re
import time
import urllib.request
import urllib.error
import threading
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import deque

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Konfiguration
AI_OS_ROOT = Path(os.environ.get("AI_OS_ROOT", Path(__file__).parent.parent))
OLLAMA_HOST = "127.0.0.1"
OLLAMA_PORT = 11434
AGENT_PORT = int(os.environ.get("AGENT_PORT", 5300))
DEFAULT_MODEL = "llama3"
CODE_MODEL = "qwen2.5-coder"

# ============================================================
# Agent Definitionen
# ============================================================

class BaseAgent:
    """Basis-Klasse für alle Agenten"""
    
    def __init__(self, name, description, model=DEFAULT_MODEL):
        self.name = name
        self.description = description
        self.model = model
        self.history = []
        self.metrics = {"calls": 0, "total_tokens": 0, "errors": 0}
    
    def get_system_prompt(self):
        """Jeder Agent definiert seinen eigenen System-Prompt"""
        raise NotImplementedError
    
    def execute(self, task, context=None):
        """Führe eine Aufgabe aus"""
        self.metrics["calls"] += 1
        system_prompt = self.get_system_prompt()
        
        if context:
            system_prompt += f"\n\nKontext:\n{json.dumps(context, ensure_ascii=False, indent=2)[:3000]}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        
        try:
            payload = json.dumps({
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 4096
                }
            }).encode("utf-8")
            
            req = urllib.request.Request(
                f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read())
                response = result.get("message", {}).get("content", "")
                self.metrics["total_tokens"] += result.get("eval_count", 0)
            
            self.history.append({"task": task[:100], "response_length": len(response)})
            if len(self.history) > 50:
                self.history = self.history[-50:]
            
            return {"success": True, "response": response, "agent": self.name}
        
        except Exception as e:
            self.metrics["errors"] += 1
            return {"success": False, "error": str(e), "agent": self.name}


class OrchestratorAgent(BaseAgent):
    """Haupt-Agent: Koordiniert und verteilt Aufgaben"""
    
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            description="Koordiniert alle Agenten, analysiert Aufgaben und verteilt sie",
            model=DEFAULT_MODEL
        )
    
    def get_system_prompt(self):
        return """Du bist der ORCHESTRATOR der KI-Fabrik. Deine Aufgaben:
1. Analysiere eingehende Aufgaben
2. Entscheide, welche Agenten benötigt werden
3. Erstelle einen Ausführungsplan
4. Koordiniere die Ergebnisse

Verfügbare Agenten:
- Research Agent: Informationssuche und Recherche
- Code Agent: Code-Generierung und -Analyse
- Writer Agent: Texterstellung und Dokumentation
- Analysis Agent: Datenanalyse und Reports
- Planner Agent: Planung und Strategie
- Memory Agent: Kontext- und Gedächtnisverwaltung

Antworte auf Deutsch. Gib einen strukturierten Plan aus."""


class ResearchAgent(BaseAgent):
    """Recherchiert und sammelt Informationen"""
    
    def __init__(self):
        super().__init__(
            name="Research",
            description="Durchsucht Wissen und sammelt Informationen",
            model=DEFAULT_MODEL
        )
    
    def get_system_prompt(self):
        return """Du bist der RESEARCH AGENT der KI-Fabrik. Deine Aufgaben:
1. Durchsuche die Wissensdatenbank nach relevanten Informationen
2. Analysiere und strukturiere gefundene Daten
3. Erstelle Zusammenfassungen
4. Identifiziere Wissenslücken

Antworte auf Deutsch. Sei präzise und gut strukturiert."""


class CodeAgent(BaseAgent):
    """Generiert und analysiert Code"""
    
    def __init__(self):
        super().__init__(
            name="Code",
            description="Generiert, analysiert und optimiert Code",
            model=CODE_MODEL
        )
    
    def get_system_prompt(self):
        return """Du bist der CODE AGENT der KI-Fabrik. Deine Aufgaben:
1. Generiere sauberen, dokumentierten Code
2. Analysiere bestehenden Code
3. Optimiere und refaktoriere
4. Erstelle Tests und Dokumentation

Unterstützte Sprachen: Python, JavaScript, TypeScript, HTML, CSS, Bash
Antworte auf Deutsch. Gib vollständigen, funktionsfähigen Code aus."""


class WriterAgent(BaseAgent):
    """Erstellt Content und Dokumentation"""
    
    def __init__(self):
        super().__init__(
            name="Writer",
            description="Erstellt Texte, Dokumentation und Content",
            model=DEFAULT_MODEL
        )
    
    def get_system_prompt(self):
        return """Du bist der WRITER AGENT der KI-Fabrik. Deine Aufgaben:
1. Erstelle professionelle Dokumentation
2. Schreibe Artikel und Berichte
3. Formatiere und strukturiere Texte
4. Optimiere bestehende Texte

Antworte auf Deutsch. Verwende Markdown-Formatierung."""


class AnalysisAgent(BaseAgent):
    """Analysiert Daten und erstellt Reports"""
    
    def __init__(self):
        super().__init__(
            name="Analysis",
            description="Analysiert Daten und erstellt Berichte",
            model=DEFAULT_MODEL
        )
    
    def get_system_prompt(self):
        return """Du bist der ANALYSIS AGENT der KI-Fabrik. Deine Aufgaben:
1. Analysiere Daten und Metriken
2. Erstelle strukturierte Reports
3. Identifiziere Trends und Muster
4. Gib Handlungsempfehlungen

Antworte auf Deutsch. Verwende Tabellen und Aufzählungen."""


class PlannerAgent(BaseAgent):
    """Erstellt Pläne und Strategien"""
    
    def __init__(self):
        super().__init__(
            name="Planner",
            description="Erstellt Ausführungspläne und Strategien",
            model=DEFAULT_MODEL
        )
    
    def get_system_prompt(self):
        return """Du bist der PLANNER AGENT der KI-Fabrik. Deine Aufgaben:
1. Erstelle detaillierte Ausführungspläne
2. Definiere Meilensteine und Deadlines
3. Identifiziere Abhängigkeiten
4. Optimiere Ressourcennutzung

Antworte auf Deutsch. Gib strukturierte Pläne mit Zeitangaben aus."""


class MemoryAgent(BaseAgent):
    """Verwaltet Kontext und Gedächtnis"""
    
    def __init__(self):
        super().__init__(
            name="Memory",
            description="Verwaltet Kontext, Gedächtnis und Sitzungen",
            model=DEFAULT_MODEL
        )
        self.short_term = deque(maxlen=20)
        self.long_term = []
    
    def get_system_prompt(self):
        return """Du bist der MEMORY AGENT der KI-Fabrik. Deine Aufgaben:
1. Extrahiere wichtige Informationen aus Unterhaltungen
2. Erstelle Zusammenfassungen für das Gedächtnis
3. Erkenne Muster über mehrere Sitzungen hinweg
4. Optimiere den Kontext für andere Agenten

Antworte auf Deutsch. Sei präzise."""


# ============================================================
# Agent System Manager
# ============================================================

class AgentSystem:
    """Verwaltet alle Agenten und deren Kommunikation"""
    
    def __init__(self):
        self.agents = {
            "orchestrator": OrchestratorAgent(),
            "research": ResearchAgent(),
            "code": CodeAgent(),
            "writer": WriterAgent(),
            "analysis": AnalysisAgent(),
            "planner": PlannerAgent(),
            "memory": MemoryAgent()
        }
        self.sessions = {}
        self.task_queue = deque()
        self.results_cache = {}
    
    def get_agent(self, name):
        """Hole einen Agenten anhand des Namens"""
        return self.agents.get(name.lower())
    
    def list_agents(self):
        """Liste alle verfügbaren Agenten"""
        return [
            {
                "name": a.name,
                "description": a.description,
                "model": a.model,
                "metrics": a.metrics
            }
            for a in self.agents.values()
        ]
    
    def execute_task(self, agent_name, task, context=None, session_id=None):
        """Führe eine Aufgabe mit einem bestimmten Agenten aus"""
        agent = self.get_agent(agent_name)
        if not agent:
            return {"success": False, "error": f"Agent '{agent_name}' nicht gefunden"}
        
        # Session-Kontext laden
        session_context = None
        if session_id and session_id in self.sessions:
            session_context = self.sessions[session_id].get("context")
        
        # Ausführen
        result = agent.execute(task, context or session_context)
        
        # Session aktualisieren
        if session_id:
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    "created": datetime.now().isoformat(),
                    "history": [],
                    "context": {}
                }
            self.sessions[session_id]["history"].append({
                "agent": agent_name,
                "task": task[:100],
                "timestamp": datetime.now().isoformat()
            })
        
        return result
    
    def orchestrate(self, task, session_id=None):
        """Orchestriere eine komplexe Aufgabe über mehrere Agenten"""
        # 1. Orchestrator analysiert die Aufgabe
        plan_result = self.agents["orchestrator"].execute(
            f"Analysiere diese Aufgabe und erstelle einen Ausführungsplan:\n{task}"
        )
        
        if not plan_result["success"]:
            return plan_result
        
        plan = plan_result["response"]
        
        # 2. Planner erstellt detaillierten Plan
        detailed_plan = self.agents["planner"].execute(
            f"Erstelle einen detaillierten Plan basierend auf dieser Analyse:\n{plan}\n\nOriginal-Aufgabe: {task}"
        )
        
        # 3. Führe die passenden Agenten aus (vereinfacht)
        results = {
            "plan": plan,
            "detailed_plan": detailed_plan.get("response", ""),
            "agent_results": {}
        }
        
        # Bestimme benötigte Agenten basierend auf Schlüsselwörtern
        task_lower = task.lower()
        active_agents = []
        
        if any(w in task_lower for w in ["code", "programmieren", "entwickeln", "python", "javascript", "skript"]):
            active_agents.append("code")
        if any(w in task_lower for w in ["recherche", "suche", "finde", "research", "information"]):
            active_agents.append("research")
        if any(w in task_lower for w in ["schreibe", "text", "dokumentation", "artikel", "bericht"]):
            active_agents.append("writer")
        if any(w in task_lower for w in ["analysiere", "analyse", "daten", "report", "metrik"]):
            active_agents.append("analysis")
        
        # Standard: Research + Writer
        if not active_agents:
            active_agents = ["research", "writer"]
        
        # Parallele Ausführung simulieren
        for agent_name in active_agents:
            agent_result = self.agents[agent_name].execute(
                f"Bearbeite diesen Teil der Aufgabe:\n{task}\n\nKontext aus Plan:\n{plan[:2000]}"
            )
            results["agent_results"][agent_name] = agent_result
        
        # 4. Memory speichert wichtige Erkenntnisse
        memory_result = self.agents["memory"].execute(
            f"Extrahiere wichtige Informationen aus dieser Sitzung:\nAufgabe: {task}\nErgebnisse: {json.dumps(results, ensure_ascii=False)[:2000]}"
        )
        results["memory"] = memory_result.get("response", "")
        
        return results
    
    def get_stats(self):
        """Hole System-Statistiken"""
        return {
            "agents": self.list_agents(),
            "sessions": len(self.sessions),
            "queue_size": len(self.task_queue),
            "cache_size": len(self.results_cache)
        }


# ============================================================
# HTTP Server
# ============================================================

agent_system = AgentSystem()

class AgentHandler(BaseHTTPRequestHandler):
    """HTTP Handler für das Agent System"""
    
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers(204)
    
    def do_GET(self):
        if self.path == "/" or self.path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "service": "AI-OS Multi-Agent System",
                "version": "2.0.0",
                "agents": len(agent_system.agents),
                "timestamp": datetime.now().isoformat()
            }).encode())
        
        elif self.path == "/agents":
            self._set_headers()
            self.wfile.write(json.dumps({"agents": agent_system.list_agents()}).encode())
        
        elif self.path == "/stats":
            self._set_headers()
            self.wfile.write(json.dumps(agent_system.get_stats()).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}
        
        if self.path == "/execute":
            agent_name = data.get("agent", "orchestrator")
            task = data.get("task", "")
            context = data.get("context")
            session_id = data.get("session_id")
            
            if not task:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Keine Aufgabe angegeben"}).encode())
                return
            
            result = agent_system.execute_task(agent_name, task, context, session_id)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif self.path == "/orchestrate":
            task = data.get("task", "")
            session_id = data.get("session_id")
            
            if not task:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Keine Aufgabe angegeben"}).encode())
                return
            
            result = agent_system.orchestrate(task, session_id)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif self.path == "/chat":
            message = data.get("message", "")
            agent_name = data.get("agent", "orchestrator")
            session_id = data.get("session_id")
            
            if not message:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Keine Nachricht"}).encode())
                return
            
            result = agent_system.execute_task(agent_name, message, session_id=session_id)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())


def main():
    """Startet das Agent System"""
    print(f"\n{'='*50}")
    print(f"🤖 AI-OS Multi-Agent System")
    print(f"{'='*50}")
    print(f"📍 Host: http://localhost:{AGENT_PORT}")
    print(f"📋 Agenten:")
    for a in agent_system.agents.values():
        print(f"   - {a.name} ({a.model})")
    print(f"{'='*50}\n")
    
    server = HTTPServer(("127.0.0.1", AGENT_PORT), AgentHandler)
    print(f"✅ Agent System läuft auf Port {AGENT_PORT}")
    print(f"📋 Endpunkte:")
    print(f"   GET  /              - Status")
    print(f"   GET  /agents        - Agenten-Liste")
    print(f"   GET  /stats         - Statistiken")
    print(f"   POST /execute       - Aufgabe ausführen")
    print(f"   POST /orchestrate   - Orchestrierte Ausführung")
    print(f"   POST /chat          - Chat mit Agent\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Agent System gestoppt")
        server.server_close()

if __name__ == "__main__":
    main()