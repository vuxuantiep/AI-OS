#!/usr/bin/env python3
"""
LiteLLM-Gateway für das AI-OS (Port 4000).

Startet den LiteLLM-Proxy als AI-OS-Dienst: EIN OpenAI-kompatibler Endpunkt
(http://127.0.0.1:4000/v1) für alle Provider — Ollama lokal, Raspberry Pi
(Tailscale), OpenRouter, HuggingFace, GitHub Models — inklusive Fallbacks.

Vorbereitung vor dem Start:
  1. Lädt die .env aus dem Projekt-Root (Secrets, OLLAMA_URL, PI_LLM_URL).
  2. Filtert Modell-Einträge aus litellm_config.yaml, deren Umgebungsvariablen
     fehlen (z.B. Pi ohne PI_LLM_URL) — sonst bricht der Proxy beim Start ab.
  3. Startet `litellm --config <gefilterte config>` als Kindprozess.

Externe Nutzer: OpenHands, LangGraph-Engine und beliebige OpenAI-SDK-Clients
(base_url=http://127.0.0.1:4000/v1, api_key beliebig, solange kein Master-Key
in LITELLM_MASTER_KEY gesetzt ist).
"""

import os
import re
import sys
import subprocess
from pathlib import Path

# Windows: umgeleitete/cp1252-Konsole kann keine Emojis -> UTF-8 erzwingen
if sys.stdout and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")  # gilt auch für den litellm-Kindprozess

AI_OS_ROOT = Path(os.environ.get("AI_OS_ROOT", Path(__file__).parent.parent.parent))
CONFIG_TEMPLATE = Path(__file__).parent / "litellm_config.yaml"
RUNTIME_CONFIG = Path(__file__).parent / ".litellm_config.runtime.yaml"  # generiert, in .gitignore
PORT = int(os.environ.get("LITELLM_PORT", 4000))


def load_env():
    """Lädt die .env ins Prozess-Environment (echte Env-Variablen haben Vorrang)."""
    env_path = AI_OS_ROOT / ".env"
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value
    except FileNotFoundError:
        pass
    # Defaults, damit os.environ/-Referenzen der lokalen Modelle immer auflösen
    os.environ.setdefault("OLLAMA_URL", "http://127.0.0.1:11434")
    # LiteLLMs Cloudflare-Provider erwartet CLOUDFLARE_*-Namen — unsere .env
    # nutzt WORKERS_AI_* (gleicher Account wie das AI-Gateway) → hier mappen.
    if os.environ.get("WORKERS_AI_API_TOKEN"):
        os.environ.setdefault("CLOUDFLARE_API_KEY", os.environ["WORKERS_AI_API_TOKEN"])
    if os.environ.get("WORKERS_AI_ACCOUNT_ID"):
        os.environ.setdefault("CLOUDFLARE_ACCOUNT_ID", os.environ["WORKERS_AI_ACCOUNT_ID"])


def build_runtime_config():
    """Entfernt Modell-Einträge mit fehlenden Umgebungsvariablen aus der Vorlage."""
    import yaml  # kommt mit litellm[proxy]
    cfg = yaml.safe_load(CONFIG_TEMPLATE.read_text(encoding="utf-8"))
    kept, dropped = [], []
    for entry in cfg.get("model_list", []):
        params = entry.get("litellm_params", {})
        missing = [
            m.group(1) for v in params.values() if isinstance(v, str)
            for m in [re.match(r"os\.environ/(\w+)$", v)]
            if m and not os.environ.get(m.group(1), "").strip()
        ]
        (dropped if missing else kept).append((entry, missing))
    cfg["model_list"] = [e for e, _ in kept]

    # Fallback-Ketten um entfernte Modelle bereinigen
    names = {e["model_name"] for e, _ in kept}
    rs = cfg.get("router_settings", {})
    fallbacks = []
    for fb in rs.get("fallbacks", []):
        for src, targets in fb.items():
            if src in names:
                targets = [t for t in targets if t in names]
                if targets:
                    fallbacks.append({src: targets})
    rs["fallbacks"] = fallbacks

    RUNTIME_CONFIG.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False),
                              encoding="utf-8")
    for entry, missing in dropped:
        print(f"⏭️  Modell '{entry['model_name']}' übersprungen (fehlt in .env: {', '.join(missing)})")
    print(f"✅ {len(kept)} Modelle aktiv: {', '.join(sorted(names))}")
    return RUNTIME_CONFIG


def main():
    load_env()
    config = build_runtime_config()
    litellm_exe = Path(sys.executable).with_name("litellm.exe" if os.name == "nt" else "litellm")
    cmd = ([str(litellm_exe)] if litellm_exe.exists() else
           [sys.executable, "-m", "litellm"])
    cmd += ["--config", str(config), "--host", "127.0.0.1", "--port", str(PORT)]
    print(f"🔀 LiteLLM-Gateway startet auf http://127.0.0.1:{PORT} (OpenAI-kompatibel: /v1)")
    # Kindprozess blockierend ausführen: Lebensdauer = Lebensdauer dieses Dienstes
    sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
