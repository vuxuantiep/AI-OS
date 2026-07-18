#!/usr/bin/env python3
"""
LLM-Router für das AI-OS Dashboard.

Routet Chat-Anfragen mit automatischem Fallback über sieben Provider:
  1. Ollama (lokal, Port 11434) — bevorzugt, kostenlos, privat.
     Wird bei Bedarf automatisch als Hintergrundprozess gestartet
     (unabhängig von VSCode/Terminal).
  2. LM Studio (lokal, Port 1234, OpenAI-kompatibel) — lokale Alternative
  3. Raspberry Pi Gateway (privat im LAN, PI_LLM_URL) — Ollama- oder OpenAI-kompatibel
  4. GitHub Models (online, GitHub-Konto/Copilot, models.github.ai)
  5. OpenRouter (online, kostenlose Open-Source-Modelle)
  6. HuggingFace Inference (online, Open-Source-Modelle)
  7. Cloudflare Workers AI (online, optional über AI Gateway)

API-Keys werden NIE im Code gespeichert. Konfiguration in der .env im Projekt-Root
(nicht versioniert, siehe .gitignore):

    OLLAMA_URL=http://127.0.0.1:11434  (oder Tailscale: http://tiep-laptop.tailed32d1.ts.net:11434)
    PI_LLM_URL=http://pi-ki-tiep.tailed32d1.ts.net:11434   (Tailscale MagicDNS, verschlüsselt)
    PI_LLM_MODEL=optionaler-modellname
    PI_LLM_API_KEY=optional
    GITHUB_MODELS_TOKEN=github_pat_... (oder GITHUB_TOKEN; Scope "models:read")
    OPENROUTER_API_KEY=sk-or-...
    HUGGINGFACE_API_KEY=hf_...
    WORKERS_AI_ACCOUNT_ID=...
    WORKERS_AI_API_TOKEN=...
    WORKERS_AI_GATEWAY=optionaler-gateway-name
    AI_OS_LLM_AUTOSTART=0  (deaktiviert den Ollama/LM-Studio-Autostart)

Achtung: bewusst NICHT "CLOUDFLARE_API_TOKEN"/"CLOUDFLARE_ACCOUNT_ID" — diese
Namen liest wrangler aus der .env mit und nutzt dann das eingeschränkte
Workers-AI-Token für Deploys (schlägt fehl).

Reihenfolge: echte Umgebungsvariablen > .env > (Alt-Fallback)
01_Verbindungen/APIs/Geheimnisse/llm_router.json. Vorlage: .env.example
"""

import os
import json
import time
import shutil
import threading
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

AI_OS_ROOT = Path(os.environ.get("AI_OS_ROOT", Path(__file__).parent.parent.parent))
ENV_PATH = AI_OS_ROOT / ".env"
SECRETS_PATH = AI_OS_ROOT / "01_Verbindungen" / "APIs" / "Geheimnisse" / "llm_router.json"  # Alt-Fallback

OLLAMA_HOST = "127.0.0.1"
OLLAMA_PORT = 11434
LMSTUDIO_HOST = "127.0.0.1"
LMSTUDIO_PORT = 1234
GITHUB_MODELS_CHAT_URL = "https://models.github.ai/inference/chat/completions"
GITHUB_MODELS_CATALOG_URL = "https://models.github.ai/catalog/models"

# Lokale Modellnamen -> gleichwertige Open-Source-Modelle bei den Online-Providern.
# Unbekannte Modelle fallen auf "default" zurück.
OPENROUTER_MODEL_MAP = {
    "default": "openai/gpt-oss-120b:free",
    "llama3": "meta-llama/llama-3.3-70b-instruct:free",
    "llama2": "meta-llama/llama-3.3-70b-instruct:free",
    "mistral": "openai/gpt-oss-20b:free",
    "deepseek-coder": "qwen/qwen3-coder:free",
    "qwen2.5-coder": "qwen/qwen3-coder:free",
}
HUGGINGFACE_MODEL_MAP = {
    "default": "meta-llama/Llama-3.3-70B-Instruct",
    "llama3": "meta-llama/Llama-3.3-70B-Instruct",
    "llama2": "meta-llama/Llama-3.3-70B-Instruct",
    "mistral": "mistralai/Mistral-7B-Instruct-v0.3",
    "deepseek-coder": "Qwen/Qwen2.5-Coder-32B-Instruct",
    "qwen2.5-coder": "Qwen/Qwen2.5-Coder-32B-Instruct",
}
GITHUB_MODEL_MAP = {
    "default": "openai/gpt-4o-mini",
    "llama3": "meta/llama-3.3-70b-instruct",
    "llama2": "meta/llama-3.3-70b-instruct",
    "mistral": "mistral-ai/mistral-small-2503",
    "deepseek-coder": "openai/gpt-4o-mini",
    "qwen2.5-coder": "openai/gpt-4o-mini",
}
CLOUDFLARE_MODEL_MAP = {
    "default": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    "llama3": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    "llama2": "@cf/meta/llama-3.1-8b-instruct-fp8",
    "mistral": "@cf/mistralai/mistral-small-3.1-24b-instruct",
    "deepseek-coder": "@cf/qwen/qwen2.5-coder-32b-instruct",
    "qwen2.5-coder": "@cf/qwen/qwen2.5-coder-32b-instruct",
}


# Weitere kostenlose OpenRouter-Modelle, falls das erste überlastet ist (HTTP 429)
# Aktuelle Liste: https://openrouter.ai/api/v1/models (IDs mit ":free")
OPENROUTER_ALTERNATES = [
    "openai/gpt-oss-120b:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "google/gemma-4-31b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
]


# ---------- Globaler LLM-Modus-Schalter (Lokal / Hybrid / Cloud) ----------
# Vom Dashboard umschaltbar:
#   "lokal"  = NUR selbst-gehostete Engines (Ollama, LM Studio, Pi über Tailscale)
#              — KEIN Fremd-Cloud-Provider. Maximaler Datenschutz.
#   "hybrid" = lokale Engine zuerst, dann Cloud-Fallback (Standard).
#   "cloud"  = Cloud/Remote ZUERST — überspringt lokale Engines (Ollama/LM Studio/
#              LiteLLM), um den EIGENEN Rechner zu entlasten. Sinnvoll, wenn die
#              lokale GPU/CPU stark ausgelastet ist. Pi (remote) bleibt erlaubt.
# Hinweis: 00_Wissen (knowledge_agent.py) ist DAVON UNABHÄNGIG immer rein lokal.
LLM_MODE_FILE = Path(__file__).parent / "llm_mode.json"
LLM_MODI = ("lokal", "hybrid", "cloud")


def get_llm_mode():
    """Aktueller Modus: 'lokal', 'hybrid' oder 'cloud' (Default: hybrid)."""
    try:
        mode = json.loads(LLM_MODE_FILE.read_text(encoding="utf-8")).get("mode", "hybrid")
        return mode if mode in LLM_MODI else "hybrid"
    except Exception:
        return "hybrid"


def set_llm_mode(mode):
    mode = str(mode).lower()
    if mode in ("local", "lokal-only"):
        mode = "lokal"
    if mode not in LLM_MODI:
        mode = "hybrid"
    LLM_MODE_FILE.write_text(json.dumps({"mode": mode}), encoding="utf-8")
    return mode


def _base_model_name(model):
    """'qwen2.5-coder:7b' -> 'qwen2.5-coder'"""
    return (model or "").split(":")[0].strip().lower()


def _clean_secret(value):
    """Platzhalter aus der Vorlage ('HIER-EINTRAGEN: ...') zählen nicht als konfiguriert."""
    value = (value or "").strip()
    return "" if (not value or " " in value or value.startswith("HIER-EINTRAGEN")) else value


def _load_env_file():
    """Liest die .env im Projekt-Root (KEY=WERT pro Zeile, # = Kommentar)."""
    data = {}
    try:
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip().strip('"').strip("'")
    except Exception:
        pass
    return data


# Ollama-Endpunkt konfigurierbar: Default lokal, per OLLAMA_URL in der .env aber
# auch ein Tailscale-Gerät (z.B. http://tiep-laptop.tailed32d1.ts.net:11434) —
# Tailscale verschlüsselt Ende-zu-Ende (WireGuard), sicherer als offenes LAN.
_boot_env = _load_env_file()
OLLAMA_URL = (os.environ.get("OLLAMA_URL") or _boot_env.get("OLLAMA_URL")
              or f"http://{OLLAMA_HOST}:{OLLAMA_PORT}").rstrip("/")
OLLAMA_IS_LOCAL = ("127.0.0.1" in OLLAMA_URL) or ("localhost" in OLLAMA_URL.lower())

# LiteLLM-Proxy (AI-OS-Dienst :4000): vereinheitlichtes Gateway mit eigenen Fallbacks
LITELLM_URL = (os.environ.get("LITELLM_URL") or _boot_env.get("LITELLM_URL")
               or "http://127.0.0.1:4000").rstrip("/")
# Modelle, die litellm_config.yaml kennt — unbekannte Namen fallen auf llama3 zurück
LITELLM_KNOWN_MODELS = {"llama3", "mistral", "qwen2.5-coder", "deepseek-coder"}


# Einige Anbieter (z.B. HuggingFace) blockieren den Standard-UA "Python-urllib" mit 403
USER_AGENT = "AI-OS-Dashboard/1.0"


def _post_json(url, payload, headers=None, timeout=180):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT, **(headers or {})},
        method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _get_json(url, headers=None, timeout=6):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


# ---------- Autostart der lokalen KI-Engine (Ollama / LM Studio) ----------
# Das Dashboard darf nicht davon abhängen, dass Ollama manuell (z.B. in einem
# VSCode-Terminal) gestartet wurde: fehlt die lokale Engine, wird sie hier als
# eigenständiger, vom Dashboard entkoppelter Hintergrundprozess gestartet.

AUTOSTART_ENABLED = (os.environ.get("AI_OS_LLM_AUTOSTART", "1").strip() != "0")
AUTOSTART_COOLDOWN = 120  # Sekunden zwischen zwei Startversuchen


def _find_executable(name, extra_paths):
    """Sucht eine ausführbare Datei im PATH und an typischen Installationsorten."""
    found = shutil.which(name)
    if found:
        return found
    for p in extra_paths:
        if p and Path(p).exists():
            return str(p)
    return None


def _find_ollama():
    local_app = os.environ.get("LOCALAPPDATA", "")
    return _find_executable("ollama", [
        Path(local_app) / "Programs" / "Ollama" / "ollama.exe" if local_app else None,
        Path("C:/Program Files/Ollama/ollama.exe"),
        Path("/usr/local/bin/ollama"),
        Path("/usr/bin/ollama"),
    ])


def _find_lmstudio_cli():
    home = Path.home()
    return _find_executable("lms", [
        home / ".lmstudio" / "bin" / "lms.exe",
        home / ".lmstudio" / "bin" / "lms",
        home / ".cache" / "lm-studio" / "bin" / "lms",
    ])


def _spawn_detached(args):
    """Startet einen Prozess vollständig entkoppelt (überlebt das Beenden des Dashboards)."""
    kwargs = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL,
              "stderr": subprocess.DEVNULL, "close_fds": True}
    if os.name == "nt":
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        CREATE_NO_WINDOW = 0x08000000
        kwargs["creationflags"] = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(args, **kwargs)


class LLMRouter:
    """Provider-Kette mit Health-Cache. Thread-sicher (Flask threaded=True)."""

    def __init__(self):
        self._lock = threading.Lock()
        self._health_cache = {}   # key -> (timestamp, bool)
        self._autostart_ts = 0
        self._pi_style = None     # "ollama" | "openai", per Health-Check erkannt
        self.last_provider = None

    # ---------- Konfiguration ----------

    def _secrets(self):
        env = _load_env_file()
        cfg = {}
        try:
            cfg = json.loads(SECRETS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

        def get(*env_keys, cfg_key):
            for key in env_keys:
                value = _clean_secret(os.environ.get(key) or env.get(key))
                if value:
                    return value
            return _clean_secret(cfg.get(cfg_key))

        return {
            "pi_url": get("PI_LLM_URL", cfg_key="pi_llm_url").rstrip("/"),
            "pi_model": get("PI_LLM_MODEL", cfg_key="pi_llm_model"),
            "pi_api_key": get("PI_LLM_API_KEY", cfg_key="pi_llm_api_key"),
            "github_token": get("GITHUB_MODELS_TOKEN", "GITHUB_TOKEN", cfg_key="github_models_token"),
            "openrouter_api_key": get("OPENROUTER_API_KEY", cfg_key="openrouter_api_key"),
            "huggingface_api_key": get("HUGGINGFACE_API_KEY", cfg_key="huggingface_api_key"),
            "cloudflare_account_id": get("WORKERS_AI_ACCOUNT_ID", "CLOUDFLARE_ACCOUNT_ID",
                                         cfg_key="cloudflare_account_id"),
            "cloudflare_api_token": get("WORKERS_AI_API_TOKEN", "CLOUDFLARE_API_TOKEN",
                                        cfg_key="cloudflare_api_token"),
            "cloudflare_gateway": get("WORKERS_AI_GATEWAY", "CLOUDFLARE_AI_GATEWAY",
                                      cfg_key="cloudflare_gateway"),
        }

    def _cf_endpoint(self, s):
        if s["cloudflare_gateway"]:
            return (f"https://gateway.ai.cloudflare.com/v1/{s['cloudflare_account_id']}"
                    f"/{s['cloudflare_gateway']}/workers-ai/v1/chat/completions")
        return (f"https://api.cloudflare.com/client/v4/accounts/"
                f"{s['cloudflare_account_id']}/ai/v1/chat/completions")

    # ---------- Health-Checks (gecacht) ----------

    def _cached_check(self, key, ttl, fn):
        now = time.time()
        with self._lock:
            ts, val = self._health_cache.get(key, (0, False))
            if now - ts < ttl:
                return val
        try:
            val = fn()
        except Exception:
            val = False
        with self._lock:
            self._health_cache[key] = (now, val)
        return val

    def ollama_online(self):
        def check():
            req = urllib.request.Request(f"{OLLAMA_URL}/api/tags",
                                         headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                return resp.status == 200
        return self._cached_check("ollama", 15, check)

    def lmstudio_online(self):
        def check():
            data = _get_json(f"http://{LMSTUDIO_HOST}:{LMSTUDIO_PORT}/v1/models", timeout=1.5)
            return isinstance(data.get("data"), list)
        return self._cached_check("lmstudio", 15, check)

    def litellm_online(self):
        def check():
            data = _get_json(f"{LITELLM_URL}/health/liveliness", timeout=1.5)
            return bool(data)
        return self._cached_check("litellm", 15, check)

    def pi_online(self):
        s = self._secrets()
        if not s["pi_url"]:
            return False
        def check():
            # Erst Ollama-Stil (/api/tags), dann OpenAI-Stil (/v1/models) probieren
            headers = {"Authorization": f"Bearer {s['pi_api_key']}"} if s["pi_api_key"] else {}
            try:
                _get_json(f"{s['pi_url']}/api/tags", headers=headers, timeout=2.5)
                self._pi_style = "ollama"
                return True
            except Exception:
                _get_json(f"{s['pi_url']}/v1/models", headers=headers, timeout=2.5)
                self._pi_style = "openai"
                return True
        return self._cached_check("pi", 30, check)

    def github_online(self):
        s = self._secrets()
        if not s["github_token"]:
            return False
        def check():
            data = _get_json(
                GITHUB_MODELS_CATALOG_URL,
                headers={"Authorization": f"Bearer {s['github_token']}",
                         "Accept": "application/vnd.github+json"})
            return bool(data)
        return self._cached_check("github", 60, check)

    def local_engine_online(self):
        return self.ollama_online() or self.lmstudio_online()

    def openrouter_online(self):
        s = self._secrets()
        if not s["openrouter_api_key"]:
            return False
        def check():
            data = _get_json("https://openrouter.ai/api/v1/key",
                             headers={"Authorization": f"Bearer {s['openrouter_api_key']}"})
            return bool(data.get("data"))
        return self._cached_check("openrouter", 60, check)

    def huggingface_online(self):
        s = self._secrets()
        if not s["huggingface_api_key"]:
            return False
        def check():
            data = _get_json("https://huggingface.co/api/whoami-v2",
                             headers={"Authorization": f"Bearer {s['huggingface_api_key']}"})
            return bool(data.get("name"))
        return self._cached_check("huggingface", 60, check)

    def cloudflare_online(self):
        s = self._secrets()
        if not (s["cloudflare_account_id"] and s["cloudflare_api_token"]):
            return False
        def check():
            data = _get_json(
                f"https://api.cloudflare.com/client/v4/accounts/"
                f"{s['cloudflare_account_id']}/ai/models/search?per_page=1",
                headers={"Authorization": f"Bearer {s['cloudflare_api_token']}"})
            return bool(data.get("success"))
        return self._cached_check("cloudflare", 60, check)

    def any_available(self):
        return (self.ollama_online() or self.lmstudio_online() or self.litellm_online()
                or self.pi_online() or self.github_online() or self.openrouter_online()
                or self.huggingface_online() or self.cloudflare_online())

    # ---------- Autostart der lokalen Engine ----------

    def autostart_local_engine(self, force=False, wait=0):
        """Startet Ollama (bevorzugt) oder LM Studio als entkoppelten Hintergrundprozess.

        wait > 0: blockiert bis zu `wait` Sekunden, bis die Engine antwortet.
        Gibt dict mit "started", "online" und "message" zurück.
        """
        if self.local_engine_online():
            return {"started": None, "online": True, "message": "Lokale KI-Engine läuft bereits."}
        if not (AUTOSTART_ENABLED or force):
            return {"started": None, "online": False,
                    "message": "Autostart deaktiviert (AI_OS_LLM_AUTOSTART=0)."}

        now = time.time()
        with self._lock:
            if not force and now - self._autostart_ts < AUTOSTART_COOLDOWN:
                return {"started": None, "online": False,
                        "message": "Startversuch läuft bereits (Cooldown aktiv)."}
            self._autostart_ts = now

        started, message = None, ""
        # Zeigt OLLAMA_URL auf ein entferntes Gerät (z.B. via Tailscale), kann ein
        # lokaler Prozessstart es nicht erreichbar machen — dann nur LM Studio probieren.
        ollama = _find_ollama() if OLLAMA_IS_LOCAL else None
        if not OLLAMA_IS_LOCAL:
            message = f"Ollama-Endpunkt ist entfernt ({OLLAMA_URL}) — dort manuell starten."
        if ollama:
            try:
                _spawn_detached([ollama, "serve"])
                started = "ollama"
                message = f"Ollama wird im Hintergrund gestartet ({ollama})."
            except Exception as e:
                message = f"Ollama-Start fehlgeschlagen: {e}"
        if not started:
            lms = _find_lmstudio_cli()
            if lms:
                try:
                    _spawn_detached([lms, "server", "start"])
                    started = "lmstudio"
                    message = f"LM Studio Server wird im Hintergrund gestartet ({lms})."
                except Exception as e:
                    message += f" LM-Studio-Start fehlgeschlagen: {e}"
        if not started and not message:
            message = ("Weder Ollama noch LM Studio gefunden. Installation: "
                       "https://ollama.com/download oder https://lmstudio.ai — "
                       "alternativ Pi-Gateway/Online-Fallback in der .env konfigurieren.")

        online = False
        if started:
            deadline = time.time() + max(0, wait)
            while True:
                with self._lock:
                    self._health_cache.pop("ollama", None)
                    self._health_cache.pop("lmstudio", None)
                online = self.local_engine_online()
                if online or time.time() >= deadline:
                    break
                time.sleep(1.0)
            if online:
                message += " Engine ist jetzt erreichbar."
        return {"started": started, "online": online, "message": message.strip()}

    def kick_autostart(self):
        """Nicht-blockierender Autostart-Anstoß (z.B. beim Laden des Dashboards)."""
        if AUTOSTART_ENABLED and not self.local_engine_online():
            threading.Thread(target=self.autostart_local_engine,
                             kwargs={"wait": 10}, daemon=True).start()

    # ---------- Provider-Aufrufe ----------

    def _chat_ollama(self, messages, model, temperature, num_predict, timeout):
        result = _post_json(
            f"{OLLAMA_URL}/api/chat",
            {"model": model, "messages": messages, "stream": False,
             "options": {"temperature": temperature, "num_predict": num_predict}},
            timeout=timeout)
        content = result.get("message", {}).get("content", "").strip()
        if not content:
            raise RuntimeError("Ollama lieferte leere Antwort")
        return content, model

    def _chat_openai_compatible(self, url, api_key, messages, model, temperature,
                                num_predict, timeout, extra_headers=None):
        result = _post_json(
            url,
            {"model": model, "messages": messages, "stream": False,
             "temperature": temperature, "max_tokens": num_predict},
            headers={"Authorization": f"Bearer {api_key}", **(extra_headers or {})},
            timeout=timeout)
        choices = result.get("choices") or []
        content = (choices[0].get("message", {}).get("content", "") if choices else "").strip()
        if not content:
            raise RuntimeError(f"Leere Antwort: {str(result)[:200]}")
        return content, model

    def _lmstudio_model(self, base):
        """Wählt das in LM Studio geladene Modell (passend zum Wunschnamen, sonst das erste)."""
        try:
            data = _get_json(f"http://{LMSTUDIO_HOST}:{LMSTUDIO_PORT}/v1/models", timeout=3)
            ids = [m.get("id", "") for m in data.get("data", []) if m.get("id")]
            for mid in ids:
                if base and base in mid.lower():
                    return mid
            for mid in ids:
                if "embed" not in mid.lower():
                    return mid
        except Exception:
            pass
        return base or "local-model"

    def _chat_pi(self, s, messages, model, temperature, num_predict, timeout):
        """Chat gegen das Raspberry-Pi-Gateway (Ollama- oder OpenAI-kompatibel)."""
        url = s["pi_url"]
        headers = {"Authorization": f"Bearer {s['pi_api_key']}"} if s["pi_api_key"] else {}
        if self._pi_style == "ollama":
            target = s["pi_model"]
            if not target:
                try:
                    tags = _get_json(f"{url}/api/tags", headers=headers, timeout=4)
                    names = [m.get("name", "") for m in tags.get("models", [])]
                    target = next((n for n in names if _base_model_name(model) in n.lower()),
                                  names[0] if names else model)
                except Exception:
                    target = model
            result = _post_json(
                f"{url}/api/chat",
                {"model": target, "messages": messages, "stream": False,
                 "options": {"temperature": temperature, "num_predict": num_predict}},
                headers=headers, timeout=timeout)
            content = result.get("message", {}).get("content", "").strip()
            if not content:
                raise RuntimeError("Pi-Gateway lieferte leere Antwort")
            return content, target
        # OpenAI-kompatibel (llama.cpp-Server, LocalAI, vLLM, ...)
        target = s["pi_model"]
        if not target:
            try:
                data = _get_json(f"{url}/v1/models", headers=headers, timeout=4)
                ids = [m.get("id", "") for m in data.get("data", []) if m.get("id")]
                target = ids[0] if ids else model
            except Exception:
                target = model
        return self._chat_openai_compatible(
            f"{url}/v1/chat/completions", s["pi_api_key"] or "none",
            messages, target, temperature, num_predict, timeout)

    # ---------- Öffentliche API ----------

    def chat(self, messages, model="llama3", temperature=0.7, num_predict=800, timeout=180):
        """
        Chat mit automatischem Fallback. Gibt dict zurück:
          {"content", "provider", "provider_label", "model"}
        Wirft RuntimeError, wenn kein Provider erreichbar ist.
        """
        s = self._secrets()
        base = _base_model_name(model)
        errors = []

        # Globaler Schalter:
        #   nur_lokal    → alle Fremd-Cloud-Provider übersprungen
        #   cloud_zuerst → lokale Engines (Ollama/LM Studio/LiteLLM) übersprungen,
        #                  um den eigenen Rechner zu entlasten (Pi bleibt, ist remote)
        _mode = get_llm_mode()
        nur_lokal = _mode == "lokal"
        cloud_zuerst = _mode == "cloud"

        # Lokale Engine nur hochfahren, wenn wir sie auch nutzen wollen.
        if not cloud_zuerst and not self.local_engine_online():
            self.autostart_local_engine(wait=8)

        if not cloud_zuerst and self.ollama_online():
            try:
                content, used = self._chat_ollama(messages, model, temperature, num_predict, timeout)
                self.last_provider = "ollama"
                return {"content": content, "provider": "ollama",
                        "provider_label": "Ollama (lokal)", "model": used}
            except Exception as e:
                errors.append(f"Ollama: {e}")

        if not cloud_zuerst and self.lmstudio_online():
            try:
                lm_model = self._lmstudio_model(base)
                content, used = self._chat_openai_compatible(
                    f"http://{LMSTUDIO_HOST}:{LMSTUDIO_PORT}/v1/chat/completions",
                    "lm-studio", messages, lm_model, temperature, num_predict, timeout)
                self.last_provider = "lmstudio"
                return {"content": content, "provider": "lmstudio",
                        "provider_label": f"LM Studio (lokal, {used})", "model": used}
            except Exception as e:
                errors.append(f"LM Studio: {e}")

        # LiteLLM startet selbst mit Ollama → im Lokal-Modus (Cloud gesperrt) UND
        # im Cloud-Modus (lokale Last vermeiden) überspringen.
        if not nur_lokal and not cloud_zuerst and self.litellm_online():
            try:
                ll_model = base if base in LITELLM_KNOWN_MODELS else "llama3"
                content, used = self._chat_openai_compatible(
                    f"{LITELLM_URL}/v1/chat/completions",
                    os.environ.get("LITELLM_MASTER_KEY", "sk-ai-os"),
                    messages, ll_model, temperature, num_predict, timeout)
                self.last_provider = "litellm"
                return {"content": content, "provider": "litellm",
                        "provider_label": f"LiteLLM Gateway ({used})", "model": used}
            except Exception as e:
                errors.append(f"LiteLLM: {e}")

        if s["pi_url"] and self.pi_online():
            try:
                content, used = self._chat_pi(s, messages, model, temperature,
                                              num_predict, min(timeout, 240))
                self.last_provider = "pi"
                return {"content": content, "provider": "pi",
                        "provider_label": f"Raspberry Pi Gateway ({used})", "model": used}
            except Exception as e:
                errors.append(f"Pi-Gateway: {e}")

        if not nur_lokal and s["github_token"]:
            try:
                gh_model = GITHUB_MODEL_MAP.get(base, GITHUB_MODEL_MAP["default"])
                content, used = self._chat_openai_compatible(
                    GITHUB_MODELS_CHAT_URL, s["github_token"], messages,
                    gh_model, temperature, num_predict, min(timeout, 120))
                self.last_provider = "github"
                return {"content": content, "provider": "github",
                        "provider_label": f"GitHub Models ({used})", "model": used}
            except Exception as e:
                errors.append(f"GitHub Models: {e}")

        if not nur_lokal and s["openrouter_api_key"]:
            # Freie Modelle sind oft überlastet (429) -> mehrere Kandidaten durchprobieren
            or_model = OPENROUTER_MODEL_MAP.get(base, OPENROUTER_MODEL_MAP["default"])
            candidates = [or_model] + [m for m in OPENROUTER_ALTERNATES if m != or_model]
            for candidate in candidates[:3]:
                try:
                    # Online-Timeouts kürzer halten als lokale (große lokale Modelle sind langsam)
                    content, used = self._chat_openai_compatible(
                        "https://openrouter.ai/api/v1/chat/completions",
                        s["openrouter_api_key"], messages, candidate,
                        temperature, num_predict, min(timeout, 120),
                        extra_headers={"HTTP-Referer": "http://localhost:5000",
                                       "X-Title": "AI-OS Dashboard"})
                    self.last_provider = "openrouter"
                    return {"content": content, "provider": "openrouter",
                            "provider_label": f"OpenRouter ({used})", "model": used}
                except Exception as e:
                    errors.append(f"OpenRouter ({candidate}): {e}")

        if not nur_lokal and s["huggingface_api_key"]:
            try:
                hf_model = HUGGINGFACE_MODEL_MAP.get(base, HUGGINGFACE_MODEL_MAP["default"])
                content, used = self._chat_openai_compatible(
                    "https://router.huggingface.co/v1/chat/completions",
                    s["huggingface_api_key"], messages, hf_model,
                    temperature, num_predict, min(timeout, 120))
                self.last_provider = "huggingface"
                return {"content": content, "provider": "huggingface",
                        "provider_label": f"HuggingFace ({used})", "model": used}
            except Exception as e:
                errors.append(f"HuggingFace: {e}")

        if not nur_lokal and s["cloudflare_account_id"] and s["cloudflare_api_token"]:
            try:
                cf_model = CLOUDFLARE_MODEL_MAP.get(base, CLOUDFLARE_MODEL_MAP["default"])
                via = "AI Gateway" if s["cloudflare_gateway"] else "Workers AI"
                content, used = self._chat_openai_compatible(
                    self._cf_endpoint(s), s["cloudflare_api_token"], messages,
                    cf_model, temperature, num_predict, min(timeout, 120))
                self.last_provider = "cloudflare"
                return {"content": content, "provider": "cloudflare",
                        "provider_label": f"Cloudflare {via} ({used})", "model": used}
            except Exception as e:
                errors.append(f"Cloudflare: {e}")

        if cloud_zuerst and not errors:
            errors.append("Cloud-Modus aktiv (lokale Engines übersprungen, um den "
                          "Rechner zu entlasten), aber kein Cloud-Provider erreichbar. "
                          "Cloud-Keys in .env prüfen oder im Dashboard auf Hybrid/Lokal schalten.")
        if not errors:
            if nur_lokal:
                errors.append("Lokal-Modus aktiv und keine lokale Engine erreichbar "
                              "(Ollama/LM Studio/Pi). Cloud ist per Schalter gesperrt — "
                              "Ollama starten oder im Dashboard auf Hybrid umschalten.")
            else:
                errors.append("Keine lokale Engine (Ollama/LM Studio) erreichbar und kein "
                              "Fallback konfiguriert (PI_LLM_URL / GITHUB_MODELS_TOKEN / "
                              "OPENROUTER_API_KEY / Cloudflare-Keys fehlen in der .env).")
        raise RuntimeError("Kein LLM-Provider verfügbar. " + " | ".join(errors))

    def generate(self, system, prompt, model="llama3", temperature=0.5,
                 num_predict=800, timeout=300):
        """Komfort-Wrapper: System + User-Prompt. Gibt (text, provider_label) zurück."""
        result = self.chat(
            [{"role": "system", "content": system},
             {"role": "user", "content": prompt}],
            model=model, temperature=temperature,
            num_predict=num_predict, timeout=timeout)
        return result["content"], result["provider_label"]

    def status(self):
        """Status aller Provider für den Dashboard-Tab 'KI-Gateway'."""
        s = self._secrets()
        ollama = self.ollama_online()
        lmstudio = self.lmstudio_online()
        litellm = self.litellm_online()
        pi_cfg = bool(s["pi_url"])
        github_cfg = bool(s["github_token"])
        openrouter_cfg = bool(s["openrouter_api_key"])
        huggingface_cfg = bool(s["huggingface_api_key"])
        cloudflare_cfg = bool(s["cloudflare_account_id"] and s["cloudflare_api_token"])
        pi = self.pi_online()
        github = self.github_online()
        openrouter = self.openrouter_online()
        huggingface = self.huggingface_online()
        cloudflare = self.cloudflare_online()

        active = next((key for key, online in [
            ("ollama", ollama), ("lmstudio", lmstudio), ("litellm", litellm),
            ("pi", pi), ("github", github),
            ("openrouter", openrouter), ("huggingface", huggingface),
            ("cloudflare", cloudflare)] if online), None)
        cf_via = "AI Gateway" if s["cloudflare_gateway"] else "Workers AI"
        providers = [
            {"key": "ollama", "name": "Ollama", "icon": "🖥️", "priority": 1,
             "desc": ("Lokale KI-Engine — bevorzugt, privat & kostenlos (Autostart aktiv)"
                      if OLLAMA_IS_LOCAL else
                      "Ollama über Tailscale — privat & Ende-zu-Ende verschlüsselt"),
             "detail": OLLAMA_URL,
             "configured": True, "online": ollama},
            {"key": "lmstudio", "name": "LM Studio", "icon": "🎛️", "priority": 2,
             "desc": "Lokale Alternative — OpenAI-kompatibler Server",
             "detail": f"http://{LMSTUDIO_HOST}:{LMSTUDIO_PORT}/v1",
             "configured": True, "online": lmstudio},
            {"key": "litellm", "name": "LiteLLM Gateway", "icon": "🚦", "priority": 3,
             "desc": "AI-OS-Dienst :4000 — ein OpenAI-Endpunkt, routet selbst mit Fallbacks",
             "detail": f"{LITELLM_URL}/v1 (Start im Tab 'Dienste')",
             "configured": True, "online": litellm},
            {"key": "pi", "name": "Raspberry Pi Gateway", "icon": "🍓", "priority": 4,
             "desc": "Privater LAN-Fallback — miniLLM auf dem Raspberry Pi 4",
             "detail": s["pi_url"] if pi_cfg
                       else "PI_LLM_URL in .env eintragen (z.B. http://raspberrypi.local:11434)",
             "configured": pi_cfg, "online": pi},
            {"key": "github", "name": "GitHub Models", "icon": "🐙", "priority": 5,
             "desc": "Online-Fallback über dein GitHub/Copilot-Konto (models.github.ai)",
             "detail": GITHUB_MODEL_MAP["default"] if github_cfg
                       else "GITHUB_MODELS_TOKEN in .env eintragen (PAT mit Scope models:read)",
             "configured": github_cfg, "online": github},
            {"key": "openrouter", "name": "OpenRouter", "icon": "🌍", "priority": 6,
             "desc": "Online-Fallback — kostenlose Open-Source-LLMs",
             "detail": OPENROUTER_MODEL_MAP["default"] if openrouter_cfg
                       else "API-Key fehlt (OPENROUTER_API_KEY in .env eintragen)",
             "configured": openrouter_cfg, "online": openrouter},
            {"key": "huggingface", "name": "HuggingFace", "icon": "🤗", "priority": 7,
             "desc": "Online-Fallback — Open-Source-LLMs via HF Inference Providers",
             "detail": HUGGINGFACE_MODEL_MAP["default"] if huggingface_cfg
                       else "API-Key fehlt (HUGGINGFACE_API_KEY in .env eintragen)",
             "configured": huggingface_cfg, "online": huggingface},
            {"key": "cloudflare", "name": f"Cloudflare {cf_via}", "icon": "☁️", "priority": 8,
             "desc": "Online-Fallback — Open-Source-LLMs auf Cloudflare Workers AI",
             "detail": CLOUDFLARE_MODEL_MAP["default"] if cloudflare_cfg
                       else "WORKERS_AI_ACCOUNT_ID + WORKERS_AI_API_TOKEN in .env eintragen",
             "configured": cloudflare_cfg, "online": cloudflare},
        ]
        return {
            "providers": providers,
            "active": active,
            "last_provider": self.last_provider,
            "any_available": active is not None,
            "autostart_enabled": AUTOSTART_ENABLED,
            "local_engine_online": ollama or lmstudio,
            "secrets_path": ".env (Projekt-Root, nicht versioniert)",
        }


LLM_ROUTER = LLMRouter()
