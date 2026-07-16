# LeadPilot CRM — Installation (AI-OS & Trace-AI OS)

LeadPilot ist **self-contained**: keine Imports aus der Host-Plattform, Persistenz
in `data/` (JSON), Konfiguration über UI + Umgebungsvariablen. Das identische
Verzeichnis läuft daher unverändert in **beiden Repos**.

## Voraussetzungen
- Python 3.10+ mit Flask (`pip install flask`)
- Sonst nichts — keine Datenbank, kein Node, kein Docker.

## Variante 1: Standalone (funktioniert überall sofort)

```bash
# Ordner "app/" an beliebige Stelle kopieren, dann:
python app.py           # -> http://localhost:5330
```

Port ändern: `LEADPILOT_PORT=5340 python app.py`

## Variante 2: In AI-OS (bereits erledigt ✅)

1. Modul liegt unter `10_Business/IT Pipeline System inkl CRM/app/`
2. `ai_os_dashboard.py`: Eintrag in `PRODUKT_PROXIES` (`"it-pipeline": {"port": 5330, ...}`)
   → erreichbar unter `/produkte/it-pipeline/` (auch via Tunnel/Tailscale)
3. `SERVICES`-Eintrag (Dienste-Tab, startbar, Health `/api/health`)
4. Produktkarte im „Produktion"-Tab

## Variante 3: In Trace-AI OS (getrenntes Repo)

1. Den kompletten Ordner `app/` ins Repo kopieren (z. B. `modules/leadpilot/`)
2. Standalone starten (siehe Variante 1) — fertig, falls kein zentrales Dashboard nötig
3. Optional hinter einen bestehenden Flask-Gateway hängen (Proxy-Muster aus AI-OS):

```python
import os, urllib.request, urllib.error
from flask import request, Response

LEADPILOT_PORT = int(os.environ.get("LEADPILOT_PORT", "5330"))

@app.route("/module/leadpilot/", defaults={"sub": ""}, methods=["GET","POST","PUT","DELETE"])
@app.route("/module/leadpilot/<path:sub>", methods=["GET","POST","PUT","DELETE"])
def leadpilot_proxy(sub):
    url = f"http://127.0.0.1:{LEADPILOT_PORT}/{sub}"
    if request.query_string:
        url += "?" + request.query_string.decode()
    data = request.get_data() if request.method in ("POST", "PUT") else None
    req = urllib.request.Request(url, data=data, method=request.method)
    if request.content_type:
        req.add_header("Content-Type", request.content_type)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return Response(r.read(), status=r.status,
                            content_type=r.headers.get("Content-Type", "text/html"))
    except urllib.error.HTTPError as e:
        return Response(e.read(), status=e.code)
    except Exception:
        return Response("LeadPilot offline", status=503)
```

Wichtig: Das Frontend nutzt **relative API-Pfade** — es funktioniert unter jedem
Pfad-Präfix (`/module/leadpilot/`, `/produkte/it-pipeline/`, `/` …).
Achtung Werkzeug-Falle: keine konkurrierende generische Route `/module/<name>/`
definieren — sonst gewinnt die generische (siehe AI-OS-Lektion), dann Dispatching
innerhalb der generischen Route machen.

## Umgebungsvariablen

| Variable | Zweck | Default |
|---|---|---|
| `LEADPILOT_PORT` | HTTP-Port | 5330 |
| `SMTP_HOST` / `SMTP_PORT` | Mail-Versand (F3) | — / 587 |
| `SMTP_USER` / `SMTP_PASS` | SMTP-Login | — |
| `SMTP_FROM` | Absender-Adresse | — |

Ohne SMTP-Konfiguration laufen alle automatischen Mails in den **Postausgang**
(sichtbar in der UI) statt verloren zu gehen.

## Website anbinden (Stufe 1 des Konzepts)

- **Kontaktformular** → `POST /api/webhooks/kontaktformular`
  mit JSON `{name, email, projektart, nachricht}` (oder Form-Daten)
- **Cal.com** → Settings → Developer → Webhooks → Subscriber-URL
  `https://<deine-domain>/produkte/it-pipeline/api/webhooks/calcom`,
  Event **BOOKING_CREATED**

Dedup: gleiche E-Mail + offener Lead → wird als Verlaufs-Eintrag angehängt statt doppelt angelegt.
