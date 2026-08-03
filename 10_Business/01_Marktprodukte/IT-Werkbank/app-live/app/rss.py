"""
RSS-Check fuer den Tech-News-Tab.

Prueft eine kleine, bewusst kurz gehaltene Liste von Quellen mit bekanntem,
stabilem RSS/Atom-Feed (nicht alle der im Frontend verlinkten Seiten bieten
einen Feed -- lieber wenige echte Feeds als viele geratene, die staendig
403/404 liefern). Neue Eintraege werden in store.rss_eintrag_speichern
dedupliziert (UNIQUE auf url) und im Tech-News-Tab als "NEU" angezeigt.

Faellt eine einzelne Quelle aus (Netzwerkfehler, Feed umgezogen, falsches
Format), wird nur diese uebersprungen -- der Lauf fuer alle anderen Quellen
laeuft trotzdem weiter, gleiche Fehlertoleranz wie scraper.py.
"""

from __future__ import annotations

import logging
from xml.etree import ElementTree as ET

import httpx

from . import store

log = logging.getLogger("werkbank.rss")

# Nur Quellen mit einem tatsaechlich bekannten, stabilen Feed -- die
# uebrigen im Tech-News-Tab verlinkten Seiten bleiben reine Klick-Links ohne
# automatische Pruefung, bis ihr Feed geprueft/ergaenzt ist.
RSS_QUELLEN: list[dict] = [
    {"thema": "IT-Architektur (Bundescloud & Cloud)", "titel": "CNCF Blog",
     "feed_url": "https://www.cncf.io/feed/"},
    {"thema": "IT-Architektur (Bundescloud & Cloud)", "titel": "Azure Updates",
     "feed_url": "https://azurecomcdn.azureedge.net/en-us/updates/feed/"},
    {"thema": "IT-Architektur (Bundescloud & Cloud)", "titel": "AWS – Was ist neu",
     "feed_url": "https://aws.amazon.com/about-aws/whats-new/recent/feed/"},
    {"thema": "Security", "titel": "heise Security",
     "feed_url": "https://www.heise.de/security/rss/news-atom.xml"},
    {"thema": "KI", "titel": "Hugging Face Blog",
     "feed_url": "https://huggingface.co/blog/feed.xml"},
    {"thema": "Automatisierung (n8n, Dify, etc.)", "titel": "n8n Blog",
     "feed_url": "https://blog.n8n.io/rss/"},
]

_NS_ATOM = "{http://www.w3.org/2005/Atom}"
_JE_QUELLE_MAX = 5


def _feed_parsen(inhalt: bytes) -> list[dict]:
    wurzel = ET.fromstring(inhalt)
    eintraege: list[dict] = []

    # RSS 2.0: <rss><channel><item>...
    for item in wurzel.findall("./channel/item")[:_JE_QUELLE_MAX]:
        titel = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        datum = (item.findtext("pubDate") or "").strip()
        if titel and link:
            eintraege.append({"titel": titel, "url": link, "veroeffentlicht": datum})

    # Atom: <feed><entry><link href="..."/>...
    if not eintraege:
        for entry in wurzel.findall(f"./{_NS_ATOM}entry")[:_JE_QUELLE_MAX]:
            titel = (entry.findtext(f"{_NS_ATOM}title") or "").strip()
            link_el = entry.find(f"{_NS_ATOM}link")
            link = link_el.get("href", "").strip() if link_el is not None else ""
            datum = (entry.findtext(f"{_NS_ATOM}updated")
                     or entry.findtext(f"{_NS_ATOM}published") or "").strip()
            if titel and link:
                eintraege.append({"titel": titel, "url": link, "veroeffentlicht": datum})

    return eintraege


async def _quelle_pruefen(quelle: dict) -> int:
    """Gibt die Anzahl neu gespeicherter Eintraege zurueck."""
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        antwort = await client.get(
            quelle["feed_url"], headers={"User-Agent": "IT-Werkbank/1.0 (Tech-News-Check)"}
        )
        antwort.raise_for_status()
        eintraege = _feed_parsen(antwort.content)

    neu = 0
    for e in eintraege:
        gespeichert = await store.rss_eintrag_speichern(
            thema=quelle["thema"],
            quelle_titel=quelle["titel"],
            titel=e["titel"],
            url=e["url"],
            veroeffentlicht=e["veroeffentlicht"],
        )
        if gespeichert:
            neu += 1
    return neu


async def rss_pruefen() -> dict:
    """Prueft alle RSS_QUELLEN, ueberspringt einzelne Ausfaelle."""
    gesamt_neu = 0
    fehlgeschlagen: list[str] = []
    for quelle in RSS_QUELLEN:
        try:
            gesamt_neu += await _quelle_pruefen(quelle)
        except Exception as fehler:  # noqa: BLE001 -- bewusst breit, einzelne Quelle darf nicht den Lauf stoppen
            fehlgeschlagen.append(quelle["titel"])
            log.warning("RSS-Quelle fehlgeschlagen (%s): %s", quelle["titel"], fehler)
    log.info("RSS-Check: %d neue Eintraege, %d/%d Quellen fehlgeschlagen",
              gesamt_neu, len(fehlgeschlagen), len(RSS_QUELLEN))
    return {"neu": gesamt_neu, "geprueft": len(RSS_QUELLEN), "fehlgeschlagen": fehlgeschlagen}
