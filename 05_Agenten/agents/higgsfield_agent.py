#!/usr/bin/env python3
"""
AI-OS Higgsfield Video Agent (Port 5303)
KI-Videoproduktion on-demand: Text-to-Video, Image-to-Video, Skript-Generierung
(Ollama) und komplette Content-Pipelines. Fertige Videos landen in
10_Business/content/videos/.
"""

import asyncio
import json
import os
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    AI_OS_ROOT, api_retry, extract_json, health_payload, load_agent_config,
    missing_key_error, monitor_log, ollama_chat, ollama_online, LLM_MODEL,
)

AGENT_PORT = int(os.environ.get("HIGGSFIELD_AGENT_PORT", 5303))
HIGGSFIELD_API_BASE = "https://api.higgsfield.ai/v1"
CONTENT_DIR = AI_OS_ROOT / "10_Business" / "content"
VIDEO_DIR = CONTENT_DIR / "videos"
JOBS_FILE = VIDEO_DIR / "jobs.json"

POLL_INTERVAL_S = 10          # Job-Status alle 10s prüfen
POLL_MAX_S = 600              # max. 10 Minuten pollen

CONFIG = load_agent_config("higgsfield-video-agent")


def _api_key():
    return os.environ.get("HIGGSFIELD_API_KEY", "").strip()


def _load_jobs():
    try:
        return json.loads(JOBS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_jobs(jobs):
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    JOBS_FILE.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")


def _register_job(job_id, kind, prompt, upstream=None):
    jobs = _load_jobs()
    jobs[job_id] = {
        "job_id": job_id,
        "kind": kind,
        "prompt": prompt[:300],
        "status": "queued",
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "video_url": None,
        "local_file": None,
        "upstream": upstream or {},
    }
    _save_jobs(jobs)
    return jobs[job_id]


def _update_job(job_id, **fields):
    jobs = _load_jobs()
    if job_id in jobs:
        jobs[job_id].update(fields, updated=datetime.now().isoformat())
        _save_jobs(jobs)
        return jobs[job_id]
    return None


@api_retry
async def _hf_request(method, path, **kwargs):
    """HTTP-Request an Higgsfield mit Retry (3 Versuche, exponentieller Backoff)."""
    headers = {"Authorization": f"Bearer {_api_key()}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.request(method, f"{HIGGSFIELD_API_BASE}{path}", headers=headers, **kwargs)
        try:
            data = resp.json()
        except ValueError:
            data = {"raw": resp.text[:500]}
        return data, resp.status_code


async def _download_video(job_id, url):
    """Lädt ein fertiges Video nach 10_Business/content/videos/ herunter."""
    try:
        VIDEO_DIR.mkdir(parents=True, exist_ok=True)
        local_path = VIDEO_DIR / f"{job_id}.mp4"
        async with httpx.AsyncClient(timeout=300, follow_redirects=True) as client:
            async with client.stream("GET", url) as resp:
                resp.raise_for_status()
                with open(local_path, "wb") as f:
                    async for chunk in resp.aiter_bytes(65536):
                        f.write(chunk)
        _update_job(job_id, local_file=str(local_path))
        await monitor_log("INFO", "HiggsfieldAgent", f"Video gespeichert: {local_path.name}")
    except Exception as e:
        await monitor_log("ERROR", "HiggsfieldAgent", f"Video-Download fehlgeschlagen ({job_id}): {e}")


async def _poll_job(job_id, upstream_id):
    """Pollt den Upstream-Job-Status alle 10s (max. 10 Minuten)."""
    waited = 0
    while waited < POLL_MAX_S:
        await asyncio.sleep(POLL_INTERVAL_S)
        waited += POLL_INTERVAL_S
        try:
            data, status = await _hf_request("GET", f"/jobs/{upstream_id}")
        except Exception as e:
            _update_job(job_id, status="error", error=str(e))
            await monitor_log("ERROR", "HiggsfieldAgent", f"Polling fehlgeschlagen ({job_id}): {e}")
            return
        state = str(data.get("status", "")).lower()
        if state in ("completed", "succeeded", "done"):
            video_url = data.get("video_url") or data.get("result", {}).get("url")
            _update_job(job_id, status="completed", video_url=video_url)
            if video_url:
                await _download_video(job_id, video_url)
            return
        if state in ("failed", "error", "cancelled"):
            _update_job(job_id, status="failed", error=data.get("error", "unbekannt"))
            await monitor_log("ERROR", "HiggsfieldAgent", f"Video-Job fehlgeschlagen: {job_id}")
            return
        _update_job(job_id, status=state or "processing")
    _update_job(job_id, status="timeout")
    await monitor_log("ERROR", "HiggsfieldAgent", f"Video-Job Timeout nach {POLL_MAX_S}s: {job_id}")


async def _start_video_job(kind, path, payload, prompt):
    """Startet einen Higgsfield-Job und registriert lokales Tracking + Polling."""
    job_id = f"vid-{uuid.uuid4().hex[:10]}"
    try:
        data, status = await _hf_request("POST", path, json=payload)
    except Exception as e:
        await monitor_log("ERROR", "HiggsfieldAgent", f"Higgsfield nicht erreichbar: {e}")
        return {"success": False, "error": f"Higgsfield API nicht erreichbar: {e}"}

    if status not in (200, 201, 202):
        await monitor_log("ERROR", "HiggsfieldAgent", f"Job-Start fehlgeschlagen ({status}): {data}")
        return {"success": False, "status_code": status, "error": data}

    upstream_id = data.get("id") or data.get("job_id") or job_id
    job = _register_job(job_id, kind, prompt, upstream={"id": upstream_id, "response": data})
    asyncio.create_task(_poll_job(job_id, upstream_id))
    return {"success": True, "job": job}


@asynccontextmanager
async def lifespan(app):
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    await monitor_log("INFO", "HiggsfieldAgent", f"Higgsfield Video Agent gestartet (Port {AGENT_PORT})")
    yield
    await monitor_log("INFO", "HiggsfieldAgent", "Higgsfield Video Agent gestoppt (Graceful Shutdown)")


app = FastAPI(title="AI-OS Higgsfield Video Agent", version="2.0.0", lifespan=lifespan)


# ========== Request-Modelle ==========

class VideoRequest(BaseModel):
    prompt: str
    duration_seconds: int = 5
    aspect_ratio: str = "9:16"
    style: Optional[str] = None


class ImageToVideoRequest(BaseModel):
    image_url: str
    prompt: Optional[str] = None
    duration_seconds: int = 5


class ScriptRequest(BaseModel):
    topic: str
    format: str = "YouTube Short"       # YouTube Short | Reel | Erklärvideo ...
    duration_seconds: int = 45
    audience: Optional[str] = None


class BatchRequest(BaseModel):
    prompts: list[str]
    duration_seconds: int = 5
    aspect_ratio: str = "9:16"


class ContentPlanRequest(BaseModel):
    topic: str
    video_count: int = 5
    format: str = "YouTube Short"
    start_jobs: bool = True             # False = nur Plan erstellen, keine Video-Jobs


# ========== Endpoints ==========

@app.get("/health")
async def health():
    jobs = _load_jobs()
    active = sum(1 for j in jobs.values() if j["status"] in ("queued", "processing", "running"))
    return health_payload(CONFIG, {
        "higgsfield_configured": bool(_api_key()),
        "ollama_online": await ollama_online(),
        "jobs_total": len(jobs),
        "jobs_active": active,
        "mode": "online" if _api_key() else "offline (nur Ollama-Features)",
    })


@app.get("/agent/info")
async def info():
    return {
        **CONFIG,
        "video_dir": str(VIDEO_DIR),
        "endpoints": [
            "GET /health", "GET /agent/info",
            "POST /agent/generate-video", "POST /agent/image-to-video",
            "GET /agent/job-status/{job_id}", "GET /agent/list-videos",
            "POST /agent/generate-script", "POST /agent/batch-generate",
            "POST /agent/create-content-plan",
        ],
    }


@app.post("/agent/generate-video")
async def generate_video(req: VideoRequest):
    if not _api_key():
        return missing_key_error("HIGGSFIELD_API_KEY")
    payload = {
        "prompt": req.prompt,
        "duration": req.duration_seconds,
        "aspect_ratio": req.aspect_ratio,
    }
    if req.style:
        payload["style"] = req.style
    return await _start_video_job("text2video", "/text2video", payload, req.prompt)


@app.post("/agent/image-to-video")
async def image_to_video(req: ImageToVideoRequest):
    if not _api_key():
        return missing_key_error("HIGGSFIELD_API_KEY")
    payload = {
        "image_url": req.image_url,
        "prompt": req.prompt or "",
        "duration": req.duration_seconds,
    }
    return await _start_video_job("image2video", "/image2video", payload, req.prompt or req.image_url)


@app.get("/agent/job-status/{job_id}")
async def job_status(job_id: str):
    job = _load_jobs().get(job_id)
    if not job:
        return {"success": False, "error": f"Job '{job_id}' nicht gefunden"}
    return {"success": True, "job": job}


@app.get("/agent/list-videos")
async def list_videos():
    jobs = _load_jobs()
    files = []
    if VIDEO_DIR.exists():
        files = [
            {"file": f.name, "size_mb": round(f.stat().st_size / 1048576, 2)}
            for f in sorted(VIDEO_DIR.glob("*.mp4"))
        ]
    return {
        "success": True,
        "jobs": sorted(jobs.values(), key=lambda j: j["created"], reverse=True),
        "local_files": files,
        "video_dir": str(VIDEO_DIR),
    }


SCRIPT_SYSTEM_PROMPT = """Du bist der VIDEO-SKRIPT-AUTOR der KI-Fabrik.
Erstelle ein Skript für ein kurzes Video.

Antworte AUSSCHLIESSLICH mit einem JSON-Objekt:
{
  "title": "...",
  "hook": "Erster Satz, der sofort Aufmerksamkeit erzeugt",
  "script": "Vollständiger Sprechertext",
  "scenes": [
    {"seconds": "0-5", "visual": "Beschreibung der Szene", "text_overlay": "..."}
  ],
  "video_prompt": "Cineastischer Text-to-Video-Prompt auf Englisch für die Videogenerierung",
  "hashtags": ["#...", "#..."]
}
KEIN Text vor oder nach dem JSON."""


@app.post("/agent/generate-script")
async def generate_script(req: ScriptRequest):
    """Generiert mit Ollama ein Video-Skript (funktioniert offline)."""
    prompt = (f"Thema: {req.topic}\nFormat: {req.format}\n"
              f"Länge: ca. {req.duration_seconds} Sekunden")
    if req.audience:
        prompt += f"\nZielgruppe: {req.audience}"
    try:
        raw = await ollama_chat(prompt, system=SCRIPT_SYSTEM_PROMPT, temperature=0.8)
    except Exception as e:
        await monitor_log("ERROR", "HiggsfieldAgent", f"Ollama nicht erreichbar: {e}")
        return {"success": False, "error": f"Ollama nicht erreichbar ({LLM_MODEL}): {e}"}

    script = extract_json(raw)
    if not script:
        return {"success": False, "error": "Skript konnte nicht geparst werden", "raw": raw[:1000]}
    return {"success": True, "script": script}


@app.post("/agent/batch-generate")
async def batch_generate(req: BatchRequest):
    if not _api_key():
        return missing_key_error("HIGGSFIELD_API_KEY")
    results = []
    for prompt in req.prompts:
        results.append(await generate_video(VideoRequest(
            prompt=prompt, duration_seconds=req.duration_seconds, aspect_ratio=req.aspect_ratio,
        )))
    started = sum(1 for r in results if r.get("success"))
    return {"success": started > 0, "started": started, "total": len(req.prompts), "jobs": results}


@app.post("/agent/create-content-plan")
async def create_content_plan(req: ContentPlanRequest):
    """Content-Pipeline: Ollama generiert Skripte, Higgsfield produziert die Videos."""
    plan_id = f"plan-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    scripts = []

    # 1. Skripte mit Ollama generieren
    for i in range(req.video_count):
        result = await generate_script(ScriptRequest(
            topic=f"{req.topic} (Video {i + 1} von {req.video_count}, eigener Blickwinkel)",
            format=req.format,
        ))
        if result.get("success"):
            scripts.append(result["script"])
        else:
            await monitor_log("ERROR", "HiggsfieldAgent", f"Skript {i + 1} fehlgeschlagen: {result.get('error')}")

    if not scripts:
        return {"success": False, "error": "Keine Skripte generiert — läuft Ollama?"}

    # 2. Für jedes Skript einen Video-Job starten (nur mit API-Key)
    jobs = []
    if req.start_jobs and _api_key():
        for script in scripts:
            video_prompt = script.get("video_prompt") or script.get("title", req.topic)
            job_result = await generate_video(VideoRequest(prompt=video_prompt))
            jobs.append({
                "title": script.get("title"),
                "job_id": job_result.get("job", {}).get("job_id"),
                "started": job_result.get("success", False),
            })
    elif req.start_jobs:
        jobs = [{"note": "HIGGSFIELD_API_KEY nicht konfiguriert — nur Skripte erstellt (Offline-Modus)"}]

    # 3. Content-Plan als JSON speichern
    plan = {
        "plan_id": plan_id,
        "topic": req.topic,
        "format": req.format,
        "created": datetime.now().isoformat(),
        "scripts": scripts,
        "jobs": jobs,
    }
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    plan_file = CONTENT_DIR / f"{plan_id}.json"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    await monitor_log("INFO", "HiggsfieldAgent", f"Content-Plan erstellt: {plan_file.name} ({len(scripts)} Skripte)")

    # 4. Tracking-Übersicht zurückgeben
    return {
        "success": True,
        "plan_id": plan_id,
        "plan_file": str(plan_file),
        "scripts_generated": len(scripts),
        "jobs_started": sum(1 for j in jobs if j.get("started")),
        "tracking": jobs,
        "titles": [s.get("title") for s in scripts],
    }


if __name__ == "__main__":
    import uvicorn
    print(f"🎬 Higgsfield Video Agent startet auf http://localhost:{AGENT_PORT}")
    uvicorn.run(app, host="127.0.0.1", port=AGENT_PORT)
