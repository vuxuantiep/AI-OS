#!/usr/bin/env python3
"""
LLM-Router für das AI-OS Dashboard.

Routet Chat-Anfragen mit automatischem Fallback über vier Provider:
  1. Ollama (lokal, Port 11434) — bevorzugt, kostenlos, privat
  2. OpenRouter (online, kostenlose Open-Source-Modelle)
  3. HuggingFace Inference (online, Open-Source-Modelle)
  4. Cloudflare Workers AI (online, optional über AI Gateway)

API-Keys werden NIE im Code gespeichert. Konfiguration in der .env im Projekt-Root
(nicht versioniert, siehe .gitignore):

    OPENROUTER_API_KEY=sk-or-...
    HUGGINGFACE_API_KEY=hf_...
    CLOUDFLARE_ACCOUNT_ID=...
    CLOUDFLARE_API_TOKEN=...
    CLOUDFLARE_AI_GATEWAY=optionaler-gateway-name

Reihenfolge: echte Umgebungsvariablen > .env > (Alt-Fallback)
01_Verbindungen/APIs/Geheimnisse/llm_router.json. Vorlage: .env.example
"""

import os
import json
import time
import threading
import urllib.request
import urllib.error
from pathlib import Path

AI_OS_ROOT = Path(os.environ.get("AI_OS_ROOT", Path(__file__).parent.parent.parent))
ENV_PATH = AI_OS_ROOT / ".env"
SECRETS_PATH = AI_OS_ROOT / "01_Verbindungen" / "APIs" / "Geheimnisse" / "llm_router.json"  # Alt-Fallback

OLLAMA_HOST = "127.0.0.1"
OLLAMA_PORT = 11434

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


class LLMRouter:
    """Provider-Kette mit Health-Cache. Thread-sicher (Flask threaded=True)."""

    def __init__(self):
        self._lock = threading.Lock()
        self._health_cache = {}   # key -> (timestamp, bool)
        self.last_provider = None

    # ---------- Konfiguration ----------

    def _secrets(self):
        env = _load_env_file()
        cfg = {}
        try:
            cfg = json.loads(SECRETS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

        def get(env_key, cfg_key):
            return _clean_secret(os.environ.get(env_key) or env.get(env_key) or cfg.get(cfg_key))

        return {
            "openrouter_api_key": get("OPENROUTER_API_KEY", "openrouter_api_key"),
            "huggingface_api_key": get("HUGGINGFACE_API_KEY", "huggingface_api_key"),
            "cloudflare_account_id": get("CLOUDFLARE_ACCOUNT_ID", "cloudflare_account_id"),
            "cloudflare_api_token": get("CLOUDFLARE_API_TOKEN", "cloudflare_api_token"),
            "cloudflare_gateway": get("CLOUDFLARE_AI_GATEWAY", "cloudflare_gateway"),
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
            with urllib.request.urlopen(
                    f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags", timeout=1.5) as resp:
                return resp.status == 200
        return self._cached_check("ollama", 15, check)

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
        return (self.ollama_online() or self.openrouter_online()
                or self.huggingface_online() or self.cloudflare_online())

    # ---------- Provider-Aufrufe ----------

    def _chat_ollama(self, messages, model, temperature, num_predict, timeout):
        result = _post_json(
            f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat",
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

        if self.ollama_online():
            try:
                content, used = self._chat_ollama(messages, model, temperature, num_predict, timeout)
                self.last_provider = "ollama"
                return {"content": content, "provider": "ollama",
                        "provider_label": "Ollama (lokal)", "model": used}
            except Exception as e:
                errors.append(f"Ollama: {e}")

        if s["openrouter_api_key"]:
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

        if s["huggingface_api_key"]:
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

        if s["cloudflare_account_id"] and s["cloudflare_api_token"]:
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

        if not errors:
            errors.append("Ollama offline und kein Online-Provider konfiguriert "
                          "(OpenRouter/Cloudflare-Keys fehlen).")
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
        openrouter_cfg = bool(s["openrouter_api_key"])
        huggingface_cfg = bool(s["huggingface_api_key"])
        cloudflare_cfg = bool(s["cloudflare_account_id"] and s["cloudflare_api_token"])
        openrouter = self.openrouter_online()
        huggingface = self.huggingface_online()
        cloudflare = self.cloudflare_online()

        active = next((key for key, online in [
            ("ollama", ollama), ("openrouter", openrouter),
            ("huggingface", huggingface), ("cloudflare", cloudflare)] if online), None)
        cf_via = "AI Gateway" if s["cloudflare_gateway"] else "Workers AI"
        providers = [
            {"key": "ollama", "name": "Ollama", "icon": "🖥️", "priority": 1,
             "desc": "Lokale KI-Engine — bevorzugt, privat & kostenlos",
             "detail": f"http://{OLLAMA_HOST}:{OLLAMA_PORT}",
             "configured": True, "online": ollama},
            {"key": "openrouter", "name": "OpenRouter", "icon": "🌍", "priority": 2,
             "desc": "Online-Fallback — kostenlose Open-Source-LLMs",
             "detail": OPENROUTER_MODEL_MAP["default"] if openrouter_cfg
                       else "API-Key fehlt (OPENROUTER_API_KEY in .env eintragen)",
             "configured": openrouter_cfg, "online": openrouter},
            {"key": "huggingface", "name": "HuggingFace", "icon": "🤗", "priority": 3,
             "desc": "Online-Fallback — Open-Source-LLMs via HF Inference Providers",
             "detail": HUGGINGFACE_MODEL_MAP["default"] if huggingface_cfg
                       else "API-Key fehlt (HUGGINGFACE_API_KEY in .env eintragen)",
             "configured": huggingface_cfg, "online": huggingface},
            {"key": "cloudflare", "name": f"Cloudflare {cf_via}", "icon": "☁️", "priority": 4,
             "desc": "Online-Fallback — Open-Source-LLMs auf Cloudflare Workers AI",
             "detail": CLOUDFLARE_MODEL_MAP["default"] if cloudflare_cfg
                       else "CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN in .env eintragen",
             "configured": cloudflare_cfg, "online": cloudflare},
        ]
        return {
            "providers": providers,
            "active": active,
            "last_provider": self.last_provider,
            "any_available": active is not None,
            "secrets_path": ".env (Projekt-Root, nicht versioniert)",
        }


LLM_ROUTER = LLMRouter()
