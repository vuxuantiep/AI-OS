# Lokale LLM-Motoren im Browser (WebLLM/wllama/native/Ollama) — Architektur + Bugs

*Ingest-Quelle: Broki-AI-Backend-Sessions 22.–23.07.2026. Kontext zum Produkt:
[[Broki-AI]]. Generisches Debugging-Muster: [[MV3-Offscreen-Dokumente-Debugging]].*

## Das Motor-Fallback-Muster

Ein agnostisches LLM-Gateway probiert mehrere KI-Engines der Reihe nach
durch, erster verfügbarer gewinnt (Muster in `modules/llm-gateway.js`,
übertragbar auf jedes Projekt mit "mal lokal, mal Cloud, mal je nach
Gerät"-Anforderung):

1. **Native On-Device-KI** (Prompt API: `window.ai`/`LanguageModel`) — 0 MB
   Download, sofort da, aber nur auf sehr neuen Browsern verfügbar.
2. **WebLLM** (WebGPU) — schnell, aber nur wenn WebGPU verfügbar ist.
3. **wllama** (WebAssembly/CPU) — läuft praktisch überall, langsamer.
4. **Ollama per HTTP** (`fetch()` gegen `127.0.0.1:11434`) — nur als
   Notlösung/Power-User-Option, siehe Warnung unten.
5. **Cloud-Fallback** — nur im expliziten Cloud-Modus.

**Wichtige Design-Entscheidung, aus einem echten Zielkonflikt gelernt:**
Motor 4 (Ollama) liefert deutlich bessere Antwortqualität als Motor 2/3, hat
aber einen entscheidenden Nachteil — er braucht eine SEPARATE, bereits
laufende Installation neben der Extension/App. Wenn das Verkaufsargument
"nur installieren, fertig" ist (typisch für Browser-Extensions/lokale Tools
an nicht-technische Endkunden), untergräbt ein Ollama-Motor als STANDARD
genau dieses Argument. Ollama gehört ans Ende der Kette, nicht an den
Anfang — auch wenn er during Debugging der bequemste/zuverlässigste Weg ist.

## Bug 1: Ollama blockt Browser-Extension-Requests per CORS (HTTP 403)

Ollama akzeptiert standardmäßig KEINE Requests mit
`Origin: chrome-extension://...` (Standard-`OLLAMA_ORIGINS`-Allowlist kennt
das Schema nicht). Trügerisch: ein GET auf `/api/tags` (reiner Reachability-
Ping) braucht keinen CORS-Preflight und geht klaglos durch — täuscht
"Ollama ist erreichbar" vor, während der eigentliche POST auf `/api/chat`
(oder `/api/embeddings`) am Preflight mit 403 scheitert. **Ein Ping-Erfolg
beweist NICHT, dass die eigentliche Nutzlast durchkommt.**

**Fix**: `OLLAMA_ORIGINS` als Umgebungsvariable auf die exakte Extension-ID
setzen (`chrome-extension://<id>`, sicherer als der Wildcard `*` — least
privilege), Ollama-Prozess neu starten. Schnell verifizierbar per
`curl -H "Origin: chrome-extension://<id>" -X POST http://127.0.0.1:11434/api/chat ...`
— deutlich schneller als ein voller Browser-Testzyklus.

## Bug 2 (der Hauptfund): wllama cached JEDES Modell, aber die Cache-API akzeptiert keine chrome-extension://-URLs

wllamas vendorte `utils.js` (`_loadBinaryResource`) versucht jedes über
`loadModelFromUrl()` geladene Modell automatisch per
`caches.open()`/`cache.put()` in der Browser-Cache-Storage-API
zwischenzuspeichern. Die Cache-API akzeptiert aber laut Spec NUR
`http(s)://`-URLs als Schlüssel — lädt eine Extension ihr eigenes Modell über
`chrome.runtime.getURL(...)` (→ `chrome-extension://...`), wirft
`cache.put()` einen Fehler: `"Failed to execute 'put' on 'Cache': Request
scheme 'chrome-extension' is unsupported"`.

Der Fehler passiert in einem ungesicherten XHR-`onload`-Handler — das
eigentliche Lade-Promise wird dadurch NIE resolved noch rejected. Sichtbares
Symptom: die Operation hängt für immer, teils sichtbar als kryptisches
`"[object ProgressEvent]"` (wenn `String(error)` naiv auf das Event
angewendet wird), teils als reines, endloses Einfrieren ohne jede
Fehlermeldung. Dieser Bug hat in der Broki-Session tagelang als
unerklärlicher WASM/Threading-Bug gegolten, bis das Debugging-Muster aus
[[MV3-Offscreen-Dokumente-Debugging]] ihn root-cause-te.

**Fix**: `window.caches` im ausführenden Kontext (z.B. Offscreen-Dokument)
VOR dem Import von wllama deaktivieren:
```js
Object.defineProperty(self, "caches", { value: undefined, configurable: true });
```
Damit betritt wllamas eigener `if (window.caches)`-Zweig gar nicht erst den
kaputten Cache-Pfad. **Nicht in der vendorten `utils.js` selbst patchen**,
wenn diese per `npm run build:vendor`/Gitignore bei jedem Rebuild
überschrieben wird — der Fix muss im eigenen, versionierten Code sitzen.

**Übertragbarkeit**: Dieser Bug betrifft vermutlich JEDES Projekt, das
`@wllama/wllama` (mind. Version 1.0.0) innerhalb einer Browser-Extension
(oder generell von einer `chrome-extension://`/`moz-extension://`-URL aus)
nutzt — nicht Broki-spezifisch.

## Bug 3: deviceMemory-basierte Modellstufen ohne Existenzprüfung

Ein häufiger Folgefehler bei RAM-abhängiger Modellwahl: die Konfiguration
verweist auf eine Modell-Datei, die das Download-Skript nie heruntergeladen
hat (Config und Download-Skript driften auseinander). Symptom: für Nutzer in
der betroffenen RAM-Klasse schlägt das Laden mit "Datei nicht gefunden" fehl
und der Motor fällt (oft stillschweigend) auf den nächsten in der Kette
zurück — leicht zu übersehen, weil es nur bestimmte Geräteklassen betrifft.
**Lehre**: Modellstufen-Konfiguration und Download-Skript müssen bei jeder
Änderung synchron geprüft werden (z.B. per einfachem Existenz-Check beim
Extension-Start, nicht nur beim manuellen Download-Lauf).

## Bug 4: große Modelle (~1GB+) können den Renderer-Prozess crashen

Ein XHR-basiertes Laden des gesamten Modells als ein einziger großer
`ArrayBuffer` (statt Streaming) kann bei Dateien im Bereich von ~1GB+ den
gesamten Renderer-Prozess zum Absturz bringen (beobachtet: nicht nur das
Offscreen-Dokument, sondern auch eine im selben Prozess laufende normale
Seite wurde mit heruntergerissen). Nur deutlich kleinere Modelle (~500MB)
liefen bisher stabil. Noch nicht abschließend gelöst — TODO: RAM-Profiling,
eventuell Streaming/Sharding größerer Modelle statt einer einzigen Anfrage.

## Related

- [[Broki-AI]] — das Produkt, in dem diese Bugs gefunden wurden
- [[MV3-Offscreen-Dokumente-Debugging]] — das Debugging-Muster, das Bug 2 löste
- Claude-Memory: `project-broki-ai` (vollständige Session-Chronologie inkl.
  aller Zwischenschritte und verworfener Hypothesen)
