#!/usr/bin/env python3
"""
AI-OS MCP Server
Exponiert lokale KI-Funktionen als MCP (Model Context Protocol) Server.
Ermöglicht anderen AI-Clients (wie Claude Desktop) den Zugriff auf lokale Modelle.
"""

import json
import os
import sys
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Konfiguration
AI_OS_ROOT = Path(os.environ.get("AI_OS_ROOT", Path(__file__).parent.parent.parent))
OLLAMA_HOST = "127.0.0.1"
OLLAMA_PORT = 11434
MCP_PORT = int(os.environ.get("MCP_PORT", 5001))

class MCPHandler(BaseHTTPRequestHandler):
    """HTTP Handler für MCP - implementiert das MCP Protokoll"""
    
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
    
    def do_OPTIONS(self):
        """CORS Preflight"""
        self._set_headers(204)
    
    def do_GET(self):
        """GET Requests - MCP Resource Discovery"""
        if self.path == "/" or self.path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "server": "AI-OS MCP Server",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            }).encode())
        
        elif self.path == "/mcp/resources":
            self._set_headers()
            resources = self._get_resources()
            self.wfile.write(json.dumps(resources).encode())
        
        elif self.path == "/mcp/tools":
            self._set_headers()
            tools = self._get_tools()
            self.wfile.write(json.dumps(tools).encode())
        
        elif self.path == "/mcp/models":
            self._send_ollama_request("/api/tags")
        
        elif self.path.startswith("/mcp/knowledge/"):
            query = self.path.split("/mcp/knowledge/", 1)[1]
            result = self._search_knowledge(query)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        """POST Requests - MCP Tool Execution"""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}
        
        if self.path == "/mcp/chat":
            result = self._handle_chat(data)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif self.path == "/mcp/generate":
            result = self._handle_generate(data)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif self.path == "/mcp/embed":
            result = self._handle_embed(data)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif self.path == "/mcp/summarize":
            result = self._handle_summarize(data)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())
    
    def log_message(self, format, *args):
        """Benutzerdefiniertes Logging"""
        print(f"[MCP] {datetime.now().strftime('%H:%M:%S')} {args[0]} {args[1]} {args[2]}")
    
    # ========== MCP Resource Discovery ==========
    
    def _get_resources(self):
        """Listet verfügbare MCP-Ressourcen"""
        return {
            "resources": [
                {
                    "uri": "mcp://ai-os/models",
                    "name": "KI Modelle",
                    "description": "Liste aller installierten Ollama-Modelle"
                },
                {
                    "uri": "mcp://ai-os/knowledge/{query}",
                    "name": "Wissenssuche",
                    "description": "Durchsuche die lokale Wissensdatenbank"
                },
                {
                    "uri": "mcp://ai-os/health",
                    "name": "Systemstatus",
                    "description": "Aktueller Status des AI-OS"
                }
            ]
        }
    
    def _get_tools(self):
        """Listet verfügbare MCP-Tools"""
        return {
            "tools": [
                {
                    "name": "chat",
                    "description": "Chatte mit einem lokalen KI-Modell",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "model": {
                                "type": "string",
                                "description": "Modellname (z.B. llama3, mistral)"
                            },
                            "message": {
                                "type": "string",
                                "description": "Deine Nachricht"
                            },
                            "system": {
                                "type": "string",
                                "description": "System-Prompt (optional)"
                            }
                        },
                        "required": ["message"]
                    }
                },
                {
                    "name": "generate",
                    "description": "Generiere Text mit einem lokalen KI-Modell",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "model": {
                                "type": "string",
                                "description": "Modellname"
                            },
                            "prompt": {
                                "type": "string",
                                "description": "Der Prompt für die Generierung"
                            },
                            "temperature": {
                                "type": "number",
                                "description": "Kreativität (0.0 - 2.0, Default: 0.7)"
                            },
                            "max_tokens": {
                                "type": "integer",
                                "description": "Maximale Token-Anzahl"
                            }
                        },
                        "required": ["prompt"]
                    }
                },
                {
                    "name": "summarize",
                    "description": "Fasse einen Text zusammen",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Der zu summarisierende Text"
                            },
                            "language": {
                                "type": "string",
                                "description": "Sprache (deutsch/englisch, Default: deutsch)"
                            }
                        },
                        "required": ["text"]
                    }
                },
                {
                    "name": "embed",
                    "description": "Erstelle Embeddings für einen Text",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Der Text für Embeddings"
                            }
                        },
                        "required": ["text"]
                    }
                },
                {
                    "name": "search_knowledge",
                    "description": "Durchsuche die lokale Wissensdatenbank mit KI",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Suchbegriff"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "list_models",
                    "description": "Liste alle installierten KI-Modelle",
                    "input_schema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    
    # ========== MCP Tool Implementierungen ==========
    
    def _send_ollama_request(self, endpoint, data=None, method="GET"):
        """Sendet eine Anfrage an die Ollama API"""
        try:
            url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}{endpoint}"
            
            if method == "GET" and data:
                url += "?" + urllib.parse.urlencode(data)
            
            req = urllib.request.Request(url, method=method)
            if data and method != "GET":
                req.data = json.dumps(data).encode("utf-8")
                req.add_header("Content-Type", "application/json")
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def _handle_chat(self, data):
        """Chat mit lokalem KI-Modell"""
        model = data.get("model", "llama3")
        message = data.get("message", "")
        system = data.get("system", "Du bist ein hilfreicher Assistent. Antworte auf Deutsch.")
        
        if not message:
            return {"error": "Keine Nachricht angegeben"}
        
        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": message}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 2048
                }
            }
            
            req = urllib.request.Request(
                f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
            
            return {
                "response": result.get("message", {}).get("content", ""),
                "model": model
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _handle_generate(self, data):
        """Textgenerierung"""
        model = data.get("model", "llama3")
        prompt = data.get("prompt", "")
        temperature = data.get("temperature", 0.7)
        max_tokens = data.get("max_tokens", 2048)
        
        if not prompt:
            return {"error": "Kein Prompt angegeben"}
        
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            req = urllib.request.Request(
                f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
            
            return {
                "response": result.get("response", ""),
                "model": model,
                "total_duration": result.get("total_duration", 0)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _handle_embed(self, data):
        """Erstelle Embeddings"""
        text = data.get("text", "")
        if not text:
            return {"error": "Kein Text angegeben"}
        
        try:
            payload = {
                "model": "nomic-embed-text",
                "prompt": text
            }
            
            req = urllib.request.Request(
                f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/embeddings",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            
            return {
                "embedding": result.get("embedding", []),
                "dimensions": len(result.get("embedding", []))
            }
        except Exception as e:
            # Fallback: Verwende chat model
            try:
                payload = {
                    "model": "llama3",
                    "prompt": f"Erstelle eine Zusammenfassung dieses Textes für die Suche: {text[:500]}",
                    "stream": False,
                    "options": {"num_predict": 100}
                }
                req = urllib.request.Request(
                    f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = json.loads(resp.read())
                return {
                    "summary": result.get("response", ""),
                    "note": "Embeddings nicht verfügbar, verwende Text-Zusammenfassung"
                }
            except:
                return {"error": str(e)}
    
    def _handle_summarize(self, data):
        """Text-Zusammenfassung"""
        text = data.get("text", "")
        language = data.get("language", "deutsch")
        
        if not text:
            return {"error": "Kein Text angegeben"}
        
        if len(text) > 8000:
            text = text[:8000] + "..."
        
        try:
            payload = {
                "model": "llama3",
                "messages": [
                    {"role": "system", "content": f"Du bist ein Experte für Textzusammenfassungen. Fasse den folgenden Text auf {language} zusammen. Sei präzise und erfasse die Hauptpunkte."},
                    {"role": "user", "content": text}
                ],
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 512}
            }
            
            req = urllib.request.Request(
                f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
            
            return {
                "summary": result.get("message", {}).get("content", ""),
                "original_length": len(data.get("text", "")),
                "language": language
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _search_knowledge(self, query):
        """Durchsuche die Wissensdatenbank mit KI"""
        knowledge_dir = AI_OS_ROOT / "00_Knowledge"
        results = []
        
        try:
            # Sammle relevante Markdown-Dateien
            files = list(knowledge_dir.rglob("*.md"))[:20]
            
            for file_path in files:
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    # Einfache Relevanz-Prüfung
                    query_words = query.lower().split()
                    content_lower = content.lower()
                    
                    # Zähle Treffer
                    matches = sum(1 for word in query_words if word in content_lower)
                    
                    if matches > 0:
                        # Extrahiere erste Zeilen als Vorschau
                        lines = content.split("\n")
                        preview_lines = [l for l in lines if l.strip() and not l.startswith("#")]
                        preview = preview_lines[0][:200] if preview_lines else lines[0][:200]
                        
                        rel_path = file_path.relative_to(AI_OS_ROOT)
                        results.append({
                            "path": str(rel_path),
                            "relevance": matches,
                            "preview": preview.strip(),
                            "title": lines[0].replace("#", "").strip() if lines else file_path.stem
                        })
                except:
                    continue
            
            # Sortiere nach Relevanz
            results.sort(key=lambda x: x["relevance"], reverse=True)
            
            return {
                "query": query,
                "results": results[:10],
                "total_found": len(results)
            }
        except Exception as e:
            return {"error": str(e), "results": []}


def main():
    """Startet den MCP-Server"""
    print(f"\n{'='*50}")
    print(f"🔌 AI-OS MCP Server")
    print(f"{'='*50}")
    print(f"📍 Host: http://localhost:{MCP_PORT}")
    print(f"📁 Wissensbasis: {AI_OS_ROOT / '00_Knowledge'}")
    print(f"🔧 Ollama: http://{OLLAMA_HOST}:{OLLAMA_PORT}")
    print(f"{'='*50}\n")
    
    server = HTTPServer(("127.0.0.1", MCP_PORT), MCPHandler)
    print(f"✅ MCP Server läuft auf Port {MCP_PORT}")
    print(f"📋 Verfügbare Endpunkte:")
    print(f"   GET  /health           - Health Check")
    print(f"   GET  /mcp/tools        - Tool-Liste")
    print(f"   GET  /mcp/resources    - Ressourcen-Liste")
    print(f"   GET  /mcp/models       - Modell-Liste")
    print(f"   POST /mcp/chat         - Chat")
    print(f"   POST /mcp/generate     - Text generieren")
    print(f"   POST /mcp/summarize    - Zusammenfassung")
    print(f"   POST /mcp/embed        - Embeddings")
    print(f"   POST /mcp/knowledge/   - Wissenssuche\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 MCP Server gestoppt")
        server.server_close()

if __name__ == "__main__":
    main()