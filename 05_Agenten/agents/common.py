#!/usr/bin/env python3
"""
Gemeinsame Bausteine für die Spezial-Agenten (Cal, Bubble, Higgsfield).
Ollama-Anbindung, Retry-Logik, Monitoring-Logging und .env-Handling.
"""

import json
import os
import re
import sys
import time
from pathlib import Path
from datetime import datetime

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Konfiguration
AI_OS_ROOT = Path(os.environ.get("AI_OS_ROOT", Path(__file__).parent.parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv(AI_OS_ROOT / ".env")
except ImportError:
    pass

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
# Hinweis: qwen3.5:9b ist lokal nicht installiert -> Default llama3 (siehe CLAUDE.md Modell-Tabelle)
LLM_MODEL = os.environ.get("AGENT_LLM_MODEL", "llama3")
MONITORING_URL = os.environ.get("MONITORING_URL", "http://127.0.0.1:5400")

# Retry-Policy für externe APIs: 3 Versuche, exponentieller Backoff (1s, 2s, 4s)
api_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.TransportError, httpx.TimeoutException)),
    reraise=True,
)


def load_agent_config(agent_id):
    """Lädt die Konfiguration eines Agenten aus der agents.json Registry."""
    registry = Path(__file__).parent / "agents.json"
    try:
        for cfg in json.loads(registry.read_text(encoding="utf-8")):
            if cfg.get("id") == agent_id:
                return cfg
    except Exception:
        pass
    return {"id": agent_id, "name": agent_id, "capabilities": []}


async def ollama_chat(prompt, system=None, model=None, temperature=0.7, timeout=180):
    """Chat-Anfrage an das lokale Ollama-Modell. Wirft Exception wenn Ollama offline."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(f"{OLLAMA_URL}/api/chat", json={
            "model": model or LLM_MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": 4096},
        })
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "")


# 15s-Cache: /health der Agenten muss schnell antworten (Dashboard-Timeout),
# darf also nicht bei jedem Aufruf live auf Ollama warten.
_ollama_health = {"ts": 0.0, "val": False}


async def ollama_online():
    """Prüft ob Ollama erreichbar ist (Ergebnis 15s gecacht)."""
    now = time.monotonic()
    if now - _ollama_health["ts"] < 15:
        return _ollama_health["val"]
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            val = resp.status_code == 200
    except Exception:
        val = False
    _ollama_health["ts"], _ollama_health["val"] = now, val
    return val


def extract_json(text):
    """Extrahiert das erste JSON-Objekt aus einer LLM-Antwort (auch aus Code-Blöcken)."""
    if not text:
        return None
    # Code-Block bevorzugen
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    candidate = match.group(1) if match else text
    # Erstes { ... } bzw. [ ... ] greifen
    for open_c, close_c in (("{", "}"), ("[", "]")):
        start = candidate.find(open_c)
        end = candidate.rfind(close_c)
        if start != -1 and end > start:
            try:
                return json.loads(candidate[start:end + 1])
            except json.JSONDecodeError:
                continue
    return None


async def monitor_log(level, source, message):
    """Schreibt einen Log-Eintrag ins Monitoring (:5400). Fehler werden verschluckt."""
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            await client.post(f"{MONITORING_URL}/log", json={
                "level": level, "source": source, "message": str(message)[:500],
            })
    except Exception:
        pass


def health_payload(config, extra=None):
    """Einheitliches /health-Format, kompatibel zum bestehenden Monitoring."""
    payload = {
        "status": "ok",
        "service": config.get("name", "Agent"),
        "agent_id": config.get("id"),
        "version": "2.0.0",
        "llm_model": LLM_MODEL,
        "timestamp": datetime.now().isoformat(),
    }
    if extra:
        payload.update(extra)
    return payload


def missing_key_error(env_name):
    """Einheitliche Fehlermeldung bei fehlendem API-Key (Offline-Modus)."""
    return {
        "success": False,
        "error": f"{env_name} nicht konfiguriert",
        "hint": f"Setze {env_name} in der .env im AI-OS-Root oder als Umgebungsvariable. "
                "Ollama-Features funktionieren auch ohne Key (Offline-Modus).",
    }
