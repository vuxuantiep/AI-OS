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
from pathlib import Path
from datetime import datetime

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

# ========== HTML TEMPLATE ==========
TEMPLATE = """
<!DOCTYPE html>
<html lang="de" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 AI-OS Dashboard</title>
    <style>
        :root {
            --bg-primary: #0a0e17;
            --bg-secondary: #111827;
            --bg-card: #1e293b;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --accent: #3b82f6;
            --accent-hover: #2563eb;
            --success: #22c55e;
            --warning: #eab308;
            --danger: #ef4444;
            --border: #334155;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
        }

        .header {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }

        .header h1 {
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .header-right {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }

        .status-dot.online { background: var(--success); box-shadow: 0 0 8px var(--success); }
        .status-dot.offline { background: var(--danger); box-shadow: 0 0 8px var(--danger); }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        .stat-card h3 {
            color: var(--text-secondary);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--text-primary);
        }

        .stat-detail {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }

        .section-title {
            font-size: 1.25rem;
            margin: 2rem 0 1rem;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .models-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .model-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 1.25rem;
            transition: all 0.2s;
        }

        .model-card:hover {
            border-color: var(--accent);
            box-shadow: 0 0 15px rgba(59,130,246,0.1);
        }

        .model-card .name {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }

        .model-card .size {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-bottom: 1rem;
        }

        .model-actions {
            display: flex;
            gap: 0.5rem;
        }

        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
        }

        .btn-primary {
            background: var(--accent);
            color: white;
        }
        .btn-primary:hover { background: var(--accent-hover); }

        .btn-success {
            background: var(--success);
            color: white;
        }
        .btn-success:hover { opacity: 0.9; }

        .btn-outline {
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-primary);
        }
        .btn-outline:hover { border-color: var(--accent); color: var(--accent); }

        .btn-danger {
            background: var(--danger);
            color: white;
        }
        .btn-danger:hover { opacity: 0.9; }

        .chat-section {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            margin-bottom: 2rem;
            overflow: hidden;
        }

        .chat-header {
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-messages {
            padding: 1.5rem;
            max-height: 400px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .message {
            padding: 1rem;
            border-radius: 10px;
            max-width: 80%;
        }

        .message.user {
            background: var(--accent);
            color: white;
            align-self: flex-end;
        }

        .message.assistant {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            align-self: flex-start;
        }

        .message .role {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.25rem;
            opacity: 0.7;
        }

        .chat-input-area {
            display: flex;
            gap: 0.5rem;
            padding: 1rem 1.5rem;
            border-top: 1px solid var(--border);
        }

        .chat-input {
            flex: 1;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            color: var(--text-primary);
            font-size: 0.9rem;
            resize: none;
            font-family: inherit;
        }

        .chat-input:focus {
            outline: none;
            border-color: var(--accent);
        }

        .file-system {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }

        .file-tree {
            margin-top: 1rem;
            font-family: 'Courier New', monospace;
            font-size: 0.875rem;
        }

        .file-tree .dir {
            color: var(--accent);
            cursor: pointer;
            padding: 0.25rem 0;
        }

        .file-tree .file {
            color: var(--text-secondary);
            padding: 0.15rem 0 0.15rem 1.5rem;
        }

        .file-tree .indent {
            padding-left: 1.5rem;
        }

        .status-bar {
            background: var(--bg-secondary);
            border-top: 1px solid var(--border);
            padding: 0.75rem 2rem;
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--text-secondary);
            position: fixed;
            bottom: 0;
            width: 100%;
        }

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
            border-radius: 12px;
            padding: 2rem;
            max-width: 500px;
            width: 90%;
        }

        .modal-content h2 {
            margin-bottom: 1rem;
        }

        .modal-content input,
        .modal-content select {
            width: 100%;
            padding: 0.75rem;
            margin-bottom: 1rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 0.9rem;
        }

        .modal-actions {
            display: flex;
            gap: 0.5rem;
            justify-content: flex-end;
        }

        @media (max-width: 768px) {
            .container { padding: 1rem; }
            .stats-grid { grid-template-columns: 1fr; }
            .models-grid { grid-template-columns: 1fr; }
            .message { max-width: 90%; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 AI-OS Dashboard</h1>
        <div class="header-right">
            <span id="connection-status">
                <span class="status-dot" id="ollama-dot"></span>
                Ollama
            </span>
            <button class="btn btn-outline" onclick="window.location.reload()">🔄 Neu laden</button>
        </div>
    </div>

    <div class="container">
        <!-- Stats -->
        <div class="stats-grid" id="stats">
            <div class="stat-card">
                <h3>🧠 KI Modelle</h3>
                <div class="stat-value" id="model-count">-</div>
                <div class="stat-detail" id="models-detail">Lade...</div>
            </div>
            <div class="stat-card">
                <h3>📁 Dateien</h3>
                <div class="stat-value" id="file-count">-</div>
                <div class="stat-detail">Im Wissensspeicher</div>
            </div>
            <div class="stat-card">
                <h3>⚡ Status</h3>
                <div class="stat-value" id="system-status">-</div>
                <div class="stat-detail" id="uptime-detail">System bereit</div>
            </div>
            <div class="stat-card">
                <h3>💾 Speicher</h3>
                <div class="stat-value" id="memory-usage">-</div>
                <div class="stat-detail">Verfügbarer RAM</div>
            </div>
        </div>

        <!-- KI Chat -->
        <div class="section-title">💬 KI Chat</div>
        <div class="chat-section">
            <div class="chat-header">
                <span>Unterhaltung mit lokaler KI</span>
                <select id="model-select" style="background:var(--bg-secondary);color:var(--text-primary);border:1px solid var(--border);border-radius:6px;padding:0.4rem 0.75rem;font-size:0.85rem;">
                </select>
            </div>
            <div class="chat-messages" id="chat-messages">
                <div class="message assistant">
                    <div class="role">🤖 System</div>
                    Hallo! Ich bin deine lokale KI. Stelle mir eine Frage oder wähle ein Modell aus.
                </div>
            </div>
            <div class="chat-input-area">
                <textarea class="chat-input" id="chat-input" rows="1" placeholder="Nachricht eingeben..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();sendMessage();}"></textarea>
                <button class="btn btn-primary" onclick="sendMessage()">Senden</button>
            </div>
        </div>

        <!-- Modelle -->
        <div class="section-title">📦 Installierte Modelle</div>
        <div class="models-grid" id="models-grid">
            <div style="grid-column:1/-1;text-align:center;padding:2rem;color:var(--text-secondary);">Lade Modelle...</div>
        </div>

        <!-- Dateisystem -->
        <div class="section-title">📂 Wissensspeicher</div>
        <div class="file-system">
            <div class="file-tree" id="file-tree">Lade Dateistruktur...</div>
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

    <div class="status-bar">
        <span id="status-left">🧠 AI-OS v1.0 | Lokales KI-Betriebssystem</span>
        <span id="status-right">Läuft auf localhost:{{ port }}</span>
    </div>

    <script>
        // === State ===
        let chatHistory = [];

        // === Load Models ===
        async function loadModels() {
            try {
                const resp = await fetch('/api/models');
                const data = await resp.json();
                const grid = document.getElementById('models-grid');
                const select = document.getElementById('model-select');
                
                if (data.error) {
                    grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:2rem;color:var(--danger);">❌ ${data.error}</div>`;
                    return;
                }

                // Stats
                document.getElementById('model-count').textContent = data.models.length;
                document.getElementById('models-detail').textContent = 
                    data.models.map(m => m.name.split(':')[0]).join(', ');

                // Grid
                grid.innerHTML = data.models.map(m => `
                    <div class="model-card">
                        <div class="name">${m.name}</div>
                        <div class="size">${m.size}</div>
                        <div class="model-actions">
                            <button class="btn btn-primary" onclick="useModel('${m.name}')">▶ Nutzen</button>
                            <button class="btn btn-danger" onclick="deleteModel('${m.name}')">🗑 Löschen</button>
                        </div>
                    </div>
                `).join('') + `
                    <div class="model-card" style="border:2px dashed var(--border);display:flex;align-items:center;justify-content:center;cursor:pointer;" onclick="openModelModal()">
                        <div style="text-align:center;color:var(--text-secondary);">
                            <div style="font-size:2rem;margin-bottom:0.5rem;">+</div>
                            <div>Neues Modell laden</div>
                        </div>
                    </div>
                `;

                // Select
                select.innerHTML = data.models.map(m => `<option value="${m.name}">${m.name}</option>`).join('');

                // Connection status
                document.getElementById('ollama-dot').className = 'status-dot online';
                document.getElementById('system-status').textContent = '✅ Online';
            } catch(e) {
                document.getElementById('ollama-dot').className = 'status-dot offline';
                document.getElementById('system-status').textContent = '❌ Offline';
                document.getElementById('models-grid').innerHTML = 
                    `<div style="grid-column:1/-1;text-align:center;padding:2rem;color:var(--danger);">❌ Verbindung zu Ollama fehlgeschlagen</div>`;
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
            } catch(e) {}
        }

        // === Load File Tree ===
        async function loadFileTree() {
            try {
                const resp = await fetch('/api/files');
                const data = await resp.json();
                document.getElementById('file-tree').innerHTML = renderTree(data.tree);
            } catch(e) {
                document.getElementById('file-tree').textContent = '❌ Konnte Dateistruktur nicht laden';
            }
        }

        function renderTree(items, depth=0) {
            if (!items || items.length === 0) return '<span style="color:var(--text-secondary)">(leer)</span>';
            const indent = ' '.repeat(depth * 2);
            return items.map(item => {
                if (item.type === 'dir') {
                    return `<div class="dir" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display==='none'?'':'none'">
                        ${indent}📁 ${item.name}</div>
                        <div class="indent" style="display:none">${renderTree(item.children, depth+1)}</div>`;
                } else {
                    return `<div class="file">${indent}📄 ${item.name}</div>`;
                }
            }).join('');
        }

        // === Chat ===
        async function sendMessage() {
            const input = document.getElementById('chat-input');
            const messages = document.getElementById('chat-messages');
            const model = document.getElementById('model-select').value;
            const text = input.value.trim();
            
            if (!text) return;
            if (!model) {
                messages.innerHTML += `<div class="message assistant"><div class="role">⚠️</div>Bitte wähle zuerst ein Modell aus.</div>`;
                return;
            }

            // Add user message
            messages.innerHTML += `<div class="message user"><div class="role">👤 Du</div>${escapeHtml(text)}</div>`;
            input.value = '';
            messages.scrollTop = messages.scrollHeight;

            // Add loading
            const loadingId = 'loading-' + Date.now();
            messages.innerHTML += `<div class="message assistant" id="${loadingId}"><div class="role">🤖 ${model}</div><div class="thinking">💭 Denke...</div></div>`;

            try {
                const resp = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ model, message: text, history: chatHistory })
                });
                const data = await resp.json();
                
                document.getElementById(loadingId).remove();
                
                if (data.error) {
                    messages.innerHTML += `<div class="message assistant"><div class="role">❌ Fehler</div>${data.error}</div>`;
                } else {
                    messages.innerHTML += `<div class="message assistant"><div class="role">🤖 ${model}</div>${escapeHtml(data.response)}</div>`;
                    chatHistory = data.history;
                }
            } catch(e) {
                document.getElementById(loadingId).remove();
                messages.innerHTML += `<div class="message assistant"><div class="role">❌ Fehler</div>Verbindung fehlgeschlagen: ${e.message}</div>`;
            }
            
            messages.scrollTop = messages.scrollHeight;
        }

        // === Model Actions ===
        function useModel(name) {
            document.getElementById('model-select').value = name;
            document.getElementById('chat-input').focus();
        }

        function openModelModal() {
            document.getElementById('model-modal').classList.add('active');
        }

        function closeModelModal() {
            document.getElementById('model-modal').classList.remove('active');
        }

        async function pullModel() {
            const name = document.getElementById('model-name-input').value.trim();
            if (!name) return;
            
            document.getElementById('model-modal').classList.remove('active');
            
            const grid = document.getElementById('models-grid');
            grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:2rem;color:var(--accent);">
                ⏳ Lade "${name}" herunter (kann einige Minuten dauern)...</div>`;
            
            try {
                const resp = await fetch('/api/pull', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ name })
                });
                const data = await resp.json();
                if (data.success) {
                    loadModels();
                } else {
                    grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:2rem;color:var(--danger);">❌ ${data.error}</div>`;
                }
            } catch(e) {
                grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:2rem;color:var(--danger);">❌ Fehler: ${e.message}</div>`;
            }
            
            document.getElementById('model-name-input').value = '';
        }

        async function deleteModel(name) {
            if (!confirm(`Modell "${name}" wirklich löschen?`)) return;
            try {
                const resp = await fetch('/api/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ name })
                });
                const data = await resp.json();
                if (data.success) loadModels();
            } catch(e) {
                alert('Fehler beim Löschen: ' + e.message);
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // === Init ===
        loadModels();
        loadStats();
        loadFileTree();
        setInterval(loadModels, 30000);
        setInterval(loadStats, 30000);
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
        # Dateianzahl
        knowledge_dir = AI_OS_ROOT / "00_Wissen"
        file_count = 0
        if knowledge_dir.exists():
            for f in knowledge_dir.rglob("*"):
                if f.is_file():
                    file_count += 1

        # Speicher
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

    # Begrenze Kontext auf letzte 20 Nachrichten
    if len(history) > 20:
        history = history[-20:]

    # Erstelle Prompt mit Kontext
    messages = [{"role": "system", "content": "Du bist ein hilfreicher Assistent. Du bist Teil des AI-OS (AI Operating System), einem lokalen KI-Betriebssystem. Antworte auf Deutsch."}]
    for h in history:
        messages.append(h)
    messages.append({"role": "user", "content": message})

    try:
        # Direkter API-Aufruf an Ollama
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

        # Aktualisiere History
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})

        return jsonify({
            "response": response,
            "history": history
        })
    except Exception as e:
        return jsonify({"error": str(e), "response": "", "history": history})

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
            # Warte auf vollständigen Download
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
    app.run(host="127.0.0.1", port=FLASK_PORT, debug=False)