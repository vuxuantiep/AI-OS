"""Google-Kalender über einen Service-Account (kopflos auf dem Pi, kein Browser-Login nötig).

Einrichtung: Kalender in Google Calendar > Einstellungen > „Für bestimmte Personen freigeben“ >
E-Mail des Service-Accounts mit „Änderungen an Terminen vornehmen“. Details: README.md.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta

from .config import Config

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def dienst(cfg: Config):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    cred = service_account.Credentials.from_service_account_file(cfg.google_sa_datei, scopes=SCOPES)
    return build("calendar", "v3", credentials=cred, cache_discovery=False)


def termine(cfg: Config, von: datetime, bis: datetime, svc=None) -> list[dict]:
    svc = svc or dienst(cfg)
    alle: list[dict] = []
    for kid in cfg.kalender_ids:
        res = svc.events().list(calendarId=kid, timeMin=von.isoformat(), timeMax=bis.isoformat(),
                                singleEvents=True, orderBy="startTime", maxResults=100).execute()
        for ev in res.get("items", []):
            if ev.get("status") != "cancelled":
                ev["_kalender"] = kid
                alle.append(ev)
    return sorted(alle, key=lambda e: e["start"].get("dateTime", e["start"].get("date", "")))


def start_zeit(ev: dict, cfg: Config) -> datetime | None:
    s = ev["start"]
    if "dateTime" in s:
        return datetime.fromisoformat(s["dateTime"]).astimezone(cfg.zeitzone)
    return None  # ganztägig


def erinnerungs_minuten(ev: dict, cfg: Config) -> list[int]:
    rem = ev.get("reminders", {})
    popups = [o for o in rem.get("overrides", []) if o.get("method") == "popup"]
    if rem.get("useDefault", True) or not popups:
        return cfg.wecker_standard_min
    return sorted({o["minutes"] for o in popups}, reverse=True)


def ist_alarm(ev: dict, cfg: Config) -> bool:
    titel = (ev.get("summary") or "").lower()
    return ev.get("colorId") == "11" or any(w in titel for w in cfg.alarm_woerter)


def tages_uebersicht(evs: list[dict], cfg: Config) -> str:
    if not evs:
        return "📅 Heute keine Termine – Zeit für dich."
    zeilen = ["📅 Heute:"]
    for ev in evs:
        st = start_zeit(ev, cfg)
        zeilen.append(f"   {'ganztägig' if st is None else st.strftime('%H:%M')}  {ev.get('summary', '(ohne Titel)')}")
    return "\n".join(zeilen)


def impuls_eintragen(cfg: Config, tag: date, titel: str, text: str, svc=None) -> None:
    """Schreibt den Tagesimpuls als ganztägigen Termin in einen eigenen Kalender (ein-/ausblendbar)."""
    if not cfg.impuls_kalender_id:
        return
    svc = svc or dienst(cfg)
    kennung = f"tagesimpuls{tag:%Y%m%d}"
    vorhanden = svc.events().list(calendarId=cfg.impuls_kalender_id,
                                  privateExtendedProperty=f"tagesimpuls={kennung}").execute().get("items")
    if vorhanden:
        return
    svc.events().insert(calendarId=cfg.impuls_kalender_id, body={
        "summary": titel,
        "description": text,
        "start": {"date": tag.isoformat()},
        "end": {"date": (tag + timedelta(days=1)).isoformat()},
        "transparency": "transparent",
        "reminders": {"useDefault": False},
        "extendedProperties": {"private": {"tagesimpuls": kennung}},
    }).execute()


def finanztermine_anlegen(cfg: Config, termine_def: list[dict], svc=None) -> list[str]:
    """Legt die jährlichen Finanz-/Steuer-Termine idempotent im ersten Kalender an."""
    svc = svc or dienst(cfg)
    kid = cfg.kalender_ids[0]
    ergebnis = []
    for t in termine_def:
        vorhanden = svc.events().list(calendarId=kid,
                                      privateExtendedProperty=f"tagesimpuls={t['kennung']}").execute().get("items")
        if vorhanden:
            ergebnis.append(f"vorhanden: {t['titel']}")
            continue
        start = datetime.combine(t["erster_termin"], time(9, 0), cfg.zeitzone)
        svc.events().insert(calendarId=kid, body={
            "summary": t["titel"],
            "description": t["beschreibung_html"],
            "start": {"dateTime": start.isoformat(), "timeZone": str(cfg.zeitzone)},
            "end": {"dateTime": (start + timedelta(minutes=45)).isoformat(), "timeZone": str(cfg.zeitzone)},
            "recurrence": ["RRULE:FREQ=YEARLY"],
            "colorId": "11",  # Tomate = Alarm-Kennzeichen für den Pi-Wecker
            "transparency": "transparent",
            "visibility": "private",
            "reminders": {"useDefault": False, "overrides": [
                {"method": "popup", "minutes": 0},
                {"method": "popup", "minutes": 24 * 60},
                {"method": "email", "minutes": 7 * 24 * 60},
            ]},
            "extendedProperties": {"private": {"tagesimpuls": t["kennung"]}},
        }).execute()
        ergebnis.append(f"angelegt: {t['titel']}")
    return ergebnis
