#!/usr/bin/env python3
"""
AI-OS Monitoring Service (Port 5400)
Metriken, Logging, Health-Checks und Tracing für alle Dienste.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import threading
from pathlib import Path
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import deque, defaultdict

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Konfiguration
MONITOR_PORT = int(os.environ.get("MONITOR_PORT", 5400))

# Services die überwacht werden
MONITORED_SERVICES = {
    "dashboard": {"host": "127.0.0.1", "port": 5000, "name": "Dashboard"},
    "mcp": {"host": "127.0.0.1", "port": 5001, "name": "MCP Server"},
    "rag": {"host": "127.0.0.1", "port": 5002, "name": "RAG Pipeline"},
    "gateway": {"host": "127.0.0.1", "port": 5100, "name": "API Gateway"},
    "workflow": {"host": "127.0.0.1", "port": 5200, "name": "Workflow Engine"},
    "agents": {"host": "127.0.0.1", "port": 5300, "name": "Agent System"},
    "ollama": {"host": "127.0.0.1", "port": 11434, "name": "Ollama"}
}


# ============================================================
# Metrics Collector
# ============================================================

class MetricsCollector:
    """Sammelt Metriken von allen Diensten"""
    
    def __init__(self):
        self.metrics_history = defaultdict(lambda: deque(maxlen=100))  # Letzte 100 Werte
        self.health_history = defaultdict(lambda: deque(maxlen=60))    # Letzte 60 Checks
        self.logs = deque(maxlen=500)                                  # Letzte 500 Logs
        self.traces = deque(maxlen=200)                                # Letzte 200 Traces
        self.collection_active = False
        self.collection_thread = None
    
    def start_collection(self, interval=10):
        """Starte regelmäßige Metrik-Erfassung"""
        self.collection_active = True
        self.collection_thread = threading.Thread(
            target=self._collect_loop,
            args=(interval,),
            daemon=True
        )
        self.collection_thread.start()
        self.add_log("INFO", "Monitoring", "Metrik-Erfassung gestartet")
    
    def stop_collection(self):
        """Stoppe Metrik-Erfassung"""
        self.collection_active = False
        self.add_log("INFO", "Monitoring", "Metrik-Erfassung gestoppt")
    
    def _collect_loop(self, interval):
        """Hauptschleife für Metrik-Erfassung"""
        while self.collection_active:
            try:
                self._collect_all_metrics()
            except Exception as e:
                self.add_log("ERROR", "Monitoring", f"Fehler bei Metrik-Erfassung: {e}")
            time.sleep(interval)
    
    def _collect_all_metrics(self):
        """Sammle Metriken von allen Diensten"""
        timestamp = datetime.now().isoformat()
        
        for name, svc in MONITORED_SERVICES.items():
            try:
                start = time.time()
                req = urllib.request.Request(
                    f"http://{svc['host']}:{svc['port']}/health",
                    method="GET"
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    response_time = (time.time() - start) * 1000  # ms
                    status = resp.status
                
                self.health_history[name].append({
                    "timestamp": timestamp,
                    "status": "up" if status == 200 else "degraded",
                    "response_time_ms": round(response_time, 2)
                })
                
            except Exception as e:
                self.health_history[name].append({
                    "timestamp": timestamp,
                    "status": "down",
                    "error": str(e)[:100]
                })
    
    def add_log(self, level, source, message):
        """Füge einen Log-Eintrag hinzu"""
        self.logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message
        })
    
    def add_trace(self, service, operation, duration_ms, status):
        """Füge einen Trace hinzu"""
        self.traces.append({
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "operation": operation,
            "duration_ms": duration_ms,
            "status": status
        })
    
    def get_service_health(self, service_name):
        """Hole Health-Status eines Dienstes"""
        history = list(self.health_history.get(service_name, []))
        if not history:
            return {"status": "unknown", "last_check": None}
        
        last = history[-1]
        uptime = sum(1 for h in history if h["status"] == "up") / len(history) * 100 if history else 0
        
        return {
            "status": last["status"],
            "last_check": last["timestamp"],
            "response_time_ms": last.get("response_time_ms"),
            "uptime_percent": round(uptime, 1),
            "checks_count": len(history)
        }
    
    def get_all_health(self):
        """Hole Health-Status aller Dienste"""
        return {
            name: self.get_service_health(name)
            for name in MONITORED_SERVICES
        }
    
    def get_system_metrics(self):
        """Hole System-Metriken"""
        services_up = sum(
            1 for h in self.get_all_health().values()
            if h["status"] == "up"
        )
        services_total = len(MONITORED_SERVICES)
        
        return {
            "services_online": f"{services_up}/{services_total}",
            "total_logs": len(self.logs),
            "total_traces": len(self.traces),
            "errors_last_hour": sum(
                1 for log in self.logs
                if log["level"] == "ERROR"
            ),
            "collection_active": self.collection_active
        }
    
    def get_recent_logs(self, level=None, source=None, limit=50):
        """Hole aktuelle Logs mit Filtern"""
        logs = list(self.logs)
        if level:
            logs = [l for l in logs if l["level"] == level]
        if source:
            logs = [l for l in logs if l["source"] == source]
        return logs[-limit:]
    
    def get_recent_traces(self, limit=50):
        """Hole aktuelle Traces"""
        return list(self.traces)[-limit:]


# ============================================================
# HTTP Server
# ============================================================

collector = MetricsCollector()

class MonitoringHandler(BaseHTTPRequestHandler):
    """HTTP Handler für das Monitoring"""
    
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers(204)
    
    def do_GET(self):
        if self.path == "/" or self.path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "service": "AI-OS Monitoring",
                "version": "2.0.0",
                "collecting": collector.collection_active,
                "timestamp": datetime.now().isoformat()
            }).encode())
        
        elif self.path == "/health/all":
            self._set_headers()
            self.wfile.write(json.dumps({
                "services": collector.get_all_health(),
                "system": collector.get_system_metrics()
            }).encode())
        
        elif self.path.startswith("/health/"):
            service = self.path.split("/health/", 1)[1]
            self._set_headers()
            self.wfile.write(json.dumps({
                "service": service,
                "health": collector.get_service_health(service)
            }).encode())
        
        elif self.path == "/metrics":
            self._set_headers()
            self.wfile.write(json.dumps({
                "system": collector.get_system_metrics(),
                "services": collector.get_all_health()
            }).encode())
        
        elif self.path == "/logs":
            level = self._get_param("level")
            source = self._get_param("source")
            limit = int(self._get_param("limit", "50"))
            self._set_headers()
            self.wfile.write(json.dumps({
                "logs": collector.get_recent_logs(level, source, limit),
                "total": len(collector.logs)
            }).encode())
        
        elif self.path == "/traces":
            limit = int(self._get_param("limit", "50"))
            self._set_headers()
            self.wfile.write(json.dumps({
                "traces": collector.get_recent_traces(limit),
                "total": len(collector.traces)
            }).encode())
        
        elif self.path == "/status":
            self._set_headers()
            health = collector.get_all_health()
            services_up = sum(1 for h in health.values() if h["status"] == "up")
            services_total = len(health)
            
            # HTML-Statusseite
            html = f"""<!DOCTYPE html>
<html lang="de" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 AI-OS Monitoring</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e17; color: #e2e8f0; padding: 2rem;
        }}
        h1 {{ margin-bottom: 2rem; }}
        .status-grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1rem; margin-bottom: 2rem;
        }}
        .status-card {{
            background: #1e293b; border: 1px solid #334155; border-radius: 12px;
            padding: 1.5rem; transition: transform 0.2s;
        }}
        .status-card:hover {{ transform: translateY(-2px); }}
        .status-card .name {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem; }}
        .status-card .status {{ font-size: 0.9rem; margin-bottom: 0.5rem; }}
        .status-card .detail {{ font-size: 0.8rem; color: #94a3b8; }}
        .up {{ color: #22c55e; }} .down {{ color: #ef4444; }} .degraded {{ color: #eab308; }}
        .summary {{
            background: #111827; border: 1px solid #334155; border-radius: 12px;
            padding: 1.5rem; margin-bottom: 2rem;
        }}
        .summary .big {{ font-size: 2rem; font-weight: bold; }}
        .refresh {{ margin-top: 1rem; padding: 0.5rem 1rem; background: #3b82f6;
            color: white; border: none; border-radius: 6px; cursor: pointer; }}
    </style>
</head>
<body>
    <h1>📊 AI-OS System Status</h1>
    <div class="summary">
        <div class="big">{services_up}/{services_total}</div>
        <div>Dienste online</div>
    </div>
    <div class="status-grid">
"""
            for name, svc in MONITORED_SERVICES.items():
                h = health.get(name, {})
                status = h.get("status", "unknown")
                status_icon = {"up": "✅", "down": "❌", "degraded": "⚠️", "unknown": "❓"}
                html += f"""
        <div class="status-card">
            <div class="name">{svc['name']}</div>
            <div class="status {status}">{status_icon.get(status, '❓')} {status.upper()}</div>
            <div class="detail">Latenz: {h.get('response_time_ms', 'N/A')}ms</div>
            <div class="detail">Uptime: {h.get('uptime_percent', 0)}%</div>
        </div>
"""
            html += """
    </div>
    <button class="refresh" onclick="location.reload()">🔄 Aktualisieren</button>
    <p style="margin-top:1rem;color:#94a3b8;font-size:0.8rem;">
        Letzte Aktualisierung: """ + datetime.now().strftime("%H:%M:%S") + """</p>
</body>
</html>"""
            self._set_headers(200, "text/html")
            self.wfile.write(html.encode("utf-8"))
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}
        
        if self.path == "/log":
            level = data.get("level", "INFO")
            source = data.get("source", "unknown")
            message = data.get("message", "")
            collector.add_log(level, source, message)
            self._set_headers()
            self.wfile.write(json.dumps({"success": True}).encode())
        
        elif self.path == "/trace":
            service = data.get("service", "unknown")
            operation = data.get("operation", "")
            duration = data.get("duration_ms", 0)
            status = data.get("status", "success")
            collector.add_trace(service, operation, duration, status)
            self._set_headers()
            self.wfile.write(json.dumps({"success": True}).encode())
        
        elif self.path == "/start":
            collector.start_collection(data.get("interval", 10))
            self._set_headers()
            self.wfile.write(json.dumps({"success": True}).encode())
        
        elif self.path == "/stop":
            collector.stop_collection()
            self._set_headers()
            self.wfile.write(json.dumps({"success": True}).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())
    
    def _get_param(self, name, default=None):
        """Extrahiere Query-Parameter"""
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        return params.get(name, [default])[0]


def main():
    """Startet den Monitoring Service"""
    print(f"\n{'='*50}")
    print(f"📊 AI-OS Monitoring Service")
    print(f"{'='*50}")
    print(f"📍 Host: http://localhost:{MONITOR_PORT}")
    print(f"📋 Überwachte Dienste:")
    for name, svc in MONITORED_SERVICES.items():
        print(f"   - {svc['name']}: {svc['host']}:{svc['port']}")
    print(f"{'='*50}\n")
    
    # Starte Metrik-Erfassung
    collector.start_collection(interval=10)
    
    server = HTTPServer(("127.0.0.1", MONITOR_PORT), MonitoringHandler)
    print(f"✅ Monitoring läuft auf Port {MONITOR_PORT}")
    print(f"📋 Endpunkte:")
    print(f"   GET  /              - Status")
    print(f"   GET  /health/all    - Alle Health-Checks")
    print(f"   GET  /health/{'{name}'} - Einzelner Health-Check")
    print(f"   GET  /metrics       - System-Metriken")
    print(f"   GET  /logs          - Logs (filterbar)")
    print(f"   GET  /traces        - Traces")
    print(f"   GET  /status        - HTML-Statusseite")
    print(f"   POST /log           - Log-Eintrag hinzufügen")
    print(f"   POST /trace         - Trace hinzufügen")
    print(f"   POST /start         - Erfassung starten")
    print(f"   POST /stop          - Erfassung stoppen\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Monitoring gestoppt")
        collector.stop_collection()
        server.server_close()

if __name__ == "__main__":
    main()