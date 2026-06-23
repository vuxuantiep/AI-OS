#!/usr/bin/env python3
"""
AI-OS API Gateway (Port 5100)
Einheitlicher API-Einstiegspunkt für alle KI-Fabrik Dienste.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Konfiguration
GATEWAY_PORT = int(os.environ.get("GATEWAY_PORT", 5100))

# Service-Registry
SERVICES = {
    "dashboard": {
        "name": "Dashboard",
        "host": "127.0.0.1",
        "port": 5000,
        "description": "Web UI"
    },
    "mcp": {
        "name": "MCP Server",
        "host": "127.0.0.1",
        "port": 5001,
        "description": "AI-Client Interface"
    },
    "rag": {
        "name": "RAG Pipeline",
        "host": "127.0.0.1",
        "port": 5002,
        "description": "Knowledge Agent"
    },
    "workflow": {
        "name": "Workflow Engine",
        "host": "127.0.0.1",
        "port": 5200,
        "description": "Workflow & Tasks"
    },
    "agents": {
        "name": "Agent System",
        "host": "127.0.0.1",
        "port": 5300,
        "description": "Multi-Agent System"
    },
    "monitoring": {
        "name": "Monitoring",
        "host": "127.0.0.1",
        "port": 5400,
        "description": "Observability"
    }
}


class GatewayHandler(BaseHTTPRequestHandler):
    """HTTP Handler für das API Gateway"""
    
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers(204)
    
    def _forward_request(self, service_name, path, method="GET", body=None):
        """Leite eine Anfrage an einen Service weiter"""
        service = SERVICES.get(service_name)
        if not service:
            return {"error": f"Service '{service_name}' nicht gefunden"}, 404
        
        try:
            url = f"http://{service['host']}:{service['port']}{path}"
            
            req = urllib.request.Request(url, method=method)
            if body:
                req.data = json.dumps(body).encode("utf-8")
                req.add_header("Content-Type", "application/json")
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                return result, resp.status
                
        except urllib.error.HTTPError as e:
            try:
                error_body = json.loads(e.read())
                return error_body, e.code
            except:
                return {"error": f"HTTP {e.code}: {e.reason}"}, e.code
        except urllib.error.URLError as e:
            return {"error": f"Service '{service_name}' nicht erreichbar: {e.reason}"}, 503
        except Exception as e:
            return {"error": str(e)}, 500
    
    def _check_service_health(self, service_name):
        """Prüfe ob ein Service erreichbar ist"""
        service = SERVICES.get(service_name)
        if not service:
            return False
        try:
            req = urllib.request.Request(f"http://{service['host']}:{service['port']}/health")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except:
            return False
    
    def do_GET(self):
        path = self.path
        
        # Gateway-Info
        if path == "/" or path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "service": "AI-OS API Gateway",
                "version": "2.0.0",
                "services": len(SERVICES),
                "timestamp": datetime.now().isoformat()
            }).encode())
        
        # Service-Registry
        elif path == "/services":
            self._set_headers()
            services_status = {}
            for name, svc in SERVICES.items():
                services_status[name] = {
                    **svc,
                    "online": self._check_service_health(name)
                }
            self.wfile.write(json.dumps({"services": services_status}).encode())
        
        # Health-Check für alle Services
        elif path == "/health/all":
            self._set_headers()
            health_status = {}
            all_ok = True
            for name in SERVICES:
                is_healthy = self._check_service_health(name)
                health_status[name] = "✅ Online" if is_healthy else "❌ Offline"
                if not is_healthy:
                    all_ok = False
            self.wfile.write(json.dumps({
                "overall": "✅ All Systems Operational" if all_ok else "⚠️ Some Services Offline",
                "services": health_status
            }).encode())
        
        # Route zu spezifischen Services
        elif path.startswith("/dashboard/"):
            result, status = self._forward_request("dashboard", path.replace("/dashboard", ""))
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        elif path.startswith("/mcp/"):
            result, status = self._forward_request("mcp", path.replace("/mcp", ""))
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        elif path.startswith("/rag/"):
            result, status = self._forward_request("rag", path.replace("/rag", ""))
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        elif path.startswith("/workflow/"):
            result, status = self._forward_request("workflow", path.replace("/workflow", ""))
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        elif path.startswith("/agents/"):
            result, status = self._forward_request("agents", path.replace("/agents", ""))
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        elif path.startswith("/monitoring/"):
            result, status = self._forward_request("monitoring", path.replace("/monitoring", ""))
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
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
        
        path = self.path
        
        # Universelle Chat-API
        if path == "/chat":
            message = data.get("message", "")
            agent = data.get("agent", "orchestrator")
            
            # Leite an Agent System weiter
            result, status = self._forward_request("agents", "/chat", "POST", {
                "message": message,
                "agent": agent
            })
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        # Universelle Task-API
        elif path == "/execute":
            task = data.get("task", "")
            agent = data.get("agent", "orchestrator")
            
            result, status = self._forward_request("agents", "/execute", "POST", {
                "task": task,
                "agent": agent
            })
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        # Orchestrierte Ausführung
        elif path == "/orchestrate":
            task = data.get("task", "")
            
            result, status = self._forward_request("agents", "/orchestrate", "POST", {
                "task": task
            })
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        # Workflow erstellen und starten
        elif path == "/workflow/run":
            name = data.get("name", "Schnell-Workflow")
            tasks = data.get("tasks", [])
            
            # Workflow erstellen
            wf_result, wf_status = self._forward_request("workflow", "/workflows/create", "POST", {
                "name": name,
                "tasks": tasks
            })
            
            if wf_status == 201 and wf_result.get("success"):
                wf_id = wf_result.get("workflow_id")
                # Workflow starten
                start_result, start_status = self._forward_request("workflow", "/workflows/start", "POST", {
                    "workflow_id": wf_id
                })
                self._set_headers(start_status)
                self.wfile.write(json.dumps({
                    "workflow_id": wf_id,
                    "status": "started",
                    "workflow": wf_result.get("workflow"),
                    "start_result": start_result
                }).encode())
            else:
                self._set_headers(wf_status)
                self.wfile.write(json.dumps(wf_result).encode())
        
        # RAG Query
        elif path == "/query":
            query = data.get("query", "")
            
            result, status = self._forward_request("rag", "/query", "POST", {
                "query": query
            })
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        # Route zu spezifischen Services
        elif path.startswith("/dashboard/"):
            result, status = self._forward_request("dashboard", path.replace("/dashboard", ""), "POST", data)
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        elif path.startswith("/mcp/"):
            result, status = self._forward_request("mcp", path.replace("/mcp", ""), "POST", data)
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        elif path.startswith("/rag/"):
            result, status = self._forward_request("rag", path.replace("/rag", ""), "POST", data)
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        elif path.startswith("/workflow/"):
            result, status = self._forward_request("workflow", path.replace("/workflow", ""), "POST", data)
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        elif path.startswith("/agents/"):
            result, status = self._forward_request("agents", path.replace("/agents", ""), "POST", data)
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        elif path.startswith("/monitoring/"):
            result, status = self._forward_request("monitoring", path.replace("/monitoring", ""), "POST", data)
            self._set_headers(status)
            self.wfile.write(json.dumps(result).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())


def main():
    """Startet das API Gateway"""
    print(f"\n{'='*50}")
    print(f"🌐 AI-OS API Gateway")
    print(f"{'='*50}")
    print(f"📍 Host: http://localhost:{GATEWAY_PORT}")
    print(f"📋 Registrierte Services:")
    for name, svc in SERVICES.items():
        print(f"   - {svc['name']}: http://{svc['host']}:{svc['port']}")
    print(f"{'='*50}\n")
    
    server = HTTPServer(("127.0.0.1", GATEWAY_PORT), GatewayHandler)
    print(f"✅ API Gateway läuft auf Port {GATEWAY_PORT}")
    print(f"📋 Endpunkte:")
    print(f"   GET  /              - Gateway-Info")
    print(f"   GET  /services      - Service-Registry")
    print(f"   GET  /health/all    - Alle Health-Checks")
    print(f"   POST /chat          - Chat (universell)")
    print(f"   POST /execute       - Task ausführen")
    print(f"   POST /orchestrate   - Orchestrierte Ausführung")
    print(f"   POST /workflow/run  - Workflow erstellen + starten")
    print(f"   POST /query         - RAG Query")
    print(f"   /{{service}}/...    - Direkt-Routing\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 API Gateway gestoppt")
        server.server_close()

if __name__ == "__main__":
    main()