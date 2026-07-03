#!/usr/bin/env python3
"""
AI-OS Cal Scheduling Agent (Port 5301)
Autonomes Terminmanagement via Cal.com API v2 + natürlichsprachliche
Terminanfragen über das lokale Ollama-Modell.
"""

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    api_retry, extract_json, health_payload, load_agent_config,
    missing_key_error, monitor_log, ollama_chat, ollama_online, LLM_MODEL,
)

AGENT_PORT = int(os.environ.get("CAL_AGENT_PORT", 5301))
CAL_API_BASE = "https://api.cal.com/v2"
CONFIG = load_agent_config("cal-scheduling-agent")


def _api_key():
    return os.environ.get("CAL_API_KEY", "").strip()


def _headers(api_version=None):
    headers = {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
    }
    if api_version:
        headers["cal-api-version"] = api_version
    return headers


@api_retry
async def _cal_request(method, path, api_version=None, **kwargs):
    """HTTP-Request an Cal.com mit Retry (3 Versuche, exponentieller Backoff)."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.request(
            method, f"{CAL_API_BASE}{path}", headers=_headers(api_version), **kwargs
        )
        try:
            data = resp.json()
        except ValueError:
            data = {"raw": resp.text[:500]}
        return data, resp.status_code


@asynccontextmanager
async def lifespan(app):
    await monitor_log("INFO", "CalAgent", f"Cal Scheduling Agent gestartet (Port {AGENT_PORT})")
    yield
    await monitor_log("INFO", "CalAgent", "Cal Scheduling Agent gestoppt (Graceful Shutdown)")


app = FastAPI(title="AI-OS Cal Scheduling Agent", version="2.0.0", lifespan=lifespan)


# ========== Request-Modelle ==========

class ScheduleRequest(BaseModel):
    title: str = "Meeting"
    start: str                          # ISO 8601, z.B. "2026-07-04T14:00:00Z"
    event_type_id: Optional[int] = None
    attendee_name: str = "Gast"
    attendee_email: Optional[str] = None
    timezone: str = "Europe/Berlin"
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class ListEventsRequest(BaseModel):
    status: str = "upcoming"            # upcoming | past | cancelled
    limit: int = 10


class CancelRequest(BaseModel):
    booking_uid: str
    reason: Optional[str] = None


class AvailabilityRequest(BaseModel):
    event_type_id: Optional[int] = None
    start: Optional[str] = None         # Default: jetzt
    end: Optional[str] = None           # Default: +7 Tage
    timezone: str = "Europe/Berlin"


class ChatRequest(BaseModel):
    message: str
    execute: bool = True                # False = nur Intent extrahieren, nichts buchen


# ========== Endpoints ==========

@app.get("/health")
async def health():
    return health_payload(CONFIG, {
        "cal_api_configured": bool(_api_key()),
        "ollama_online": await ollama_online(),
        "mode": "online" if _api_key() else "offline (nur Ollama-Features)",
    })


@app.get("/agent/info")
async def info():
    return {
        **CONFIG,
        "endpoints": [
            "GET /health", "GET /agent/info",
            "POST /agent/schedule-meeting", "POST /agent/list-events",
            "POST /agent/cancel-event", "POST /agent/check-availability",
            "POST /agent/chat",
        ],
    }


@app.post("/agent/schedule-meeting")
async def schedule_meeting(req: ScheduleRequest):
    if not _api_key():
        return missing_key_error("CAL_API_KEY")

    payload = {
        "start": req.start,
        "attendee": {
            "name": req.attendee_name,
            "email": req.attendee_email or os.environ.get("CAL_USERNAME", "") + "@example.com",
            "timeZone": req.timezone,
        },
        "metadata": {"source": "AI-OS", "title": req.title},
    }
    if req.event_type_id:
        payload["eventTypeId"] = req.event_type_id
    if req.duration_minutes:
        payload["lengthInMinutes"] = req.duration_minutes
    if req.notes:
        payload["bookingFieldsResponses"] = {"notes": req.notes}

    try:
        data, status = await _cal_request("POST", "/bookings", api_version="2024-08-13", json=payload)
        ok = status in (200, 201)
        if not ok:
            await monitor_log("ERROR", "CalAgent", f"Buchung fehlgeschlagen ({status}): {data}")
        return {"success": ok, "status_code": status, "booking": data.get("data", data)}
    except Exception as e:
        await monitor_log("ERROR", "CalAgent", f"Cal.com nicht erreichbar: {e}")
        return {"success": False, "error": f"Cal.com API nicht erreichbar: {e}"}


@app.post("/agent/list-events")
async def list_events(req: ListEventsRequest = ListEventsRequest()):
    if not _api_key():
        return missing_key_error("CAL_API_KEY")
    try:
        data, status = await _cal_request(
            "GET", "/bookings", api_version="2024-08-13",
            params={"status": req.status, "take": req.limit},
        )
        bookings = data.get("data", data.get("bookings", []))
        return {"success": status == 200, "count": len(bookings) if isinstance(bookings, list) else 0,
                "events": bookings}
    except Exception as e:
        await monitor_log("ERROR", "CalAgent", f"Termine abrufen fehlgeschlagen: {e}")
        return {"success": False, "error": str(e)}


@app.post("/agent/cancel-event")
async def cancel_event(req: CancelRequest):
    if not _api_key():
        return missing_key_error("CAL_API_KEY")
    try:
        data, status = await _cal_request(
            "POST", f"/bookings/{req.booking_uid}/cancel", api_version="2024-08-13",
            json={"cancellationReason": req.reason or "Abgesagt via AI-OS"},
        )
        return {"success": status in (200, 201), "status_code": status, "result": data.get("data", data)}
    except Exception as e:
        await monitor_log("ERROR", "CalAgent", f"Absage fehlgeschlagen: {e}")
        return {"success": False, "error": str(e)}


@app.post("/agent/check-availability")
async def check_availability(req: AvailabilityRequest = AvailabilityRequest()):
    if not _api_key():
        return missing_key_error("CAL_API_KEY")

    start = req.start or datetime.now().isoformat()
    end = req.end or (datetime.now() + timedelta(days=7)).isoformat()
    params = {"startTime": start, "endTime": end, "timeZone": req.timezone}
    if req.event_type_id:
        params["eventTypeId"] = req.event_type_id
    username = os.environ.get("CAL_USERNAME", "").strip()
    if username:
        params["usernameList"] = username

    try:
        data, status = await _cal_request("GET", "/slots/available", params=params)
        return {"success": status == 200, "range": {"start": start, "end": end},
                "slots": data.get("data", data)}
    except Exception as e:
        await monitor_log("ERROR", "CalAgent", f"Verfügbarkeit fehlgeschlagen: {e}")
        return {"success": False, "error": str(e)}


INTENT_SYSTEM_PROMPT = """Du bist der Scheduling-Intent-Parser der KI-Fabrik.
Heute ist {today} ({weekday}). Extrahiere aus der Nutzereingabe einen Termin-Intent.

Antworte AUSSCHLIESSLICH mit einem JSON-Objekt in exakt diesem Format:
{{
  "action": "schedule" | "list" | "cancel" | "availability",
  "title": "Kurzer Titel",
  "duration_minutes": 30,
  "preferred_datetime": "YYYY-MM-DDTHH:MM:SS",
  "attendee_email": null,
  "event_type_id": null
}}

Regeln:
- Relative Angaben (morgen, nächsten Montag) in absolute Daten umrechnen.
- Fehlende Werte auf null setzen, duration_minutes Default 30.
- KEIN Text vor oder nach dem JSON."""


@app.post("/agent/chat")
async def chat(req: ChatRequest):
    """Natürlichsprachliche Terminanfrage -> Intent-Extraktion via Ollama -> Ausführung."""
    now = datetime.now()
    system = INTENT_SYSTEM_PROMPT.format(
        today=now.strftime("%Y-%m-%d %H:%M"),
        weekday=["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"][now.weekday()],
    )
    try:
        raw = await ollama_chat(req.message, system=system, temperature=0.2)
    except Exception as e:
        await monitor_log("ERROR", "CalAgent", f"Ollama nicht erreichbar: {e}")
        return {"success": False, "error": f"Ollama nicht erreichbar ({LLM_MODEL}): {e}"}

    intent = extract_json(raw)
    if not intent:
        return {"success": False, "error": "Intent konnte nicht extrahiert werden", "raw": raw[:500]}

    result = {"success": True, "intent": intent, "executed": False}
    if not req.execute or not _api_key():
        if not _api_key():
            result["note"] = "Offline-Modus: CAL_API_KEY nicht konfiguriert, Intent wurde nur extrahiert."
        return result

    # Intent ausführen
    action = intent.get("action")
    if action == "schedule" and intent.get("preferred_datetime"):
        exec_result = await schedule_meeting(ScheduleRequest(
            title=intent.get("title") or "Meeting",
            start=intent["preferred_datetime"],
            duration_minutes=intent.get("duration_minutes"),
            attendee_email=intent.get("attendee_email"),
            event_type_id=intent.get("event_type_id"),
        ))
    elif action == "list":
        exec_result = await list_events(ListEventsRequest())
    elif action == "availability":
        exec_result = await check_availability(AvailabilityRequest())
    else:
        exec_result = {"success": False, "error": f"Aktion '{action}' benötigt weitere Angaben"}

    result.update({"executed": True, "result": exec_result})
    return result


if __name__ == "__main__":
    import uvicorn
    print(f"📅 Cal Scheduling Agent startet auf http://localhost:{AGENT_PORT}")
    uvicorn.run(app, host="127.0.0.1", port=AGENT_PORT)
