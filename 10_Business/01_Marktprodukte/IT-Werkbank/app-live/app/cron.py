"""
Taeglicher Cronjob der IT-Werkbank.

Laeuft im selben Prozess wie die API (APScheduler, kein eigener Dienst noetig).
Vier Aufgaben pro Lauf:
  1. Wissen aktuell halten: Themenliste aus SCRAPER_THEMEN (.env) oder
     automatisch aus den Modul-Stichworten abgeleitet.
  2. Vom CEO eingetragene eigene Quellen mit aktualisieren.
  3. Tech-News: RSS-Quellen (app/rss.py) auf neue Eintraege pruefen.
  4. Aufbewahrungsfrist: Chatsitzungen aelter als SITZUNG_AUFBEWAHRUNG_TAGE
     (Standard 7 Tage) loeschen.
"""

from __future__ import annotations

import logging
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from . import module_katalog, rss, scraper, store

log = logging.getLogger("werkbank.cron")

_scheduler: AsyncIOScheduler | None = None


def themen() -> list[tuple[str, str]]:
    """Liste aus (thema, modul). Manuell ueber SCRAPER_THEMEN ueberschreibbar."""
    eigene = os.getenv("SCRAPER_THEMEN", "").strip()
    if eigene:
        return [(t.strip(), "assistent") for t in eigene.split(",") if t.strip()]
    return [
        (f"{m.name} aktuelle Best Practices und Sicherheitshinweise 2026", m.id)
        for m in module_katalog.MODULE
        if m.id != "assistent"
    ]


async def _taeglicher_lauf() -> None:
    for thema, modul in themen():
        ergebnis = await scraper.thema_aktualisieren(thema, modul)
        log.info("Cron-Lauf (Thema) %s: %s", thema, ergebnis.get("status"))

    # Vom CEO selbst eingetragene Quellen taeglich mit aktualisieren
    for quelle in await store.quellen_liste():
        ergebnis = await scraper.quelle_aktualisieren(quelle["url"], quelle["titel"], quelle["modul"])
        log.info("Cron-Lauf (Quelle) %s: %s", quelle["url"], ergebnis.get("status"))

    # Tech-News: RSS-Quellen auf neue Eintraege pruefen
    rss_ergebnis = await rss.rss_pruefen()
    log.info("Cron-Lauf (Tech-News RSS): %s", rss_ergebnis)

    # Aufbewahrungsfrist: Chatsitzungen aelter als 1 Woche entfernen
    tage = int(os.getenv("SITZUNG_AUFBEWAHRUNG_TAGE", "7"))
    geloescht = await store.alte_sitzungen_loeschen(tage)
    log.info("Aufbewahrungsfrist: %d Sitzung(en) aelter als %d Tage geloescht", geloescht, tage)


def starten() -> None:
    global _scheduler
    zeit = os.getenv("SCRAPER_CRON_ZEIT", "05:30")
    stunde, minute = zeit.split(":")
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        _taeglicher_lauf,
        CronTrigger(hour=int(stunde), minute=int(minute)),
        id="werkbank-taeglich",
        replace_existing=True,
    )
    _scheduler.start()
    log.info("Wissens-Cronjob gestartet, taeglich um %s Uhr", zeit)


def stoppen() -> None:
    if _scheduler:
        _scheduler.shutdown(wait=False)
