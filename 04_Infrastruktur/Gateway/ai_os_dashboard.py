#!/usr/bin/env python3
"""
AI-OS Dashboard
Zentrale Weboberfläche für das lokale KI-Betriebssystem.
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from flask import Flask, render_template_string, jsonify, request
except ImportError:
    print("Flask nicht installiert. Installiere mit: pip install flask")
    sys.exit(1)

AI_OS_ROOT = Path(os.environ.get("AI_OS_ROOT", Path(__file__).parent.parent.parent))
OLLAMA_HOST = "127.0.0.1"
OLLAMA_PORT = 11434
FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))

app = Flask(__name__)

# ========== DIENSTE-REGISTRY (Ebenen-Struktur) ==========
SERVICES = [
    {"key": "dashboard", "name": "Dashboard", "icon": "🖥️", "port": FLASK_PORT,
     "desc": "Zentrale Weboberfläche (diese Seite)", "layer": "04_Infrastruktur", "script": None, "env_key": None},
    {"key": "mcp", "name": "MCP Server", "icon": "🔌", "port": 5001,
     "desc": "AI-Client-Schnittstelle (Claude Desktop u.a.)", "layer": "04_Infrastruktur",
     "script": "04_Infrastruktur/Gateway/mcp_server.py", "env_key": "MCP_PORT"},
    {"key": "rag", "name": "Gedächtnis / RAG", "icon": "🧠", "port": 5002,
     "desc": "Wissens-Indexer & Vektorsuche", "layer": "06_Gedächtnis",
     "script": "06_Gedächtnis/knowledge_agent.py", "env_key": None},
    {"key": "gateway", "name": "API Gateway", "icon": "🌐", "port": 5100,
     "desc": "Zentraler Einstiegspunkt für alle Dienste", "layer": "04_Infrastruktur",
     "script": "04_Infrastruktur/Gateway/api_gateway.py", "env_key": "GATEWAY_PORT"},
    {"key": "workflow", "name": "Workflow Engine", "icon": "🔄", "port": 5200,
     "desc": "DAG-basierte Aufgaben-Pipelines", "layer": "05_Agenten",
     "script": "05_Agenten/workflow_engine.py", "env_key": "WORKFLOW_PORT"},
    {"key": "agents", "name": "Agent System", "icon": "🤖", "port": 5300,
     "desc": "7 spezialisierte KI-Agenten", "layer": "05_Agenten",
     "script": "05_Agenten/agent_system.py", "env_key": "AGENT_PORT"},
    {"key": "monitoring", "name": "Monitoring", "icon": "📊", "port": 5400,
     "desc": "Health-Checks, Metriken, Logs", "layer": "08_Monitoring",
     "script": "08_Monitoring/monitoring_service.py", "env_key": "MONITOR_PORT"},
]

KNOWLEDGE_CATEGORIES = [
    {"key": "business", "name": "Business-Knowledge", "icon": "💼", "path": "Business-Knowledge",
     "desc": "Produkte, Kunden, Strategien"},
    {"key": "technical", "name": "Technical-Knowledge", "icon": "🛠️", "path": "Technical-Knowledge",
     "desc": "APIs, Docker, FastAPI, Python"},
    {"key": "agent", "name": "Agent-Knowledge", "icon": "🤖", "path": "Agent-Knowledge",
     "desc": "Rollen, Fähigkeiten, Grenzen"},
    {"key": "project", "name": "Project-Knowledge", "icon": "📋", "path": "Project-Knowledge",
     "desc": "Entscheidungen, ADRs, Architektur"},
    {"key": "short_memory", "name": "Short-Memory", "icon": "⚡", "path": "Memory/Short-Memory",
     "desc": "Kurzfristiger Session-Kontext"},
    {"key": "long_memory", "name": "Long-Memory", "icon": "🗄️", "path": "Memory/Long-Memory",
     "desc": "Dauerhaftes, konsolidiertes Wissen"},
    {"key": "episodic_memory", "name": "Episodic-Memory", "icon": "📖", "path": "Memory/Episodic-Memory",
     "desc": "Konkrete vergangene Ereignisse"},
    {"key": "prompts", "name": "Prompt-Library", "icon": "✍️", "path": "Prompt-Library",
     "desc": "Wiederverwendbare Prompts"},
    {"key": "sop", "name": "SOP-Library", "icon": "📑", "path": "SOP-Library",
     "desc": "Standard Operating Procedures"},
    {"key": "vector", "name": "Vector-Database", "icon": "🧬", "path": "Vector-Database",
     "desc": "Vektor-Index für semantische Suche"},
]

# Architektur-Stand: die 11 Ebenen im Repo-Root, gruppiert wie im Ebenen-Stapel
ARCHITECTURE_LAYERS = [
    {"key": "wissen", "name": "00_Wissen", "icon": "📚", "desc": "Obsidian Vault — Rohwissen, Notizen", "group": "Wissen & Organisation"},
    {"key": "verbindungen", "name": "01_Verbindungen", "icon": "🔗", "desc": "APIs, CLI, MCP-Client-Configs", "group": "Wissen & Organisation"},
    {"key": "faehigkeiten", "name": "02_Fähigkeiten", "icon": "🎯", "desc": "Skills & Vorlagen", "group": "Wissen & Organisation"},
    {"key": "ablaeufe", "name": "03_Abläufe", "icon": "🔁", "desc": "Routinen & Automatisierung", "group": "Wissen & Organisation"},
    {"key": "infrastruktur", "name": "04_Infrastruktur", "icon": "🏗️", "desc": "Gateway, Runtime, Config, Doku", "group": "Plattform"},
    {"key": "agenten", "name": "05_Agenten", "icon": "🤖", "desc": "Agentenlayer", "group": "Plattform"},
    {"key": "gedaechtnis", "name": "06_Gedächtnis", "icon": "🧠", "desc": "Memory-Layer (RAG)", "group": "Plattform"},
    {"key": "sicherheit", "name": "07_Sicherheit", "icon": "🔒", "desc": "Security & Compliance", "group": "Plattform"},
    {"key": "monitoring2", "name": "08_Monitoring", "icon": "📊", "desc": "Health, Metriken, Logs", "group": "Plattform"},
    {"key": "backup", "name": "09_Backup-Recovery", "icon": "💾", "desc": "Backup & Disaster Recovery", "group": "Plattform"},
    {"key": "business", "name": "10_Business", "icon": "💼", "desc": "Geschäftsprojekte", "group": "Business"},
]

WIKI_DIRS = [
    {"key": "wiki", "name": "Wiki / Referenzen", "path": "00_Wissen/04_Referenzen/Wiki"},
    {"key": "architektur", "name": "Architektur-Dokumentation", "path": "04_Infrastruktur/Dokumentation/Architektur"},
]

FILE_ICONS = {
    ".pdf": "📕", ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️",
    ".docx": "📘", ".md": "📝", ".one": "📓", ".excalidraw": "✏️",
}


def check_service_health(port, timeout=1.2):
    """Prüft per HTTP, ob ein Dienst auf dem gegebenen Port antwortet."""
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/health")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


# ========== HTML TEMPLATE ==========
TEMPLATE = """
<!DOCTYPE html>
<html lang="de" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 AI-OS Dashboard</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        :root {
            --bg-primary: #0a0a0b;
            --bg-secondary: #0f0f11;
            --bg-tertiary: #141417;
            --bg-card: #18181c;
            --bg-elevated: #1e1e24;
            --bg-hover: #25252d;
            --text-primary: #f0f0f5;
            --text-secondary: #b0b0bb;
            --text-muted: #707078;
            --accent: #5b9cf5;
            --accent-hover: #7ab3ff;
            --accent-soft: rgba(91,156,245,0.12);
            --accent-glow: rgba(91,156,245,0.25);
            --success: #34d399;
            --success-soft: rgba(52,211,153,0.12);
            --warning: #fbbf24;
            --warning-soft: rgba(251,191,36,0.12);
            --danger: #f87171;
            --danger-soft: rgba(248,113,113,0.12);
            --border: rgba(255,255,255,0.06);
            --border-strong: rgba(255,255,255,0.12);
            --radius: 16px;
            --radius-sm: 10px;
            --radius-xs: 6px;
            --shadow: 0 8px 32px rgba(0,0,0,0.5);
            --shadow-lg: 0 16px 48px rgba(0,0,0,0.6);
            --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            height: 100vh;
            overflow: hidden;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            position: relative;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: 
                radial-gradient(circle at 25% 25%, rgba(91,156,245,0.04) 0%, transparent 50%),
                radial-gradient(circle at 75% 75%, rgba(52,211,153,0.04) 0%, transparent 50%),
                linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px;
            pointer-events: none;
            z-index: 0;
        }

        .app { position: relative; z-index: 1; }

        .app { display: flex; height: 100vh; }

        /* ===== Sidebar ===== */
        .sidebar {
            width: 230px;
            flex-shrink: 0;
            background: rgba(15,15,17,0.85);
            border-right: 1px solid var(--border);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            display: flex;
            flex-direction: column;
            padding: 1.25rem 0.9rem;
            transition: width 0.2s ease, transform 0.2s ease;
            overflow: hidden;
            z-index: 10;
        }

        /* Desktop: Hamburger klappt Sidebar auf Icon-Leiste zusammen */
        .app.sidebar-collapsed .sidebar { width: 68px; padding-left: 0.5rem; padding-right: 0.5rem; }
        .app.sidebar-collapsed .sidebar .label,
        .app.sidebar-collapsed .sidebar .nav-badge { display: none; }
        .app.sidebar-collapsed .nav-item { justify-content: center; }
        .app.sidebar-collapsed .brand { justify-content: center; padding-left: 0; padding-right: 0; }

        .sidebar-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.55);
            z-index: 150;
        }

        .brand {
            font-size: 1.05rem;
            font-weight: 700;
            padding: 0.5rem 0.6rem 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            width: 100%;
            text-align: left;
            padding: 0.6rem 0.75rem;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            border-radius: var(--radius-sm);
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: all var(--transition);
            margin-bottom: 0.15rem;
            position: relative;
        }

        .nav-item:hover {
            background: var(--bg-hover);
            color: var(--text-primary);
            transform: translateX(2px);
        }

        .nav-item.active {
            background: var(--accent-soft);
            color: var(--accent);
            box-shadow: 0 0 0 1px var(--accent-glow);
        }

        .nav-badge {
            margin-left: auto;
            font-size: 0.7rem;
            padding: 0.15rem 0.5rem;
            border-radius: 999px;
            background: var(--bg-hover);
            color: var(--text-secondary);
            font-weight: 600;
            letter-spacing: 0.02em;
        }
        .nav-badge.warn { background: var(--danger-soft); color: var(--danger); animation: pulse 2s infinite; }

        .sidebar-footer {
            margin-top: auto;
            padding: 0.75rem 0.6rem 0.25rem;
            border-top: 1px solid var(--border);
            font-size: 0.8rem;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* ===== Main ===== */
        .main { 
            flex: 1; 
            display: flex; 
            flex-direction: column; 
            min-width: 0;
            background: transparent;
        }

        .topbar {
            padding: 1.1rem 2rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
            background: rgba(10,10,11,0.75);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            position: sticky;
            top: 0;
            z-index: 5;
        }

        .topbar h2 {
            font-size: 1.2rem;
            font-weight: 600;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            letter-spacing: -0.01em;
        }

        .topbar-actions { display: flex; align-items: center; gap: 0.75rem; }

        .pill {
            font-size: 0.8rem;
            padding: 0.35rem 0.85rem;
            border-radius: 999px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            font-weight: 500;
            backdrop-filter: blur(8px);
        }
        .pill.ok {
            color: var(--success);
            border-color: rgba(52,211,153,0.3);
            background: var(--success-soft);
        }
        .pill.warn {
            color: var(--danger);
            border-color: rgba(248,113,113,0.3);
            background: var(--danger-soft);
        }

        .content {
            flex: 1;
            overflow-y: auto;
            padding: 1.75rem 2rem 3rem;
        }

        .tab-panel { display: none; animation: fadein 0.18s ease; }
        .tab-panel.active { display: block; }

        @keyframes fadein { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

        .status-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            display: inline-block;
            flex-shrink: 0;
        }

        .status-dot.online { background: var(--success); box-shadow: 0 0 8px var(--success); }
        .status-dot.offline { background: var(--danger); }
        .status-dot.pending { background: var(--warning); animation: pulse 1s infinite; }

        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 1.1rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-tertiary) 100%);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.25rem 1.4rem;
            transition: all var(--transition);
            display: flex;
            gap: 1rem;
            align-items: flex-start;
            position: relative;
            overflow: hidden;
        }

        .stat-card::after {
            content: '';
            position: absolute;
            top: 0; right: 0;
            width: 80px; height: 80px;
            background: radial-gradient(circle, var(--accent-soft) 0%, transparent 70%);
            opacity: 0;
            transition: opacity var(--transition);
        }

        .stat-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
        .stat-card:hover::after { opacity: 1; }

        .stat-icon {
            width: 44px; height: 44px;
            border-radius: var(--radius-sm);
            background: var(--accent-soft);
            border: 1px solid var(--border-strong);
            display: flex; align-items: center; justify-content: center;
            font-size: 1.3rem;
            flex-shrink: 0;
            position: relative;
            z-index: 1;
        }

        .stat-card h3 {
            color: var(--text-secondary);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.3rem;
            font-weight: 600;
        }

        .stat-value { font-size: 1.6rem; font-weight: 700; line-height: 1.2; }
        .stat-detail { font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.2rem; }

        .section-title {
            font-size: 1rem;
            font-weight: 600;
            margin: 0 0 1rem;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .section-title .muted { font-weight: 400; color: var(--text-secondary); font-size: 0.85rem; }

        /* ===== Services ===== */
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
            gap: 1rem;
        }

        .service-card {
            background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-tertiary) 100%);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.25rem 1.4rem;
            transition: all var(--transition);
            position: relative;
            overflow: hidden;
        }

        .service-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--accent) 0%, var(--success) 100%);
            opacity: 0;
            transition: opacity var(--transition);
        }

        .service-card:hover {
            border-color: var(--border-strong);
            transform: translateY(-3px);
            box-shadow: var(--shadow);
        }
        .service-card:hover::before { opacity: 1; }

        .service-card .head {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        }

        .service-card .icon {
            font-size: 1.4rem;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--accent-soft);
            border-radius: var(--radius-xs);
        }

        .service-card .name { font-weight: 600; font-size: 0.95rem; flex: 1; letter-spacing: -0.01em; }
        .service-card .desc { font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 1rem; min-height: 2.2em; line-height: 1.5; }
        .service-card .meta { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; }
        .service-card .port { font-size: 0.75rem; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; letter-spacing: 0.02em; }

        /* ===== Models / Knowledge grids ===== */
        .models-grid, .knowledge-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.1rem;
        }

        .model-card, .knowledge-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.25rem 1.4rem;
            transition: all var(--transition);
            position: relative;
        }

        .model-card:hover, .knowledge-card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }

        .model-card .name, .knowledge-card .name {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.4rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            letter-spacing: -0.01em;
        }

        .model-card .size { font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 1.1rem; font-family: 'JetBrains Mono', monospace; }
        .knowledge-card .desc { font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 0.85rem; line-height: 1.5; }
        .knowledge-card .count { font-size: 1.6rem; font-weight: 700; background: var(--accent-soft); color: var(--accent); padding: 0.25rem 0.75rem; border-radius: var(--radius-xs); display: inline-block; }
        .knowledge-card .count-label { font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.2rem; }

        .model-actions { display: flex; gap: 0.5rem; }

        .btn {
            padding: 0.5rem 0.9rem;
            border: none;
            border-radius: var(--radius-sm);
            cursor: pointer;
            font-size: 0.83rem;
            font-weight: 600;
            transition: all 0.15s;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
        }

        .btn-primary {
            background: var(--accent);
            color: white;
            box-shadow: 0 2px 8px rgba(91,156,245,0.25);
        }
        .btn-primary:hover {
            background: var(--accent-hover);
            box-shadow: 0 4px 12px rgba(91,156,245,0.4);
            transform: translateY(-1px);
        }

        .btn-success {
            background: var(--success);
            color: white;
            box-shadow: 0 2px 8px rgba(52,211,153,0.25);
        }
        .btn-success:hover { opacity: 0.9; box-shadow: 0 4px 12px rgba(52,211,153,0.4); }

        .btn-outline {
            background: transparent;
            border: 1px solid var(--border-strong);
            color: var(--text-primary);
            backdrop-filter: blur(8px);
        }
        .btn-outline:hover {
            border-color: var(--accent);
            color: var(--accent);
            background: var(--accent-soft);
        }

        .btn-danger {
            background: var(--danger-soft);
            color: var(--danger);
            border: 1px solid transparent;
        }
        .btn-danger:hover { background: var(--danger); color: white; border-color: var(--danger); }

        .btn-sm { padding: 0.35rem 0.7rem; font-size: 0.75rem; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-icon { padding: 0.6rem 0.75rem; flex-shrink: 0; }

        #mic-btn.recording {
            background: var(--danger);
            border-color: var(--danger);
            color: white;
            animation: pulse 1s infinite;
        }

        .hamburger-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 38px;
            height: 38px;
            flex-shrink: 0;
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-primary);
            border-radius: var(--radius-sm);
            cursor: pointer;
            font-size: 1.05rem;
        }
        .hamburger-btn:hover { border-color: var(--accent); color: var(--accent); }

        /* ===== Chat ===== */
        .chat-layout {
            display: flex;
            gap: 1.25rem;
            height: calc(100vh - 220px);
        }

        .chat-layout .chat-section { flex: 1; min-width: 0; height: 100%; }

        .chat-section {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .chat-header {
            padding: 0.8rem 1.25rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: wrap;
            flex-shrink: 0;
        }

        .chat-title { font-weight: 600; font-size: 0.92rem; }
        .chat-header-actions { display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap; }

        #rag-toggle.active { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }

        .message .msg-body p { margin: 0 0 0.5em; }
        .message .msg-body p:last-child { margin-bottom: 0; }
        .message .msg-body code {
            background: rgba(255,255,255,0.08);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 0.08em 0.35em;
            font-family: Consolas, 'Courier New', monospace;
            font-size: 0.85em;
        }
        .message .msg-body pre {
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 0.7rem 0.85rem;
            overflow-x: auto;
            margin: 0.5em 0;
        }
        .message .msg-body pre code { background: none; border: none; padding: 0; }
        .message .msg-body ul { margin: 0.35em 0 0.35em 1.2em; }

        .msg-copy {
            float: right;
            margin-left: 0.6rem;
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 0.8rem;
            padding: 0;
        }
        .msg-copy:hover { color: var(--accent); }

        .rag-sources {
            margin-top: 0.55rem;
            padding-top: 0.5rem;
            border-top: 1px dashed var(--border);
            font-size: 0.72rem;
            color: var(--text-muted);
        }

        .chat-messages {
            padding: 1.25rem;
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 0.9rem;
        }

        .message { padding: 0.85rem 1rem; border-radius: 12px; max-width: 78%; line-height: 1.5; }

        .message.user { background: var(--accent); color: white; align-self: flex-end; }
        .message.assistant { background: var(--bg-secondary); border: 1px solid var(--border); align-self: flex-start; }

        .message .role {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.3rem;
            opacity: 0.7;
        }

        .thinking { display: flex; gap: 0.25rem; align-items: center; }
        .thinking span { width: 6px; height: 6px; border-radius: 50%; background: var(--text-secondary); animation: bounce 1.2s infinite; }
        .thinking span:nth-child(2) { animation-delay: 0.15s; }
        .thinking span:nth-child(3) { animation-delay: 0.3s; }
        @keyframes bounce { 0%,60%,100% { transform: translateY(0); opacity: 0.5; } 30% { transform: translateY(-4px); opacity: 1; } }

        .chat-input-area {
            display: flex;
            gap: 0.5rem;
            padding: 0.9rem 1.25rem;
            border-top: 1px solid var(--border);
            flex-shrink: 0;
        }

        .chat-input {
            flex: 1;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 0.7rem 0.9rem;
            color: var(--text-primary);
            font-size: 0.9rem;
            resize: none;
            font-family: inherit;
        }

        .chat-input:focus { outline: none; border-color: var(--accent); }

        select {
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 0.4rem 0.7rem;
            font-size: 0.83rem;
        }

        /* ===== Ideen-Panel (Notizzettel + Skizze) ===== */
        .idea-panel {
            width: 320px;
            flex-shrink: 0;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .idea-panel-tabs { display: flex; border-bottom: 1px solid var(--border); flex-shrink: 0; }

        .idea-tab {
            flex: 1;
            padding: 0.75rem 0.5rem;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: color 0.15s, border-color 0.15s;
        }
        .idea-tab:hover { color: var(--text-primary); }
        .idea-tab.active { color: var(--accent); border-bottom-color: var(--accent); }

        .idea-tab-panel { display: none; flex: 1; flex-direction: column; padding: 1rem; overflow-y: auto; min-height: 0; }
        .idea-tab-panel.active { display: flex; }

        #notepad {
            flex: 1;
            resize: none;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            color: var(--text-primary);
            padding: 0.75rem;
            font-size: 0.85rem;
            font-family: inherit;
            margin-bottom: 0.75rem;
            min-height: 160px;
        }
        #notepad:focus { outline: none; border-color: var(--accent); }

        .idea-panel-actions { display: flex; gap: 0.5rem; justify-content: space-between; flex-shrink: 0; }
        .idea-panel-actions .btn { flex: 1; justify-content: center; }

        .sketch-toolbar {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
            flex-wrap: wrap;
            flex-shrink: 0;
        }

        .sketch-toolbar input[type="color"] {
            width: 32px; height: 32px;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: transparent;
            cursor: pointer;
            padding: 0;
        }

        .sketch-toolbar input[type="range"] { width: 80px; }
        .sketch-tool.active { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }

        #sketch-canvas {
            width: 100%;
            aspect-ratio: 1 / 1;
            background: #ffffff;
            border-radius: var(--radius-sm);
            cursor: crosshair;
            touch-action: none;
            flex-shrink: 0;
        }

        .idea-panel-hint { font-size: 0.72rem; color: var(--text-secondary); margin-top: 0.6rem; line-height: 1.4; }

        /* ===== Files ===== */
        .file-system {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.4rem;
        }

        .file-tree { font-family: 'Courier New', monospace; font-size: 0.85rem; }
        .file-tree .dir { color: var(--accent); cursor: pointer; padding: 0.25rem 0; user-select: none; }
        .file-tree .file { color: var(--text-secondary); padding: 0.15rem 0 0.15rem 1.5rem; }
        .file-tree .indent { padding-left: 1.5rem; }

        .empty-state { text-align: center; padding: 3rem 1rem; color: var(--text-secondary); }
        .empty-state.error { color: var(--danger); }

        /* ===== Modal ===== */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }

        .modal.active { display: flex; }

        .modal-content {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.75rem;
            max-width: 460px;
            width: 90%;
        }

        .modal-content h2 { margin-bottom: 0.5rem; font-size: 1.1rem; }
        .modal-content p { color: var(--text-secondary); font-size: 0.88rem; margin-bottom: 1.1rem; }

        .modal-content input {
            width: 100%;
            padding: 0.7rem;
            margin-bottom: 1rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            color: var(--text-primary);
            font-size: 0.9rem;
        }

        .modal-actions { display: flex; gap: 0.5rem; justify-content: flex-end; }

        /* ===== Toasts ===== */
        #toast-container {
            position: fixed;
            bottom: 1.5rem;
            right: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            z-index: 2000;
        }

        .toast {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-left: 3px solid var(--accent);
            border-radius: var(--radius-sm);
            padding: 0.75rem 1.1rem;
            font-size: 0.85rem;
            box-shadow: var(--shadow);
            opacity: 0;
            transform: translateY(8px);
            transition: opacity 0.25s, transform 0.25s;
            max-width: 320px;
        }
        .toast.show { opacity: 1; transform: translateY(0); }
        .toast.success { border-left-color: var(--success); }
        .toast.error { border-left-color: var(--danger); }

        /* ===== Architektur: Ebenen-Stapel ===== */
        .layer-band {
            background: linear-gradient(180deg, var(--bg-card), var(--bg-secondary));
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.1rem 1.3rem 1.3rem;
        }

        .layer-band-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-secondary);
            font-weight: 700;
            margin-bottom: 0.75rem;
        }

        .layer-band-items {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 0.75rem;
        }

        .layer-chip {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 0.65rem 0.85rem;
        }

        .layer-chip.missing { opacity: 0.45; border-style: dashed; }
        .layer-chip .icon { font-size: 1.15rem; flex-shrink: 0; }
        .layer-chip .name { font-size: 0.85rem; font-weight: 600; }
        .layer-chip .desc { font-size: 0.72rem; color: var(--text-secondary); }
        .layer-chip .count {
            margin-left: auto;
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--accent);
            background: var(--accent-soft);
            border-radius: 999px;
            padding: 0.15rem 0.55rem;
            flex-shrink: 0;
        }

        .layer-arrow {
            text-align: center;
            color: var(--text-secondary);
            font-size: 1.1rem;
            padding: 0.35rem 0;
            opacity: 0.6;
        }

        /* ===== Architektur: Wiki-Dokumente ===== */
        .wiki-doc-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 0.6rem;
        }

        .wiki-doc {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 0.6rem 0.8rem;
            text-decoration: none;
            color: var(--text-primary);
            transition: border-color 0.15s, transform 0.15s;
            overflow: hidden;
        }

        .wiki-doc:hover { border-color: var(--accent); transform: translateY(-1px); }
        .wiki-doc .icon { font-size: 1.1rem; flex-shrink: 0; }
        .wiki-doc .name { font-size: 0.8rem; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .wiki-doc .size { font-size: 0.7rem; color: var(--text-secondary); flex-shrink: 0; }

        /* Chat + Ideen-Panel stapeln, sobald es eng wird */
        @media (max-width: 1150px) {
            .chat-layout { flex-direction: column; height: auto; }
            .chat-layout .chat-section { height: 62vh; }
            .idea-panel { width: 100%; height: 380px; }
        }

        /* Sidebar wird zur ausklappbaren Drawer-Leiste (Hamburger) */
        @media (max-width: 900px) {
            .sidebar {
                position: fixed;
                top: 0; left: 0;
                height: 100vh;
                width: 250px !important;
                padding-left: 0.9rem !important;
                padding-right: 0.9rem !important;
                transform: translateX(-100%);
                z-index: 200;
                box-shadow: var(--shadow);
            }
            .sidebar .label, .sidebar .nav-badge { display: inline-flex !important; }
            .app.sidebar-collapsed .sidebar .nav-item,
            .app.sidebar-collapsed .brand { justify-content: flex-start; }

            .app.mobile-nav-open .sidebar { transform: translateX(0); }
            .app.mobile-nav-open .sidebar-overlay { display: block; }

            .topbar { padding: 0.85rem 1rem; flex-wrap: wrap; row-gap: 0.6rem; }
            .content { padding: 1.1rem 1rem 2.5rem; }

            .stats-grid, .services-grid, .models-grid, .knowledge-grid, .wiki-doc-grid {
                grid-template-columns: 1fr;
            }
            .layer-band-items { grid-template-columns: 1fr; }

            .message { max-width: 92%; }
            .chat-layout .chat-section { height: 58vh; }
            .idea-panel { height: 340px; }
        }

        @media (max-width: 480px) {
            .topbar-actions { width: 100%; justify-content: space-between; }
            .stat-card { padding: 1rem; }
        }
    </style>
</head>
<body>
    <div class="app">
        <aside class="sidebar">
            <div class="brand">🧠 <span class="label">AI-OS</span></div>
            <nav>
                <button class="nav-item active" data-tab="overview" onclick="showTab('overview')">📊 <span class="label">Übersicht</span></button>
                <button class="nav-item" data-tab="services" onclick="showTab('services')">🧩 <span class="label">Dienste</span><span class="nav-badge" id="services-badge">-</span></button>
                <button class="nav-item" data-tab="chat" onclick="showTab('chat')">💬 <span class="label">Chat</span></button>
                <button class="nav-item" data-tab="models" onclick="showTab('models')">📦 <span class="label">Modelle</span></button>
                <button class="nav-item" data-tab="knowledge" onclick="showTab('knowledge')">🧠 <span class="label">Gedächtnis</span></button>
                <button class="nav-item" data-tab="files" onclick="showTab('files')">📂 <span class="label">Dateien</span></button>
                <button class="nav-item" data-tab="architecture" onclick="showTab('architecture')">🏛️ <span class="label">Architektur</span></button>
            </nav>
            <div class="sidebar-footer">
                <span class="status-dot" id="ollama-dot"></span>
                <span class="label">Ollama</span>
            </div>
        </aside>

        <div class="sidebar-overlay" id="sidebar-overlay" onclick="closeMobileNav()"></div>

        <div class="main">
            <div class="topbar">
                <div style="display:flex;align-items:center;gap:0.75rem;min-width:0;">
                    <button class="hamburger-btn" onclick="toggleSidebar()" title="Menü ein-/ausblenden">☰</button>
                    <h2 id="topbar-title">📊 Übersicht</h2>
                </div>
                <div class="topbar-actions">
                    <span class="pill" id="services-summary">Dienste werden geprüft...</span>
                    <button class="btn btn-outline btn-sm" onclick="refreshAll()">🔄 Aktualisieren</button>
                </div>
            </div>

            <div class="content">
                <!-- === Übersicht === -->
                <section class="tab-panel active" id="tab-overview">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-icon">🧠</div>
                            <div>
                                <h3>KI Modelle</h3>
                                <div class="stat-value" id="model-count">-</div>
                                <div class="stat-detail" id="models-detail">Lade...</div>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">🧩</div>
                            <div>
                                <h3>Dienste online</h3>
                                <div class="stat-value" id="services-count">-</div>
                                <div class="stat-detail">von 7 Ebenen-Diensten</div>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">📁</div>
                            <div>
                                <h3>Dateien</h3>
                                <div class="stat-value" id="file-count">-</div>
                                <div class="stat-detail">Im Wissensspeicher (00_Wissen)</div>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">💾</div>
                            <div>
                                <h3>Speicher</h3>
                                <div class="stat-value" id="memory-usage">-</div>
                                <div class="stat-detail" id="uptime-detail">System bereit</div>
                            </div>
                        </div>
                    </div>

                    <div class="section-title">🧩 Dienste-Status <span class="muted">– Klick auf "Dienste" für Details & Start-Optionen</span></div>
                    <div class="services-grid" id="overview-services-grid">
                        <div class="empty-state">Lade Dienste...</div>
                    </div>
                </section>

                <!-- === Dienste === -->
                <section class="tab-panel" id="tab-services">
                    <div class="section-title">🧩 Alle Dienste der AI-OS Ebenen-Struktur</div>
                    <div class="services-grid" id="services-grid">
                        <div class="empty-state">Lade Dienste...</div>
                    </div>
                </section>

                <!-- === Chat === -->
                <section class="tab-panel" id="tab-chat">
                    <div class="chat-layout">
                        <div class="chat-section">
                            <div class="chat-header">
                                <span class="chat-title">💬 Business-Ideen-Chat</span>
                                <div class="chat-header-actions">
                                    <button class="btn btn-outline btn-sm" id="rag-toggle" onclick="toggleRagMode()" title="Antworten mit Kontext aus deiner Wissensdatenbank (Gedächtnis/RAG-Dienst)">🧠 Wissensmodus</button>
                                    <button class="btn btn-outline btn-sm" onclick="exportChat()" title="Chat als Markdown herunterladen">⬇</button>
                                    <button class="btn btn-outline btn-sm" onclick="clearChat()" title="Chatverlauf löschen">🗑</button>
                                    <select id="model-select"></select>
                                </div>
                            </div>
                            <div class="chat-messages" id="chat-messages">
                                <div class="message assistant">
                                    <div class="role">🤖 System</div>
                                    Hallo! Ich bin deine lokale KI. Nutze rechts den Notizzettel oder die Skizze, um deine
                                    Business-Idee vorzuformulieren, oder sprich sie direkt über das Mikrofon ein.
                                </div>
                            </div>
                            <div class="chat-input-area">
                                <button class="btn btn-outline btn-icon" id="mic-btn" onclick="toggleMic()" title="Spracheingabe (Mikrofon)">🎤</button>
                                <textarea class="chat-input" id="chat-input" rows="1" placeholder="Nachricht eingeben oder Mikrofon nutzen..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();sendMessage();}"></textarea>
                                <button class="btn btn-primary" onclick="sendMessage()">Senden</button>
                            </div>
                        </div>

                        <aside class="idea-panel">
                            <div class="idea-panel-tabs">
                                <button class="idea-tab active" data-idea-tab="notes" onclick="showIdeaTab('notes')">🗒️ Notizzettel</button>
                                <button class="idea-tab" data-idea-tab="sketch" onclick="showIdeaTab('sketch')">✏️ Skizze</button>
                            </div>
                            <div class="idea-tab-panel active" id="idea-tab-notes">
                                <textarea id="notepad" placeholder="Sammle hier Stichpunkte zu deiner Business-Idee — Zielgruppe, Problem, Lösung, offene Fragen — bevor du sie als Nachricht formulierst."></textarea>
                                <div class="idea-panel-actions">
                                    <button class="btn btn-outline btn-sm" onclick="clearNotepad()">🗑 Leeren</button>
                                    <button class="btn btn-primary btn-sm" onclick="insertNotepadIntoChat()">➡ In Chat einfügen</button>
                                </div>
                            </div>
                            <div class="idea-tab-panel" id="idea-tab-sketch">
                                <div class="sketch-toolbar">
                                    <button class="btn btn-outline btn-sm sketch-tool active" id="tool-pen" onclick="setSketchTool('pen')" title="Stift">✏️</button>
                                    <button class="btn btn-outline btn-sm sketch-tool" id="tool-eraser" onclick="setSketchTool('eraser')" title="Radierer">🧽</button>
                                    <input type="color" id="sketch-color" value="#3987e5" title="Farbe">
                                    <input type="range" id="sketch-size" min="1" max="24" value="3" title="Stiftdicke">
                                    <button class="btn btn-outline btn-sm" onclick="undoSketch()" title="Rückgängig">↩️</button>
                                    <button class="btn btn-outline btn-sm" onclick="clearSketch()" title="Alles löschen">🗑</button>
                                    <button class="btn btn-outline btn-sm" onclick="saveSketchAsPng()" title="Als PNG speichern">💾</button>
                                </div>
                                <canvas id="sketch-canvas" width="640" height="640"></canvas>
                                <div class="idea-panel-hint">Skizziere Ideen, Diagramme, Flowcharts — wird lokal gespeichert. ↩️ macht den letzten Strich rückgängig.</div>
                            </div>
                        </aside>
                    </div>
                </section>

                <!-- === Modelle === -->
                <section class="tab-panel" id="tab-models">
                    <div class="section-title">📦 Installierte Ollama-Modelle</div>
                    <div class="models-grid" id="models-grid">
                        <div class="empty-state">Lade Modelle...</div>
                    </div>
                </section>

                <!-- === Gedächtnis === -->
                <section class="tab-panel" id="tab-knowledge">
                    <div class="section-title">🧠 Wissensmodell (06_Gedächtnis) <span class="muted">– bewusst getrennte Kategorien statt einem einzigen Vektorindex</span></div>
                    <div class="knowledge-grid" id="knowledge-grid">
                        <div class="empty-state">Lade Gedächtnis-Übersicht...</div>
                    </div>
                </section>

                <!-- === Dateien === -->
                <section class="tab-panel" id="tab-files">
                    <div class="section-title">📂 Wissensspeicher (00_Wissen)</div>
                    <div class="file-system">
                        <div class="file-tree" id="file-tree">Lade Dateistruktur...</div>
                    </div>
                </section>

                <!-- === Architektur === -->
                <section class="tab-panel" id="tab-architecture">
                    <div class="section-title">🏛️ Ebenen-Stapel <span class="muted">– Live-Stand deines AI-OS, kein statisches Diagramm</span></div>
                    <div id="layer-stack">
                        <div class="empty-state">Lade Architektur-Stand...</div>
                    </div>

                    <div class="section-title" style="margin-top:2.25rem;">📖 Referenz- & Architektur-Dokumente</div>
                    <div id="wiki-docs">
                        <div class="empty-state">Lade Dokumente...</div>
                    </div>
                </section>
            </div>
        </div>
    </div>

    <!-- New Model Modal -->
    <div class="modal" id="model-modal">
        <div class="modal-content">
            <h2>📥 Neues Modell laden</h2>
            <input type="text" id="model-name-input" placeholder="z.B. llama3.2" list="model-suggestions">
            <datalist id="model-suggestions">
                <option value="llama3.2">
                <option value="llama3.2:1b">
                <option value="mistral">
                <option value="phi3">
                <option value="gemma2">
                <option value="qwen2.5">
                <option value="deepseek-coder">
                <option value="nomic-embed-text">
            </datalist>
            <div class="modal-actions">
                <button class="btn btn-outline" onclick="closeModelModal()">Abbrechen</button>
                <button class="btn btn-success" onclick="pullModel()">📥 Herunterladen</button>
            </div>
        </div>
    </div>

    <!-- Confirm Modal -->
    <div class="modal" id="confirm-modal">
        <div class="modal-content">
            <h2 id="confirm-title">Bist du sicher?</h2>
            <p id="confirm-text"></p>
            <div class="modal-actions">
                <button class="btn btn-outline" onclick="closeConfirmModal()">Abbrechen</button>
                <button class="btn btn-danger" id="confirm-action-btn">Bestätigen</button>
            </div>
        </div>
    </div>

    <div id="toast-container"></div>

    <script>
        // === State ===
        let chatHistory = [];
        let knownServices = [];

        // === Tabs ===
        function showTab(tab) {
            document.querySelectorAll('.tab-panel').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tab).classList.add('active');
            document.querySelector(`.nav-item[data-tab="${tab}"]`).classList.add('active');
            const titles = {overview: '📊 Übersicht', services: '🧩 Dienste', chat: '💬 Chat', models: '📦 Modelle', knowledge: '🧠 Gedächtnis', files: '📂 Dateien', architecture: '🏛️ Architektur'};
            document.getElementById('topbar-title').textContent = titles[tab] || tab;
            closeMobileNav();
        }

        // === Hamburger / Sidebar ===
        function isMobile() { return window.innerWidth <= 900; }

        function toggleSidebar() {
            const app = document.querySelector('.app');
            if (isMobile()) {
                app.classList.toggle('mobile-nav-open');
            } else {
                app.classList.toggle('sidebar-collapsed');
                localStorage.setItem('aios-sidebar-collapsed', app.classList.contains('sidebar-collapsed') ? '1' : '0');
            }
        }

        function closeMobileNav() {
            document.querySelector('.app').classList.remove('mobile-nav-open');
        }

        function restoreSidebarPreference() {
            if (!isMobile() && localStorage.getItem('aios-sidebar-collapsed') === '1') {
                document.querySelector('.app').classList.add('sidebar-collapsed');
            }
        }

        // === Ideen-Panel: Notizzettel & Skizze ===
        function showIdeaTab(tab) {
            document.querySelectorAll('.idea-tab').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.idea-tab-panel').forEach(el => el.classList.remove('active'));
            document.querySelector(`.idea-tab[data-idea-tab="${tab}"]`).classList.add('active');
            document.getElementById('idea-tab-' + tab).classList.add('active');
        }

        function setupNotepad() {
            const pad = document.getElementById('notepad');
            pad.value = localStorage.getItem('aios-notepad') || '';
            pad.addEventListener('input', () => localStorage.setItem('aios-notepad', pad.value));
        }

        function clearNotepad() {
            const pad = document.getElementById('notepad');
            pad.value = '';
            localStorage.removeItem('aios-notepad');
            pad.focus();
        }

        function insertNotepadIntoChat() {
            const text = document.getElementById('notepad').value.trim();
            if (!text) { toast('Notizzettel ist leer.', 'error'); return; }
            const input = document.getElementById('chat-input');
            input.value = (input.value.trim() ? input.value.trim() + '\\n\\n' : '') + text;
            input.focus();
            toast('Notizen in die Nachricht übernommen — jetzt anpassen & senden.', 'success');
        }

        let sketchCtx = null;
        let sketchDrawing = false;
        let sketchTool = 'pen';
        let sketchUndoStack = [];

        function setSketchTool(tool) {
            sketchTool = tool;
            document.querySelectorAll('.sketch-tool').forEach(el => el.classList.remove('active'));
            document.getElementById('tool-' + tool).classList.add('active');
        }

        function pushSketchUndo() {
            const canvas = document.getElementById('sketch-canvas');
            sketchUndoStack.push(canvas.toDataURL());
            if (sketchUndoStack.length > 25) sketchUndoStack.shift();
        }

        function undoSketch() {
            if (!sketchUndoStack.length) { toast('Nichts zum Rückgängigmachen.'); return; }
            const canvas = document.getElementById('sketch-canvas');
            const prev = sketchUndoStack.pop();
            const img = new Image();
            img.onload = () => {
                sketchCtx.globalCompositeOperation = 'source-over';
                sketchCtx.clearRect(0, 0, canvas.width, canvas.height);
                sketchCtx.drawImage(img, 0, 0, canvas.width, canvas.height);
                persistSketch();
            };
            img.src = prev;
        }

        function persistSketch() {
            const canvas = document.getElementById('sketch-canvas');
            try { localStorage.setItem('aios-sketch', canvas.toDataURL()); } catch (e) {}
        }

        function setupSketch() {
            const canvas = document.getElementById('sketch-canvas');
            sketchCtx = canvas.getContext('2d');
            sketchCtx.lineCap = 'round';
            sketchCtx.lineJoin = 'round';

            const saved = localStorage.getItem('aios-sketch');
            if (saved) {
                const img = new Image();
                img.onload = () => sketchCtx.drawImage(img, 0, 0, canvas.width, canvas.height);
                img.src = saved;
            }

            function pos(e) {
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                const clientX = e.touches ? e.touches[0].clientX : e.clientX;
                const clientY = e.touches ? e.touches[0].clientY : e.clientY;
                return { x: (clientX - rect.left) * scaleX, y: (clientY - rect.top) * scaleY };
            }

            function start(e) {
                sketchDrawing = true;
                pushSketchUndo();
                const p = pos(e);
                sketchCtx.beginPath();
                sketchCtx.moveTo(p.x, p.y);
                e.preventDefault();
            }
            function move(e) {
                if (!sketchDrawing) return;
                const p = pos(e);
                if (sketchTool === 'eraser') {
                    sketchCtx.globalCompositeOperation = 'destination-out';
                    sketchCtx.strokeStyle = 'rgba(0,0,0,1)';
                    sketchCtx.lineWidth = document.getElementById('sketch-size').value * 3;
                } else {
                    sketchCtx.globalCompositeOperation = 'source-over';
                    sketchCtx.strokeStyle = document.getElementById('sketch-color').value;
                    sketchCtx.lineWidth = document.getElementById('sketch-size').value;
                }
                sketchCtx.lineTo(p.x, p.y);
                sketchCtx.stroke();
                e.preventDefault();
            }
            function end() {
                if (!sketchDrawing) return;
                sketchDrawing = false;
                sketchCtx.globalCompositeOperation = 'source-over';
                persistSketch();
            }

            canvas.addEventListener('mousedown', start);
            canvas.addEventListener('mousemove', move);
            window.addEventListener('mouseup', end);
            canvas.addEventListener('touchstart', start, { passive: false });
            canvas.addEventListener('touchmove', move, { passive: false });
            canvas.addEventListener('touchend', end);
        }

        function clearSketch() {
            pushSketchUndo();
            const canvas = document.getElementById('sketch-canvas');
            sketchCtx.globalCompositeOperation = 'source-over';
            sketchCtx.clearRect(0, 0, canvas.width, canvas.height);
            localStorage.removeItem('aios-sketch');
        }

        function saveSketchAsPng() {
            const canvas = document.getElementById('sketch-canvas');
            // Auf weißen Hintergrund kompositieren, sonst wäre das PNG transparent
            const out = document.createElement('canvas');
            out.width = canvas.width;
            out.height = canvas.height;
            const octx = out.getContext('2d');
            octx.fillStyle = '#ffffff';
            octx.fillRect(0, 0, out.width, out.height);
            octx.drawImage(canvas, 0, 0);
            const a = document.createElement('a');
            a.download = 'ai-os-skizze.png';
            a.href = out.toDataURL('image/png');
            a.click();
            toast('Skizze als PNG gespeichert.', 'success');
        }

        // === Mikrofon / Spracheingabe ===
        let recognition = null;
        let recognizing = false;
        let micBaseText = '';

        function setupSpeechRecognition() {
            const micBtn = document.getElementById('mic-btn');
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                micBtn.disabled = true;
                micBtn.title = 'Spracheingabe wird von diesem Browser nicht unterstützt (z.B. Chrome verwenden)';
                return;
            }
            recognition = new SpeechRecognition();
            recognition.lang = 'de-DE';
            recognition.continuous = true;
            recognition.interimResults = true;

            recognition.onstart = () => {
                recognizing = true;
                micBtn.classList.add('recording');
                const input = document.getElementById('chat-input');
                micBaseText = input.value.trim();
                if (micBaseText) micBaseText += ' ';
            };

            recognition.onresult = (event) => {
                let interim = '';
                let finalChunk = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) finalChunk += transcript + ' ';
                    else interim += transcript;
                }
                if (finalChunk) micBaseText += finalChunk;
                document.getElementById('chat-input').value = micBaseText + interim;
            };

            recognition.onerror = (e) => {
                if (e.error !== 'no-speech' && e.error !== 'aborted') {
                    toast('Spracheingabe-Fehler: ' + e.error, 'error');
                }
                stopMicUi();
            };

            recognition.onend = () => stopMicUi();
        }

        function toggleMic() {
            if (!recognition) return;
            if (recognizing) {
                recognition.stop();
            } else {
                try { recognition.start(); } catch (e) {}
            }
        }

        function stopMicUi() {
            recognizing = false;
            document.getElementById('mic-btn').classList.remove('recording');
        }

        // === Toasts ===
        function toast(msg, type = 'info') {
            const container = document.getElementById('toast-container');
            const el = document.createElement('div');
            el.className = 'toast ' + type;
            el.textContent = msg;
            container.appendChild(el);
            requestAnimationFrame(() => el.classList.add('show'));
            setTimeout(() => {
                el.classList.remove('show');
                setTimeout(() => el.remove(), 300);
            }, 3800);
        }

        // === Confirm Modal ===
        function askConfirm(title, text, onConfirm) {
            document.getElementById('confirm-title').textContent = title;
            document.getElementById('confirm-text').textContent = text;
            const btn = document.getElementById('confirm-action-btn');
            const freshBtn = btn.cloneNode(true);
            btn.replaceWith(freshBtn);
            freshBtn.addEventListener('click', () => { closeConfirmModal(); onConfirm(); });
            document.getElementById('confirm-modal').classList.add('active');
        }
        function closeConfirmModal() {
            document.getElementById('confirm-modal').classList.remove('active');
        }

        // === Load Models ===
        async function loadModels() {
            try {
                const resp = await fetch('/api/models');
                const data = await resp.json();
                const grid = document.getElementById('models-grid');
                const select = document.getElementById('model-select');

                if (data.error) {
                    grid.innerHTML = `<div class="empty-state error">❌ ${data.error}</div>`;
                    document.getElementById('ollama-dot').className = 'status-dot offline';
                    return;
                }

                document.getElementById('model-count').textContent = data.models.length;
                document.getElementById('models-detail').textContent =
                    data.models.length ? data.models.map(m => m.name.split(':')[0]).join(', ') : 'Keine Modelle installiert';

                grid.innerHTML = (data.models.length ? data.models.map(m => `
                    <div class="model-card">
                        <div class="name">🧠 ${m.name}</div>
                        <div class="size">${m.size}</div>
                        <div class="model-actions">
                            <button class="btn btn-primary btn-sm" onclick="useModel('${m.name}')">▶ Nutzen</button>
                            <button class="btn btn-danger btn-sm" onclick="confirmDeleteModel('${m.name}')">🗑 Löschen</button>
                        </div>
                    </div>
                `).join('') : '') + `
                    <div class="model-card" style="border:2px dashed var(--border);display:flex;align-items:center;justify-content:center;cursor:pointer;" onclick="openModelModal()">
                        <div style="text-align:center;color:var(--text-secondary);">
                            <div style="font-size:1.6rem;margin-bottom:0.3rem;">+</div>
                            <div style="font-size:0.85rem;">Neues Modell laden</div>
                        </div>
                    </div>
                `;

                select.innerHTML = data.models.map(m => `<option value="${m.name}">${m.name}</option>`).join('');

                document.getElementById('ollama-dot').className = 'status-dot online';
            } catch (e) {
                document.getElementById('ollama-dot').className = 'status-dot offline';
                document.getElementById('models-grid').innerHTML = `<div class="empty-state error">❌ Verbindung zu Ollama fehlgeschlagen</div>`;
            }
        }

        // === Load Stats ===
        async function loadStats() {
            try {
                const resp = await fetch('/api/stats');
                const data = await resp.json();
                document.getElementById('file-count').textContent = data.files;
                document.getElementById('memory-usage').textContent = data.memory;
                document.getElementById('uptime-detail').textContent = data.os;
            } catch (e) {}
        }

        // === Load Services ===
        function renderServiceCard(svc) {
            const statusClass = svc.online ? 'online' : 'offline';
            const canStart = !svc.online && svc.key !== 'dashboard';
            return `
                <div class="service-card">
                    <div class="head">
                        <span class="icon">${svc.icon}</span>
                        <span class="name">${svc.name}</span>
                        <span class="status-dot ${statusClass}" title="${svc.online ? 'Online' : 'Offline'}"></span>
                    </div>
                    <div class="desc">${svc.desc}</div>
                    <div class="meta">
                        <span class="port">:${svc.port} · ${svc.layer}</span>
                        ${canStart
                            ? `<button class="btn btn-success btn-sm" onclick="startService('${svc.key}', this)">▶ Starten</button>`
                            : (svc.online ? `<span class="pill ok" style="padding:0.2rem 0.6rem;">läuft</span>` : '')}
                    </div>
                </div>`;
        }

        async function loadServices() {
            try {
                const resp = await fetch('/api/services');
                const data = await resp.json();
                knownServices = data.services;
                const html = data.services.map(renderServiceCard).join('');
                document.getElementById('services-grid').innerHTML = html;
                document.getElementById('overview-services-grid').innerHTML = html;

                const online = data.services.filter(s => s.online).length;
                const total = data.services.length;
                document.getElementById('services-count').textContent = `${online}/${total}`;
                document.getElementById('services-badge').textContent = `${online}/${total}`;
                document.getElementById('services-badge').className = 'nav-badge' + (online < total ? ' warn' : '');

                const summary = document.getElementById('services-summary');
                summary.textContent = `${online}/${total} Dienste online`;
                summary.className = 'pill ' + (online === total ? 'ok' : (online === 0 ? 'warn' : ''));
            } catch (e) {
                document.getElementById('services-grid').innerHTML = `<div class="empty-state error">❌ Dienste-Status konnte nicht geladen werden</div>`;
            }
        }

        async function startService(key, btnEl) {
            btnEl.disabled = true;
            btnEl.textContent = '⏳ Startet...';
            try {
                const resp = await fetch('/api/services/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ key })
                });
                const data = await resp.json();
                if (data.success) {
                    toast('Dienst wird gestartet, prüfe in Kürze den Status...', 'success');
                    setTimeout(loadServices, 2500);
                } else {
                    toast('Fehler: ' + data.error, 'error');
                    btnEl.disabled = false;
                    btnEl.textContent = '▶ Starten';
                }
            } catch (e) {
                toast('Fehler: ' + e.message, 'error');
                btnEl.disabled = false;
                btnEl.textContent = '▶ Starten';
            }
        }

        // === Load Knowledge Overview ===
        async function loadKnowledge() {
            try {
                const resp = await fetch('/api/knowledge');
                const data = await resp.json();
                document.getElementById('knowledge-grid').innerHTML = data.categories.map(c => `
                    <div class="knowledge-card">
                        <div class="name">${c.icon} ${c.name}</div>
                        <div class="desc">${c.desc}</div>
                        <div class="count">${c.count}</div>
                        <div class="count-label">Dateien</div>
                    </div>
                `).join('');
            } catch (e) {
                document.getElementById('knowledge-grid').innerHTML = `<div class="empty-state error">❌ Gedächtnis-Übersicht konnte nicht geladen werden</div>`;
            }
        }

        // === Load File Tree ===
        async function loadFileTree() {
            try {
                const resp = await fetch('/api/files');
                const data = await resp.json();
                document.getElementById('file-tree').innerHTML = renderTree(data.tree);
            } catch (e) {
                document.getElementById('file-tree').innerHTML = `<div class="empty-state error">❌ Konnte Dateistruktur nicht laden</div>`;
            }
        }

        function renderTree(items, depth = 0) {
            if (!items || items.length === 0) return '<span style="color:var(--text-secondary)">(leer)</span>';
            const indent = ' '.repeat(depth * 2);
            return items.map(item => {
                if (item.type === 'dir') {
                    return `<div class="dir" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display==='none'?'':'none'">
                        ${indent}📁 ${item.name}</div>
                        <div class="indent" style="display:none">${renderTree(item.children, depth + 1)}</div>`;
                } else {
                    return `<div class="file">${indent}📄 ${item.name}</div>`;
                }
            }).join('');
        }

        // === Architektur ===
        async function loadArchitecture() {
            try {
                const resp = await fetch('/api/architecture');
                const data = await resp.json();
                const groups = {};
                data.layers.forEach(l => { (groups[l.group] = groups[l.group] || []).push(l); });

                document.getElementById('layer-stack').innerHTML = Object.entries(groups).map(([group, layers]) => `
                    <div class="layer-band">
                        <div class="layer-band-label">${group}</div>
                        <div class="layer-band-items">
                            ${layers.map(l => `
                                <div class="layer-chip ${l.exists ? '' : 'missing'}">
                                    <span class="icon">${l.icon}</span>
                                    <div>
                                        <div class="name">${l.name}</div>
                                        <div class="desc">${l.desc}</div>
                                    </div>
                                    <span class="count">${l.exists ? l.count : '—'}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('<div class="layer-arrow">↓</div>');
            } catch (e) {
                document.getElementById('layer-stack').innerHTML = `<div class="empty-state error">❌ Architektur-Stand konnte nicht geladen werden</div>`;
            }
        }

        async function loadWikiDocs() {
            try {
                const resp = await fetch('/api/wiki-docs');
                const data = await resp.json();
                document.getElementById('wiki-docs').innerHTML = data.dirs.map(d => `
                    <div class="section-title" style="font-size:0.9rem;margin-top:1.25rem;">${d.name} <span class="muted">(${d.count})</span></div>
                    <div class="wiki-doc-grid">
                        ${d.files.length ? d.files.map(f => `
                            <a class="wiki-doc" href="${f.url}" target="_blank" rel="noopener">
                                <span class="icon">${f.icon}</span>
                                <span class="name" title="${f.name}">${f.name}</span>
                                <span class="size">${f.size}</span>
                            </a>
                        `).join('') : '<div class="empty-state" style="padding:1rem;">Keine Dokumente</div>'}
                    </div>
                `).join('');
            } catch (e) {
                document.getElementById('wiki-docs').innerHTML = `<div class="empty-state error">❌ Dokumente konnten nicht geladen werden</div>`;
            }
        }

        // === Chat ===
        let ragMode = false;

        function toggleRagMode() {
            ragMode = !ragMode;
            document.getElementById('rag-toggle').classList.toggle('active', ragMode);
            toast(ragMode
                ? 'Wissensmodus an — Antworten nutzen deine Wissensdatenbank (RAG-Dienst, Port 5002).'
                : 'Wissensmodus aus — direkter Modell-Chat.');
        }

        // Minimaler, sicherer Markdown-Renderer: erst escapen, dann formatieren
        function renderMarkdown(text) {
            let html = escapeHtml(text);
            html = html.replace(/```([\\s\\S]*?)```/g, (m, code) => `<pre><code>${code.trim()}</code></pre>`);
            html = html.replace(/`([^`\\n]+)`/g, '<code>$1</code>');
            html = html.replace(/\\*\\*([^*\\n]+)\\*\\*/g, '<strong>$1</strong>');
            const blocks = html.split(/\\n{2,}/).map(block => {
                if (block.startsWith('<pre>')) return block;
                const lines = block.split('\\n');
                if (lines.every(l => /^[-*] /.test(l.trim()) || l.trim() === '')) {
                    const items = lines.filter(l => l.trim()).map(l => `<li>${l.trim().slice(2)}</li>`).join('');
                    return `<ul>${items}</ul>`;
                }
                return `<p>${block.replace(/\\n/g, '<br>')}</p>`;
            });
            return blocks.join('');
        }

        function appendMessage(cls, roleLabel, bodyHtml, withCopy = false, rawText = '') {
            const messages = document.getElementById('chat-messages');
            const el = document.createElement('div');
            el.className = 'message ' + cls;
            el.innerHTML = `<div class="role">${roleLabel}${withCopy ? '<button class="msg-copy" title="Antwort kopieren">📋</button>' : ''}</div><div class="msg-body">${bodyHtml}</div>`;
            if (withCopy) {
                el.querySelector('.msg-copy').addEventListener('click', () => {
                    navigator.clipboard.writeText(rawText).then(
                        () => toast('Antwort kopiert.', 'success'),
                        () => toast('Kopieren fehlgeschlagen.', 'error'));
                });
            }
            messages.appendChild(el);
            messages.scrollTop = messages.scrollHeight;
            return el;
        }

        function persistChat() {
            try { localStorage.setItem('aios-chat-history', JSON.stringify(chatHistory)); } catch (e) {}
        }

        function restoreChat() {
            try {
                chatHistory = JSON.parse(localStorage.getItem('aios-chat-history') || '[]');
            } catch (e) { chatHistory = []; }
            for (const h of chatHistory) {
                if (h.role === 'user') appendMessage('user', '👤 Du', renderMarkdown(h.content));
                else if (h.role === 'assistant') appendMessage('assistant', '🤖 KI', renderMarkdown(h.content), true, h.content);
            }
        }

        function clearChat() {
            askConfirm('Chat leeren?', 'Der gesamte Chatverlauf wird gelöscht.', () => {
                chatHistory = [];
                localStorage.removeItem('aios-chat-history');
                document.getElementById('chat-messages').innerHTML =
                    `<div class="message assistant"><div class="role">🤖 System</div><div class="msg-body">Chat geleert. Teile deine nächste Business-Idee!</div></div>`;
            });
        }

        function exportChat() {
            if (!chatHistory.length) { toast('Noch kein Chatverlauf vorhanden.', 'error'); return; }
            const lines = chatHistory.map(h => (h.role === 'user' ? '## 👤 Du\\n\\n' : '## 🤖 KI\\n\\n') + h.content);
            const blob = new Blob(['# AI-OS Chat-Export\\n\\n' + lines.join('\\n\\n---\\n\\n')], { type: 'text/markdown' });
            const a = document.createElement('a');
            a.download = 'ai-os-chat.md';
            a.href = URL.createObjectURL(blob);
            a.click();
            URL.revokeObjectURL(a.href);
            toast('Chat als Markdown exportiert.', 'success');
        }

        async function sendMessage() {
            const input = document.getElementById('chat-input');
            const model = document.getElementById('model-select').value;
            const text = input.value.trim();

            if (!text) return;
            if (!model) {
                toast('Bitte wähle zuerst ein Modell aus.', 'error');
                return;
            }

            appendMessage('user', '👤 Du', renderMarkdown(text));
            input.value = '';

            const roleLabel = ragMode ? `🧠 ${model} + Wissen` : `🤖 ${model}`;
            const loadingEl = appendMessage('assistant', roleLabel,
                '<div class="thinking"><span></span><span></span><span></span></div>');

            try {
                const endpoint = ragMode ? '/api/rag-chat' : '/api/chat';
                const resp = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ model, message: text, history: chatHistory })
                });
                const data = await resp.json();
                loadingEl.remove();

                if (data.error) {
                    appendMessage('assistant', '❌ Fehler', renderMarkdown(data.error));
                } else {
                    let body = renderMarkdown(data.response);
                    if (data.sources && data.sources.length) {
                        body += `<div class="rag-sources">📎 Quellen: ${data.sources.map(escapeHtml).join(' · ')}</div>`;
                    }
                    appendMessage('assistant', roleLabel, body, true, data.response);
                    chatHistory.push({ role: 'user', content: text });
                    chatHistory.push({ role: 'assistant', content: data.response });
                    if (chatHistory.length > 40) chatHistory = chatHistory.slice(-40);
                    persistChat();
                }
            } catch (e) {
                loadingEl.remove();
                appendMessage('assistant', '❌ Fehler', `Verbindung fehlgeschlagen: ${escapeHtml(e.message)}`);
            }
        }

        // === Model Actions ===
        function useModel(name) {
            document.getElementById('model-select').value = name;
            showTab('chat');
            document.getElementById('chat-input').focus();
        }

        function openModelModal() { document.getElementById('model-modal').classList.add('active'); }
        function closeModelModal() { document.getElementById('model-modal').classList.remove('active'); }

        async function pullModel() {
            const name = document.getElementById('model-name-input').value.trim();
            if (!name) return;

            document.getElementById('model-modal').classList.remove('active');
            toast(`Lade "${name}" herunter (kann einige Minuten dauern)...`);

            try {
                const resp = await fetch('/api/pull', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ name })
                });
                const data = await resp.json();
                if (data.success) {
                    toast(`"${name}" erfolgreich installiert.`, 'success');
                    loadModels();
                } else {
                    toast('Fehler: ' + data.error, 'error');
                }
            } catch (e) {
                toast('Fehler: ' + e.message, 'error');
            }

            document.getElementById('model-name-input').value = '';
        }

        function confirmDeleteModel(name) {
            askConfirm('Modell löschen?', `"${name}" wird dauerhaft von der Festplatte entfernt.`, () => deleteModel(name));
        }

        async function deleteModel(name) {
            try {
                const resp = await fetch('/api/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ name })
                });
                const data = await resp.json();
                if (data.success) {
                    toast(`"${name}" gelöscht.`, 'success');
                    loadModels();
                } else {
                    toast('Fehler: ' + data.error, 'error');
                }
            } catch (e) {
                toast('Fehler beim Löschen: ' + e.message, 'error');
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function refreshAll() {
            loadModels();
            loadStats();
            loadServices();
            loadKnowledge();
            loadArchitecture();
            toast('Aktualisiert.');
        }

        // === Init ===
        restoreSidebarPreference();
        setupNotepad();
        setupSketch();
        setupSpeechRecognition();
        restoreChat();
        loadModels();
        loadStats();
        loadServices();
        loadKnowledge();
        loadFileTree();
        loadArchitecture();
        loadWikiDocs();
        setInterval(loadModels, 30000);
        setInterval(loadStats, 30000);
        setInterval(loadServices, 15000);
    </script>
</body>
</html>
"""

# ========== API ROUTES ==========

@app.route("/")
def index():
    return render_template_string(TEMPLATE, port=FLASK_PORT)

@app.route("/api/models")
def get_models():
    """Listet alle installierten Ollama-Modelle"""
    try:
        req = urllib.request.Request(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            models = []
            for m in data.get("models", []):
                size_gb = m["size"] / (1024**3)
                models.append({
                    "name": m["name"],
                    "size": f"{size_gb:.1f} GB" if size_gb > 1 else f"{m['size']/(1024**2):.0f} MB"
                })
            return jsonify({"models": models})
    except Exception as e:
        return jsonify({"error": str(e), "models": []})

@app.route("/api/stats")
def get_stats():
    """System-Statistiken"""
    try:
        knowledge_dir = AI_OS_ROOT / "00_Wissen"
        file_count = 0
        if knowledge_dir.exists():
            for f in knowledge_dir.rglob("*"):
                if f.is_file():
                    file_count += 1

        try:
            import psutil
            mem = psutil.virtual_memory()
            memory_str = f"{mem.available / (1024**3):.1f} GB"
            os_str = f"CPU: {psutil.cpu_percent()}% | RAM: {mem.percent}%"
        except ImportError:
            memory_str = "psutil nicht installiert"
            os_str = "System"

        return jsonify({
            "files": file_count,
            "memory": memory_str,
            "os": os_str
        })
    except Exception as e:
        return jsonify({"files": 0, "memory": "N/A", "os": str(e)})

@app.route("/api/services")
def get_services():
    """Prüft parallel den Online-Status aller AI-OS-Dienste (Ebenen-Struktur)."""
    def check(svc):
        online = True if svc["key"] == "dashboard" else check_service_health(svc["port"])
        return {**{k: v for k, v in svc.items() if k not in ("script", "env_key")}, "online": online}

    with ThreadPoolExecutor(max_workers=len(SERVICES)) as pool:
        results = list(pool.map(check, SERVICES))

    return jsonify({"services": results})

@app.route("/api/services/start", methods=["POST"])
def start_service_route():
    """Startet einen einzelnen AI-OS-Dienst als Hintergrundprozess."""
    key = (request.json or {}).get("key", "")
    svc = next((s for s in SERVICES if s["key"] == key), None)
    if not svc or not svc.get("script"):
        return jsonify({"error": "Unbekannter oder nicht startbarer Dienst"})

    script_path = AI_OS_ROOT / svc["script"]
    if not script_path.exists():
        return jsonify({"error": f"Skript nicht gefunden: {svc['script']}"})

    try:
        env = os.environ.copy()
        env["AI_OS_ROOT"] = str(AI_OS_ROOT)
        if svc.get("env_key"):
            env[svc["env_key"]] = str(svc["port"])
        subprocess.Popen(
            [sys.executable, str(script_path)],
            env=env,
            cwd=str(AI_OS_ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/knowledge")
def get_knowledge():
    """Datei-Anzahl pro Wissenskategorie in 06_Gedächtnis."""
    root = AI_OS_ROOT / "06_Gedächtnis"
    categories = []
    for cat in KNOWLEDGE_CATEGORIES:
        p = root / cat["path"]
        count = 0
        if p.exists():
            count = sum(1 for f in p.rglob("*") if f.is_file() and f.name != ".gitkeep")
        categories.append({**cat, "count": count})
    return jsonify({"categories": categories})

@app.route("/api/architecture")
def get_architecture():
    """Live-Stand der Ebenen-Struktur: Datei-Anzahl je Root-Ordner."""
    layers = []
    for layer in ARCHITECTURE_LAYERS:
        p = AI_OS_ROOT / layer["name"]
        exists = p.exists()
        count = sum(1 for f in p.rglob("*") if f.is_file()) if exists else 0
        layers.append({**layer, "count": count, "exists": exists})
    return jsonify({"layers": layers})

@app.route("/api/wiki-docs")
def get_wiki_docs():
    """Listet die Architektur-/Referenzdokumente aus Wiki und Dokumentation/Architektur."""
    result = []
    for d in WIKI_DIRS:
        p = AI_OS_ROOT / d["path"]
        files = []
        if p.exists():
            for f in sorted(p.iterdir()):
                if f.is_file() and not f.name.startswith("."):
                    size = f.stat().st_size
                    size_str = f"{size/1024:.0f} KB" if size < 1024*1024 else f"{size/1024/1024:.1f} MB"
                    files.append({
                        "name": f.name,
                        "icon": FILE_ICONS.get(f.suffix.lower(), "📄"),
                        "size": size_str,
                        "url": f"/api/wiki-file/{d['key']}/{f.name}",
                    })
        result.append({**d, "files": files, "count": len(files)})
    return jsonify({"dirs": result})

@app.route("/api/wiki-file/<dir_key>/<path:filename>")
def get_wiki_file(dir_key, filename):
    """Liefert eine Datei aus einem der beiden Wiki-/Architektur-Verzeichnisse (whitelisted, pfadsicher)."""
    from flask import send_from_directory
    d = next((x for x in WIKI_DIRS if x["key"] == dir_key), None)
    if not d:
        return jsonify({"error": "Unbekanntes Verzeichnis"}), 404
    try:
        return send_from_directory(str(AI_OS_ROOT / d["path"]), filename)
    except Exception:
        return jsonify({"error": "Datei nicht gefunden"}), 404

@app.route("/api/files")
def get_files():
    """Dateistruktur des Wissensspeichers"""
    def build_tree(path):
        items = []
        try:
            for entry in sorted(path.iterdir()):
                if entry.name.startswith(".") or entry.name.startswith("_"):
                    continue
                if entry.is_dir():
                    children = build_tree(entry)
                    items.append({
                        "name": entry.name,
                        "type": "dir",
                        "children": children
                    })
                elif entry.suffix in [".md", ".txt", ".py", ".json", ".yaml", ".yml", ".toml"]:
                    items.append({
                        "name": entry.name,
                        "type": "file"
                    })
        except PermissionError:
            pass
        return items

    try:
        tree = build_tree(AI_OS_ROOT / "00_Wissen")
        return jsonify({"tree": tree})
    except Exception as e:
        return jsonify({"error": str(e), "tree": []})

@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat mit lokalem KI-Modell"""
    data = request.json
    model = data.get("model", "llama3")
    message = data.get("message", "")
    history = data.get("history", [])

    if len(history) > 20:
        history = history[-20:]

    messages = [{"role": "system", "content": "Du bist ein hilfreicher Assistent. Du bist Teil des AI-OS (AI Operating System), einem lokalen KI-Betriebssystem. Antworte auf Deutsch."}]
    for h in history:
        messages.append(h)
    messages.append({"role": "user", "content": message})

    try:
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 2048
            }
        }).encode("utf-8")

        req = urllib.request.Request(
            f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            response = result.get("message", {}).get("content", "")

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})

        return jsonify({
            "response": response,
            "history": history
        })
    except Exception as e:
        return jsonify({"error": str(e), "response": "", "history": history})

@app.route("/api/rag-chat", methods=["POST"])
def rag_chat():
    """Wissensmodus: leitet die Frage an den Gedächtnis/RAG-Dienst (Port 5002, /query) weiter."""
    data = request.json or {}
    message = data.get("message", "")
    model = data.get("model", "llama3")
    if not message:
        return jsonify({"error": "Keine Nachricht angegeben"})

    try:
        payload = json.dumps({"query": message, "model": model}).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:5002/query",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())

        if result.get("error") and not result.get("answer"):
            return jsonify({"error": result["error"]})

        return jsonify({
            "response": result.get("answer", ""),
            "sources": result.get("sources", [])
        })
    except urllib.error.URLError:
        return jsonify({"error": "Gedächtnis/RAG-Dienst nicht erreichbar (Port 5002). Starte ihn im Dienste-Tab und indiziere ggf. die Wissensdatenbank."})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/pull", methods=["POST"])
def pull_model():
    """Lädt ein neues Modell herunter"""
    name = request.json.get("name", "")
    if not name:
        return jsonify({"error": "Kein Modellname angegeben"})

    try:
        payload = json.dumps({"name": name}).encode("utf-8")
        req = urllib.request.Request(
            f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/pull",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=600) as resp:
            for line in resp:
                pass
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/delete", methods=["POST"])
def delete_model():
    """Löscht ein Modell"""
    name = request.json.get("name", "")
    if not name:
        return jsonify({"error": "Kein Modellname angegeben"})

    try:
        payload = json.dumps({"name": name}).encode("utf-8")
        req = urllib.request.Request(
            f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/delete",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="DELETE"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            pass
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    print(f"🧠 AI-OS Dashboard startet auf http://localhost:{FLASK_PORT}")
    print(f"📁 Wissensbasis: {AI_OS_ROOT / '00_Wissen'}")
    print(f"🔧 Ollama: http://{OLLAMA_HOST}:{OLLAMA_PORT}")
    app.run(host="127.0.0.1", port=FLASK_PORT, debug=False, threaded=True)
