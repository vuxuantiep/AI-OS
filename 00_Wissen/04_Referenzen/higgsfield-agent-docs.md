# 🎬 Higgsfield Video Agent

#wichtig — Referenz für den Higgsfield.ai Video-Content-Agenten der KI-Fabrik

## Zweck
KI-Videoproduktion on-demand: Text-to-Video und Image-to-Video über
[Higgsfield.ai](https://higgsfield.ai), Skript-Generierung mit dem lokalen
Ollama-Modell und komplette Content-Pipelines (Thema → N Skripte → N Video-Jobs).
Fertige Videos werden nach `10_Business/content/videos/` heruntergeladen.

- **Datei:** `05_Agenten/agents/higgsfield_agent.py`
- **Port:** 5303 → http://localhost:5303
- **Gateway-Route:** `http://localhost:5100/api/agents/higgsfield/*`
- **Registry:** `05_Agenten/agents/agents.json` → `higgsfield-video-agent`
- Siehe auch [[cal-agent-docs]], [[bubble-agent-docs]]

## Endpoints
| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/health` | Status-Check (inkl. aktive Jobs) |
| GET | `/agent/info` | Agent-Metadaten |
| POST | `/agent/generate-video` | Text-to-Video-Job starten |
| POST | `/agent/image-to-video` | Bild-to-Video-Job starten |
| GET | `/agent/job-status/{job_id}` | Status eines Video-Jobs |
| GET | `/agent/list-videos` | Alle Jobs + lokal gespeicherte Videos |
| POST | `/agent/generate-script` | Video-Skript via Ollama (offline-fähig) |
| POST | `/agent/batch-generate` | Mehrere Videos aus einer Prompt-Liste |
| POST | `/agent/create-content-plan` | Komplette Content-Pipeline (Skripte + Jobs + Plan-JSON) |

## API-Keys
```
HIGGSFIELD_API_KEY=hf_...
```
Ohne Key: Offline-Modus — `/agent/generate-script` und
`/agent/create-content-plan` (mit `"start_jobs": false` bzw. nur Skripte) funktionieren via Ollama.

## Beispiel-Requests
```bash
# Video generieren
curl -X POST http://localhost:5303/agent/generate-video \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Cinematic drone shot over a futuristic AI factory at sunset", "aspect_ratio": "9:16"}'

# Skript generieren (offline-fähig)
curl -X POST http://localhost:5303/agent/generate-script \
  -d '{"topic": "KI-Agenten für Unternehmer", "format": "YouTube Short", "duration_seconds": 45}'

# Komplette Content-Pipeline
curl -X POST http://localhost:5303/agent/create-content-plan \
  -d '{"topic": "5 YouTube Shorts über KI-Agenten für Unternehmer", "video_count": 5}'

# Job-Status
curl http://localhost:5303/agent/job-status/vid-a1b2c3d4e5
```

## Ablagestruktur
- Content-Pläne: `10_Business/content/plan-YYYYMMDD-HHMMSS.json`
- Videos: `10_Business/content/videos/{job_id}.mp4`
- Job-Tracking: `10_Business/content/videos/jobs.json`

## Known Issues
- Job-Polling: alle 10s, Timeout nach 10 Minuten (`status: "timeout"` — Job kann
  upstream trotzdem noch fertig werden; erneut `/agent/job-status` prüfen).
- Die Higgsfield-API-Pfade (`/text2video`, `/jobs/{id}`) sind gegen die öffentliche
  Doku zu verifizieren, sobald ein API-Key vorliegt — Response-Parsing ist tolerant
  gebaut (`id`/`job_id`, `video_url`/`result.url`), aber ungetestet gegen die Live-API.
- Polling-Tasks leben im Prozess: Wird der Agent neu gestartet, werden laufende
  Jobs nicht weiter gepollt (Status bleibt auf `processing`; manuell per Job-Status prüfen).
- Content-Plan mit 5 Videos = 5 sequentielle Ollama-Aufrufe → je nach Modell mehrere Minuten.
