"""Tagesimpuls zusammenstellen: Sprichwort, Wortwahl-Tausch, EQ-Übung, Affirmation, Witz (DE + VI).

Rotation ist zustandslos: Jede Liste wird pro Jahr mit festem Seed gemischt, der Tag des Jahres
wählt den Eintrag. So gibt es keine Wiederholung, bis eine Liste einmal durchlaufen ist, und
der Pi braucht keine Datenbank.
"""
from __future__ import annotations

import json
import random
from datetime import date
from pathlib import Path

KATEGORIEN = ("sprichwort", "wortwahl", "eq_uebung", "affirmation", "witz")


def lade_inhalte(pfad: Path) -> dict[str, list[dict]]:
    daten = json.loads(pfad.read_text(encoding="utf-8"))
    return {k: daten[k] for k in KATEGORIEN}


def eintrag_fuer_tag(liste: list[dict], tag: date, kategorie: str) -> dict:
    reihenfolge = list(range(len(liste)))
    random.Random(f"{tag.year}-{kategorie}").shuffle(reihenfolge)
    return liste[reihenfolge[(tag.timetuple().tm_yday - 1) % len(liste)]]


def impuls(inhalte: dict[str, list[dict]], tag: date) -> dict[str, dict]:
    return {k: eintrag_fuer_tag(inhalte[k], tag, k) for k in KATEGORIEN}


def als_text(imp: dict[str, dict]) -> str:
    s, w, q, a, j = (imp[k] for k in KATEGORIEN)
    return "\n".join([
        "💬 Sprichwort",
        f"   🇩🇪 {s['de']}",
        f"   🇻🇳 {s['vi']}",
        f"   → {s['sinn']}",
        "",
        "🔁 Wortwahl des Tages",
        f"   statt: „{w['statt_de']}“",
        f"   besser: „{w['besser_de']}“",
        f"   🇻🇳 „{w['statt_vi']}“ → „{w['besser_vi']}“",
        f"   Warum: {w['warum']}",
        "",
        "❤️ EQ-Übung",
        f"   🇩🇪 {q['de']}",
        f"   🇻🇳 {q['vi']}",
        "",
        f"✨ {a['de']}",
        f"   {a['vi']}",
        "",
        "😄 Witz",
        f"   🇩🇪 {j['de']}",
        f"   🇻🇳 {j['vi']}",
    ])
