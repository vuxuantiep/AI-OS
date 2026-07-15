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

# Headless-Start (pythonw.exe, z.B. Windows-Aufgabenplanung): stdout/stderr sind
# dann None -> in Logdatei umleiten, sonst stürzt jeder print() ab.
if sys.stdout is None or sys.stderr is None:
    _log_path = Path(__file__).parent.parent.parent / "08_Monitoring" / "dashboard_headless.log"
    _log_path.parent.mkdir(parents=True, exist_ok=True)
    _log_file = open(_log_path, "a", buffering=1, encoding="utf-8", errors="replace")
    sys.stdout = sys.stdout or _log_file
    sys.stderr = sys.stderr or _log_file
elif sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from flask import Flask, render_template, jsonify, request
except ImportError:
    print("Flask nicht installiert. Installiere mit: pip install flask")
    sys.exit(1)

AI_OS_ROOT = Path(os.environ.get("AI_OS_ROOT", Path(__file__).parent.parent.parent))
FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))

# LLM-Router: lokale Engine (Ollama/LM Studio) mit Fallback auf Pi-Gateway (Tailscale),
# GitHub Models, OpenRouter, HuggingFace und Cloudflare Workers AI.
# OLLAMA_URL kommt aus der .env (Default lokal, alternativ Tailscale-Gerät).
sys.path.insert(0, str(Path(__file__).parent))
from llm_router import LLM_ROUTER, OLLAMA_URL

app = Flask(__name__)

# Windows-Registry liefert für .js/.mjs oft "text/plain" — dann verweigern
# Browser ES-Module und Worker die Ausführung. Deshalb explizit registrieren.
import mimetypes
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/javascript", ".mjs")
mimetypes.add_type("application/wasm", ".wasm")
mimetypes.add_type("application/manifest+json", ".webmanifest")

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
    {"key": "litellm", "name": "LiteLLM Gateway", "icon": "🚦", "port": 4000,
     "desc": "OpenAI-kompatibler Proxy über alle LLM-Provider (Ollama, Pi, Cloud)",
     "layer": "04_Infrastruktur", "script": "04_Infrastruktur/Gateway/litellm_gateway.py",
     "env_key": "LITELLM_PORT", "health_path": "/health/liveliness"},
    {"key": "workflow", "name": "Workflow Engine", "icon": "🔄", "port": 5200,
     "desc": "DAG-basierte Aufgaben-Pipelines", "layer": "05_Agenten",
     "script": "05_Agenten/workflow_engine.py", "env_key": "WORKFLOW_PORT"},
    {"key": "agents", "name": "Agent System", "icon": "🤖", "port": 5300,
     "desc": "10 spezialisierte KI-Agenten", "layer": "05_Agenten",
     "script": "05_Agenten/agent_system.py", "env_key": "AGENT_PORT"},
    {"key": "langgraph", "name": "LangGraph Engine", "icon": "🕸️", "port": 5500,
     "desc": "Fabrik-Pipeline als Zustandsgraph (Plan → Dev → QA-Schleife)",
     "layer": "05_Agenten", "script": "05_Agenten/langgraph_engine.py",
     "env_key": "LANGGRAPH_PORT"},
    {"key": "monitoring", "name": "Monitoring", "icon": "📊", "port": 5400,
     "desc": "Health-Checks, Metriken, Logs", "layer": "08_Monitoring",
     "script": "08_Monitoring/monitoring_service.py", "env_key": "MONITOR_PORT"},
    {"key": "cal_agent", "name": "Scheduling Agent", "icon": "📅", "port": 5301,
     "desc": "Terminmanagement via Cal.com + Ollama-Intents", "layer": "05_Agenten",
     "script": "05_Agenten/agents/cal_agent.py", "env_key": "CAL_AGENT_PORT"},
    {"key": "bubble_agent", "name": "Bubble No-Code Agent", "icon": "🫧", "port": 5302,
     "desc": "Bubble.io-Daten, Workflows & UI-Specs", "layer": "05_Agenten",
     "script": "05_Agenten/agents/bubble_agent.py", "env_key": "BUBBLE_AGENT_PORT"},
    {"key": "higgsfield_agent", "name": "Video Agent", "icon": "🎬", "port": 5303,
     "desc": "KI-Videoproduktion & Content-Pipeline (Higgsfield)", "layer": "05_Agenten",
     "script": "05_Agenten/agents/higgsfield_agent.py", "env_key": "HIGGSFIELD_AGENT_PORT"},
    {"key": "openhands", "name": "OpenHands Dev-Agent", "icon": "🙌", "port": 3000,
     "desc": "Autonomer Coding-Agent (Docker) — nutzt LiteLLM als LLM-Backend",
     "layer": "05_Agenten", "script": "05_Agenten/openhands_launcher.py",
     "env_key": "OPENHANDS_PORT", "health_path": "/"},
    {"key": "kiavatar_board", "name": "KI-Avatar Board", "icon": "🎬", "port": 5310,
     "desc": "Pipeline-Board für KI-Avatar-Videos (YouTube-Automation & TikTok-Shop)",
     "layer": "10_Business", "script": "10_Business/KI-Avatar/board/app.py",
     "env_key": "KIAVATAR_BOARD_PORT", "health_path": "/api/health"},
    {"key": "research_agent", "name": "Research-Agent (Checker)", "icon": "🔎", "port": 5320,
     "desc": "Market-Research für AI Business Checker: Reddit/RSS-Scan nach KI-Abzock-Angeboten",
     "layer": "10_Business", "script": "10_Business/KI-Avatar/research-agent/app.py",
     "env_key": "RESEARCH_AGENT_PORT", "health_path": "/api/health"},
]

AGENTS_REGISTRY_PATH = AI_OS_ROOT / "05_Agenten" / "agents" / "agents.json"
AGENT_ACTION_PORTS = (5300, 5301, 5302, 5303)

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

# Browser-Produkte (statische Web-Apps) aus 10_Business — whitelisted wie WIKI_DIRS.
PRODUKT_DIRS = {
    "dokucheck": "10_Business/Lokal-SML-Webassembly-MultiMemory/Produkt/dokucheck-lokal",
}

FILE_ICONS = {
    ".pdf": "📕", ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️",
    ".docx": "📘", ".md": "📝", ".one": "📓", ".excalidraw": "✏️",
}


# Timeout großzügig: die Spezial-Agenten prüfen in /health selbst Ollama mit,
# das kann unter Last >1s dauern — sonst erscheinen laufende Dienste als offline.
def check_service_health(port, timeout=4, path="/health"):
    """Prüft per HTTP, ob ein Dienst auf dem gegebenen Port antwortet."""
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}")
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

        result = LLM_ROUTER.chat(
            [{"role": "user", "content": prompt}],
            model=model, temperature=0.3, num_predict=600, timeout=180)
        profile = result["content"].strip()
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


# ========== KI-FABRIK: CEO -> CTO Auftrags-Pipeline ==========
# Der CEO beauftragt aus der Ideenwerkstatt den CTO-Agenten. Der CTO bestätigt den
# Eingang kurz und führt den Auftrag dann Schritt für Schritt durch die Fabrik
# (Analyse -> Entwicklung -> Qualität -> Abschluss). Jeder Schritt läuft über das
# Agent-System (:5300), fällt bei Nichtverfügbarkeit auf Ollama direkt zurück.
# Aufträge = kurzfristiger Arbeitskontext -> Short-Memory; Ergebnis-Dokumente -> 10_Business.

FACTORY_ORDERS_PATH = AI_OS_ROOT / "06_Gedächtnis" / "Memory" / "Short-Memory" / "factory_orders.json"
FACTORY_RESULTS_DIR = AI_OS_ROOT / "10_Business" / "KI-Fabrik-Auftraege"
FACTORY_MODEL = "llama3"
_factory_lock = threading.Lock()

# Scrum-Modell: CEO = Product Owner, CTO = Scrum Master, Agenten = Dev-Team.
# Jede Auftrags-Version ist ein Sprint; die Retrospektive fließt in den nächsten Sprint ein.
FACTORY_STEPS = [
    {"key": "annahme",     "station": "cto",      "label": "Sprint-Planung: CTO (Scrum Master) nimmt den Auftrag an"},
    {"key": "analyse",     "station": "planner",  "label": "Backlog & Umsetzungsplan (Sprint-Planung)"},
    {"key": "entwicklung", "station": "dev",      "label": "Sprint: Technisches Konzept (Dev-Team)"},
    {"key": "prototyp",    "station": "lab",      "label": "Sprint-Inkrement: Klickbarer Prototyp als Testumgebung"},
    {"key": "qualitaet",   "station": "test",     "label": "QA-Review: bestanden / nicht bestanden (max. 1 Nachbesserungs-Schleife)"},
    {"key": "abnahme",     "station": "approval", "label": "Sprint Review: CEO-Abnahme als Product Owner (Human in the Loop)"},
    {"key": "abschluss",   "station": "deploy",   "label": "Release: Produktion des finalen Produkts & Auslieferung"},
    {"key": "retro",       "station": "cto",      "label": "Retrospektive: Team-Erkenntnisse für den nächsten Sprint"},
]
FACTORY_PROTO_DIR = FACTORY_RESULTS_DIR / "Prototypen"
FACTORY_PRODUCT_DIR = FACTORY_RESULTS_DIR / "Produkte"


def _load_factory_orders():
    try:
        return json.loads(FACTORY_ORDERS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_factory_orders(orders):
    FACTORY_ORDERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    FACTORY_ORDERS_PATH.write_text(json.dumps(orders, ensure_ascii=False, indent=1), encoding="utf-8")


def _factory_update_order(order_id, updater):
    """Lädt, mutiert (per Callback) und speichert einen Auftrag atomar. Gibt den Auftrag zurück."""
    with _factory_lock:
        orders = _load_factory_orders()
        order = next((o for o in orders if o["id"] == order_id), None)
        if order is None:
            return None
        updater(order)
        order["updated_at"] = datetime.now().isoformat(timespec="seconds")
        _save_factory_orders(orders)
        return order


def _factory_set_step(order_id, step_key, status, output=None, engine=None):
    def upd(order):
        order["current_step"] = step_key
        for s in order["steps"]:
            if s["key"] == step_key:
                s["status"] = status
                if output is not None:
                    s["output"] = output[:8000]
                if engine is not None:
                    s["engine"] = engine
                now = datetime.now().isoformat(timespec="seconds")
                if status == "active" and not s.get("started_at"):
                    s["started_at"] = now
                if status in ("done", "error"):
                    s["finished_at"] = now
    return _factory_update_order(order_id, upd)


def _llm_generate(system, prompt, num_predict=800, temperature=0.5, timeout=300):
    """LLM-Aufruf über den Router (Ollama -> OpenRouter -> Cloudflare).
    Gibt (text, provider_label) zurück; wirft Exception, wenn kein Provider erreichbar."""
    return LLM_ROUTER.generate(
        system, prompt, model=FACTORY_MODEL,
        temperature=temperature, num_predict=num_predict, timeout=timeout)


def _agent_system_execute(agent, task, timeout=300):
    """Führt eine Aufgabe über das Agent-System (:5300) aus; None wenn nicht verfügbar/fehlgeschlagen."""
    try:
        payload = json.dumps({"agent": agent, "task": task}).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:5300/execute",
            data=payload, headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read())
        if result.get("success") and result.get("response"):
            return result["response"].strip()
    except Exception:
        pass
    return None


def _factory_run_step(order_id, step_key, agent, fallback_system, task, num_predict=800):
    """Ein Fabrik-Schritt: bevorzugt Agent-System, sonst Ollama direkt. Gibt (text, engine) zurück."""
    _factory_set_step(order_id, step_key, "active")
    text = _agent_system_execute(agent, task)
    engine = f"Agent-System :5300 ({agent})"
    if not text:
        text, provider_label = _llm_generate(fallback_system, task, num_predict=num_predict)
        engine = provider_label
    _factory_set_step(order_id, step_key, "done", output=text, engine=engine)
    return text, engine


def _extract_html(text):
    """Extrahiert das HTML-Dokument aus einer LLM-Antwort (Markdown-Fences, Vor-/Nachtext)."""
    m = re.search(r"```(?:html)?\s*(<!DOCTYPE.*?|<html.*?)```", text, re.S | re.I)
    if m:
        text = m.group(1)
    start = text.find("<!DOCTYPE")
    if start == -1:
        start = text.lower().find("<html")
    if start == -1:
        return None
    end = text.lower().rfind("</html>")
    return text[start:end + 7] if end != -1 else text[start:]


def _factory_build_prototype(order_id, briefing, concept):
    """Testlabor: erzeugt einen klickbaren Ein-Datei-HTML-Prototyp als Testumgebung für den CEO."""
    _factory_set_step(order_id, "prototyp", "active")
    task = (
        "Baue einen klickbaren HTML-Prototyp (Mockup) für dieses Produkt, damit der CEO es "
        "vor der Freigabe testen kann.\n\n"
        "STRIKTE REGELN:\n"
        "- GENAU EINE HTML-Datei: CSS und JavaScript inline, KEINE externen Ressourcen/CDNs.\n"
        "- Funktionierende Demo mit realistischen Beispieldaten und 2-3 klickbaren Kernfunktionen "
        "(Buttons, Formulare, Tabs), Zustand nur im Speicher.\n"
        "- Modernes, sauberes Design, deutsche Oberfläche, oben ein Hinweisbanner "
        "'🧪 Prototyp — KI-Fabrik Testumgebung'.\n"
        "- Antworte NUR mit dem vollständigen HTML-Code (beginnend mit <!DOCTYPE html>), "
        "kein erklärender Text.\n\n"
        f"BRIEFING:\n{briefing}\n\nTECHNISCHES KONZEPT:\n{concept[:2500]}"
    )
    text = _agent_system_execute("code", task, timeout=420)
    engine = "Agent-System :5300 (code)"
    if not text:
        text, engine = _llm_generate(
            "Du bist der CODE/DEV AGENT der KI-Fabrik und ein exzellenter Frontend-Entwickler. "
            "Du lieferst ausschließlich lauffähigen Code ohne Erklärtext.",
            task, num_predict=3000, timeout=600)
    html = _extract_html(text)
    if not html:
        html = ("<!DOCTYPE html><html lang=\"de\"><head><meta charset=\"utf-8\">"
                "<title>Prototyp</title></head><body style=\"font-family:sans-serif;padding:2rem;\">"
                "<h2>🧪 Prototyp — KI-Fabrik Testumgebung</h2>"
                "<p>Das Modell lieferte kein gültiges HTML. Rohausgabe:</p>"
                f"<pre style=\"white-space:pre-wrap;\">{html_module.escape(text[:6000])}</pre></body></html>")
    # Versions-Kennzeichnung: Badge mit Sprint-Version fest in den Prototyp einbetten
    with _factory_lock:
        _orders = _load_factory_orders()
    version = next((o.get("version", 1) for o in _orders if o["id"] == order_id), 1)
    badge = (f'<div style="position:fixed;top:8px;right:8px;z-index:99999;background:rgba(17,17,17,0.85);'
             f'color:#fff;padding:4px 12px;border-radius:14px;font:600 12px sans-serif;">'
             f'🏭 Prototyp v{version} · {order_id}</div>')
    html, n = re.subn(r"<body[^>]*>", lambda m: m.group(0) + badge, html, count=1, flags=re.I)
    if not n:
        html = badge + html
    FACTORY_PROTO_DIR.mkdir(parents=True, exist_ok=True)
    (FACTORY_PROTO_DIR / f"{order_id}.html").write_text(html, encoding="utf-8")
    _factory_update_order(order_id, lambda o: o.update(prototype_file=f"/factory/prototype/{order_id}"))
    summary = (f"Sprint-Inkrement bereit: klickbarer Prototyp v{version} ({len(html)} Zeichen) unter "
               f"/factory/prototype/{order_id} — der Product Owner (CEO) kann das Produkt vor der Freigabe testen.")
    _factory_set_step(order_id, "prototyp", "done", output=summary, engine=engine)


def _factory_build_product(order):
    """Produktion: baut aus Konzept, Prototyp und CEO-Feedback das FINALE, benutzbare Produkt.

    Kein Mockup — eine vollständige Ein-Datei-Web-App mit dauerhafter Datenspeicherung,
    abgelegt unter 10_Business/KI-Fabrik-Auftraege/Produkte/. Gibt (Pfad, Engine) zurück.
    """
    order_id = order["id"]
    version = order.get("version", 1)
    idea_name = order.get("idea", {}).get("name", "Produkt")
    briefing = _idea_briefing(order)
    concept = _factory_step_output(order, "entwicklung")
    qa = _factory_step_output(order, "qualitaet")
    approval = order.get("ceo_approval") or {}
    proto_path = FACTORY_PROTO_DIR / f"{order_id}.html"
    proto_html = proto_path.read_text(encoding="utf-8") if proto_path.exists() else ""

    task = (
        "Baue jetzt das FINALE, AUSLIEFERBARE PRODUKT: eine vollständige, sofort produktiv "
        "nutzbare Web-App in GENAU EINER HTML-Datei. Das ist KEIN Mockup, KEIN MVP und KEINE "
        "Demo — der Nutzer arbeitet ab heute täglich damit und erwartet echten Mehrwert.\n\n"
        "STRIKTE REGELN:\n"
        "- GENAU EINE HTML-Datei: CSS und JavaScript inline, KEINE externen Ressourcen/CDNs.\n"
        "- ALLE Kernfunktionen aus dem Konzept funktionieren wirklich (anlegen, bearbeiten, "
        "löschen, suchen/filtern/sortieren — was das Produkt braucht).\n"
        "- Daten werden mit localStorage DAUERHAFT gespeichert und beim Laden wiederhergestellt; "
        "zusätzlich Export/Import als JSON-Datei, damit dem Nutzer nichts verloren geht.\n"
        "- Start mit leerem Zustand + kurzem Onboarding-Hinweis. KEINE Fake-/Beispieldaten.\n"
        "- Professionelles, modernes, responsives Design (Desktop & Handy), deutsche Oberfläche.\n"
        "- KEIN 'Prototyp'-Banner, keine Platzhalter, kein Lorem Ipsum, keine toten Buttons.\n"
        "- Antworte NUR mit dem vollständigen HTML-Code (beginnend mit <!DOCTYPE html>), "
        "kein erklärender Text.\n\n"
        f"BRIEFING:\n{briefing}\n\n"
        f"TECHNISCHES KONZEPT:\n{concept[:2500]}\n\n"
        f"QA-HINWEISE (beheben!):\n{qa[:1200]}\n\n"
        + (f"CEO-FEEDBACK AUS DER ABNAHME (zwingend umsetzen!):\n{approval.get('comment')}\n\n"
           if approval.get("comment") else "")
        + (f"FREIGEGEBENER PROTOTYP ALS AUSGANGSBASIS (vervollständigen, nicht verschlechtern):\n{proto_html[:5000]}"
           if proto_html else "")
    )
    text = _agent_system_execute("code", task, timeout=600)
    engine = "Agent-System :5300 (code)"
    if not text:
        text, engine = _llm_generate(
            "Du bist der CODE/DEV AGENT der KI-Fabrik und ein exzellenter Frontend-Entwickler. "
            "Du lieferst ausschließlich vollständigen, produktionsreifen Code ohne Erklärtext.",
            task, num_predict=6000, timeout=900)
    html = _extract_html(text)
    if not html and proto_html:
        # Notfall-Fallback: der freigegebene Prototyp ist besser als gar keine Auslieferung
        html, engine = proto_html, engine + " · Fallback: freigegebener Prototyp"
    if not html:
        return None, engine
    badge = (f'<div style="position:fixed;bottom:8px;right:8px;z-index:99999;background:rgba(17,17,17,0.7);'
             f'color:#fff;padding:3px 10px;border-radius:12px;font:600 11px sans-serif;opacity:0.85;">'
             f'🏭 KI-Fabrik Release v{version}</div>')
    html, n = re.subn(r"<body[^>]*>", lambda m: m.group(0) + badge, html, count=1, flags=re.I)
    if not n:
        html = badge + html
    safe_name = re.sub(r"[^\w\-]+", "_", idea_name)[:40] or "Produkt"
    FACTORY_PRODUCT_DIR.mkdir(parents=True, exist_ok=True)
    product_path = FACTORY_PRODUCT_DIR / f"{order_id}_{safe_name}_v{version}.html"
    product_path.write_text(html, encoding="utf-8")
    _factory_update_order(order_id, lambda o: o.update(product_file=f"/factory/product/{order_id}"))
    return product_path, engine


def _idea_key(name):
    """Normalisierter Schlüssel, um Versionen derselben Idee zu erkennen."""
    return re.sub(r"\W+", "", str(name)).lower()


def _idea_briefing(order):
    idea = order.get("idea", {})
    parts = [
        f"Produktidee: {idea.get('name', '')} (Sprint/Version v{order.get('version', 1)})",
        f"Zielgruppe: {idea.get('target', '')}",
        f"Problem: {idea.get('problem', '')}",
        f"Lösungsansatz: {idea.get('solution', '')}",
    ]
    if order.get("note"):
        parts.append(f"Zusätzliche Anweisung des CEO (Product Owner): {order['note']}")
    return "\n".join(parts)


def _process_factory_order(order_id):
    """Hintergrund-Worker: führt einen Auftrag durch alle Fabrik-Stationen."""
    order = _factory_update_order(order_id, lambda o: o.update(status="processing"))
    if not order:
        return
    briefing = _idea_briefing(order)
    idea_name = order.get("idea", {}).get("name", "Unbenannt")

    try:
        # 1) CTO-Agent bestätigt den Auftragseingang (kurz, damit der CEO sofort Rückmeldung hat)
        _factory_set_step(order_id, "annahme", "active")
        cto_engine = f"CTO-Agent ({FACTORY_MODEL})"
        try:
            confirmation, provider_label = _llm_generate(
                "Du bist der CTO-AGENT der KI-Fabrik. Der CEO hat dir soeben einen Auftrag erteilt. "
                "Bestätige kurz und professionell auf Deutsch (2-3 Sätze): dass du den Auftrag erhalten "
                "hast, wie du ihn verstanden hast, und dass du ihn jetzt durch die Fabrik-Pipeline "
                "(Planung, Entwicklung, Qualität) führst. Keine Überschriften, nur die Bestätigung.",
                briefing, num_predict=220, temperature=0.6, timeout=120)
            cto_engine = f"CTO-Agent · {provider_label}"
        except Exception:
            confirmation = (f"Auftrag „{idea_name}“ erhalten. Ich habe das Briefing verstanden und "
                            "starte jetzt die Bearbeitung in der KI-Fabrik: Planung, Entwicklung und "
                            "Qualitätsprüfung laufen der Reihe nach an. Du wirst hier live informiert.")
        _factory_update_order(order_id, lambda o: o.update(cto_confirmation=confirmation))
        _factory_set_step(order_id, "annahme", "done", output=confirmation, engine=cto_engine)

        # 2) Analyse & Umsetzungsplan
        plan, _ = _factory_run_step(
            order_id, "analyse", "planner",
            "Du bist der PLANNER AGENT der KI-Fabrik. Erstelle strukturierte, realistische Umsetzungspläne. Antworte auf Deutsch in Markdown.",
            "Der CTO hat folgenden CEO-Auftrag angenommen. Erstelle einen kompakten Umsetzungsplan "
            "(Ziel, 3-5 Arbeitspakete, Risiken, grobe Zeitschätzung):\n\n" + briefing,
            num_predict=800)

        # 3) Technisches Konzept
        concept, _ = _factory_run_step(
            order_id, "entwicklung", "code",
            "Du bist der CODE/DEV AGENT der KI-Fabrik. Erstelle technische Konzepte und Architektur-Vorschläge. Antworte auf Deutsch in Markdown.",
            "Erstelle auf Basis von Briefing und Plan ein kompaktes technisches Konzept "
            "(Architektur, Komponenten, Tech-Stack, MVP-Umfang):\n\nBRIEFING:\n" + briefing +
            "\n\nUMSETZUNGSPLAN:\n" + plan[:2500],
            num_predict=900)

        # 3b) Testlabor: klickbarer Prototyp als Testumgebung für die CEO-Abnahme
        _factory_build_prototype(order_id, briefing, concept)

        # 4) QA-Review mit Kreislauf: fällt die Prüfung durch, geht es EINMAL zurück
        #    in die Entwicklung (Nachbesserungs-Schleife), dann erneut durch Labor & QA.
        qa_system = ("Du bist der ANALYSIS/QA AGENT der KI-Fabrik (Scrum-Team). Prüfe Konzepte kritisch "
                     "auf Lücken und Risiken. Beginne deine Antwort zwingend mit genau einer Zeile "
                     "'URTEIL: BESTANDEN' oder 'URTEIL: NICHT BESTANDEN'. Antworte auf Deutsch, kurz und strukturiert.")
        qa_task = ("Prüfe das folgende Konzept kritisch: größte Stärken, Top-3-Risiken, konkrete "
                   "Verbesserungen, Gesamturteil. Erste Zeile: URTEIL wie vorgegeben.\n\nBRIEFING:\n"
                   + briefing + "\n\nKONZEPT:\n")
        review, _ = _factory_run_step(order_id, "qualitaet", "analysis",
                                      qa_system, qa_task + concept[:3000], num_predict=500)

        if "NICHT BESTANDEN" in review[:80].upper():
            _factory_update_order(order_id, lambda o: o.update(rework_count=1))
            concept, _ = _factory_run_step(
                order_id, "entwicklung", "code",
                "Du bist der CODE/DEV AGENT der KI-Fabrik (Scrum Dev-Team). Überarbeite dein Konzept "
                "anhand des QA-Feedbacks. Antworte auf Deutsch in Markdown.",
                "Nachbesserungs-Schleife: Die QA hat das Konzept NICHT bestanden. Überarbeite es und "
                "behebe die genannten Punkte.\n\nBRIEFING:\n" + briefing +
                "\n\nALTES KONZEPT:\n" + concept[:2000] + "\n\nQA-FEEDBACK:\n" + review[:1500],
                num_predict=900)
            _factory_build_prototype(order_id, briefing, concept)
            _factory_run_step(order_id, "qualitaet", "analysis", qa_system,
                              "ZWEITE PRÜFUNG nach Nachbesserung. " + qa_task + concept[:3000],
                              num_predict=500)

        # 5) Human in the Loop: Fabrik pausiert, bis der CEO die Ergebnisse freigibt.
        #    Die Auslieferung startet erst über /api/factory/orders/approve.
        _factory_set_step(order_id, "abnahme", "active",
                          output="Warte auf Prüfung und Freigabe durch den CEO. "
                                 "Ergebnisse von Planung, Entwicklung und Qualität liegen vor.")
        _factory_update_order(order_id, lambda o: o.update(status="awaiting_approval"))
    except Exception as e:
        err = f"Bearbeitung abgebrochen: {e}"
        _factory_set_step(order_id, _load_current_step(order_id), "error", output=err)
        _factory_update_order(order_id, lambda o: o.update(status="error", error=err))


def _factory_step_output(order, key):
    return next((s.get("output") or "" for s in order.get("steps", []) if s.get("key") == key), "")


def _finalize_factory_order(order_id):
    """Auslieferung nach CEO-Freigabe: Ergebnis-Dokument in 10_Business ablegen."""
    with _factory_lock:
        orders = _load_factory_orders()
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return
    idea_name = order.get("idea", {}).get("name", "Unbenannt")
    version = order.get("version", 1)
    try:
        _factory_set_step(order_id, "abschluss", "active")
        safe_name = re.sub(r"[^\w\-]+", "_", idea_name)[:40] or "Auftrag"
        FACTORY_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        result_path = FACTORY_RESULTS_DIR / f"{order_id}_{safe_name}_v{version}.md"
        approval = order.get("ceo_approval") or {}
        approval_line = f"- Sprint Review / CEO-Abnahme: freigegeben am {approval.get('decided_at', '?')}"
        if approval.get("comment"):
            approval_line += f" — Kommentar: {approval['comment']}"
        rework_line = ("- QA-Kreislauf: 1 Nachbesserungs-Schleife durchlaufen\n"
                       if order.get("rework_count") else "")
        prev_line = (f"- Vorgänger-Sprint: {order['previous_order']}\n"
                     if order.get("previous_order") else "")
        doc = (
            f"# 🏭 KI-Fabrik Auftrag: {idea_name} — Version v{version}\n\n"
            f"- Auftrags-ID: {order_id}\n"
            f"- Sprint/Version: v{version}\n"
            f"{prev_line}"
            f"- Erstellt: {order.get('created_at')}\n"
            f"{rework_line}"
            f"{approval_line}\n"
            f"- Prototyp (Testumgebung): /factory/prototype/{order_id}\n"
            f"- Release: {datetime.now().isoformat(timespec='seconds')}\n\n"
            f"## 👔 CEO-Briefing (Product Owner)\n\n{_idea_briefing(order)}\n\n"
            f"## 🧑‍💼 CTO-Bestätigung (Scrum Master)\n\n{order.get('cto_confirmation') or ''}\n\n"
            f"## 📋 Backlog & Umsetzungsplan\n\n{_factory_step_output(order, 'analyse')}\n\n"
            f"## ⚙️ Technisches Konzept (Dev-Team)\n\n{_factory_step_output(order, 'entwicklung')}\n\n"
            f"## 🔬 Sprint-Inkrement / Prototyp\n\n{_factory_step_output(order, 'prototyp')}\n\n"
            f"## 🧪 QA-Review\n\n{_factory_step_output(order, 'qualitaet')}\n\n"
            f"## 👔 Sprint Review / CEO-Abnahme (Human in the Loop)\n\n{_factory_step_output(order, 'abnahme')}\n"
        )
        result_path.write_text(doc, encoding="utf-8")
        summary = (f"Release v{version} ausgeliefert: 10_Business/KI-Fabrik-Auftraege/{result_path.name}")
        _factory_set_step(order_id, "abschluss", "done", output=summary, engine="Dashboard")
        _factory_update_order(order_id, lambda o: o.update(
            result_file=f"10_Business/KI-Fabrik-Auftraege/{result_path.name}"))

        # Retrospektive (Scrum): Erkenntnisse des Teams fließen in den nächsten Sprint ein
        try:
            _factory_set_step(order_id, "retro", "active")
            retro, retro_engine = _llm_generate(
                "Du bist der Scrum Master (CTO) der KI-Fabrik und moderierst die Sprint-Retrospektive. "
                "Antworte auf Deutsch, kompakt in Markdown mit genau diesen Abschnitten: "
                "## Was lief gut\n## Was verbessern\n## Aktionen für den nächsten Sprint (max. 3)",
                f"Sprint v{version} für „{idea_name}“ ist released. QA-Review:\n"
                + _factory_step_output(order, "qualitaet")[:1200]
                + "\n\nCEO-Feedback bei der Abnahme:\n" + (approval.get("comment") or "(kein Kommentar)")
                + ("\n\nHinweis: Es gab eine QA-Nachbesserungs-Schleife." if order.get("rework_count") else ""),
                num_predict=400, temperature=0.4, timeout=240)
            _factory_set_step(order_id, "retro", "done", output=retro, engine=retro_engine)
            _factory_update_order(order_id, lambda o: o.update(retro=retro[:3000]))
            with result_path.open("a", encoding="utf-8") as fh:
                fh.write(f"\n## 🔁 Retrospektive (für Sprint v{version + 1})\n\n{retro}\n")
        except Exception as re_err:
            _factory_set_step(order_id, "retro", "error", output=f"Retrospektive übersprungen: {re_err}")

        _factory_update_order(order_id, lambda o: o.update(status="completed"))
    except Exception as e:
        err = f"Auslieferung fehlgeschlagen: {e}"
        _factory_set_step(order_id, "abschluss", "error", output=err)
        _factory_update_order(order_id, lambda o: o.update(status="error", error=err))


def _load_current_step(order_id):
    with _factory_lock:
        orders = _load_factory_orders()
    order = next((o for o in orders if o["id"] == order_id), None)
    return order.get("current_step", "annahme") if order else "annahme"


def _factory_recover_stale():
    """Markiert nach einem Dashboard-Neustart hängengebliebene Aufträge als unterbrochen.
    Aufträge in CEO-Abnahme (awaiting_approval) warten legitim auf den Menschen und bleiben erhalten."""
    with _factory_lock:
        orders = _load_factory_orders()
        changed = False
        for o in orders:
            if o.get("status") in ("queued", "processing"):
                o["status"] = "error"
                o["error"] = "Durch Dashboard-Neustart unterbrochen. Bitte erneut beauftragen."
                for s in o.get("steps", []):
                    if s.get("status") == "active":
                        s["status"] = "error"
                changed = True
        if changed:
            _save_factory_orders(orders)


# ========== API ROUTES ==========

@app.route("/")
def index():
    # HTML liegt ausgelagert in templates/dashboard.html — keine Python-Escape-Fallen mehr
    return render_template("dashboard.html", port=FLASK_PORT)

@app.route("/api/models")
def get_models():
    """Listet alle installierten Ollama-Modelle"""
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
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

@app.route("/api/llm/status")
def llm_status():
    """Status des LLM-Routers: welche Provider konfiguriert/online sind, wer aktiv routet."""
    return jsonify(LLM_ROUTER.status())

@app.route("/api/llm/start", methods=["POST"])
def llm_start():
    """Startet die lokale KI-Engine (Ollama oder LM Studio) als entkoppelten Hintergrundprozess."""
    return jsonify(LLM_ROUTER.autostart_local_engine(force=True, wait=12))

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

@app.route("/health")
def health():
    """Health-Check für Monitoring (:5400) und API Gateway (:5100)."""
    return jsonify({
        "status": "ok",
        "service": "AI-OS Dashboard",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/api/services")
def get_services():
    """Prüft parallel den Online-Status aller AI-OS-Dienste (Ebenen-Struktur)."""
    def check(svc):
        online = True if svc["key"] == "dashboard" else check_service_health(
            svc["port"], path=svc.get("health_path", "/health"))
        return {**{k: v for k, v in svc.items() if k not in ("script", "env_key", "health_path")},
                "online": online}

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
        kwargs = {"env": env, "cwd": str(AI_OS_ROOT),
                  "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        if os.name == "nt":
            # Vollständig entkoppeln — auch aus dem Job-Objekt der Aufgabenplanung
            # ausbrechen, sonst killt ein Dashboard-Neustart alle gestarteten Dienste mit.
            DETACHED = 0x00000008 | 0x00000200 | 0x08000000  # DETACHED|NEW_GROUP|NO_WINDOW
            CREATE_BREAKAWAY_FROM_JOB = 0x01000000
            try:
                subprocess.Popen([sys.executable, str(script_path)],
                                 creationflags=DETACHED | CREATE_BREAKAWAY_FROM_JOB, **kwargs)
            except OSError:
                # Breakaway nicht erlaubt (kein Job / Job verbietet es) -> ohne versuchen
                subprocess.Popen([sys.executable, str(script_path)],
                                 creationflags=DETACHED, **kwargs)
        else:
            subprocess.Popen([sys.executable, str(script_path)],
                             start_new_session=True, **kwargs)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)})

def _fetch_json(url, timeout=3):
    """Holt JSON von einem lokalen Dienst, None bei Fehler."""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


@app.route("/api/agents/fleet")
def agents_fleet():
    """Live-Status der kompletten Agenten-Flotte: 7 lokale (:5300) + 3 Spezial-Agenten."""
    fleet = []

    # Lokale Agenten vom Agent System (:5300)
    data = _fetch_json("http://127.0.0.1:5300/agents", timeout=4)
    agent_system_online = data is not None
    if data:
        for a in data.get("agents", []):
            if a.get("type") == "remote":
                continue  # Spezial-Agenten unten mit Live-Health ergänzen
            fleet.append({
                "id": a["name"].lower(), "name": f"🤖 {a['name']} Agent",
                "description": a.get("description", ""), "model": a.get("model"),
                "type": "local", "port": 5300, "online": True,
                "metrics": a.get("metrics", {}),
            })
    else:
        for name, desc in [("Orchestrator", "Koordiniert alle Agenten"), ("Research", "Recherche"),
                           ("Code", "Code-Generierung"), ("Writer", "Texte & Doku"),
                           ("Analysis", "Datenanalyse"), ("Planner", "Planung"),
                           ("Memory", "Gedächtnisverwaltung")]:
            fleet.append({"id": name.lower(), "name": f"🤖 {name} Agent", "description": desc,
                          "type": "local", "port": 5300, "online": False})

    # Spezial-Agenten aus der Registry mit Live-Health-Check
    try:
        registry = json.loads(AGENTS_REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception:
        registry = []

    def check(cfg):
        health = _fetch_json(f"http://127.0.0.1:{cfg['port']}/health", timeout=5)
        return {
            "id": cfg.get("id"), "name": cfg.get("name"), "description": cfg.get("description"),
            "port": cfg.get("port"), "capabilities": cfg.get("capabilities", []),
            "model": cfg.get("llm_model"), "type": "remote",
            "online": health is not None, "health": health,
        }

    if registry:
        with ThreadPoolExecutor(max_workers=len(registry)) as pool:
            fleet.extend(pool.map(check, registry))

    return jsonify({
        "agent_system_online": agent_system_online,
        "agents": fleet,
        "total": len(fleet),
        "online": sum(1 for a in fleet if a.get("online")),
    })


@app.route("/api/agents/action", methods=["POST"])
def agent_action():
    """Proxy für Quick-Actions der Agenten-Karten (nur lokale Agent-Ports)."""
    payload = request.get_json(silent=True) or {}
    port = int(payload.get("port", 0))
    path = payload.get("path", "")
    method = (payload.get("method") or "POST").upper()
    body = payload.get("payload") or {}

    allowed_path = path.startswith("/agent") or path in ("/health", "/agents", "/chat", "/stats")
    if port not in AGENT_ACTION_PORTS or not allowed_path or method not in ("GET", "POST"):
        return jsonify({"error": "Ungültige Agent-Anfrage"}), 400

    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method=method)
        if method == "POST":
            req.data = json.dumps(body).encode("utf-8")
            req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=300) as resp:
            return jsonify(json.loads(resp.read()))
    except urllib.error.HTTPError as e:
        try:
            return jsonify(json.loads(e.read())), e.code
        except Exception:
            return jsonify({"error": f"HTTP {e.code}: {e.reason}"}), e.code
    except Exception as e:
        return jsonify({"error": f"Agent auf Port {port} nicht erreichbar: {e}"}), 503


@app.route("/api/factory/orders", methods=["GET"])
def factory_orders_list():
    """Live-Status aller KI-Fabrik-Aufträge + Verfügbarkeit von CTO (Ollama) und Agent-System."""
    with _factory_lock:
        orders = _load_factory_orders()
    orders.sort(key=lambda o: o.get("created_at", ""), reverse=True)
    return jsonify({
        "orders": orders[:30],
        "steps": FACTORY_STEPS,
        "cto_online": LLM_ROUTER.any_available(),
        "cto_engine": LLM_ROUTER.status()["active"],
        "agent_system_online": check_service_health(5300),
    })


@app.route("/api/factory/orders", methods=["POST"])
def factory_order_create():
    """CEO beauftragt den CTO-Agenten mit einer Idee; Bearbeitung startet im Hintergrund."""
    data = request.get_json(silent=True) or {}
    idea = data.get("idea") or {}
    if not idea.get("name"):
        return jsonify({"error": "Keine Idee angegeben."}), 400
    if not LLM_ROUTER.any_available():
        LLM_ROUTER.kick_autostart()
        return jsonify({"error": "CTO-Agent nicht erreichbar: keine lokale KI-Engine "
                                 "(Ollama/LM Studio) online und kein Fallback (Pi-Gateway/"
                                 "GitHub Models/OpenRouter/Cloudflare) konfiguriert. "
                                 "Autostart wurde angestoßen — siehe Tab 'KI-Gateway'."}), 503

    order = _factory_create_order(idea, str(data.get("note", ""))[:1000])
    return jsonify({"order": order})


def _factory_create_order(idea, note, previous_order=None):
    """Legt einen Auftrag (Sprint) an; die Version zählt pro Idee automatisch hoch."""
    now = datetime.now()
    order = {
        "id": f"ord_{now.strftime('%Y%m%d_%H%M%S')}",
        "idea": {
            "name": str(idea.get("name", ""))[:120],
            "target": str(idea.get("target", ""))[:300],
            "problem": str(idea.get("problem", ""))[:300],
            "solution": str(idea.get("solution", ""))[:2000],
        },
        "note": str(note or "")[:2500],
        "version": 1,
        "previous_order": previous_order,
        "rework_count": 0,
        "retro": None,
        "status": "queued",
        "current_step": "annahme",
        "cto_confirmation": None,
        "ceo_approval": None,
        "prototype_file": None,
        "error": None,
        "result_file": None,
        "steps": [{**s, "status": "pending", "output": None, "engine": None,
                   "started_at": None, "finished_at": None} for s in FACTORY_STEPS],
        "created_at": now.isoformat(timespec="seconds"),
        "updated_at": now.isoformat(timespec="seconds"),
    }
    with _factory_lock:
        orders = _load_factory_orders()
        key = _idea_key(order["idea"]["name"])
        order["version"] = 1 + max(
            [o.get("version", 1) for o in orders
             if _idea_key(o.get("idea", {}).get("name", "")) == key] or [0])
        if order["id"] in {o["id"] for o in orders}:
            order["id"] += f"_{len(orders)}"
        orders.append(order)
        _save_factory_orders(orders)

    threading.Thread(target=_process_factory_order, args=(order["id"],), daemon=True).start()
    return order


@app.route("/api/factory/orders/revise", methods=["POST"])
def factory_order_revise():
    """Kreislauf: startet den Folge-Sprint (neue Version) mit CEO-Feedback und Retrospektive der Vorversion."""
    data = request.get_json(silent=True) or {}
    prev_id = data.get("id", "")
    extra = str(data.get("note", "")).strip()[:800]
    with _factory_lock:
        orders = _load_factory_orders()
    prev = next((o for o in orders if o["id"] == prev_id), None)
    if not prev:
        return jsonify({"error": "Auftrag nicht gefunden."}), 404
    if prev.get("status") not in ("completed", "rejected", "error"):
        return jsonify({"error": "Eine neue Version ist erst nach Abschluss oder Ablehnung des Sprints möglich."}), 409
    if not LLM_ROUTER.any_available():
        return jsonify({"error": "Kein LLM erreichbar — siehe Tab 'KI-Gateway'."}), 503

    parts = [f"Kreislauf/Folge-Sprint: Neue Version des Auftrags {prev_id} (v{prev.get('version', 1)})."]
    ceo = prev.get("ceo_approval") or {}
    if ceo.get("comment"):
        verdict = "Freigabe" if ceo.get("decision") == "approve" else "Ablehnung"
        parts.append(f"CEO-Feedback ({verdict} der Vorversion): {ceo['comment']}")
    if prev.get("retro"):
        parts.append(f"Retrospektive der Vorversion (umsetzen!):\n{prev['retro'][:1200]}")
    if extra:
        parts.append(f"Neue Anweisung des CEO: {extra}")
    order = _factory_create_order(dict(prev.get("idea") or {}), "\n\n".join(parts), previous_order=prev_id)
    return jsonify({"order": order})


@app.route("/factory/prototype/<order_id>")
def factory_prototype(order_id):
    """Testumgebung: liefert den klickbaren Prototyp eines Auftrags für die CEO-Abnahme aus."""
    if not re.fullmatch(r"ord_[\w]+", order_id):
        return "Ungültige Auftrags-ID", 400
    path = FACTORY_PROTO_DIR / f"{order_id}.html"
    if not path.exists():
        return "Für diesen Auftrag existiert (noch) kein Prototyp.", 404
    return path.read_text(encoding="utf-8"), 200, {
        "Content-Type": "text/html; charset=utf-8",
        # Prototyp ist LLM-generierter Code: keine externen Quellen, kein Zugriff auf das Dashboard
        "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; "
                                   "script-src 'unsafe-inline'; img-src data:; sandbox allow-scripts",
    }


@app.route("/api/factory/orders/approve", methods=["POST"])
def factory_order_approve():
    """CEO-Abnahme (Human in the Loop): Freigabe startet die Auslieferung, Ablehnung stoppt den Auftrag."""
    data = request.get_json(silent=True) or {}
    order_id = data.get("id", "")
    decision = data.get("decision", "")
    comment = str(data.get("comment", "")).strip()[:500]
    if decision not in ("approve", "reject"):
        return jsonify({"error": "Ungültige Entscheidung (approve/reject)."}), 400

    with _factory_lock:
        orders = _load_factory_orders()
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return jsonify({"error": "Auftrag nicht gefunden."}), 404
    if order.get("status") != "awaiting_approval":
        return jsonify({"error": "Auftrag wartet nicht auf CEO-Abnahme."}), 409

    now = datetime.now().isoformat(timespec="seconds")
    if decision == "approve":
        note = "✅ Freigegeben durch den CEO." + (f" Kommentar: {comment}" if comment else "")
        _factory_set_step(order_id, "abnahme", "done", output=note, engine="CEO (Mensch)")
        order = _factory_update_order(order_id, lambda o: o.update(
            status="processing",
            ceo_approval={"decision": "approve", "comment": comment, "decided_at": now}))
        threading.Thread(target=_finalize_factory_order, args=(order_id,), daemon=True).start()
    else:
        note = "🚫 Abgelehnt durch den CEO." + (f" Begründung: {comment}" if comment else "")
        _factory_set_step(order_id, "abnahme", "error", output=note, engine="CEO (Mensch)")
        order = _factory_update_order(order_id, lambda o: o.update(
            status="rejected",
            ceo_approval={"decision": "reject", "comment": comment, "decided_at": now}))
    return jsonify({"order": order})


@app.route("/api/factory/orders/delete", methods=["POST"])
def factory_order_delete():
    """Entfernt einen Auftrag aus der Liste (Ergebnis-Dokument in 10_Business bleibt erhalten)."""
    order_id = (request.get_json(silent=True) or {}).get("id", "")
    with _factory_lock:
        orders = _load_factory_orders()
        remaining = [o for o in orders if o["id"] != order_id]
        if len(remaining) == len(orders):
            return jsonify({"error": "Auftrag nicht gefunden"}), 404
        _save_factory_orders(remaining)
    return jsonify({"success": True})


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

# Eigenständige Produkt-Dienste (eigene Flask-Server) hinter /produkte/<name>/.
# Proxy statt Redirect/Direktlink, damit sie auch über Cloudflare-Tunnel und
# Tailscale erreichbar sind (dort ist nur Port 5000 exponiert). Die Dienste
# nutzen relative API-Pfade und funktionieren daher unter beiden URLs.
# Achtung: KEINE eigene Route pro Dienst — Werkzeug würde /produkte/<prod>/
# bevorzugen; das Dispatching übernimmt serve_produkt unten.
KIAVATAR_BOARD_PORT = int(os.environ.get("KIAVATAR_BOARD_PORT", "5310"))
RESEARCH_AGENT_PORT = int(os.environ.get("RESEARCH_AGENT_PORT", "5320"))

PRODUKT_PROXIES = {
    "ki-avatar": {"port": KIAVATAR_BOARD_PORT, "name": "KI-Avatar Board",
                  "start": "python 10_Business/KI-Avatar/board/app.py"},
    "ai-checker": {"port": RESEARCH_AGENT_PORT, "name": "AI Business Checker (Research-Agent)",
                   "start": "python 10_Business/KI-Avatar/research-agent/app.py"},
}

def _produkt_proxy(cfg, subpath):
    from flask import Response
    url = f"http://127.0.0.1:{cfg['port']}/{subpath}"
    if request.query_string:
        url += "?" + request.query_string.decode("utf-8", "ignore")
    data = request.get_data() if request.method in ("POST", "PUT") else None
    req = urllib.request.Request(url, data=data, method=request.method)
    if request.content_type:
        req.add_header("Content-Type", request.content_type)
    try:
        # Großzügig: der Scan des Research-Agenten dauert 1-2 Minuten (Reddit-Drosselung)
        with urllib.request.urlopen(req, timeout=300) as resp:
            return Response(resp.read(), status=resp.status,
                            content_type=resp.headers.get("Content-Type", "text/html"))
    except urllib.error.HTTPError as e:
        return Response(e.read(), status=e.code,
                        content_type=e.headers.get("Content-Type", "application/json"))
    except Exception:
        return Response(
            f"<h1>{cfg['name']} ist offline</h1>"
            f"<p>Starten mit: <code>{cfg['start']}</code> "
            "oder über den Dienste-Tab im Dashboard.</p>",
            status=503, content_type="text/html; charset=utf-8")

@app.route("/produkte/<prod>/", methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/produkte/<prod>/<path:filename>", methods=["GET", "POST", "PUT", "DELETE"])
def serve_produkt(prod, filename="index.html"):
    """Liefert eine Browser-Produkt-App (z.B. DokuCheck Lokal) als statische Dateien.
    Whitelisted über PRODUKT_DIRS, pfadsicher via send_from_directory.
    Bewusst OHNE restriktive CSP: die Apps brauchen Worker, WASM und IndexedDB.
    Sonderfall PRODUKT_PROXIES: Proxy zu eigenständigen Diensten (Board :5310, Research-Agent :5320)."""
    if prod in PRODUKT_PROXIES:
        return _produkt_proxy(PRODUKT_PROXIES[prod], "" if filename == "index.html" else filename)
    if request.method != "GET":
        return jsonify({"error": "Nur GET erlaubt"}), 405
    from flask import send_from_directory
    pfad = PRODUKT_DIRS.get(prod)
    if not pfad:
        return jsonify({"error": "Unbekanntes Produkt"}), 404
    try:
        return send_from_directory(str(AI_OS_ROOT / pfad), filename)
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
        result = LLM_ROUTER.chat(
            messages, model=model, temperature=0.7, num_predict=2048, timeout=120)
        response = result["content"]

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})

        log_interaction(message, response, mode="chat")

        return jsonify({
            "response": response,
            "history": history,
            "provider": result["provider"],
            "provider_label": result["provider_label"],
            "model_used": result["model"]
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
        result = LLM_ROUTER.chat(
            [{"role": "user", "content": prompt}],
            model=model, temperature=0.4, num_predict=800, timeout=180)
        brief = result["content"]

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
            f"{OLLAMA_URL}/api/pull",
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
            f"{OLLAMA_URL}/api/delete",
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
    print(f"🔧 Ollama: {OLLAMA_URL}")
    # Lokale KI-Engine (Ollama/LM Studio) bei Bedarf automatisch mitstarten —
    # das Dashboard ist damit unabhängig von VSCode oder manuell gestarteten Terminals.
    _auto = LLM_ROUTER.autostart_local_engine(wait=6)
    if _auto.get("started"):
        print(f"⚙️ {_auto['message']}")
    _llm = LLM_ROUTER.status()
    print(f"🔀 KI-Gateway: aktiver Provider = {_llm['active'] or 'KEINER (lokale Engine offline, keine Fallback-Keys)'}")
    _factory_recover_stale()
    threading.Thread(target=_news_daily_worker, daemon=True).start()
    app.run(host="127.0.0.1", port=FLASK_PORT, debug=False, threaded=True)
