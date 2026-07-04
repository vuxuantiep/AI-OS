#!/usr/bin/env python3
"""
OpenHands-Launcher für das AI-OS (Port 3000).

Startet den autonomen Coding-Agenten OpenHands (https://openhands.dev) als
Docker-Container und bindet ihn an die AI-OS-Infrastruktur an:

  OpenHands (GUI :3000) ──▶ LiteLLM-Gateway (:4000) ──▶ Ollama / Pi / Online-Fallbacks

LLM-Einstellung in der OpenHands-Oberfläche (Settings -> LLM -> Advanced):
  Custom Model:  openai/llama3          (oder openai/qwen2.5-coder für Code)
  Base URL:      http://host.docker.internal:4000/v1
  API Key:       sk-ai-os               (beliebig, solange kein LITELLM_MASTER_KEY gesetzt)

Der Container läuft detached weiter, auch wenn dieser Launcher endet.
Stoppen: docker stop openhands-app
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

if sys.stdout and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

OPENHANDS_IMAGE = "docker.openhands.dev/openhands/openhands:1.8"
AGENT_SERVER_REPO = "ghcr.io/openhands/agent-server"
AGENT_SERVER_TAG = "1.26.0-python"
CONTAINER_NAME = "openhands-app"
PORT = int(os.environ.get("OPENHANDS_PORT", 3000))
STATE_DIR = Path.home() / ".openhands"


def run(args, timeout=60):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def docker_ready():
    try:
        return run(["docker", "info", "--format", "{{.ServerVersion}}"]).returncode == 0
    except Exception:
        return False


def ensure_docker():
    """Startet Docker Desktop (Windows), falls der Daemon nicht läuft."""
    if docker_ready():
        return True
    desktop = Path("C:/Program Files/Docker/Docker/Docker Desktop.exe")
    if os.name == "nt" and desktop.exists():
        print("🐳 Docker Desktop wird gestartet...")
        subprocess.Popen([str(desktop)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):  # bis zu 3 Minuten warten
            time.sleep(3)
            if docker_ready():
                return True
    return docker_ready()


def container_state():
    r = run(["docker", "inspect", "--format", "{{.State.Status}}", CONTAINER_NAME])
    return r.stdout.strip() if r.returncode == 0 else None


def start_container():
    state = container_state()
    if state == "running":
        print("✅ OpenHands-Container läuft bereits.")
        return True
    if state is not None:
        print("▶️ Vorhandenen OpenHands-Container starten...")
        return run(["docker", "start", CONTAINER_NAME], timeout=120).returncode == 0

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📦 Starte OpenHands ({OPENHANDS_IMAGE}) — erster Start lädt das Image (mehrere GB)...")
    cmd = [
        "docker", "run", "-d",
        "--name", CONTAINER_NAME,
        "--pull=always",
        "-e", f"AGENT_SERVER_IMAGE_REPOSITORY={AGENT_SERVER_REPO}",
        "-e", f"AGENT_SERVER_IMAGE_TAG={AGENT_SERVER_TAG}",
        "-e", "LOG_ALL_EVENTS=true",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-v", f"{STATE_DIR}:/.openhands",
        "-p", f"{PORT}:3000",
        "--add-host", "host.docker.internal:host-gateway",
        "--restart", "unless-stopped",
        OPENHANDS_IMAGE,
    ]
    r = run(cmd, timeout=1800)
    if r.returncode != 0:
        print(f"❌ docker run fehlgeschlagen: {r.stderr.strip()[:500]}")
        return False
    return True


def wait_healthy(seconds=90):
    for _ in range(seconds // 3):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(3)
    return False


def main():
    if not ensure_docker():
        print("❌ Docker-Daemon nicht erreichbar. Bitte Docker Desktop starten und erneut versuchen.")
        sys.exit(1)
    if not start_container():
        sys.exit(1)
    if wait_healthy():
        print(f"✅ OpenHands läuft: http://localhost:{PORT}")
        print("   LLM-Setup (einmalig, Settings -> LLM -> Advanced):")
        print("   Custom Model = openai/llama3 | Base URL = http://host.docker.internal:4000/v1 | API Key = sk-ai-os")
    else:
        print("⚠️ Container gestartet, UI noch nicht erreichbar — beim ersten Start dauert der Image-Download.")


if __name__ == "__main__":
    main()
