"""Kalender-Wecker: läuft jede Minute, schickt fällige Erinnerungen als Push (mit Ton/Alarm).

Google selbst kann nur stille Pop-ups oder E-Mails. Der Pi ergänzt:
- jede Erinnerung als ntfy-Push mit Ton (Priorität 4),
- Termine mit ⏰/„Wecker“/„Alarm“ im Titel oder Farbe Tomate als WECKER (Priorität 5 + Ton am Pi).
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta

from . import benachrichtigung, kalender
from .config import Config

NACHHOL_FENSTER = timedelta(minutes=5)  # Pi kurz aus / Timer verspätet → trotzdem senden


def faellige(evs: list[dict], cfg: Config, jetzt: datetime, gesendet: set[str]) -> list[tuple[dict, int, str]]:
    out = []
    for ev in evs:
        st = kalender.start_zeit(ev, cfg)
        if st is None:
            continue
        for minuten in kalender.erinnerungs_minuten(ev, cfg):
            ausloeser = st - timedelta(minutes=minuten)
            schluessel = f"{ev.get('id')}|{st.isoformat()}|{minuten}"
            if ausloeser <= jetzt < ausloeser + NACHHOL_FENSTER and schluessel not in gesendet:
                out.append((ev, minuten, schluessel))
    return out


def _lade_zustand(cfg: Config) -> dict[str, str]:
    try:
        return json.loads(cfg.zustand_datei.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _speichere_zustand(cfg: Config, zustand: dict[str, str], jetzt: datetime) -> None:
    grenze = (jetzt - timedelta(days=3)).isoformat()
    zustand = {k: v for k, v in zustand.items() if v >= grenze}
    cfg.zustand_datei.parent.mkdir(parents=True, exist_ok=True)
    cfg.zustand_datei.write_text(json.dumps(zustand, indent=1), encoding="utf-8")


def lauf(cfg: Config, jetzt: datetime | None = None, trocken: bool = False, evs: list[dict] | None = None) -> int:
    jetzt = jetzt or datetime.now(cfg.zeitzone)
    if evs is None:
        vorlauf = max(cfg.wecker_standard_min + [24 * 60]) + 5
        evs = kalender.termine(cfg, jetzt - timedelta(minutes=10), jetzt + timedelta(minutes=vorlauf))
    zustand = _lade_zustand(cfg)
    treffer = faellige(evs, cfg, jetzt, set(zustand))
    for ev, minuten, schluessel in treffer:
        st = kalender.start_zeit(ev, cfg)
        alarm = kalender.ist_alarm(ev, cfg)
        wann = "JETZT" if minuten == 0 else f"in {minuten} min" if minuten < 120 else f"am {st:%d.%m. um %H:%M}"
        text = f"{st:%H:%M} Uhr – {ev.get('summary', '(ohne Titel)')}"
        if ev.get("location"):
            text += f"\n📍 {ev['location']}"
        benachrichtigung.nachricht(
            cfg, f"{'⏰ WECKER' if alarm else '🔔 Termin'} {wann}", text,
            prioritaet=5 if alarm else 4, tags=["alarm_clock" if alarm else "calendar"],
            klick=ev.get("htmlLink", ""), trocken=trocken)
        if alarm:
            benachrichtigung.ton(cfg, trocken=trocken)
        zustand[schluessel] = jetzt.isoformat()
    if not trocken:
        _speichere_zustand(cfg, zustand, jetzt)
    return len(treffer)
