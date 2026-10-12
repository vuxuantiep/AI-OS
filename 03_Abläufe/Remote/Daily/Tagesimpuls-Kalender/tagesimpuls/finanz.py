"""Finanz- und Steuer-Erinnerungen am 01.06. und 01.12. (Push mit Links + Kalendertermine + .ics)."""
from __future__ import annotations

from datetime import date, datetime, timezone

from .config import Config

CHECKLISTE = {
    "juni": {
        "titel": "🧾 Steuererklärung & Finanz-Halbjahres-Check",
        "text": [
            "Steuererklärung fürs Vorjahr – Frist ohne Steuerberater: 31.07. (aktuelle Frist auf elster.de prüfen)",
            "1. WISO öffnen, Vorjahresdaten übernehmen, Belegabruf starten",
            "2. Werbungskosten: Fahrten, Arbeitsmittel, Fortbildung, Homeoffice, Bewerbungskosten",
            "3. Sonderausgaben: Altersvorsorge, Spenden, Versicherungen",
            "4. Haushaltsnahe Dienste / Handwerker (Rechnung + Überweisung)",
            "5. Vermietung? Anlage V mit Belegen",
            "6. Über ELSTER abgeben – Bescheid später gegen Erklärung prüfen",
            "7. Finanzplan: Halbjahres-Soll/Ist, Sparquote, Notgroschen, Ziele anpassen",
        ],
    },
    "dezember": {
        "titel": "💶 Finanz-Check & Steuer: Jahresende vorbereiten",
        "text": [
            "Was bis 31.12. noch zählt:",
            "1. Finanzplan: Soll/Ist des Jahres, Plan fürs nächste Jahr anlegen",
            "2. Belege des Jahres sammeln (Arbeitsmittel, Fortbildung, Fahrten, Spenden, Handwerker)",
            "3. Geplante berufliche Ausgaben ggf. noch vor 31.12. tätigen",
            "4. Spenden und Altersvorsorge-Einzahlungen vor Jahresende",
            "5. Freistellungsauftrag bei den Banken prüfen",
            "6. Jobwechsel im Jahr? Bewerbungs-/Fahrt-/Umzugskosten notieren",
            "7. Notgroschen und Sparquote prüfen",
        ],
    },
}


def art_fuer_tag(tag: date) -> str | None:
    return {(6, 1): "juni", (12, 1): "dezember"}.get((tag.month, tag.day))


def links(cfg: Config) -> list[tuple[str, str]]:
    return [("WISO öffnen", cfg.wiso_url), ("Finanzplan bearbeiten", cfg.finanzplan_url), ("ELSTER", cfg.elster_url)]


def termin_definitionen(cfg: Config, heute: date) -> list[dict]:
    def naechster(monat: int) -> date:
        d = date(heute.year, monat, 1)
        return d if d >= heute else date(heute.year + 1, monat, 1)

    defs = []
    for art, monat in (("juni", 6), ("dezember", 12)):
        c = CHECKLISTE[art]
        html = "<br>".join(c["text"]) + "<br><br>" + "<br>".join(
            f'<a href="{u}">{l}</a>' for l, u in links(cfg))
        defs.append({"kennung": f"finanz-{art}", "titel": c["titel"], "erster_termin": naechster(monat),
                     "beschreibung_html": html, "text": "\\n".join(c["text"])})
    return defs


def _esc(t: str) -> str:
    return t.replace(",", r"\,").replace(";", r"\;")


def ics(cfg: Config, heute: date) -> str:
    """iCalendar-Datei zum Sofort-Import (Google übernimmt beim Import keine Alarme, sondern die
    Standard-Benachrichtigungen des Kalenders; Apple/Outlook übernehmen die VALARMs)."""
    stempel = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    zeilen = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//AI-OS//Tagesimpuls//DE", "CALSCALE:GREGORIAN"]
    for d in termin_definitionen(cfg, heute):
        start = d["erster_termin"]
        linktext = "\\n".join(f"{l}: {u}" for l, u in links(cfg))
        zeilen += [
            "BEGIN:VEVENT",
            f"UID:{d['kennung']}@ai-os-tagesimpuls",
            f"DTSTAMP:{stempel}",
            f"DTSTART;TZID=Europe/Berlin:{start:%Y%m%d}T090000",
            f"DTEND;TZID=Europe/Berlin:{start:%Y%m%d}T094500",
            "RRULE:FREQ=YEARLY",
            f"SUMMARY:{_esc(d['titel'])}",
            f"DESCRIPTION:{_esc(d['text'])}\\n\\n{_esc(linktext)}",
            "CLASS:PRIVATE",
            "TRANSP:TRANSPARENT",
            "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{d['titel']}", "TRIGGER:PT0M", "END:VALARM",
            "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:Morgen: {d['titel']}", "TRIGGER:-P1D", "END:VALARM",
            "END:VEVENT",
        ]
    zeilen.append("END:VCALENDAR")
    return "\r\n".join(zeilen) + "\r\n"
