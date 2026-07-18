#!/usr/bin/env python3
"""Broki Pi — HTTP-Server (:8088): liefert den signierten RAG-Index an die
Browser-Extensions im Tailscale-Netz.

Endpunkte (gegenstück zu tailscale-sync.js der Extension):
  GET /index/manifest.json?rolle=<r>  → Manifest der Rolle (Version, Dateien, Signaturen)
  GET /index/<datei>.jsonl            → signiertes Partitions-Paket (JSON-Zeilen)
  GET /health                         → {"ok": true, "rollen": [...]}

Sicherheit: Der Server liefert NUR aus index_data/ (whitelisted, pfadsicher).
Die Vertraulichkeit im Netz übernimmt Tailscale (WireGuard); die Integrität
die ECDSA-Signatur, die die Extension prüft. Kein Schreib-Endpunkt.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Windows-Konsole ist per Default cp1252 → Emoji im print() crasht. UTF-8 erzwingen.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HIER = Path(__file__).parent
DATA_DIR = HIER / "index_data"
PORT = int(os.environ.get("BROKI_PI_PORT", 8088))


class Handler(BaseHTTPRequestHandler):
    def _senden(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")  # Extension-Herkunft
        self.end_headers()
        self.wfile.write(body if isinstance(body, bytes) else json.dumps(body).encode())

    def do_GET(self):
        u = urlparse(self.path)

        if u.path == "/health":
            rollen = [p.stem.replace("manifest_", "")
                      for p in DATA_DIR.glob("manifest_*.json")] if DATA_DIR.exists() else []
            return self._senden(200, {"ok": True, "rollen": rollen})

        if u.path == "/index/manifest.json":
            rolle = (parse_qs(u.query).get("rolle") or ["mitarbeiter"])[0]
            mf = DATA_DIR / f"manifest_{rolle}.json"
            if not mf.exists():
                return self._senden(404, {"error": f"Unbekannte Rolle: {rolle}"})
            return self._senden(200, mf.read_bytes())

        if u.path.startswith("/index/"):
            name = u.path[len("/index/"):]
            # Pfadsicher: nur einfacher Dateiname, nur .jsonl aus DATA_DIR
            if "/" in name or ".." in name or not name.endswith(".jsonl"):
                return self._senden(400, {"error": "Ungültiger Pfad"})
            datei = DATA_DIR / name
            if not datei.exists():
                return self._senden(404, {"error": "Partition nicht gefunden"})
            return self._senden(200, datei.read_bytes(), "application/x-ndjson")

        self._senden(404, {"error": "Not found"})

    def log_message(self, *a):
        pass  # keine Zugriffs-Logs (Datenschutz)


def main():
    if not DATA_DIR.exists():
        print("⚠️  index_data/ fehlt — erst 'python index_builder.py' ausführen.")
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)  # 0.0.0.0 = auch über Tailscale-IP
    print(f"🍓 Broki-Pi-Server läuft auf :{PORT} (Tailscale-erreichbar). Strg+C beendet.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()
