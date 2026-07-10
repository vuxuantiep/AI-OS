# Hermes auf dem Raspberry Pi 4B — mit Tailscale-Anbindung ans AI-OS

Stand: 10.07.2026 · Tailnet: `tailed32d1.ts.net` (Geräte: `tiep-laptop`, `pi-ki-tiep`)

## Kurzantwort auf die drei Fragen

| Frage | Antwort |
|-------|---------|
| Läuft Hermes auf dem Pi 4B? | **Ja.** Hermes ist Teil des FastAPI-Backends (`backend/`) — pures Python, läuft problemlos auf ARM64 mit wenig RAM. |
| Kann das LLM auch auf dem Pi laufen? | **Nur eingeschränkt.** Ollama gibt es für ARM64, aber der Pi 4B schafft nur Mini-Modelle (qwen2.5:0.5b, tinyllama) mit wenigen Tokens/Sekunde. llama3 (4,7 GB) ist zu groß bzw. unbrauchbar langsam. |
| Empfohlene Architektur? | **Split über Tailscale:** Hermes + Backend laufen 24/7 auf dem Pi, die LLM-Aufrufe gehen durchs Tailnet an Ollama auf `tiep-laptop`. Genau dafür gibt es die Env-Variable `AIOS_OLLAMA_URL`. |

## Ziel-Architektur

```
┌─────────────────────────┐          Tailscale (WireGuard)          ┌──────────────────────────┐
│ pi-ki-tiep (Pi 4B)      │  ─────────────────────────────────────▶ │ tiep-laptop              │
│                         │   AIOS_OLLAMA_URL=                      │                          │
│  AI-OS Backend :8000    │   http://tiep-laptop.tailed32d1         │  Ollama :11434           │
│  ├─ Hermes (learn/ask/  │   .ts.net:11434                         │  ├─ llama3 (Chat)        │
│  │  work/status)        │                                         │  └─ nomic-embed-text     │
│  ├─ RAG + Vector Store  │ ◀─────────────────────────────────────  │                          │
│  └─ Agent-Pipeline      │   Zugriff von überall im Tailnet:       │  Dashboard :5000 (kann   │
│                         │   http://pi-ki-tiep:8000/docs           │  Pi-Backend aufrufen)    │
└─────────────────────────┘                                         └──────────────────────────┘
```

Vorteil: Der Pi ist dein immer-laufender "Mitarbeiter-Arbeitsplatz" (spart Strom gegenüber
dem Laptop), die Rechenleistung fürs LLM bleibt auf dem Laptop. Fällt der Laptop aus,
kann der Pi als Fallback ein Mini-Modell lokal nutzen (siehe Schritt 6).

## Schritt-für-Schritt-Anleitung

### Schritt 1 — Ollama auf dem Laptop im Tailnet erreichbar machen

Ollama bindet standardmäßig nur an `127.0.0.1`. Auf **tiep-laptop** (PowerShell als Admin):

```powershell
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0", "User")
# Ollama neu starten (Taskleisten-Icon beenden, neu öffnen)
```

Test vom Pi aus (Schritt 3): `curl http://tiep-laptop.tailed32d1.ts.net:11434/api/tags`

> Sicherheit: Port 11434 ist damit im LAN offen. Wer es strenger will, nutzt die
> Windows-Firewall und erlaubt eingehend 11434 nur für das Tailscale-Interface
> (Adapterbereich 100.64.0.0/10).

### Schritt 2 — Pi vorbereiten (SSH auf pi-ki-tiep)

```bash
# Tailscale läuft laut Tailnet-Übersicht bereits — sonst:
curl -fsSL https://tailscale.com/install.sh | sh && sudo tailscale up

# uv installieren (bringt bei Bedarf selbst Python 3.12+ mit)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Repo holen
git clone https://github.com/vuxuantiep/AI-OS.git ~/AI-OS
cd ~/AI-OS/backend
uv sync
```

### Schritt 3 — Konfiguration: LLM-Aufrufe zum Laptop schicken

```bash
cat > ~/AI-OS/backend/.env <<'EOF'
AIOS_OLLAMA_URL=http://tiep-laptop.tailed32d1.ts.net:11434
AIOS_CHAT_MODEL=llama3
AIOS_EMBEDDING_MODEL=nomic-embed-text
EOF
```

Verbindungstest:

```bash
curl http://tiep-laptop.tailed32d1.ts.net:11434/api/tags   # muss die Modellliste zeigen
```

### Schritt 4 — Backend starten und Hermes anlernen

```bash
cd ~/AI-OS/backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Von irgendeinem Gerät im Tailnet (Laptop, Handy mit Tailscale-App):

```bash
curl -X POST http://pi-ki-tiep:8000/api/hermes/learn    # Hermes liest Ziele & Roadmap
curl http://pi-ki-tiep:8000/api/hermes/status           # Wissensstand prüfen
```

Swagger-UI: `http://pi-ki-tiep:8000/docs`

> Falls der Kurzname nicht auflöst: MagicDNS in der Tailscale-Admin-Konsole
> (DNS → MagicDNS) aktivieren oder die `100.x.y.z`-IP des Pi verwenden
> (`tailscale ip -4` auf dem Pi).

### Schritt 5 — Als Dauerdienst einrichten (systemd)

```bash
sudo tee /etc/systemd/system/aios-backend.service <<'EOF'
[Unit]
Description=AI-OS Backend (Hermes)
After=network-online.target tailscaled.service
Wants=network-online.target

[Service]
User=pi
WorkingDirectory=/home/pi/AI-OS/backend
ExecStart=/home/pi/.local/bin/uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now aios-backend
systemctl status aios-backend
```

Ab jetzt startet Hermes bei jedem Pi-Neustart automatisch und ist von allen
Tailnet-Geräten erreichbar — ohne Portfreigaben ins Internet, ohne Cloudflare.

### Schritt 6 — Optional: Mini-LLM als lokaler Fallback auf dem Pi

Wenn der Laptop aus ist, kann der Pi selbst ein kleines Modell bedienen:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:0.5b          # ~400 MB, läuft auf dem Pi 4B
ollama pull nomic-embed-text      # Embeddings gehen auf dem Pi gut
```

Umschalten per `.env`: `AIOS_OLLAMA_URL=http://localhost:11434` und
`AIOS_CHAT_MODEL=qwen2.5:0.5b`. (Eine automatische Fallback-Kette ist der
passende Anwendungsfall für den LiteLLM-Gateway — Roadmap-Erweiterung.)

### Schritt 7 — Optional: HTTPS-Zugriff per `tailscale serve`

```bash
sudo tailscale serve --bg 8000
# → https://pi-ki-tiep.tailed32d1.ts.net (gültiges Zertifikat, nur im Tailnet)
```

## Hinweise & Grenzen

- **Pi 4B RAM:** Backend + JSON-Vector-Store brauchen < 200 MB. Qdrant im Docker
  läuft auch auf ARM64, ist auf dem Pi aber erst bei großen Wissensbeständen nötig.
- **Wissensbasis liegt auf dem Pi** (`backend/data/vector_store.json`). Hermes'
  Journal wächst dort — Backup über das bestehende Backup-Konzept (09_Backup-Recovery).
- **Latenz:** Embedding + Chat laufen über das Tailnet zum Laptop; im Heimnetz
  identisch schnell, unterwegs abhängig von der Verbindung beider Geräte.
- Das Dokument `hermes-tailscale-setup.md` (Downloads) beschreibt das Docker-Produkt
  "Hermes Desktop" mit Dashboard-Sidecar — unser Hermes ist stattdessen nativ ins
  AI-OS-Backend integriert; die Tailscale-Grundidee (nichts öffentlich exponieren,
  alles nur im Tailnet) übernehmen wir 1:1.
