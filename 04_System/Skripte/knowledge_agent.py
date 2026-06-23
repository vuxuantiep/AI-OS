#!/usr/bin/env python3
"""
AI-OS Knowledge Agent
Semantische Vektorsuche über die lokale Wissensdatenbank.
Ermöglicht RAG (Retrieval Augmented Generation) mit lokalen KI-Modellen.
"""

import json
import os
import sys
import re
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Konfiguration
AI_OS_ROOT = Path(os.environ.get("AI_OS_ROOT", Path(__file__).parent.parent.parent))
OLLAMA_HOST = "127.0.0.1"
OLLAMA_PORT = 11434
AGENT_PORT = 5002
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3"

# Vektordatenbank (einfache JSON-basierte Implementierung)
VECTOR_DB_PATH = AI_OS_ROOT / "04_System" / "Data" / "vector_store.json"

class SimpleVectorStore:
    """Einfache Vektordatenbank für semantische Suche"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.documents = []
        self.embeddings = []
        self._load()
    
    def _load(self):
        """Lade gespeicherte Vektordaten"""
        if self.db_path.exists():
            try:
                data = json.loads(self.db_path.read_text(encoding="utf-8"))
                self.documents = data.get("documents", [])
                self.embeddings = data.get("embeddings", [])
                print(f"📚 Vektordatenbank geladen: {len(self.documents)} Dokumente")
            except Exception as e:
                print(f"⚠️ Konnte Vektordatenbank nicht laden: {e}")
    
    def _save(self):
        """Speichere Vektordaten"""
        try:
            data = {
                "documents": self.documents,
                "embeddings": self.embeddings,
                "updated": datetime.now().isoformat()
            }
            self.db_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"⚠️ Konnte Vektordatenbank nicht speichern: {e}")
    
    def get_embedding(self, text):
        """Erstelle Embedding via Ollama"""
        try:
            payload = json.dumps({
                "model": EMBED_MODEL,
                "prompt": text[:2000]  # Begrenze Textlänge
            }).encode("utf-8")
            
            req = urllib.request.Request(
                f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/embeddings",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                return result.get("embedding", [])
        except Exception as e:
            print(f"⚠️ Embedding-Fehler: {e}")
            return None
    
    def cosine_similarity(self, a, b):
        """Berechne Kosinus-Ähnlichkeit zwischen zwei Vektoren"""
        if not a or not b:
            return 0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0
        return dot / (norm_a * norm_b)
    
    def add_document(self, path, title, content, chunk_index=0):
        """Füge ein Dokument zur Vektordatenbank hinzu"""
        # Prüfe ob bereits vorhanden
        doc_id = f"{path}#chunk{chunk_index}"
        if any(d["id"] == doc_id for d in self.documents):
            return False
        
        embedding = self.get_embedding(content[:2000])
        if not embedding:
            return False
        
        self.documents.append({
            "id": doc_id,
            "path": path,
            "title": title,
            "content": content[:2000],
            "chunk_index": chunk_index,
            "added": datetime.now().isoformat()
        })
        self.embeddings.append(embedding)
        self._save()
        return True
    
    def search(self, query, top_k=5):
        """Semantische Suche"""
        query_embedding = self.get_embedding(query)
        if not query_embedding:
            return []
        
        # Berechne Ähnlichkeiten
        scores = []
        for i, doc_embedding in enumerate(self.embeddings):
            score = self.cosine_similarity(query_embedding, doc_embedding)
            scores.append((score, i))
        
        # Sortiere nach Relevanz
        scores.sort(key=lambda x: x[0], reverse=True)
        
        # Gib Top-Ergebnisse zurück
        results = []
        for score, idx in scores[:top_k]:
            if score > 0.1:  # Mindestrelevanz
                doc = self.documents[idx]
                results.append({
                    "score": round(score, 4),
                    "path": doc["path"],
                    "title": doc["title"],
                    "content": doc["content"][:500] + "..." if len(doc["content"]) > 500 else doc["content"],
                    "chunk": doc["chunk_index"]
                })
        
        return results
    
    def index_knowledge_base(self):
        """Indiziere alle Markdown-Dateien in der Wissensdatenbank"""
        knowledge_dir = AI_OS_ROOT / "00_Wissen"
        if not knowledge_dir.exists():
            print("⚠️ Wissensdatenbank nicht gefunden")
            return 0
        
        indexed = 0
        files = list(knowledge_dir.rglob("*.md"))
        
        print(f"📖 Indiziere {len(files)} Dateien...")
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                if not content.strip():
                    continue
                
                rel_path = str(file_path.relative_to(AI_OS_ROOT))
                title = file_path.stem
                
                # Extrahiere Titel aus Markdown
                first_line = content.split("\n")[0].strip()
                if first_line.startswith("#"):
                    title = first_line.lstrip("#").strip()
                
                # Teile große Dokumente in Chunks
                chunks = self._chunk_text(content, 1500)
                
                for i, chunk in enumerate(chunks):
                    if self.add_document(rel_path, title, chunk, i):
                        indexed += 1
                
                if indexed % 10 == 0 and indexed > 0:
                    print(f"  ... {indexed} Chunks indiziert")
                    
            except Exception as e:
                print(f"⚠️ Fehler bei {file_path.name}: {e}")
        
        print(f"✅ {indexed} Chunks indiziert")
        return indexed
    
    def _chunk_text(self, text, max_chars=1500):
        """Teile Text in sinnvolle Chunks"""
        # Entferne leere Zeilen am Anfang/Ende
        text = text.strip()
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        paragraphs = text.split("\n\n")
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_chars:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                # Wenn ein einzelner Paragraph zu lang ist, teile ihn
                if len(para) > max_chars:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    current_chunk = ""
                    for sent in sentences:
                        if len(current_chunk) + len(sent) + 1 <= max_chars:
                            if current_chunk:
                                current_chunk += " " + sent
                            else:
                                current_chunk = sent
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            current_chunk = sent
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = ""
                else:
                    current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def clear(self):
        """Leere die Vektordatenbank"""
        self.documents = []
        self.embeddings = []
        self._save()
        print("🗑️ Vektordatenbank geleert")


class KnowledgeAgentHandler(BaseHTTPRequestHandler):
    """HTTP Handler für den Knowledge Agent"""
    
    def __init__(self, *args, **kwargs):
        self.vector_store = SimpleVectorStore(VECTOR_DB_PATH)
        super().__init__(*args, **kwargs)
    
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
                "documents": len(self.vector_store.documents),
                "embeddings": len(self.vector_store.embeddings)
            }).encode())
        
        elif self.path == "/stats":
            self._set_headers()
            self.wfile.write(json.dumps({
                "documents": len(self.vector_store.documents),
                "embeddings": len(self.vector_store.embeddings),
                "db_path": str(VECTOR_DB_PATH),
                "knowledge_path": str(AI_OS_ROOT / "00_Wissen")
            }).encode())
        
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
        
        if self.path == "/search":
            result = self._handle_search(data)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif self.path == "/query":
            result = self._handle_query(data)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif self.path == "/index":
            result = self._handle_index()
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        
        elif self.path == "/clear":
            self.vector_store.clear()
            self._set_headers()
            self.wfile.write(json.dumps({"success": True}).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())
    
    def _handle_search(self, data):
        """Semantische Suche"""
        query = data.get("query", "")
        top_k = data.get("top_k", 5)
        
        if not query:
            return {"error": "Keine Suchanfrage angegeben"}
        
        results = self.vector_store.search(query, top_k)
        return {
            "query": query,
            "results": results,
            "total": len(results)
        }
    
    def _handle_query(self, data):
        """RAG Query: Suche + KI-Antwort"""
        query = data.get("query", "")
        model = data.get("model", CHAT_MODEL)
        
        if not query:
            return {"error": "Keine Anfrage angegeben"}
        
        # 1. Semantische Suche
        search_results = self.vector_store.search(query, 3)
        
        # 2. Kontext aus den Suchergebnissen bauen
        context_parts = []
        sources = []
        for r in search_results:
            context_parts.append(f"Aus: {r['path']}\n{r['content']}")
            sources.append(r['path'])
        
        context = "\n\n---\n\n".join(context_parts) if context_parts else "Keine relevanten Dokumente gefunden."
        
        # 3. Prompt mit Kontext
        system_prompt = """Du bist ein Wissensassistent für das AI-OS (AI Operating System). 
Beantworte Fragen basierend auf dem folgenden Kontext aus der Wissensdatenbank.
Wenn die Antwort nicht im Kontext zu finden ist, sage das ehrlich.
Antworte auf Deutsch und verweise auf die Quellen."""
        
        user_prompt = f"""Kontext aus der Wissensdatenbank:
{context}

Frage: {query}

Antworte basierend auf dem Kontext. Nenne die Quellen am Ende."""
        
        # 4. KI-Antwort generieren
        try:
            payload = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 1024
                }
            }).encode("utf-8")
            
            req = urllib.request.Request(
                f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
                answer = result.get("message", {}).get("content", "")
            
            return {
                "query": query,
                "answer": answer,
                "sources": sources,
                "context_used": len(context_parts) > 0
            }
        except Exception as e:
            return {
                "query": query,
                "answer": f"Fehler bei der Generierung: {str(e)}",
                "sources": sources,
                "error": str(e)
            }
    
    def _handle_index(self):
        """Indiziere die Wissensdatenbank neu"""
        count = self.vector_store.index_knowledge_base()
        return {
            "success": True,
            "indexed": count,
            "total": len(self.vector_store.documents)
        }


def main():
    """Startet den Knowledge Agent"""
    print(f"\n{'='*50}")
    print(f"📚 AI-OS Knowledge Agent")
    print(f"{'='*50}")
    print(f"📍 Host: http://localhost:{AGENT_PORT}")
    print(f"📁 Vektordatenbank: {VECTOR_DB_PATH}")
    print(f"🔧 Embedding-Modell: {EMBED_MODEL}")
    print(f"{'='*50}\n")
    
    # Initialisiere Vektordatenbank
    vector_store = SimpleVectorStore(VECTOR_DB_PATH)
    
    # Prüfe ob Embedding-Modell verfügbar ist
    try:
        test_embedding = vector_store.get_embedding("Test")
        if test_embedding:
            print(f"✅ Embedding-Modell '{EMBED_MODEL}' verfügbar")
        else:
            print(f"⚠️ Embedding-Modell '{EMBED_MODEL}' nicht verfügbar")
            print(f"   Installiere mit: ollama pull {EMBED_MODEL}")
    except:
        print(f"⚠️ Konnte Embedding-Modell nicht testen")
    
    # Starte Server mit eigener Handler-Klasse
    handler = type('Handler', (KnowledgeAgentHandler,), {
        '__init__': lambda self, *args, **kwargs: KnowledgeAgentHandler.__init__(self, *args, **kwargs)
    })
    
    # Korrigiere: Erstelle eine Instanz mit der VectorStore-Referenz
    class AgentHandler(BaseHTTPRequestHandler):
        vector_store = vector_store
        
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
                    "documents": len(self.vector_store.documents),
                    "embeddings": len(self.vector_store.embeddings)
                }).encode())
            elif self.path == "/stats":
                self._set_headers()
                self.wfile.write(json.dumps({
                    "documents": len(self.vector_store.documents),
                    "embeddings": len(self.vector_store.embeddings),
                    "db_path": str(VECTOR_DB_PATH)
                }).encode())
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
            
            if self.path == "/search":
                query = data.get("query", "")
                top_k = data.get("top_k", 5)
                if not query:
                    result = {"error": "Keine Suchanfrage"}
                else:
                    result = {"query": query, "results": self.vector_store.search(query, top_k)}
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            elif self.path == "/query":
                query = data.get("query", "")
                model = data.get("model", CHAT_MODEL)
                if not query:
                    self._set_headers()
                    self.wfile.write(json.dumps({"error": "Keine Anfrage"}).encode())
                    return
                
                search_results = self.vector_store.search(query, 3)
                context_parts = []
                sources = []
                for r in search_results:
                    context_parts.append(f"Aus: {r['path']}\n{r['content']}")
                    sources.append(r['path'])
                context = "\n\n---\n\n".join(context_parts) if context_parts else "Keine relevanten Dokumente gefunden."
                
                try:
                    payload = json.dumps({
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "Du bist ein Wissensassistent. Antworte basierend auf dem Kontext. Antworte auf Deutsch."},
                            {"role": "user", "content": f"Kontext:\n{context}\n\nFrage: {query}"}
                        ],
                        "stream": False,
                        "options": {"temperature": 0.3, "num_predict": 1024}
                    }).encode("utf-8")
                    
                    req = urllib.request.Request(
                        f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/chat",
                        data=payload,
                        headers={"Content-Type": "application/json"},
                        method="POST"
                    )
                    with urllib.request.urlopen(req, timeout=120) as resp:
                        result = json.loads(resp.read())
                        answer = result.get("message", {}).get("content", "")
                    
                    self._set_headers()
                    self.wfile.write(json.dumps({
                        "query": query, "answer": answer, "sources": sources
                    }).encode())
                except Exception as e:
                    self._set_headers(500)
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            
            elif self.path == "/index":
                count = self.vector_store.index_knowledge_base()
                self._set_headers()
                self.wfile.write(json.dumps({"success": True, "indexed": count}).encode())
            
            elif self.path == "/clear":
                self.vector_store.clear()
                self._set_headers()
                self.wfile.write(json.dumps({"success": True}).encode())
            
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())
    
    server = HTTPServer(("127.0.0.1", AGENT_PORT), AgentHandler)
    print(f"✅ Knowledge Agent läuft auf Port {AGENT_PORT}")
    print(f"📋 Verfügbare Endpunkte:")
    print(f"   GET  /              - Status")
    print(f"   GET  /stats         - Statistiken")
    print(f"   POST /search        - Semantische Suche")
    print(f"   POST /query         - RAG Query (Suche + KI)")
    print(f"   POST /index         - Wissensdatenbank indizieren")
    print(f"   POST /clear         - Vektordatenbank leeren\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Knowledge Agent gestoppt")
        server.server_close()

if __name__ == "__main__":
    main()