#!/usr/bin/env python3
"""
AI-OS Dashboard
Zentrale Weboberfläche für das lokale KI-Betriebssystem.
"""

import os
import re
import sys
import json
import time
import threading
import subprocess
import email.utils
import html as html_module
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from flask import Flask, render_template, jsonify, request
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


# ========== KI-/TECH-NEWS (täglicher CEO-Brief) ==========

NEWS_FEEDS = [
    {"source": "heise online", "url": "https://www.heise.de/rss/heise-atom.xml"},
    {"source": "Golem", "url": "https://rss.golem.de/rss.php?feed=RSS2.0"},
    {"source": "t3n", "url": "https://t3n.de/rss.xml"},
    {"source": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"},
    {"source": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
]

# Tages-News = kurzfristiger Kontext -> gehört architektonisch ins Short-Memory
NEWS_CACHE_PATH = AI_OS_ROOT / "06_Gedächtnis" / "Memory" / "Short-Memory" / "news_cache.json"
NEWS_MAX_ITEMS = 15
_news_lock = threading.Lock()


def _strip_html(text):
    """Entfernt Tags/Entities aus RSS-Beschreibungen für die Kurz-Info."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html_module.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_feed(source, raw):
    """Parst RSS 2.0 und Atom mit stdlib; liefert Liste von Items."""
    items = []
    root = ET.fromstring(raw)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    for item in root.iter("item"):  # RSS 2.0
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = _strip_html(item.findtext("description") or "")
        pub = item.findtext("pubDate") or ""
        try:
            ts = email.utils.parsedate_to_datetime(pub).timestamp() if pub else 0
        except Exception:
            ts = 0
        if title:
            items.append({"source": source, "title": title, "link": link,
                          "summary": desc[:280], "ts": ts})

    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):  # Atom
        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
        link_el = entry.find("atom:link[@rel='alternate']", ns)
        if link_el is None:
            link_el = entry.find("atom:link", ns)
        link = link_el.get("href") if link_el is not None else ""
        desc = _strip_html(entry.findtext("atom:summary", default="", namespaces=ns)
                           or entry.findtext("atom:content", default="", namespaces=ns))
        pub = entry.findtext("atom:updated", default="", namespaces=ns) \
              or entry.findtext("atom:published", default="", namespaces=ns)
        try:
            ts = datetime.fromisoformat(pub.replace("Z", "+00:00")).timestamp() if pub else 0
        except Exception:
            ts = 0
        if title:
            items.append({"source": source, "title": title, "link": link,
                          "summary": desc[:280], "ts": ts})

    return items


def fetch_news():
    """Holt alle Feeds (fehlertolerant pro Feed), sortiert nach Datum, kappt auf NEWS_MAX_ITEMS."""
    all_items, errors = [], []
    for feed in NEWS_FEEDS:
        try:
            req = urllib.request.Request(feed["url"], headers={"User-Agent": "AI-OS-Dashboard/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                all_items.extend(_parse_feed(feed["source"], resp.read()))
        except Exception as e:
            errors.append(f"{feed['source']}: {e}")

    all_items.sort(key=lambda x: x["ts"], reverse=True)
    return all_items[:NEWS_MAX_ITEMS], errors


def load_news_cache():
    try:
        return json.loads(NEWS_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None


def refresh_news_cache():
    """Holt die News und schreibt den Tages-Cache. Gibt den Cache-Inhalt zurück."""
    items, errors = fetch_news()
    cache = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "fetched_at": datetime.now().isoformat(timespec="minutes"),
        "items": items,
        "errors": errors,
        "brief": None,  # KI-Brief wird auf Abruf erzeugt und hier mitgecacht
    }
    with _news_lock:
        NEWS_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        NEWS_CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return cache


def get_news_cached(force=False):
    """Liefert den Tages-Cache; holt automatisch neu, wenn der Tag gewechselt hat (= tägliche Recherche)."""
    cache = load_news_cache()
    today = datetime.now().strftime("%Y-%m-%d")
    if force or not cache or cache.get("date") != today or not cache.get("items"):
        cache = refresh_news_cache()
    return cache


def _news_daily_worker():
    """Hintergrund-Thread: prüft stündlich, ob der Tages-Cache noch aktuell ist."""
    while True:
        try:
            get_news_cached()
        except Exception:
            pass
        time.sleep(3600)


# ========== LERNENDER AGENT (Komponente 1 der Drei-Komponenten-Architektur) ==========
# Echtes Lernen durch Gedächtnis-Konsolidierung: Interaktionen -> Episodic-Memory,
# Lern-Zyklus destilliert daraus per lokalem Modell ein Nutzerprofil -> Long-Memory,
# das Dialogsystem injiziert dieses Profil in seine Antworten.

EPISODIC_LOG_PATH = AI_OS_ROOT / "06_Gedächtnis" / "Memory" / "Episodic-Memory" / "chat_log.jsonl"
PROFILE_PATH = AI_OS_ROOT / "06_Gedächtnis" / "Memory" / "Long-Memory" / "nutzerprofil.md"
LEARN_META_PATH = AI_OS_ROOT / "06_Gedächtnis" / "Memory" / "Long-Memory" / "learn_meta.json"
LEARN_EVERY_N = 10          # Auto-Lernzyklus nach so vielen neuen Interaktionen
LEARN_WINDOW = 50           # so viele jüngste Interaktionen fließen in einen Zyklus ein
_learn_lock = threading.Lock()
_learning_active = threading.Event()


def log_interaction(question, answer, mode="chat"):
    """Protokolliert eine Dialog-Interaktion ins Episodic-Memory (JSONL, append-only)."""
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "mode": mode,
        "question": question[:500],
        "answer": (answer or "")[:500],
    }
    try:
        with _learn_lock:
            EPISODIC_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(EPISODIC_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        return
    # Auto-Lernen: nach LEARN_EVERY_N neuen Interaktionen im Hintergrund konsolidieren
    try:
        meta = load_learn_meta()
        if count_interactions() - meta.get("learned_count", 0) >= LEARN_EVERY_N:
            threading.Thread(target=run_learning_cycle, args=("llama3",), daemon=True).start()
    except Exception:
        pass


def count_interactions():
    try:
        with open(EPISODIC_LOG_PATH, encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())
    except Exception:
        return 0


def load_learn_meta():
    try:
        return json.loads(LEARN_META_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_profile():
    try:
        return PROFILE_PATH.read_text(encoding="utf-8")
    except Exception:
        return ""


def recent_interactions(n=LEARN_WINDOW):
    try:
        with open(EPISODIC_LOG_PATH, encoding="utf-8") as f:
            lines = [line for line in f if line.strip()]
        return [json.loads(line) for line in lines[-n:]]
    except Exception:
        return []


def run_learning_cycle(model="llama3"):
    """Konsolidiert jüngste Interaktionen + bisheriges Profil zu einem aktualisierten Nutzerprofil."""
    if _learning_active.is_set():
        return {"error": "Ein Lernzyklus läuft bereits."}
    _learning_active.set()
    try:
        episodes = recent_interactions()
        if not episodes:
            return {"error": "Noch keine Interaktionen im Episodic-Memory."}

        old_profile = load_profile() or "(noch leer)"
        episode_text = "\n".join(
            f"- [{e['ts']}] Frage: {e['question'][:180]}" for e in episodes
        )
        prompt = (
            "Du bist der Lern-Agent eines lokalen AI-OS. Aktualisiere das Nutzerprofil auf Basis "
            "der jüngsten Interaktionen. Das Profil hilft dem Dialogsystem, künftig passender zu "
            "antworten.\n\n"
            f"Bisheriges Profil:\n{old_profile[:1500]}\n\n"
            f"Jüngste Interaktionen (nur Fragen des Nutzers):\n{episode_text}\n\n"
            "Schreibe das aktualisierte Profil als kompaktes Markdown mit genau diesen Abschnitten:\n"
            "## Interessen & Themen\n## Aktuelle Projekte\n## Kommunikations-Vorlieben\n"
            "## Wiederkehrende Fragen\n"
            "Maximal 20 Zeilen gesamt. Nur belegbare Beobachtungen aus den Interaktionen, "
            "keine Erfindungen. Antworte nur mit dem Profil, auf Deutsch."
        )

        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 600},
        }).encode("utf-8")
        req = urllib.request.Request(
            f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat",
            data=payload, headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read())
        profile = result.get("message", {}).get("content", "").strip()
        if not profile:
            return {"error": "Modell lieferte kein Profil."}

        stamp = datetime.now().isoformat(timespec="minutes")
        with _learn_lock:
            PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            PROFILE_PATH.write_text(
                f"<!-- Automatisch gelernt am {stamp} aus {len(episodes)} Interaktionen -->\n{profile}\n",
                encoding="utf-8")
            LEARN_META_PATH.write_text(json.dumps({
                "learned_count": count_interactions(),
                "last_learned_at": stamp,
                "model": model,
            }), encoding="utf-8")
        return {"profile": profile, "episodes_used": len(episodes), "learned_at": stamp}
    except Exception as e:
        return {"error": str(e)}
    finally:
        _learning_active.clear()


def personalization_prompt():
    """Liefert den Profil-Zusatz für den System-Prompt des Dialogsystems (leer, wenn nichts gelernt)."""
    profile = load_profile()
    if not profile:
        return ""
    return (
        "\n\nWas du bisher über diesen Nutzer gelernt hast (nutze es, um passender zu antworten, "
        f"aber erwähne das Profil nicht ungefragt):\n{profile[:1200]}"
    )


# ========== API ROUTES ==========

@app.route("/")
def index():
    # HTML liegt ausgelagert in templates/dashboard.html — keine Python-Escape-Fallen mehr
    return render_template("dashboard.html", port=FLASK_PORT)

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

    system = ("Du bist ein hilfreicher Assistent. Du bist Teil des AI-OS (AI Operating System), "
              "einem lokalen KI-Betriebssystem. Antworte auf Deutsch.")
    if data.get("personalize", True):
        system += personalization_prompt()

    messages = [{"role": "system", "content": system}]
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

        log_interaction(message, response, mode="chat")

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

        log_interaction(message, result.get("answer", ""), mode="rag")

        return jsonify({
            "response": result.get("answer", ""),
            "sources": result.get("sources", [])
        })
    except urllib.error.URLError:
        return jsonify({"error": "Gedächtnis/RAG-Dienst nicht erreichbar (Port 5002). Starte ihn im Dienste-Tab und indiziere ggf. die Wissensdatenbank."})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/learning")
def get_learning():
    """Status des Lern-Agenten: Profil, Interaktions-Zähler, letzter Lernzyklus."""
    meta = load_learn_meta()
    total = count_interactions()
    return jsonify({
        "profile": load_profile(),
        "interactions_total": total,
        "new_since_learn": max(0, total - meta.get("learned_count", 0)),
        "last_learned_at": meta.get("last_learned_at"),
        "learning_active": _learning_active.is_set(),
        "auto_every": LEARN_EVERY_N,
    })

@app.route("/api/learning/run", methods=["POST"])
def learning_run():
    """Startet einen Lernzyklus manuell (blockierend, liefert das neue Profil)."""
    model = (request.json or {}).get("model", "llama3")
    return jsonify(run_learning_cycle(model))

@app.route("/api/learning/reset", methods=["POST"])
def learning_reset():
    """Löscht Gelerntes: Nutzerprofil, Episodic-Log und Lern-Metadaten."""
    with _learn_lock:
        for p in (PROFILE_PATH, EPISODIC_LOG_PATH, LEARN_META_PATH):
            try:
                p.unlink()
            except FileNotFoundError:
                pass
            except Exception as e:
                return jsonify({"error": str(e)})
    return jsonify({"success": True})

@app.route("/api/news")
def get_news():
    """Tages-News zu KI & Technologie (Cache erneuert sich automatisch täglich)."""
    force = request.args.get("refresh") == "1"
    try:
        cache = get_news_cached(force=force)
        return jsonify(cache)
    except Exception as e:
        return jsonify({"error": str(e), "items": []})

@app.route("/api/news/brief", methods=["POST"])
def news_brief():
    """Erzeugt per lokalem Modell einen kurzen CEO-Brief aus den Tages-Schlagzeilen und cached ihn."""
    model = (request.json or {}).get("model", "llama3")
    cache = get_news_cached()
    if not cache.get("items"):
        return jsonify({"error": "Keine News im Cache — bitte zuerst aktualisieren."})

    if cache.get("brief") and not (request.json or {}).get("force"):
        return jsonify({"brief": cache["brief"], "cached": True})

    headlines = "\n".join(
        f"- [{i['source']}] {i['title']}: {i['summary'][:150]}" for i in cache["items"]
    )
    prompt = (
        "Du bist der Research-Agent eines AI-OS und schreibst den täglichen Tech-Brief für den CEO.\n"
        "Fasse aus diesen heutigen Schlagzeilen die 3-5 wichtigsten Entwicklungen zu KI und neuer "
        "Technologie zusammen. Pro Punkt: ein fetter Kurztitel und 1-2 Sätze, was es ist und warum es "
        "für ein kleines KI-Unternehmen relevant sein könnte. Antworte auf Deutsch, nur die Punkte.\n\n"
        f"Schlagzeilen:\n{headlines}"
    )

    try:
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.4, "num_predict": 800},
        }).encode("utf-8")
        req = urllib.request.Request(
            f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat",
            data=payload, headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read())
        brief = result.get("message", {}).get("content", "")

        cache["brief"] = brief
        with _news_lock:
            NEWS_CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
        return jsonify({"brief": brief, "cached": False})
    except Exception as e:
        return jsonify({"error": f"Brief konnte nicht erzeugt werden: {e}"})

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
    threading.Thread(target=_news_daily_worker, daemon=True).start()
    app.run(host="127.0.0.1", port=FLASK_PORT, debug=False, threaded=True)
