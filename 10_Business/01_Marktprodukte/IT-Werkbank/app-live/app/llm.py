"""
LLM-Kette der IT-Werkbank.

Ziel: der Assistent antwortet immer. Die Kette wird von oben nach unten
durchprobiert, der erste Anbieter der liefert gewinnt. Faellt das lokale
Modell aus (Rechner aus, Modell laedt, GPU belegt), uebernimmt die Cloud
ohne Zutun des Benutzers.

Reihenfolge und Begruendung:
  1. lokal   — kostenlos, Daten bleiben im Haus, aber nicht immer verfuegbar
  2. cloud A — Hauptfallback, starkes Modell
  3. cloud B — zweiter Anbieter, falls A gestoert ist

Ein Anbieter, der scheitert, wird fuer AUSFALL_SPERRE Sekunden uebersprungen.
Das verhindert, dass jede Anfrage auf einen toten lokalen Endpunkt wartet.
"""

from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass

import httpx

AUSFALL_SPERRE = 120  # Sekunden, die ein gescheiterter Anbieter uebersprungen wird


@dataclass
class Anbieter:
    name: str
    art: str  # "lokal" oder "cloud"
    protokoll: str  # "openai" oder "anthropic"
    url: str
    modell: str
    schluessel: str = ""
    basic_auth_nutzer: str = ""
    basic_auth_passwort: str = ""
    zeitlimit: float = 60.0
    gesperrt_bis: float = 0.0

    @property
    def einsatzbereit(self) -> bool:
        hat_zugang = bool(self.schluessel) or bool(self.basic_auth_passwort)
        return bool(self.url) and time.monotonic() >= self.gesperrt_bis and (
            self.art == "lokal" or hat_zugang
        )

    def sperren(self) -> None:
        self.gesperrt_bis = time.monotonic() + AUSFALL_SPERRE

    def freigeben(self) -> None:
        self.gesperrt_bis = 0.0


def kette_aus_umgebung() -> list[Anbieter]:
    """Baut die Anbieterkette aus Umgebungsvariablen."""
    return [
        Anbieter(
            name="lokal",
            art="lokal",
            protokoll="openai",
            url=os.getenv("LOKAL_URL", "http://litellm:4000/v1/chat/completions"),
            modell=os.getenv("LOKAL_MODELL", "qwen3-32b"),
            schluessel=os.getenv("LOKAL_KEY", ""),
            zeitlimit=float(os.getenv("LOKAL_ZEITLIMIT", "45")),
        ),
        Anbieter(
            name="hermes",
            art="cloud",
            protokoll="openai",
            url=os.getenv("HERMES_URL", "http://hermes:9119/api/chat"),
            modell=os.getenv("HERMES_MODELL", "default"),
            basic_auth_nutzer=os.getenv("HERMES_BENUTZER", ""),
            basic_auth_passwort=os.getenv("HERMES_PASSWORT", ""),
        ),
        # Drei zusaetzliche, direkt angebundene Cloud-Anbieter (nicht ueber
        # das lokale LiteLLM-Gateway geroutet) -- Ziel: mindestens einer
        # davon soll unabhaengig davon erreichbar sein, ob der Gateway-Prozess
        # auf dem Host gerade laeuft oder nicht. Jeder wird uebersprungen,
        # solange sein Schluessel in .env leer ist (gleiche Logik wie
        # Anthropic/OpenAI unten).
        Anbieter(
            name="openrouter",
            art="cloud",
            protokoll="openai",
            url="https://openrouter.ai/api/v1/chat/completions",
            modell=os.getenv("OPENROUTER_MODELL", "meta-llama/llama-3.3-70b-instruct"),
            schluessel=os.getenv("OPENROUTER_API_KEY", ""),
        ),
        Anbieter(
            name="cloudflare",
            art="cloud",
            protokoll="openai",
            # Gleiche WORKERS_AI_*-Variablennamen wie im Rest des AI-OS
            # (litellm_config.yaml, zentrale .env) -- nicht CLOUDFLARE_*, damit
            # ein einmal eingetragener Schluessel ueberall gilt.
            # Zwei Betriebsarten: mit WORKERS_AI_GATEWAY ueber das Cloudflare AI
            # Gateway (Caching/Analytics inklusive), sonst direkt gegen die
            # OpenAI-kompatible Workers-AI-Schnittstelle. Ohne ACCOUNT_ID bleibt
            # die URL leer -> Anbieter gilt als nicht einsatzbereit, kein Crash.
            url=(
                f"https://gateway.ai.cloudflare.com/v1/{os.getenv('WORKERS_AI_ACCOUNT_ID', '')}"
                f"/{os.getenv('WORKERS_AI_GATEWAY', '')}/workers-ai/v1/chat/completions"
                if os.getenv("WORKERS_AI_ACCOUNT_ID") and os.getenv("WORKERS_AI_GATEWAY")
                else (
                    f"https://api.cloudflare.com/client/v4/accounts/"
                    f"{os.getenv('WORKERS_AI_ACCOUNT_ID', '')}/ai/v1/chat/completions"
                    if os.getenv("WORKERS_AI_ACCOUNT_ID")
                    else ""
                )
            ),
            modell=os.getenv("CLOUDFLARE_MODELL", "@cf/meta/llama-3.1-8b-instruct-fast"),
            schluessel=os.getenv("WORKERS_AI_API_TOKEN", ""),
        ),
        Anbieter(
            name="huggingface",
            art="cloud",
            protokoll="openai",
            url="https://router.huggingface.co/v1/chat/completions",
            modell=os.getenv("HUGGINGFACE_MODELL", "meta-llama/Llama-3.3-70B-Instruct"),
            schluessel=os.getenv("HUGGINGFACE_API_KEY", ""),
        ),
        Anbieter(
            # Google AI Studio hat (Stand 01.08.2026) ein echtes Gratiskontingent
            # ohne Kauf/Kreditkarte -- deshalb hier vor den kostenpflichtigen
            # Cloud-Stufen einsortiert, direkt nach den anderen kostenlosen/
            # bereits vorhandenen Schluesseln.
            name="gemini",
            art="cloud",
            protokoll="openai",
            # Google bietet eine OpenAI-kompatible Schnittstelle fuer Gemini an,
            # dadurch kein eigener Protokoll-Zweig noetig.
            url="https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
            modell=os.getenv("GEMINI_MODELL", "gemini-2.5-flash"),
            schluessel=os.getenv("GEMINI_API_KEY", ""),
        ),
        Anbieter(
            # Groq: eigene, sehr schnelle Inferenz-Hardware (LPU), OpenAI-
            # kompatible Schnittstelle, Schluessel bereits in der Root-.env.
            name="groq",
            art="cloud",
            protokoll="openai",
            url="https://api.groq.com/openai/v1/chat/completions",
            modell=os.getenv("GROQ_MODELL", "llama-3.3-70b-versatile"),
            schluessel=os.getenv("GROQ_API_KEY", ""),
        ),
        Anbieter(
            name="cloud-anthropic",
            art="cloud",
            protokoll="anthropic",
            url="https://api.anthropic.com/v1/messages",
            modell=os.getenv("ANTHROPIC_MODELL", "claude-sonnet-4-6"),
            # In der zentralen Root-.env steht der Schluessel unter
            # "Claude_API_KEY" (abweichende Schreibweise) -- ANTHROPIC_API_KEY
            # bleibt als Fallback fuer den Fall, dass sich das noch angleicht.
            schluessel=os.getenv("Claude_API_KEY") or os.getenv("ANTHROPIC_API_KEY", ""),
        ),
        Anbieter(
            name="cloud-openai",
            art="cloud",
            protokoll="openai",
            url="https://api.openai.com/v1/chat/completions",
            modell=os.getenv("OPENAI_MODELL", "gpt-4.1"),
            schluessel=os.getenv("OPENAI_API_KEY", ""),
        ),
    ]


KETTE = kette_aus_umgebung()


@dataclass
class Ergebnis:
    text: str
    anbieter: str
    art: str
    modell: str
    versuche: list[str]


class KeinAnbieter(RuntimeError):
    """Kein Anbieter der Kette war erreichbar."""


# ---------------------------------------------------------------------------
# Anfrageformate der beiden Protokolle
# ---------------------------------------------------------------------------

def _openai_anfrage(a: Anbieter, systemprompt: str, verlauf: list[dict]) -> tuple[dict, dict]:
    kopf = {"Content-Type": "application/json"}
    if a.schluessel:
        kopf["Authorization"] = f"Bearer {a.schluessel}"
    last = {
        "model": a.modell,
        "temperature": 0.2,
        "max_tokens": 1600,
        "messages": [{"role": "system", "content": systemprompt}, *verlauf],
    }
    return last, kopf


def _anthropic_anfrage(a: Anbieter, systemprompt: str, verlauf: list[dict]) -> tuple[dict, dict]:
    kopf = {
        "Content-Type": "application/json",
        "x-api-key": a.schluessel,
        "anthropic-version": "2023-06-01",
    }
    last = {
        "model": a.modell,
        "max_tokens": 1600,
        "temperature": 0.2,
        "system": systemprompt,
        "messages": verlauf,
    }
    return last, kopf


def _auth(a: Anbieter) -> httpx.BasicAuth | None:
    """Basic-Auth fuer Anbieter wie Hermes, die keinen Bearer-/x-api-key-Header nutzen."""
    if a.basic_auth_passwort:
        return httpx.BasicAuth(a.basic_auth_nutzer, a.basic_auth_passwort)
    return None


def _text_aus_antwort(protokoll: str, daten: dict) -> str:
    if protokoll == "anthropic":
        blocks = daten.get("content", [])
        return "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
    return daten["choices"][0]["message"]["content"].strip()


# ---------------------------------------------------------------------------
# Aufruf mit Fallback
# ---------------------------------------------------------------------------

# Cloudflare Workers AI bietet mit DEMSELBEN Zugang deutlich staerkere Modelle als das
# 8B-Standardmodell. Das 8B-Modell erfand bei Code-Aufgaben nicht existierende Cmdlets
# (New-MgGraphClient, Set-MgUserMailbox); Coder-32B und Llama-70B lieferten im Test
# korrekte Exchange-Befehle in < 2 s. Faellt das Wunschmodell aus (z. B. Tageskontingent),
# wird im selben Durchlauf das konfigurierte Basismodell versucht.
CLOUDFLARE_STARK = os.getenv("CLOUDFLARE_STARK_MODELL", "@cf/meta/llama-3.3-70b-instruct-fp8-fast")
CLOUDFLARE_CODE = os.getenv("CLOUDFLARE_CODE_MODELL", "@cf/qwen/qwen2.5-coder-32b-instruct")


async def frage(systemprompt: str, verlauf: list[dict], code: bool = False) -> Ergebnis:
    """Fragt die Kette durch und gibt die erste brauchbare Antwort zurueck.
    code=True: bei Cloudflare zuerst das Coder-Modell (Generator-/Skript-Module)."""
    versuche: list[str] = []
    letzter_fehler: Exception | None = None

    for a in KETTE:
        if not a.einsatzbereit:
            versuche.append(f"{a.name}: uebersprungen")
            continue

        bauer = _anthropic_anfrage if a.protokoll == "anthropic" else _openai_anfrage
        modelle = [a.modell]
        if a.name == "cloudflare":
            wunsch = CLOUDFLARE_CODE if code else CLOUDFLARE_STARK
            modelle = [m for m in (wunsch, a.modell) if m] if wunsch != a.modell else [a.modell]

        for modell in modelle:
            last, kopf = bauer(a, systemprompt, verlauf)
            last["model"] = modell
            try:
                async with httpx.AsyncClient(timeout=a.zeitlimit) as client:
                    antwort = await client.post(a.url, json=last, headers=kopf, auth=_auth(a))
                    antwort.raise_for_status()
                    text = _text_aus_antwort(a.protokoll, antwort.json())
                if not text:
                    raise ValueError("leere Antwort")
                a.freigeben()
                versuche.append(f"{a.name}: ok")
                return Ergebnis(text, a.name, a.art, modell, versuche)

            except (httpx.HTTPError, KeyError, IndexError, ValueError) as fehler:
                letzter_fehler = fehler
                versuche.append(f"{a.name}/{modell.split('/')[-1]}: {type(fehler).__name__}")
        a.sperren()

    raise KeinAnbieter(
        "Kein Anbieter erreichbar. Versuche: " + "; ".join(versuche)
    ) from letzter_fehler


async def einbetten(texte: list[str]) -> list[list[float]]:
    """Vektoren fuer RAG. Lokal zuerst (falls konfiguriert), danach Cloud.
    Kurzes Zeitlimit pro Quelle (10s) -- ein unerreichbarer erster Eintrag
    darf eine RAG-Anfrage nicht mehr um bis zu 60s verzoegern (siehe
    Multi-Cloud-LLM-Fallback: gleiche Falle wie bei "lokal" im Chat)."""
    quellen = [
        (
            os.getenv("EINBETTUNG_URL", ""),
            os.getenv("EINBETTUNG_MODELL", "nomic-embed-text"),
            os.getenv("LOKAL_KEY", ""),
        ),
        (
            # Cloudflare Workers AI -- gleiche Zugangsdaten wie der Chat-Anbieter
            # "cloudflare", 768-dimensionales Modell passend zu VEKTORGROESSE.
            f"https://api.cloudflare.com/client/v4/accounts/"
            f"{os.getenv('WORKERS_AI_ACCOUNT_ID', '')}/ai/v1/embeddings"
            if os.getenv("WORKERS_AI_ACCOUNT_ID") else "",
            "@cf/baai/bge-base-en-v1.5",
            os.getenv("WORKERS_AI_API_TOKEN", ""),
        ),
        (
            "https://api.openai.com/v1/embeddings",
            "text-embedding-3-small",
            os.getenv("OPENAI_API_KEY", ""),
        ),
    ]
    for url, modell, schluessel in quellen:
        if not url or (url.startswith("https://api.") and not schluessel):
            continue
        kopf = {"Content-Type": "application/json"}
        if schluessel:
            kopf["Authorization"] = f"Bearer {schluessel}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                antwort = await client.post(
                    url, json={"model": modell, "input": texte}, headers=kopf
                )
                antwort.raise_for_status()
                daten = antwort.json()["data"]
            return [eintrag["embedding"] for eintrag in daten]
        except (httpx.HTTPError, KeyError):
            continue
    raise KeinAnbieter("Kein Einbettungsdienst erreichbar.")


async def zustand() -> list[dict]:
    """Kurzer Erreichbarkeitstest fuer die Anzeige im Frontend."""

    async def pruefen(a: Anbieter) -> dict:
        if not a.einsatzbereit:
            ohne_zugang = a.art == "cloud" and not (a.schluessel or a.basic_auth_passwort)
            grund = "kein Zugang" if ohne_zugang else "gesperrt"
            return {"name": a.name, "art": a.art, "modell": a.modell, "zustand": grund}
        try:
            last, kopf = (
                _anthropic_anfrage if a.protokoll == "anthropic" else _openai_anfrage
            )(a, "Antworte mit: ok", [{"role": "user", "content": "ok"}])
            last["max_tokens"] = 5
            async with httpx.AsyncClient(timeout=10) as client:
                antwort = await client.post(a.url, json=last, headers=kopf, auth=_auth(a))
                antwort.raise_for_status()
            return {"name": a.name, "art": a.art, "modell": a.modell, "zustand": "bereit"}
        except httpx.HTTPError:
            return {"name": a.name, "art": a.art, "modell": a.modell, "zustand": "gestoert"}

    return list(await asyncio.gather(*(pruefen(a) for a in KETTE)))
