# Chrome MV3 Offscreen-Dokumente — Fallstricke + Debugging-Muster

*Ingest-Quelle: Broki-AI-Backend-Sessions 22.–23.07.2026 (echte, reproduzierte
Bugs, keine Spekulation). Generisches Wissen — gilt für JEDE Manifest-V3-
Extension in diesem AI-OS, nicht nur Broki. Details/Kontext: [[Broki-AI]].*

## Was Offscreen-Dokumente sind und wofür man sie braucht

Ein Offscreen-Dokument ist eine normale (unsichtbare) Seite MIT DOM, die eine
MV3-Extension per `chrome.offscreen.createDocument()` erzeugen kann. Nötig,
weil ein Service Worker (der `background.js`-Kontext in MV3) laut HTML-Spec
KEIN dynamisches `import()` ausführen darf ("import() is disallowed on
ServiceWorkerGlobalScope") — jede WASM/WebGPU-lastige Arbeit (WebLLM, wllama,
Clipboard, Audio) muss deshalb in ein Offscreen-Dokument ausgelagert werden.
Kommunikation läuft über den normalen Message-Bus:
`chrome.runtime.sendMessage({ target: "offscreen", ... })`, wobei der
Service-Worker-Handler `target === "offscreen"`-Nachrichten explizit
ignoriert (`return false`), damit nicht zwei Handler gleichzeitig antworten.

## Fallstrick 1: Offscreen-Dokumente sind für Browser-Automatisierung unsichtbar

Playwright (und vermutlich jedes andere CDP-basierte Tool, auch "Browser
Use" o.ä. — dieselbe zugrundeliegende Einschränkung) verfolgt `context.on
("page", ...)` NUR für normale Tabs/Popups. Offscreen-Dokumente tauchen dort
NIE auf — jeder `console.log()` darin ist für automatisierte Tests praktisch
unsichtbar. Das hat in der Broki-Session wiederholt zu falschen Annahmen
geführt ("das Logging zeigt nichts" wurde fälschlich als "der Code läuft
nicht" interpretiert, obwohl der Code lief, nur die Ausgabe nie ankam).

## Fallstrick 2: Offscreen-Dokumente haben NICHT alle Extension-APIs

Empirisch verifiziert (23.07.2026): `chrome.storage` ist im Offscreen-
Dokument-Kontext selbst `undefined`, obwohl die Extension die Berechtigung
`"storage"` im Manifest hat. Offscreen-Dokumente bekommen nur eine
eingeschränkte API-Teilmenge — welche APIs genau verfügbar sind, ist nicht
vollständig dokumentiert, also im Zweifel IMMER direkt testen statt annehmen.

## Debugging-Muster, das beide Fallstricke gleichzeitig umgeht

Wenn weder Browser-Automatisierung noch direktes In-Context-Logging (wegen
Fallstrick 2) funktionieren: **den Service Worker als Relais nutzen.**

1. Offscreen-Dokument schickt Fortschritts-Checkpoints per
   `chrome.runtime.sendMessage({ typ: "irgendein-checkpoint", daten: {...} })`
   — normale Messages, kein `target: "offscreen"`, landen also beim Service-
   Worker-Handler.
2. Der Service Worker (voller API-Zugriff) schreibt sie in
   `chrome.storage.local.set(...)`.
3. Ein Test/eine Diagnose liest `chrome.storage.local.get(...)` aus — das
   funktioniert unabhängig davon, ob das Offscreen-Dokument zwischenzeitlich
   abgestürzt ist, weil `chrome.storage` auf Platte persistiert und vom
   (dann toten) Offscreen-Kontext unabhängig ist.
4. Zusätzlich lohnt sich `self.addEventListener("unhandledrejection", ...)`
   im Offscreen-Dokument — Fehler, die in nicht abgesicherten Callbacks
   (z.B. XHR-`onload`-Handlern) auftreten, werden sonst NIE sichtbar, weder
   im Test noch im echten Betrieb.

Dieses Muster war der entscheidende Schlüssel, um einen seit Tagen
unerklärlichen `"[object ProgressEvent]"`-Bug in wllama root-zucausen (siehe
[[Lokale-LLM-Motoren-Browser]]) — reine Spekulation über mögliche Ursachen
(WASM-Crash, SharedArrayBuffer, Threading) hatte vorher tagelang zu nichts
geführt.

## Fallstrick 3: `page.evaluate()`/`sw.evaluate()` auf langsame Cross-Context-Roundtrips ist instabil

Playwright-Aufrufe, die auf eine langsame Offscreen-Antwort warten (z.B.
Modell-Laden über mehrere Sekunden), enden gehäuft mit
`TargetClosedError: Target page, context or browser has been closed` —
vermutlich weil der Service Worker oder die Seite mitten im Warten recycelt/
beendet wird. Workaround: Nachrichten "fire-and-forget" abschicken (nicht in
einem einzigen `evaluate()`-Aufruf auf die volle Antwort warten), dann
separat per Polling (`chrome.storage.local` o.ä.) den Fortschritt abfragen.

## Related

- [[Broki-AI]] — das Produkt, in dem diese Bugs gefunden wurden
- [[Lokale-LLM-Motoren-Browser]] — der konkrete wllama-Bug, der mit diesem
  Muster gelöst wurde
- Claude-Memory: `project-broki-ai` (vollständige Session-Chronologie)
