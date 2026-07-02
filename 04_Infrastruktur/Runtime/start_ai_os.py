#!/usr/bin/env python3
"""
AI-OS V2 System Launcher
Startet alle Komponenten der KI-Fabrik.
"""

import subprocess
import sys
import os
import time
import json
import threading
import webbrowser
from pathlib import Path

# Konfiguration
AI_OS_ROOT = Path(__file__).parent.parent.parent
OLLAMA_HOST = "127.0.0.1"
OLLAMA_PORT = 11434

# Service-Konfiguration
SERVICES = [
    {"name": "Dashboard", "script": "ai_os_dashboard.py", "port": 5000, "env": {"FLASK_PORT": "5000"}},
    {"name": "MCP Server", "script": "mcp_server.py", "port": 5001, "env": {"MCP_PORT": "5001"}},
    {"name": "RAG Pipeline", "script": "knowledge_agent.py", "port": 5002, "env": {}},
    {"name": "API Gateway", "script": "api_gateway.py", "port": 5100, "env": {"GATEWAY_PORT": "5100"}},
    {"name": "Workflow Engine", "script": "workflow_engine.py", "port": 5200, "env": {"WORKFLOW_PORT": "5200"}},
    {"name": "Agent System", "script": "agent_system.py", "port": 5300, "env": {"AGENT_PORT": "5300"}},
    {"name": "Monitoring", "script": "monitoring_service.py", "port": 5400, "env": {"MONITOR_PORT": "5400"}},
]

def check_ollama():
    """Prüft ob Ollama läuft und startet es falls nötig"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        print("✅ Ollama läuft bereits")
        return True
    except:
        print("🔄 Starte Ollama...")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        return True

def check_ollama_connection():
    """Testet die Verbindung zu Ollama"""
    import urllib.request
    try:
        req = urllib.request.Request(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            models = data.get("models", [])
            print(f"✅ Ollama API erreichbar - {len(models)} Modelle geladen:")
            for m in models[:5]:
                print(f"   - {m['name']}")
            if len(models) > 5:
                print(f"   ... und {len(models) - 5} weitere")
            return True
    except Exception as e:
        print(f"❌ Ollama API nicht erreichbar: {e}")
        return False

def start_service(service):
    """Startet einen einzelnen Service"""
    script_path = Path(__file__).parent / service["script"]
    if not script_path.exists():
        print(f"⚠️ {service['name']}: Skript nicht gefunden")
        return None
    
    print(f"  🚀 Starte {service['name']} auf Port {service['port']}...")
    env = os.environ.copy()
    env["AI_OS_ROOT"] = str(AI_OS_ROOT)
    for key, val in service["env"].items():
        env[key] = val
    
    proc = subprocess.Popen(
        [sys.executable, str(script_path)],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1.5)
    
    if proc.poll() is None:
        print(f"  ✅ {service['name']} läuft auf http://localhost:{service['port']}")
        return proc
    else:
        print(f"  ❌ {service['name']} konnte nicht gestartet werden")
        return None

def print_dashboard(processes):
    """Zeigt das Start-Dashboard an"""
    print("\n" + "=" * 60)
    print("🧠  AI-OS V2 - KI-FABRIK")
    print("=" * 60)
    print()
    print("  📊 Service-Status:")
    print()
    for svc in SERVICES:
        proc = processes.get(svc["name"])
        if proc and proc.poll() is None:
            print(f"    ✅  {svc['name']:20s}  http://localhost:{svc['port']}")
        elif proc:
            print(f"    ❌  {svc['name']:20s}  Fehler")
        else:
            print(f"    ⚠️  {svc['name']:20s}  Nicht verfügbar")
    
    print()
    print("=" * 60)
    print("  🌐  API Gateway:  http://localhost:5100")
    print("  📊  Monitoring:   http://localhost:5400/status")
    print("  🖥️   Dashboard:   http://localhost:5000")
    print("=" * 60)
    print()
    print("  🔧  Drücke Strg+C um alle Komponenten zu stoppen")
    print()

def main():
    print("\n" + "=" * 60)
    print("🧠  AI-OS V2 - KI-FABRIK LAUNCHER")
    print("=" * 60 + "\n")

    # Phase 1: Ollama prüfen
    print("📡 Phase 1/3: KI-Engine prüfen")
    print("-" * 40)
    if not check_ollama():
        print("❌ Ollama konnte nicht gestartet werden")
        sys.exit(1)
    check_ollama_connection()
    print()

    # Phase 2: Services starten
    print("🔧 Phase 2/3: Dienste starten")
    print("-" * 40)
    
    processes = {}
    for svc in SERVICES:
        proc = start_service(svc)
        processes[svc["name"]] = proc
    print()

    # Phase 3: Dashboard
    print("🎯 Phase 3/3: System bereit")
    print("-" * 40)
    print_dashboard(processes)

    # Dashboard im Browser öffnen
    if processes.get("Dashboard"):
        webbrowser.open("http://localhost:5000")

    # Auf Beendigung warten
    try:
        while True:
            time.sleep(1)
            for svc in SERVICES:
                proc = processes.get(svc["name"])
                if proc and proc.poll() is not None:
                    print(f"⚠️ {svc['name']} wurde unerwartet beendet")
                    processes[svc["name"]] = None
    except KeyboardInterrupt:
        print("\n\n🛑  Beende alle Komponenten...")
        print("-" * 40)
        for svc in reversed(SERVICES):
            proc = processes.get(svc["name"])
            if proc and proc.poll() is None:
                print(f"  ⏹️  {svc['name']} wird gestoppt...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except:
                    proc.kill()
        print("✅  KI-Fabrik heruntergefahren")
        print()

if __name__ == "__main__":
    main()