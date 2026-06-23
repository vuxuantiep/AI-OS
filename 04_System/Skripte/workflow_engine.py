#!/usr/bin/env python3
"""
AI-OS Workflow Engine (Port 5200)
DAG-basierte Workflow-Ausführung mit Task-Orchestrierung.
"""

import json
import os
import sys
import time
import uuid
import threading
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import deque
from queue import PriorityQueue
import urllib.request
import urllib.error

# Konfiguration
AI_OS_ROOT = Path(os.environ.get("AI_OS_ROOT", Path(__file__).parent.parent.parent))
OLLAMA_HOST = "127.0.0.1"
OLLAMA_PORT = 11434
WORKFLOW_PORT = int(os.environ.get("WORKFLOW_PORT", 5200))
AGENT_PORT = int(os.environ.get("AGENT_PORT", 5300))

# ============================================================
# Task Definition
# ============================================================

class Task:
    """Ein einzelner Task im Workflow"""
    
    def __init__(self, task_id, name, agent, prompt, depends_on=None, priority=5, max_retries=2):
        self.id = task_id
        self.name = name
        self.agent = agent  # Welcher Agent soll ausführen
        self.prompt = prompt
        self.depends_on = depends_on or []  # Liste von Task-IDs
        self.priority = priority  # 1 (hoch) - 10 (niedrig)
        self.max_retries = max_retries
        self.status = "pending"  # pending, running, completed, failed
        self.result = None
        self.error = None
        self.retries = 0
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "agent": self.agent,
            "prompt": self.prompt[:100] + "..." if len(self.prompt) > 100 else self.prompt,
            "depends_on": self.depends_on,
            "priority": self.priority,
            "status": self.status,
            "retries": self.retries,
            "max_retries": self.max_retries,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "has_result": self.result is not None,
            "has_error": self.error is not None
        }


# ============================================================
# Workflow Definition
# ============================================================

class Workflow:
    """Ein Workflow besteht aus mehreren Tasks mit Abhängigkeiten"""
    
    def __init__(self, workflow_id, name, description=""):
        self.id = workflow_id
        self.name = name
        self.description = description
        self.tasks = {}  # task_id -> Task
        self.status = "draft"  # draft, running, completed, failed, cancelled
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
        self.context = {}  # Geteilter Kontext zwischen Tasks
    
    def add_task(self, name, agent, prompt, depends_on=None, priority=5, max_retries=2):
        """Füge einen Task zum Workflow hinzu"""
        task_id = f"task_{len(self.tasks) + 1}_{uuid.uuid4().hex[:6]}"
        task = Task(task_id, name, agent, prompt, depends_on, priority, max_retries)
        self.tasks[task_id] = task
        return task_id
    
    def get_ready_tasks(self):
        """Hole alle Tasks, die bereit zur Ausführung sind"""
        ready = []
        for task in self.tasks.values():
            if task.status != "pending":
                continue
            # Prüfe ob alle Abhängigkeiten erfüllt sind
            all_deps_met = True
            for dep_id in task.depends_on:
                dep_task = self.tasks.get(dep_id)
                if not dep_task or dep_task.status != "completed":
                    all_deps_met = False
                    break
            if all_deps_met:
                ready.append(task)
        # Sortiere nach Priorität
        ready.sort(key=lambda t: t.priority)
        return ready
    
    def is_complete(self):
        """Prüfe ob der Workflow abgeschlossen ist"""
        if not self.tasks:
            return False
        return all(t.status in ["completed", "failed"] for t in self.tasks.values())
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "tasks": len(self.tasks),
            "completed_tasks": sum(1 for t in self.tasks.values() if t.status == "completed"),
            "failed_tasks": sum(1 for t in self.tasks.values() if t.status == "failed"),
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }


# ============================================================
# Workflow Engine
# ============================================================

class WorkflowEngine:
    """Verwaltet Workflows und führt Tasks aus"""
    
    def __init__(self):
        self.workflows = {}
        self.task_queue = deque()
        self.active_threads = {}
        self.max_parallel = 3
        self.execution_history = []
    
    def create_workflow(self, name, description=""):
        """Erstelle einen neuen Workflow"""
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        workflow = Workflow(workflow_id, name, description)
        self.workflows[workflow_id] = workflow
        return workflow
    
    def get_workflow(self, workflow_id):
        """Hole einen Workflow anhand der ID"""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self):
        """Liste alle Workflows"""
        return [wf.to_dict() for wf in self.workflows.values()]
    
    def start_workflow(self, workflow_id):
        """Starte einen Workflow"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {"error": "Workflow nicht gefunden"}
        
        if workflow.status != "draft":
            return {"error": f"Workflow ist bereits {workflow.status}"}
        
        workflow.status = "running"
        workflow.started_at = datetime.now().isoformat()
        
        # Starte Ausführung in separatem Thread
        thread = threading.Thread(target=self._execute_workflow, args=(workflow,))
        thread.daemon = True
        thread.start()
        self.active_threads[workflow_id] = thread
        
        return {"success": True, "workflow_id": workflow_id}
    
    def _execute_workflow(self, workflow):
        """Führe einen Workflow aus (in Thread)"""
        try:
            while not workflow.is_complete():
                ready_tasks = workflow.get_ready_tasks()
                
                if not ready_tasks:
                    # Warte auf laufende Tasks
                    time.sleep(0.5)
                    continue
                
                # Führe bereite Tasks aus (max parallel)
                for task in ready_tasks[:self.max_parallel]:
                    thread = threading.Thread(target=self._execute_task, args=(workflow, task))
                    thread.daemon = True
                    thread.start()
                
                time.sleep(0.5)
            
            # Workflow-Status aktualisieren
            all_completed = all(t.status == "completed" for t in workflow.tasks.values())
            workflow.status = "completed" if all_completed else "failed"
            workflow.completed_at = datetime.now().isoformat()
            
            self.execution_history.append({
                "workflow_id": workflow.id,
                "status": workflow.status,
                "completed_at": workflow.completed_at
            })
            
        except Exception as e:
            workflow.status = "failed"
            workflow.completed_at = datetime.now().isoformat()
            print(f"❌ Workflow {workflow.id} fehlgeschlagen: {e}")
    
    def _execute_task(self, workflow, task):
        """Führe einen einzelnen Task aus"""
        task.status = "running"
        task.started_at = datetime.now().isoformat()
        
        while task.retries <= task.max_retries:
            try:
                # Rufe Agent System auf
                payload = json.dumps({
                    "agent": task.agent,
                    "task": task.prompt,
                    "context": workflow.context
                }).encode("utf-8")
                
                req = urllib.request.Request(
                    f"http://127.0.0.1:{AGENT_PORT}/execute",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                
                with urllib.request.urlopen(req, timeout=300) as resp:
                    result = json.loads(resp.read())
                
                if result.get("success"):
                    task.status = "completed"
                    task.result = result.get("response", "")
                    task.completed_at = datetime.now().isoformat()
                    
                    # Speichere Ergebnis im Workflow-Kontext
                    workflow.context[f"{task.id}_result"] = task.result
                    print(f"  ✅ Task '{task.name}' abgeschlossen")
                    return
                else:
                    raise Exception(result.get("error", "Unbekannter Fehler"))
                    
            except Exception as e:
                task.retries += 1
                task.error = str(e)
                if task.retries > task.max_retries:
                    task.status = "failed"
                    task.completed_at = datetime.now().isoformat()
                    print(f"  ❌ Task '{task.name}' fehlgeschlagen: {e}")
                else:
                    print(f"  🔄 Task '{task.name}' erneuter Versuch ({task.retries}/{task.max_retries})")
                    time.sleep(1)
    
    def cancel_workflow(self, workflow_id):
        """Breche einen Workflow ab"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {"error": "Workflow nicht gefunden"}
        
        workflow.status = "cancelled"
        workflow.completed_at = datetime.now().isoformat()
        
        # Setze alle laufenden Tasks auf failed
        for task in workflow.tasks.values():
            if task.status == "running":
                task.status = "failed"
                task.error = "Workflow abgebrochen"
        
        return {"success": True}
    
    def create_sample_workflow(self):
        """Erstelle einen Beispiel-Workflow"""
        wf = self.create_workflow(
            "KI-Recherche & Bericht",
            "Durchläuft Recherche, Analyse und Erstellung eines Berichts"
        )
        
        # Task 1: Recherche
        t1 = wf.add_task(
            name="Recherche durchführen",
            agent="research",
            prompt="Recherchiere Informationen über aktuelle KI-Trends 2026",
            priority=1
        )
        
        # Task 2: Analyse (abhängig von Task 1)
        t2 = wf.add_task(
            name="Daten analysieren",
            agent="analysis",
            prompt="Analysiere die gefundenen Informationen und identifiziere die wichtigsten Trends",
            depends_on=[t1],
            priority=2
        )
        
        # Task 3: Bericht schreiben (abhängig von Task 2)
        wf.add_task(
            name="Bericht erstellen",
            agent="writer",
            prompt="Erstelle einen professionellen Bericht über die aktuellen KI-Trends basierend auf der Analyse",
            depends_on=[t2],
            priority=3
        )
        
        return wf


# ============================================================
# HTTP Server
# ============================================================

engine = WorkflowEngine()

class WorkflowHandler(BaseHTTPRequestHandler):
    """HTTP Handler für die Workflow Engine"""
    
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
                "service": "AI-OS Workflow Engine",
                "version": "2.0.0",
                "workflows": len(engine.workflows),
                "timestamp": datetime.now().isoformat()
            }).encode())
        
        elif self.path == "/workflows":
            self._set_headers()
            self.wfile.write(json.dumps({"workflows": engine.list_workflows()}).encode())
        
        elif self.path.startswith("/workflows/"):
            wf_id = self.path.split("/workflows/", 1)[1]
            wf = engine.get_workflow(wf_id)
            if wf:
                self._set_headers()
                tasks = {tid: t.to_dict() for tid, t in wf.tasks.items()}
                self.wfile.write(json.dumps({
                    "workflow": wf.to_dict(),
                    "tasks": tasks,
                    "context_keys": list(wf.context.keys())
                }).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Workflow nicht gefunden"}).encode())
        
        elif self.path == "/stats":
            self._set_headers()
            self.wfile.write(json.dumps({
                "total_workflows": len(engine.workflows),
                "active_workflows": sum(1 for w in engine.workflows.values() if w.status == "running"),
                "completed_workflows": sum(1 for w in engine.workflows.values() if w.status == "completed"),
                "execution_history": len(engine.execution_history)
            }).encode())
        
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
        
        if self.path == "/workflows/create":
            name = data.get("name", f"Workflow_{uuid.uuid4().hex[:6]}")
            description = data.get("description", "")
            wf = engine.create_workflow(name, description)
            
            # Tasks hinzufügen falls vorhanden
            for task_data in data.get("tasks", []):
                wf.add_task(
                    name=task_data.get("name", "Task"),
                    agent=task_data.get("agent", "research"),
                    prompt=task_data.get("prompt", ""),
                    depends_on=task_data.get("depends_on"),
                    priority=task_data.get("priority", 5)
                )
            
            self._set_headers(201)
            self.wfile.write(json.dumps({
                "success": True,
                "workflow": wf.to_dict(),
                "workflow_id": wf.id
            }).encode())
        
        elif self.path == "/workflows/start":
            wf_id = data.get("workflow_id", "")
            result = engine.start_workflow(wf_id)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif self.path == "/workflows/cancel":
            wf_id = data.get("workflow_id", "")
            result = engine.cancel_workflow(wf_id)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif self.path == "/workflows/sample":
            wf = engine.create_sample_workflow()
            self._set_headers(201)
            self.wfile.write(json.dumps({
                "success": True,
                "workflow": wf.to_dict(),
                "workflow_id": wf.id,
                "message": "Beispiel-Workflow erstellt. Starte mit POST /workflows/start"
            }).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())


def main():
    """Startet die Workflow Engine"""
    print(f"\n{'='*50}")
    print(f"🔄 AI-OS Workflow Engine")
    print(f"{'='*50}")
    print(f"📍 Host: http://localhost:{WORKFLOW_PORT}")
    print(f"🔗 Agent System: http://localhost:{AGENT_PORT}")
    print(f"{'='*50}\n")
    
    server = HTTPServer(("127.0.0.1", WORKFLOW_PORT), WorkflowHandler)
    print(f"✅ Workflow Engine läuft auf Port {WORKFLOW_PORT}")
    print(f"📋 Endpunkte:")
    print(f"   GET  /                    - Status")
    print(f"   GET  /workflows           - Workflow-Liste")
    print(f"   GET  /workflows/{'{id}'}  - Workflow-Details")
    print(f"   GET  /stats               - Statistiken")
    print(f"   POST /workflows/create    - Workflow erstellen")
    print(f"   POST /workflows/start     - Workflow starten")
    print(f"   POST /workflows/cancel    - Workflow abbrechen")
    print(f"   POST /workflows/sample    - Beispiel-Workflow\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Workflow Engine gestoppt")
        server.server_close()

if __name__ == "__main__":
    main()