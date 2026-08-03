"""
Web-Scraper-Agent der IT-Werkbank.

Haelt das Wissen aktuell: sucht ueber die im AI-OS bereits laufende SearXNG-Instanz
(keine zusaetzlichen Kosten/Schluessel), laedt die besten Treffer, extrahiert den
Haupttext (trafilatura), fasst ueber die bestehende LLM-Kette zusammen und schreibt
das Ergebnis als Wiki-Seite. Ein Thema hat einen stabilen Slug -- ein taeglicher
Lauf aktualisiert dieselbe Seite, statt Duplikate anzuhaeufen.
"""

from __future__ import annotations

import asyncio
import contextlib
import os
import re

import httpx
import trafilatura
from youtube_transcript_api import YouTubeTranscriptApi

from . import llm, rag, store

SEARX_URL = os.getenv("SEARX_URL", "http://searxng:8080")
MAX_TREFFER = 5
MAX_SEITENGROESSE = 400_000  # Bytes, verhindert riesige Downloads

# Microsoft Learn ist die Nachfolgeplattform der frueheren MSDN-/TechNet-Doku
# (MSDN-Inhalte wurden inzwischen groesstenteils nach learn.microsoft.com
# umgezogen) -- fuer die stark Microsoft-lastigen Fachmodule (M365, Entra ID,
# Windows Server, Hyper-V, PowerShell, MDM/Intune) die verlaesslichste Quelle.
MICROSOFT_SEITEN = ("learn.microsoft.com", "msdn.microsoft.com")

# Themen mit diesen Stichworten werden bei Erstanlage als "neu" markiert --
# blinkendes Abzeichen am Modul im Frontend, statt im Wiki zu verschwinden.
# Bewusst breit gefasst (Sicherheit allgemein, nicht nur Windows), da der
# Scraper Themen aus allen Modulen zieht (IT Sicherheit, KI Sicherheit,
# Server Haertung, ...). Ueber WICHTIGE_SCHLUESSELWOERTER in der .env
# ueberschreibbar.
STANDARD_WICHTIGE_SCHLUESSELWOERTER = (
    "sicherheit", "security", "härtung", "haertung", "hardening",
    "schwachstelle", "vulnerability", "cve", "exploit", "ransomware",
    "phishing", "zero trust", "zero-trust", "iam", "angriff", "patch",
)


def _ist_wichtig(thema: str) -> bool:
    eigene = os.getenv("WICHTIGE_SCHLUESSELWOERTER", "").strip()
    woerter = tuple(w.strip() for w in eigene.split(",") if w.strip()) if eigene else STANDARD_WICHTIGE_SCHLUESSELWOERTER
    tief = thema.lower()
    return any(w in tief for w in woerter)


def _slug(text: str) -> str:
    ersatz = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    for alt, neu in ersatz.items():
        text = text.lower().replace(alt, neu)
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80] or "thema"


async def _suchen_roh(query: str, max_treffer: int) -> list[dict]:
    async with httpx.AsyncClient(timeout=20) as client:
        antwort = await client.get(
            f"{SEARX_URL}/search",
            params={"q": query, "format": "json", "language": "de"},
        )
        antwort.raise_for_status()
        daten = antwort.json()
    return [
        {"titel": r.get("title", ""), "url": r.get("url", ""), "kurz": r.get("content", "")}
        for r in daten.get("results", [])[:max_treffer]
        if r.get("url")
    ]


async def suchen(thema: str, max_treffer: int = MAX_TREFFER) -> list[dict]:
    """Fragt SearXNG ab, gibt Titel/URL/Kurzbeschreibung zurueck."""
    return await _suchen_roh(thema, max_treffer)


async def suchen_microsoft(thema: str, max_treffer: int = 3) -> list[dict]:
    """Sucht gezielt auf Microsoft Learn/MSDN -- die offizielle Quelle fuer die
    Microsoft-Fachmodule. Laeuft zusaetzlich zur allgemeinen Suche, nicht
    anstelle davon (bei Nicht-Microsoft-Themen liefert sie einfach wenig)."""
    filter_ = " OR ".join(f"site:{s}" for s in MICROSOFT_SEITEN)
    return await _suchen_roh(f"{thema} ({filter_})", max_treffer)


async def _seite_holen(url: str) -> str:
    """Laedt eine Seite als Rohtext (HTML). Leerer String bei Fehler/zu gross."""
    async with httpx.AsyncClient(
        timeout=15, follow_redirects=True, headers={"User-Agent": "IT-Werkbank/1.0"}
    ) as client:
        antwort = await client.get(url)
        antwort.raise_for_status()
        if len(antwort.content) > MAX_SEITENGROESSE:
            return ""
        return antwort.text


async def _reddit_text(url: str) -> str:
    """Reddit rendert Beitraege per JavaScript -- eine normale HTML-Anfrage
    liefert keinen Text. Die offizielle .json-Variante ist oeffentlich, ohne
    Login abrufbar und liefert Titel, Text und Kommentare strukturiert."""
    json_url = url.split("?")[0].rstrip("/") + ".json"
    async with httpx.AsyncClient(
        timeout=15, headers={"User-Agent": "IT-Werkbank/1.0 (Wissens-Scraper, nicht kommerziell)"}
    ) as client:
        antwort = await client.get(json_url)
        antwort.raise_for_status()
        daten = antwort.json()

    beitrag = daten[0]["data"]["children"][0]["data"]
    teile = [f"# {beitrag.get('title', '')}", beitrag.get("selftext", "")]
    kommentare = sorted(
        (k["data"] for k in daten[1]["data"]["children"] if k.get("kind") == "t1"),
        key=lambda k: k.get("score", 0),
        reverse=True,
    )
    for k in kommentare[:8]:
        text = k.get("body", "")
        if text and text != "[deleted]":
            teile.append(f"> {text[:600]}")
    return "\n\n".join(t for t in teile if t).strip()


def _youtube_video_id(url: str) -> str | None:
    treffer = re.search(r"(?:youtu\.be/|[?&]v=|/embed/|/shorts/)([A-Za-z0-9_-]{11})", url)
    return treffer.group(1) if treffer else None


def _youtube_text(url: str) -> str:
    """YouTube-Seiten sind JavaScript-gerendert -- trafilatura findet dort
    keinen Text. Untertitel/Transkript (automatisch oder manuell) lassen sich
    aber direkt als Text abrufen, ohne das Video herunterzuladen/anzusehen.
    Deutsch zuerst, Englisch als Fallback; ganz ohne Untertitel -> leer."""
    video_id = _youtube_video_id(url)
    if not video_id:
        return ""
    try:
        eintraege = YouTubeTranscriptApi.get_transcript(video_id, languages=["de", "de-DE", "en", "en-US"])
    except Exception:
        return ""
    return " ".join(e.get("text", "") for e in eintraege).strip()


async def _text_extrahieren(url: str) -> tuple[str, str]:
    """Zentrale Extraktionslogik, von seite_laden() UND quelle_aktualisieren()
    genutzt -- Sonderfaelle (Reddit, YouTube) an einer Stelle gepflegt statt
    doppelt. Gibt (Text, Titel-Rohdaten fuer Fallback) zurueck."""
    if "reddit.com" in url:
        return (await _reddit_text(url), "")
    if "youtube.com" in url or "youtu.be" in url:
        # Blockierender Aufruf der Bibliothek in einen Thread auslagern, damit
        # der Event-Loop waehrenddessen nicht blockiert.
        text = await asyncio.to_thread(_youtube_text, url)
        return (text, "")
    html = await _seite_holen(url)
    text = trafilatura.extract(html, include_comments=False, include_tables=False) if html else ""
    return ((text or "").strip(), html)


async def seite_laden(url: str) -> str:
    """Laedt eine Seite und extrahiert den Haupttext. Leerer String bei Fehler."""
    try:
        text, _ = await _text_extrahieren(url)
        return text
    except (httpx.HTTPError, Exception):
        return ""


def _titel_aus_html(html: str, ersatz: str) -> str:
    treffer = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return re.sub(r"\s+", " ", treffer.group(1)).strip()[:150] if treffer else ersatz


ZUSAMMENFASSUNGS_PROMPT = """Du fasst Web-Rechercheergebnisse fuer die Wissensdatenbank eines
IT-Systemadministrators zusammen. Schreibe eine kompakte, sachliche Wiki-Seite auf Deutsch:
- Nur belegte Fakten aus den gelieferten Quellenausschnitten, keine Erfindungen.
- Konkrete Versionen, Befehle, Einstellungen nennen, wo vorhanden.
- Quellen von learn.microsoft.com/msdn.microsoft.com sind die offizielle
  Microsoft-Dokumentation -- bei Widerspruch zu anderen Quellen ihnen folgen
  und das kurz vermerken.
- Am Ende ein Abschnitt "Quellen" mit den genutzten URLs.
- Wenn die Quellen widerspruechlich sind, das benennen statt zu glaetten."""


async def _zusammenfassen_und_speichern(
    slug: str, titel: str, modul: str, quellen_texte: list[str], genutzte_urls: list[str]
) -> str:
    kontext = "\n\n".join(quellen_texte)[:12000]
    verlauf = [{"role": "user", "content": f"Thema: {titel}\n\nQuellenausschnitte:\n\n{kontext}"}]
    ergebnis = await llm.frage(ZUSAMMENFASSUNGS_PROMPT, verlauf)

    inhalt = ergebnis.text
    if "Quellen" not in inhalt:
        inhalt += "\n\n## Quellen\n" + "\n".join(f"- {u}" for u in genutzte_urls)

    await store.wiki_schreiben(slug, titel, modul, inhalt, wichtig=_ist_wichtig(titel))
    with contextlib.suppress(Exception):
        # Vektor-Indexierung ist Komfort (schnelleres Wiederfinden) -- die
        # Wiki-Seite selbst ist auch ohne funktionierendes Embedding-Modell
        # gespeichert und im Wiki-Tab sichtbar.
        await rag.wiki_speichern(slug, titel, modul, inhalt)
    return inhalt


async def quelle_aktualisieren(url: str, titel: str = "", modul: str = "assistent") -> dict:
    """Laedt eine vom CEO selbst eingetragene Quelle direkt (keine Suche noetig,
    die URL ist schon bekannt gut), fasst sie zusammen und speichert sie als
    Wiki-Seite. Der taegliche Cronjob ruft das fuer jede eingetragene Quelle auf,
    damit auch handverlesene Links aktuell gehalten werden.

    Slug bewusst NUR aus der URL gebildet, nie aus dem Titel: der Titel ist beim
    allerersten Aufruf noch leer (dann erst nach dem Laden bekannt) und wuerde bei
    einem zweiten Aufruf (z.B. durch den Cronjob) einen ANDEREN Slug ergeben als
    beim ersten Mal -- das hat frueher echte Duplikate erzeugt (zwei Wiki-Seiten
    fuer dieselbe Quelle, einmal URL-Slug, einmal Titel-Slug, mit doppelt
    eingebetteten Chunks in Qdrant). Die URL ist ohnehin der Primaerschluessel der
    quellen-Tabelle (store.quelle_hinzufuegen), also bereits stabil und eindeutig."""
    slug = f"quelle-{_slug(url)}"
    try:
        text, html = await _text_extrahieren(url)
        if not text:
            await store.scraper_lauf_eintragen(titel or url, modul, slug, "keine_quellen")
            return {"thema": titel or url, "slug": slug, "status": "keine_quellen"}

        endgueltiger_titel = titel or (_titel_aus_html(html, url) if html else url)
        quellen_texte = [f"### {endgueltiger_titel} ({url})\n{text[:6000]}"]
        await _zusammenfassen_und_speichern(slug, endgueltiger_titel, modul, quellen_texte, [url])
        await store.scraper_lauf_eintragen(endgueltiger_titel, modul, slug, "ok")
        return {"thema": endgueltiger_titel, "slug": slug, "status": "ok", "quellen": [url]}

    except (httpx.HTTPError, llm.KeinAnbieter, Exception) as fehler:
        await store.scraper_lauf_eintragen(titel or url, modul, slug, f"fehler: {type(fehler).__name__}")
        return {"thema": titel or url, "slug": slug, "status": "fehler", "grund": str(fehler)}


async def thema_aktualisieren(thema: str, modul: str = "assistent", mit_microsoft: bool = True) -> dict:
    """Kompletter Lauf: suchen -> laden -> zusammenfassen -> als Wiki-Seite speichern.
    mit_microsoft=False fuer Praxis-/Community-Themen (Reddit, Fachpresse) -- dann
    gehen alle Suchplaetze in die allgemeine Suche statt geteilt mit Microsoft Learn."""
    slug = f"web-{_slug(thema)}"
    try:
        ms_treffer = await suchen_microsoft(thema) if mit_microsoft else []
        allgemein = await suchen(thema, max_treffer=MAX_TREFFER - len(ms_treffer))
        gesehen = {t["url"] for t in ms_treffer}
        treffer = ms_treffer + [t for t in allgemein if t["url"] not in gesehen]
        quellen_texte = []
        genutzte_urls = []
        for t in treffer:
            text = await seite_laden(t["url"])
            if text:
                quellen_texte.append(f"### {t['titel']} ({t['url']})\n{text[:3000]}")
                genutzte_urls.append(t["url"])

        if not quellen_texte:
            await store.scraper_lauf_eintragen(thema, modul, slug, "keine_quellen")
            return {"thema": thema, "slug": slug, "status": "keine_quellen"}

        await _zusammenfassen_und_speichern(slug, thema, modul, quellen_texte, genutzte_urls)
        await store.scraper_lauf_eintragen(thema, modul, slug, "ok")
        return {"thema": thema, "slug": slug, "status": "ok", "quellen": genutzte_urls}

    except (httpx.HTTPError, llm.KeinAnbieter, Exception) as fehler:
        await store.scraper_lauf_eintragen(thema, modul, slug, f"fehler: {type(fehler).__name__}")
        return {"thema": thema, "slug": slug, "status": "fehler", "grund": str(fehler)}
