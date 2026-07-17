#!/usr/bin/env python3
"""Selbsttest der Feed-Scraper-Wasm-Komponente (Phase 1).

Startet Wassette als HTTP-MCP-Server, ruft das Komponenten-Tool auf und prüft:
  1. Erlaubter Feed-Host liefert Items (Funktionstest)
  2. Nicht freigegebener Host wird von der Sandbox verweigert (Sicherheitstest)

Aufruf:  python test-scraper.py
Voraussetzung: Komponente ist geladen + Policy gesetzt (siehe README).
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WASSETTE = os.path.expanduser(r"~\Tools\wassette\wassette.exe")
URL = "http://127.0.0.1:9001/mcp"
TOOL = "local_feed-scraper_scraper_fetch-feed"
FEED_ERLAUBT = "https://www.tagesschau.de/index~rss2.xml"
FEED_VERBOTEN = "https://example.com/feed.xml"

_session = {"id": None}


def rpc(method, params, id=None):
    body = {"jsonrpc": "2.0", "method": method, "params": params}
    if id is not None:
        body["id"] = id
    headers = {"Content-Type": "application/json",
               "Accept": "application/json, text/event-stream"}
    if _session["id"]:
        headers["Mcp-Session-Id"] = _session["id"]
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers=headers)
    resp = urllib.request.urlopen(req, timeout=60)
    if resp.headers.get("Mcp-Session-Id"):
        _session["id"] = resp.headers["Mcp-Session-Id"]
    raw = resp.read().decode()
    for line in raw.splitlines():
        if line.startswith("data:"):
            return json.loads(line[5:])
    return json.loads(raw) if raw.strip() else None


def tool_text(antwort):
    try:
        return antwort["result"]["content"][0]["text"]
    except (KeyError, IndexError):
        return json.dumps(antwort)


def main():
    print("🚀 Starte Wassette-Testserver …")
    server = subprocess.Popen([WASSETTE, "serve", "--streamable-http"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(3)
        rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                           "clientInfo": {"name": "test-scraper", "version": "0.1"}}, 1)
        rpc("notifications/initialized", {})

        print(f"\n📡 TEST 1 — erlaubter Feed ({FEED_ERLAUBT}):")
        text = tool_text(rpc("tools/call", {"name": TOOL,
                                            "arguments": {"url": FEED_ERLAUBT}}, 2))
        daten = json.loads(text)
        if "ok" in daten:
            items = daten["ok"]
            print(f"   ✅ {len(items)} Items empfangen. Beispiel:")
            print(f"      „{items[0]['titel'][:70]}“ ({items[0]['datum']})")
        else:
            print(f"   ❌ FEHLGESCHLAGEN: {text[:200]}")
            return 1

        print(f"\n🔒 TEST 2 — verbotener Host ({FEED_VERBOTEN}), MUSS scheitern:")
        text2 = tool_text(rpc("tools/call", {"name": TOOL,
                                             "arguments": {"url": FEED_VERBOTEN}}, 3))
        if "err" in text2 and ("verweigert" in text2 or "error" in text2.lower()):
            print("   ✅ Sandbox hat den Zugriff verweigert (deny-by-default wirkt).")
        else:
            print(f"   ❌ ACHTUNG: Zugriff wurde NICHT blockiert! Antwort: {text2[:200]}")
            return 1

        print("\n🎉 Beide Tests bestanden — Komponente funktioniert und ist eingesperrt.")
        return 0
    finally:
        server.terminate()
        print("🧹 Testserver gestoppt.")


if __name__ == "__main__":
    sys.exit(main())
