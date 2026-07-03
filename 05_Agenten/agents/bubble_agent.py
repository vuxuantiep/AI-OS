#!/usr/bin/env python3
"""
AI-OS Bubble No-Code Agent (Port 5302)
Brücke zwischen AI-OS und Bubble.io: liest/schreibt Daten (Data API),
triggert Workflows (Workflow API) und generiert UI-Spezifikationen via Ollama.
"""

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    api_retry, extract_json, health_payload, load_agent_config,
    missing_key_error, monitor_log, ollama_chat, ollama_online, LLM_MODEL,
)

AGENT_PORT = int(os.environ.get("BUBBLE_AGENT_PORT", 5302))
CONFIG = load_agent_config("bubble-nocode-agent")

# Synchronisierungs-Status (In-Memory, wie results_cache im Agent System)
SYNC_STATE = {
    "last_action": None,
    "last_action_at": None,
    "last_success": None,
    "actions_total": 0,
    "errors_total": 0,
}


def _token():
    return os.environ.get("BUBBLE_API_TOKEN", "").strip()


def _app_name():
    return os.environ.get("BUBBLE_APP_NAME", "").strip()


def _configured():
    return bool(_token() and _app_name())


def _data_url(object_type, uid=None):
    base = f"https://{_app_name()}.bubbleapps.io/api/1.1/obj/{object_type}"
    return f"{base}/{uid}" if uid else base


def _wf_url(workflow_name):
    return f"https://{_app_name()}.bubbleapps.io/api/1.1/wf/{workflow_name}"


def _track(action, success):
    SYNC_STATE["last_action"] = action
    SYNC_STATE["last_action_at"] = datetime.now().isoformat()
    SYNC_STATE["last_success"] = success
    SYNC_STATE["actions_total"] += 1
    if not success:
        SYNC_STATE["errors_total"] += 1


@api_retry
async def _bubble_request(method, url, **kwargs):
    """HTTP-Request an Bubble.io mit Retry (3 Versuche, exponentieller Backoff)."""
    headers = {"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.request(method, url, headers=headers, **kwargs)
        try:
            data = resp.json()
        except ValueError:
            data = {"raw": resp.text[:500]}
        return data, resp.status_code


@asynccontextmanager
async def lifespan(app):
    await monitor_log("INFO", "BubbleAgent", f"Bubble No-Code Agent gestartet (Port {AGENT_PORT})")
    yield
    await monitor_log("INFO", "BubbleAgent", "Bubble No-Code Agent gestoppt (Graceful Shutdown)")


app = FastAPI(title="AI-OS Bubble No-Code Agent", version="2.0.0", lifespan=lifespan)


# ========== Request-Modelle ==========

class FetchRequest(BaseModel):
    object_type: str
    constraints: Optional[list] = None   # Bubble-Constraint-Objekte
    limit: int = 100
    fetch_all: bool = False              # True = cursor-basiert alles laden


class CreateRequest(BaseModel):
    object_type: str
    fields: dict


class UpdateRequest(BaseModel):
    object_type: str
    record_id: str
    fields: dict


class DeleteRequest(BaseModel):
    object_type: str
    record_id: str


class WorkflowRequest(BaseModel):
    workflow_name: str
    parameters: Optional[dict] = None


class UISpecRequest(BaseModel):
    description: str
    app_context: Optional[str] = None


# ========== Endpoints ==========

@app.get("/health")
async def health():
    return health_payload(CONFIG, {
        "bubble_configured": _configured(),
        "bubble_app": _app_name() or None,
        "ollama_online": await ollama_online(),
        "mode": "online" if _configured() else "offline (nur Ollama-Features)",
    })


@app.get("/agent/info")
async def info():
    return {
        **CONFIG,
        "endpoints": [
            "GET /health", "GET /agent/info", "GET /agent/sync-status",
            "POST /agent/fetch-data", "POST /agent/create-record",
            "POST /agent/update-record", "POST /agent/delete-record",
            "POST /agent/trigger-workflow", "POST /agent/generate-ui-spec",
        ],
    }


@app.get("/agent/sync-status")
async def sync_status():
    return {"success": True, "configured": _configured(), "sync": SYNC_STATE}


@app.post("/agent/fetch-data")
async def fetch_data(req: FetchRequest):
    if not _configured():
        return missing_key_error("BUBBLE_API_TOKEN / BUBBLE_APP_NAME")

    results, cursor, remaining = [], 0, 1
    try:
        while remaining > 0:
            params = {"cursor": cursor, "limit": min(req.limit, 100)}
            if req.constraints:
                import json as _json
                params["constraints"] = _json.dumps(req.constraints)
            data, status = await _bubble_request("GET", _data_url(req.object_type), params=params)
            if status != 200:
                _track(f"fetch:{req.object_type}", False)
                await monitor_log("ERROR", "BubbleAgent", f"fetch-data {status}: {data}")
                return {"success": False, "status_code": status, "error": data}

            response = data.get("response", {})
            batch = response.get("results", [])
            results.extend(batch)
            remaining = response.get("remaining", 0)
            cursor += len(batch)
            # Pagination nur fortsetzen wenn gewünscht und Fortschritt da ist
            if not req.fetch_all or not batch or len(results) >= req.limit:
                break

        _track(f"fetch:{req.object_type}", True)
        return {"success": True, "count": len(results), "remaining": remaining, "results": results}
    except Exception as e:
        _track(f"fetch:{req.object_type}", False)
        await monitor_log("ERROR", "BubbleAgent", f"Bubble nicht erreichbar: {e}")
        return {"success": False, "error": str(e)}


@app.post("/agent/create-record")
async def create_record(req: CreateRequest):
    if not _configured():
        return missing_key_error("BUBBLE_API_TOKEN / BUBBLE_APP_NAME")
    try:
        data, status = await _bubble_request("POST", _data_url(req.object_type), json=req.fields)
        ok = status in (200, 201)
        _track(f"create:{req.object_type}", ok)
        return {"success": ok, "status_code": status, "record_id": data.get("id"), "result": data}
    except Exception as e:
        _track(f"create:{req.object_type}", False)
        await monitor_log("ERROR", "BubbleAgent", f"create-record fehlgeschlagen: {e}")
        return {"success": False, "error": str(e)}


@app.post("/agent/update-record")
async def update_record(req: UpdateRequest):
    if not _configured():
        return missing_key_error("BUBBLE_API_TOKEN / BUBBLE_APP_NAME")
    try:
        data, status = await _bubble_request(
            "PATCH", _data_url(req.object_type, req.record_id), json=req.fields
        )
        ok = status in (200, 204)
        _track(f"update:{req.object_type}", ok)
        return {"success": ok, "status_code": status, "result": data}
    except Exception as e:
        _track(f"update:{req.object_type}", False)
        await monitor_log("ERROR", "BubbleAgent", f"update-record fehlgeschlagen: {e}")
        return {"success": False, "error": str(e)}


@app.post("/agent/delete-record")
async def delete_record(req: DeleteRequest):
    if not _configured():
        return missing_key_error("BUBBLE_API_TOKEN / BUBBLE_APP_NAME")
    try:
        data, status = await _bubble_request("DELETE", _data_url(req.object_type, req.record_id))
        ok = status in (200, 204)
        _track(f"delete:{req.object_type}", ok)
        return {"success": ok, "status_code": status, "result": data}
    except Exception as e:
        _track(f"delete:{req.object_type}", False)
        await monitor_log("ERROR", "BubbleAgent", f"delete-record fehlgeschlagen: {e}")
        return {"success": False, "error": str(e)}


@app.post("/agent/trigger-workflow")
async def trigger_workflow(req: WorkflowRequest):
    if not _configured():
        return missing_key_error("BUBBLE_API_TOKEN / BUBBLE_APP_NAME")
    try:
        data, status = await _bubble_request(
            "POST", _wf_url(req.workflow_name), json=req.parameters or {}
        )
        ok = status in (200, 201, 204)
        _track(f"workflow:{req.workflow_name}", ok)
        if not ok:
            await monitor_log("ERROR", "BubbleAgent", f"Workflow {req.workflow_name} -> {status}")
        return {"success": ok, "status_code": status, "result": data}
    except Exception as e:
        _track(f"workflow:{req.workflow_name}", False)
        await monitor_log("ERROR", "BubbleAgent", f"trigger-workflow fehlgeschlagen: {e}")
        return {"success": False, "error": str(e)}


UI_SPEC_SYSTEM_PROMPT = """Du bist der UI-Architekt der KI-Fabrik für Bubble.io No-Code-Apps.
Erstelle aus der Beschreibung eine strukturierte Bubble.io-UI-Spezifikation.

Antworte AUSSCHLIESSLICH mit einem JSON-Objekt in diesem Format:
{
  "app_name": "...",
  "pages": [
    {
      "name": "...",
      "purpose": "...",
      "elements": [
        {"type": "RepeatingGroup", "data_source": "Search for <Type>", "columns": 1, "rows": 10, "cell_content": ["..."]},
        {"type": "Input", "field": "...", "content_format": "text|email|number|date", "placeholder": "..."},
        {"type": "Button", "label": "...", "triggers_workflow": "..."}
      ]
    }
  ],
  "data_types": [
    {"name": "...", "fields": [{"name": "...", "type": "text|number|date|yes/no|<CustomType>"}]}
  ],
  "workflows": [
    {"name": "...", "trigger": "...", "steps_pseudocode": ["Step 1: ...", "Step 2: ..."]}
  ]
}

KEIN Text vor oder nach dem JSON. Antworte auf Deutsch innerhalb der Werte."""


@app.post("/agent/generate-ui-spec")
async def generate_ui_spec(req: UISpecRequest):
    """Generiert mit Ollama eine Bubble.io-UI-Spezifikation (funktioniert offline)."""
    prompt = req.description
    if req.app_context:
        prompt += f"\n\nKontext zur bestehenden App:\n{req.app_context[:2000]}"
    try:
        raw = await ollama_chat(prompt, system=UI_SPEC_SYSTEM_PROMPT, temperature=0.4)
    except Exception as e:
        await monitor_log("ERROR", "BubbleAgent", f"Ollama nicht erreichbar: {e}")
        return {"success": False, "error": f"Ollama nicht erreichbar ({LLM_MODEL}): {e}"}

    spec = extract_json(raw)
    _track("generate-ui-spec", spec is not None)
    if not spec:
        return {"success": False, "error": "UI-Spec konnte nicht geparst werden", "raw": raw[:1000]}
    return {"success": True, "spec": spec}


if __name__ == "__main__":
    import uvicorn
    print(f"🫧 Bubble No-Code Agent startet auf http://localhost:{AGENT_PORT}")
    uvicorn.run(app, host="127.0.0.1", port=AGENT_PORT)
