# 📅 Cal Scheduling Agent

#wichtig — Referenz für den Cal.com Scheduling-Agenten der KI-Fabrik

## Zweck
Autonomes Terminmanagement via [Cal.com](https://cal.com) API v2: Termine buchen,
auflisten, absagen und Verfügbarkeiten prüfen. Natürlichsprachliche Anfragen
("Buche mir morgen 14 Uhr einen 30-Minuten-Call mit Max") werden mit dem lokalen
Ollama-Modell in strukturierte Termin-Intents übersetzt.

- **Datei:** `05_Agenten/agents/cal_agent.py`
- **Port:** 5301 → http://localhost:5301
- **Gateway-Route:** `http://localhost:5100/api/agents/cal/*`
- **Registry:** `05_Agenten/agents/agents.json` → `cal-scheduling-agent`
- Siehe auch [[bubble-agent-docs]], [[higgsfield-agent-docs]]

## Endpoints
| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/health` | Status-Check (inkl. `cal_api_configured`, `ollama_online`) |
| GET | `/agent/info` | Agent-Metadaten (Name, Rolle, Fähigkeiten) |
| POST | `/agent/schedule-meeting` | Termin buchen (Cal.com Bookings API) |
| POST | `/agent/list-events` | Kommende Termine abrufen |
| POST | `/agent/cancel-event` | Termin absagen (`booking_uid`) |
| POST | `/agent/check-availability` | Freie Slots abrufen (Default: nächste 7 Tage) |
| POST | `/agent/chat` | Natürlichsprachliche Terminanfrage via Ollama |

## API-Keys
In `.env` im AI-OS-Root (siehe `.env.example`, echte Keys NICHT versionieren):
```
CAL_API_KEY=cal_live_...
CAL_USERNAME=dein-cal-username
```
Ohne Key läuft der Agent im **Offline-Modus**: `/agent/chat` extrahiert Intents
weiterhin via Ollama, führt aber nichts aus.

## Beispiel-Requests
```bash
# Natürlichsprachlich buchen
curl -X POST http://localhost:5301/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Buche mir morgen um 14 Uhr einen 30-Minuten-Call mit Max"}'

# Nur Intent extrahieren, nichts ausführen
curl -X POST http://localhost:5301/agent/chat \
  -d '{"message": "Termin nächsten Montag 10 Uhr", "execute": false}'

# Direkt buchen
curl -X POST http://localhost:5301/agent/schedule-meeting \
  -d '{"title": "Call mit Max", "start": "2026-07-04T14:00:00Z", "duration_minutes": 30, "event_type_id": 12345}'

# Verfügbarkeit prüfen
curl -X POST http://localhost:5301/agent/check-availability -d '{}'
```

## Known Issues
- Cal.com Bookings-API benötigt i.d.R. eine gültige `event_type_id` — ohne sie
  kann die Buchung mit HTTP 400 abgelehnt werden. Event-Types im Cal.com-Dashboard nachschlagen.
- Intent-Extraktion nutzt `llama3` (Default, `AGENT_LLM_MODEL` in `.env`);
  relative Datumsangaben ("übermorgen") sind je nach Modell nicht immer exakt — Intent vor `execute` prüfen.
- Der Header `cal-api-version: 2024-08-13` wird für Bookings-Endpoints gesetzt;
  bei API-Änderungen von Cal.com hier zuerst nachsehen.
- Retry-Logik: 3 Versuche mit exponentiellem Backoff (nur bei Netzwerk-/Timeout-Fehlern).
