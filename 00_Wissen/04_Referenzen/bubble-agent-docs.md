# 🫧 Bubble No-Code Agent

#wichtig — Referenz für den Bubble.io-Agenten der KI-Fabrik

## Zweck
Brücke zwischen AI-OS und [Bubble.io](https://bubble.io): liest und schreibt
Datensätze (Data API), triggert Bubble-Workflows (Workflow API) und generiert
mit dem lokalen Ollama-Modell strukturierte UI-Spezifikationen für neue Bubble-Apps.

- **Datei:** `05_Agenten/agents/bubble_agent.py`
- **Port:** 5302 → http://localhost:5302
- **Gateway-Route:** `http://localhost:5100/api/agents/bubble/*`
- **Registry:** `05_Agenten/agents/agents.json` → `bubble-nocode-agent`
- Siehe auch [[cal-agent-docs]], [[higgsfield-agent-docs]]

## Endpoints
| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/health` | Status-Check (inkl. `bubble_configured`, `ollama_online`) |
| GET | `/agent/info` | Agent-Metadaten |
| GET | `/agent/sync-status` | Sync-Status AI-OS ↔ Bubble (letzte Aktion, Fehlerzähler) |
| POST | `/agent/fetch-data` | Datensätze lesen (cursor-basierte Pagination via `fetch_all`) |
| POST | `/agent/create-record` | Neuen Datensatz anlegen |
| POST | `/agent/update-record` | Datensatz aktualisieren (PATCH) |
| POST | `/agent/delete-record` | Datensatz löschen |
| POST | `/agent/trigger-workflow` | Bubble-Workflow auslösen |
| POST | `/agent/generate-ui-spec` | UI-Spec via Ollama generieren (offline-fähig) |

## API-Keys
```
BUBBLE_API_TOKEN=...        # Bubble: Settings → API → Private Key
BUBBLE_APP_NAME=meine-app   # aus https://meine-app.bubbleapps.io
```
API-URLs: Data `https://{APP}.bubbleapps.io/api/1.1/obj/{type}`,
Workflow `https://{APP}.bubbleapps.io/api/1.1/wf/{name}`.

## Beispiel-Requests
```bash
# Daten lesen (max 100, alles: "fetch_all": true)
curl -X POST http://localhost:5302/agent/fetch-data \
  -H "Content-Type: application/json" \
  -d '{"object_type": "kunde", "limit": 50}'

# Datensatz anlegen
curl -X POST http://localhost:5302/agent/create-record \
  -d '{"object_type": "kunde", "fields": {"name": "Max Muster", "email": "max@example.com"}}'

# Workflow triggern
curl -X POST http://localhost:5302/agent/trigger-workflow \
  -d '{"workflow_name": "send_welcome_email", "parameters": {"user_id": "123x456"}}'

# UI-Spec generieren (funktioniert ohne Bubble-Keys)
curl -X POST http://localhost:5302/agent/generate-ui-spec \
  -d '{"description": "Erstelle eine CRM-Ansicht für Kundenkontakte mit Name, Email, Status"}'
```

## Known Issues
- Data/Workflow API müssen in Bubble aktiviert sein (Settings → API), sonst 404.
- Workflows müssen als "API Workflow" mit öffentlichem Endpoint angelegt sein.
- `constraints` erwartet das Bubble-Format `[{"key": "...", "constraint_type": "equals", "value": "..."}]`.
- Bei Free-Plan-Apps drosselt Bubble die API stark (Rate Limits) — Retry-Logik fängt nur Netzwerkfehler ab, keine 429.
- UI-Spec ist ein Bauplan (Pseudocode-Workflows), kein importierbares Bubble-Format.
