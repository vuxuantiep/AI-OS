# 📋 Aktuelle Arbeiten — Arbeitsjournal

> Tägliche Dokumentation der kompletten Arbeit am AI-OS (von Claude geführt).
> Zweck: Überblick behalten + aus dem Code lernen. Neuester Tag oben.
> Details zur Architektur: [[../../docs/AI-Engineering-Roadmap|Roadmap]] · Lernguide: `docs/AI-OS-Backend-Lernguide.html`

---

## 2026-07-15 (Tag 5) — Usecase 3: „AI Business Checker" geplant

### Was heute entstanden ist

Dritter Usecase fürs KI-Avatar-Produkt: **AI Business Checker** — YouTube-Kanal +
TikTok-Shorts, der „Geld verdienen mit KI"-Anbieter auf Seriosität prüft
(Warnung/Aufklärung, Animation statt Avatar).

1. **Plan** (`01_Usecases/usecase-ai-business-checker.md`): Kanal-Konzept mit
   4 wiederkehrenden Formaten, angepasste Pipeline (Research-Scan → Scoring →
   **Dossier** → Skript → Stimme → **Animation** → Edit → QA/Legal → Posting),
   Monetarisierung (bewusst KEINE Affiliates → Unabhängigkeit), 4-Phasen-Roadmap.
   Animation via Remotion-Templates = einzige bezahlte API (HeyGen) entfällt hier.
2. **Market-Research-Agent** (`Konzept-KI Avatar/market-research-agent.md`):
   Quellen-Prioritäten (amtlich > dokumentierend > Community), Warnsignal-Katalog
   W1–W8, JSON-Dossier-Format mit Beleg-Pflicht (URL + Zitat + Datum),
   Scoring-Rubrik, harte Verhaltensregeln (2-Quellen-Minimum, neutrale Sprache,
   Positivbefunde melden — Agent ist Rechercheur, kein Richter).
3. **Compliance-Critic-Agent → Check 7 „Äußerungsrecht"**: verbotene Begriffe
   ohne Urteil („Betrug") = Block, jede Tatsachenbehauptung muss dem Dossier
   zuordenbar sein, 2-Quellen-Minimum, Stellungnahme-Pflicht bei Deep-Dives
   (Verdachtsberichterstattung!). Neues Schema-Feld `aeusserungsrecht`.
4. **Board erweitert**: dritter Usecase mit eigenem Filter-Chip + Badge-Farbe,
   Label-Mapping von hartkodiertem Ternary auf `UC_LABEL`-Map umgestellt.

### Wichtigste Design-Entscheidung (gelernt)

Bei einem Prüf-/Warn-Kanal ist **Äußerungsrecht der härteste Blocker**, nicht
Plattform-Compliance: Eine falsche Tatsachenbehauptung über einen benannten
Anbieter = Abmahnung. Deshalb Dossier-Stufe als Pflicht-Input VOR dem Skript
(keine Behauptung ohne Beleg-Datensatz) statt Legal-Check erst am Ende.

### Nachtrag: Wirtschaftlichkeits-Gate als neue Pflicht-Regel

Neue CEO-Anweisung dauerhaft verankert: Jede neue Produktplanung enthält ab jetzt
einen **Wirtschaftlichkeits-Prüfer-Agenten**, und Umsetzung startet erst nach Freigabe.

1. **Agent-Prompt** (`10_Business/wirtschaftlichkeits-pruefer-agent.md`, wiederverwendbar
   für alle Produkte): Marktbedarf → Einnahmequellen-Inventar (mit Voraussetzungen +
   „fließt ab Monat X") → 3-Szenarien-Rechnung (P70/P50/P20 mit Anlaufkurve) →
   Kosten inkl. Arbeitszeit → Break-even → GO/GO_MIT_AUFLAGEN/PIVOT/NO_GO.
   Wichtigste Regeln: keine Zahl ohne Herkunft, €/Arbeitsstunde immer ausweisen
   (versteckte Selbstausbeutung!), Monat 1–6 bei Content ≈ 0 € ehrlich einplanen.
2. **Erste Anwendung** (`wirtschaftlichkeit-ai-business-checker.md`): Marktbedarf 7/10,
   5 Einnahmequellen (Affiliate bewusst ausgeschlossen), Basis-Szenario ~250–450 €/Mon.
   in Monat 12, Break-even Cash Monat ~9–10, ABER nur ~8–10 €/h — der echte Hebel ist
   die Pipeline-Wiederverwendung über alle 3 Usecases + Digitalprodukt in Jahr 2.
   → **GO_MIT_AUFLAGEN** (3-Monats-Meilenstein, 15h/Woche- und 500-€-Deckel),
   Status WARTET_AUF_FREIGABE.
3. **CLAUDE.md**: als Arbeitsregel 4 „Wirtschaftlichkeits-Gate" eingetragen
   (Secrets rückte auf 5), zusätzlich als Feedback-Memory gespeichert.

### Nachtrag 2: CEO-Freigabe erteilt → Phase 0 umgesetzt

**Freigabe 15.07.2026** (GO_MIT_AUFLAGEN dokumentiert), danach beide Phase-0-Bausteine gebaut:

1. **Market-Research-Agent v1** (`research-agent/app.py`, Flask :5320, im Dashboard
   als Dienst registriert): scannt Reddit + Verbraucherdienst-Blog + Watchlist
   Internet (optional SearXNG via env), bewertet gegen Warnsignal-Katalog W1–W8
   (Regex-Heuristik) + KI-Relevanz-Filter, dedupliziert, persistiert atomar.
   API: `/api/scan` (POST), `/api/funde?empfehlung=video_kandidat`, CLI `--scan`.
   **Erster Live-Scan: 104 Funde, 2 Video-Kandidaten** (Deepfake-Promi-Werbung),
   „Peak Momentum Erfahrungen" auf der Beobachtungsliste — das Format trägt.
2. **Remotion-Template-Set** (`animation/`): CheckerLong (16:9) + CheckerShort
   (9:16) als EIN datengetriebenes Template — Dossier-JSON rein, Video raus.
   Szenen: Intro → Warnsignal-Karten (Zitat + Quellenleiste) → animierter
   Risiko-Score (Ampelfarben) → Checklisten-Outro. KI-Label ab Sekunde 1 fest
   eingebaut (Art. 50). Dauer wächst via `calculateMetadata` automatisch mit
   der Warnsignal-Anzahl. **Test-Render: 14-s-Short komplett (420 Frames, 1,8 MB)**
   + 2 Preview-Frames visuell geprüft.

**Stolpersteine des Tages:**
- Reddits JSON-API liefert pauschal 403 (auch mit Browser-UA) — die **RSS-Endpunkte
  (`old.reddit.com/.../search.rss`) funktionieren**. Merke: bei Reddit-Scraping
  ohne OAuth immer RSS statt JSON. Zusätzlich ≥4 s Pause, sonst 429.
- Watchlist Internet: Feed liegt unter `/rss/`, nicht `/rss.xml`.
- Feed-Parser namespace-agnostisch bauen (`tag.split('}')[-1]`), damit RSS 2.0
  UND Atom (Reddit) mit demselben Code funktionieren.

### Nachtrag 3: Research-Agent global + eigene Quellen (CEO-Wunsch)

1. **Globale Quellen eingebaut** (Kanal-Ziel: weltweite Sichtbarkeit, DE + US + VN):
   FTC Consumer Alerts + FTC Consumer Protection News (USA), VnExpress Pháp
   luật/Số hóa + Tuổi Trẻ Pháp luật (Vietnam). Warnsignal-Muster jetzt
   dreisprachig DE/EN/VI („lừa đảo", „việc nhẹ lương cao", „đa cấp", „earn $X/day").
   Scan-Verteilung nach Umbau: 81 AT, 22 VN, 13 US, 14 Reddit ✓
2. **Eigene-Quellen-Feature**: Eingabe-Box auf der Startseite — URL rein,
   `erkenne_quelle()` prüft automatisch: direkter RSS/Atom-Feed? In der HTML-Seite
   verlinkter Feed (`<link type="application/rss+xml">`)? Sonst Seiten-Scan
   (sichtbarer Text, Inhalts-Hash in der Dedup-URL → geänderte Seite = neuer Fund).
   API: GET/POST/DELETE `/api/quellen`, Persistenz `data/custom_sources.json`.
   Getestet: WordPress-Blog → Feed autodetected ✓, ScamAdviser → Seiten-Scan ✓.

### Nachtrag 4: AI Business Checker im Dashboard sichtbar

Dritte Produktkarte im Produkte-Tab (🔎 AI Business Checker, Status-Pill +
Öffnen-Button). Dafür den ki-avatar-Proxy zu `PRODUKT_PROXIES` verallgemeinert
(Dict prod→Port, Dispatching weiter in `serve_produkt`): `/produkte/ai-checker/`
→ :5320. Status-Check im Frontend als Schleife über `PRODUCT_SERVICES` statt
Einzelfunktion. Proxy-Timeout 15→300 s, weil der Scan-Button über den Proxy
einen 1–2-Minuten-POST macht. Getestet: alle 3 Produkte via :5000 erreichbar,
Checker-Health über Proxy 200 ✓.

---

## 2026-07-14 (Tag 4) — KI-Avatar: Produktstart + Pipeline-Board (Port 5310)

### Was heute entstanden ist

Neues Business-Produkt **KI-Avatar** unter `10_Business/KI-Avatar/` gestartet
(2 Usecases: YouTube-Automation, TikTok-Shop) — inkl. Trello-artigem
**Pipeline-Board** als AI-OS-Erweiterung:

1. **Compliance-Critic-Agent überarbeitet** (`Konzept-KI Avatar/compliance-critic-agent.md`):
   - Batch-Schema um Felder ergänzt, die der Prüfkatalog referenzierte, aber nie bekam
     (`transcript`, `duration_seconds`, `daily_shoppable_count`, `channel_metadata`, `native_ai_label_set`)
   - Enum-Bug `youtube_short` vs. `youtube_shorts` gefixt
   - Explizite Status-Ableitungsregel (fail→BLOCKED, warning→APPROVED_WITH_WARNING)
   - Art. 50 EU-KI-VO plattformunabhängig gemacht (gilt ab 02.08.2026!)
   - False-Positive-Schutz: "Geld-zurück-Garantie" ≠ Heilsversprechen

2. **Pipeline-Board** (`board/app.py` + `templates/board.html`, Flask, Port 5310):
   - 8 Spalten = Pipeline-Stufen (Trend-Scan → … → Posting → Veröffentlicht)
   - Karten = Videos: Usecase, Plattform, Kanal, Compliance-Status, Notizen
   - Drag & Drop (HTML5, optimistisches Update mit Rollback bei API-Fehler)
   - Usecase-Filter-Chips, Farben wie im Architektur-Diagramm
     (türkis = selbst gehostet, koralle = externe API, grau = Ein-/Ausgabe)
   - REST-API: GET /api/board, POST/PUT/DELETE /api/cards, POST /api/cards/id/move
   - Persistenz: `board/data/board.json` (atomares Schreiben via tmp + os.replace)

### Was ich dabei gelernt/beachtet habe

- **LLM-Agent-Prompts brauchen ein vollständiges Eingabe-Schema:** Jede Prüfung im
  Prompt, für die kein Eingabefeld existiert, zwingt das Modell zum Raten. Regel:
  erst Felder definieren, dann Prüfungen darauf aufbauen — und für fehlende
  optionale Felder explizit `manual_review`/`n/a` vorschreiben statt Block.
- **Bekannte Stolpersteine vorab entschärft:** JS aus dem Template extrahiert und
  mit `node --check` geprüft (Dashboard-Lektion), `sys.stdout.reconfigure(utf-8)`
  gegen den Windows-Print-Bug, eigener Port 5310 statt 5000 (keine Zombie-Kollision).
- **Atomares JSON-Schreiben** (`tmp` + `os.replace`) verhindert kaputte board.json
  bei Absturz mitten im Schreiben.

### Verifikation

Server gestartet, komplette API durchgetestet: Health ✓, Board laden (8 Stufen,
Seed-Karten) ✓, Karte anlegen ✓, verschieben ✓, Compliance updaten ✓, ungültige
Stufe → 400 ✓, löschen ✓, Startseite HTTP 200 ✓, JS/Python-Syntax ✓.

### Nachtrag (gleicher Tag): Dashboard-Integration „Produkte"-Tab

Beide Produkte ins AI-OS-Dashboard eingruppiert:

1. **Neuer Nav-Tab „🛍️ Produkte“** (`templates/dashboard.html`) — ersetzt den
   einzelnen DocuCheck-Button. Panel mit Produktkarten (service-card-Stil):
   DocuCheck Local + KI-Avatar Pipeline-Board, je mit Beschreibung, Status-Pill
   und Öffnen-Button. Deep-Link `/#products` funktioniert über den bestehenden
   Hash-Mechanismus automatisch.
2. **Proxy `/produkte/ki-avatar/` → 127.0.0.1:5310** (`ai_os_dashboard.py`) —
   bewusst Proxy statt Direktlink auf `localhost:5310`: über Cloudflare-Tunnel
   und Tailscale ist nur Port 5000 exponiert; so ist das Board auch remote
   nutzbar. GET/POST/PUT/DELETE werden mit Body + Content-Type durchgereicht,
   bei Offline-Board kommt eine 503-Seite mit Startbefehl.
3. **Board auf relative API-Pfade umgestellt** (`board.html`: `api()` strippt
   führenden Slash) — dieselbe Datei funktioniert standalone (`/api/board`)
   und hinter dem Proxy (`/produkte/ki-avatar/api/board`). Der ⌂-AI-OS-Link
   zeigt hinter dem Proxy auf `/` statt hart auf `localhost:5000`.
4. **Dienst-Registrierung**: KI-Avatar Board als SERVICES-Eintrag (Port 5310,
   `health_path: /api/health`, Layer 10_Business) — erscheint im Dienste-Tab
   und ist von dort startbar; `app.py` liest jetzt `KIAVATAR_BOARD_PORT` aus.

**Gelernt (durch Test widerlegte Annahme!):** Ich hatte erwartet, dass Werkzeug
die spezifischere Route `/produkte/ki-avatar/<path>` vor `/produkte/<prod>/<path>`
matcht — tut es NICHT: die generische Route gewann, der Proxy bekam nie Requests
(Symptom: `{"error": "Unbekanntes Produkt"}` + 405 bei POST). Lösung: keine
konkurrierende Route, sondern Dispatching **innerhalb** von `serve_produkt`
(`if prod == "ki-avatar": return _kiavatar_proxy(...)`). Merksatz: Bei
überlappenden Flask-Routen nie auf Prioritätsregeln verlassen — selbst dispatchen.

**Zombie-Falle erneut bestätigt:** Auf Port 5000 lief noch ein `pythonw` von
GESTERN (13.07., PID 65672) und servierte alten Code, während der neue Server
scheinbar fehlerfrei startete (Windows erlaubt Doppel-Bind). Erst
`Get-NetTCPConnection -LocalPort 5000` + `Stop-Process` machte den Weg frei —
genau wie in der Memory-Notiz dokumentiert.

Außerdem: Ein Sub-Dienst hinter einem Pfad-Proxy darf im Frontend keine
absoluten Pfade (`/api/...`) verwenden, sonst landen die Requests am falschen
Server — deshalb nutzt das Board jetzt relative Pfade.

**End-to-End verifiziert:** Proxy-CRUD komplett (POST/MOVE/DELETE über
`/produkte/ki-avatar/api/...`) ✓, Board-Seite via Proxy HTTP 200 ✓, DocuCheck
weiterhin HTTP 200 ✓, Offline-Fall → 503-Hinweisseite mit Startbefehl ✓,
Produkte-Tab im Dashboard-HTML vorhanden ✓.

---

## 2026-07-12 (Tag 3) — DokuCheck Lokal v0.2: Browser-KI als erstes Produkt

### Was heute entstanden ist

| # | Arbeit | Ort |
|---|--------|-----|
| 1 | **DokuCheck Lokal v0.2** — Prototyp-Monolith zerlegt in saubere App (HTML/CSS/JS, kein Build-Toolchain) | `10_Business/Lokal-SML-Webassembly-MultiMemory/Produkt/dokucheck-lokal/` |
| 2 | **Vendoring statt CDN**: WebLLM 0.2.79, pdf.js 4.4.168, Tesseract.js 5.1.1 + Sprachdaten (deu/eng/vie) lokal eingecheckt | `.../vendor/` |
| 3 | **WebLLM in Web Worker** verschoben — UI bleibt während Inferenz responsiv | `worker.js` |
| 4 | **OCR-Modul** (Bild → Text, WASM, läuft ohne WebGPU) + 📷 Kamera-Aufnahme mobil | `ocr.js` |
| 5 | **Übersetzen** (Deutsch/Englisch/Vietnamesisch) über das geladene SLM — keine neue Bibliothek | `app.js` |
| 6 | **BM25-Retrieval** statt Keyword-Zählen + Map-Reduce-Zusammenfassung für lange Dokumente | `app.js` |
| 7 | **Multi-Memory-Panel** (IndexedDB): Episodic (Verlauf), Semantic (Dokumente), Procedural (Prüfroutinen), Tool (Modellwahl) | `memory/` |
| 8 | **PWA**: installierbar, App-Shell offline (Service Worker), Manifest + Icon | `sw.js`, `manifest.webmanifest` |
| 9 | **Dashboard-Integration**: Route `/produkte/<prod>/` + Nav-Button „🛡️ DokuCheck Lokal" | `ai_os_dashboard.py`, `templates/dashboard.html` |
| 10 | Wiki-Kopie → Redirect-Stub (eine Quelle der Wahrheit) | `00_Wissen/04_Referenzen/Wiki/dokucheck-lokal.html` |
| 11 | **Mehrsprachigkeit DE/EN/VI** — Umschalter in der Beweisleiste, komplette UI + KI-Prompts übersetzt (locker formuliert), Wahl wird in Tool Memory gemerkt | `i18n.js` (107 Schlüssel × 3 Sprachen), `index.html` (`data-i18n`), `app.js` |
| 12 | **Schritt-Führung** — „✓ bereit“-Badges an Schritt 1/2/3, Schritt 3 ausgegraut bis alles bereit ist, dann Anscrollen + Puls-Highlight + grüner Nächster-Schritt-Hinweis | `app.js` (`statusFlow()`), `index.html`, `styles.css` |
| 13 | **Scan-PDF-Rettung** — PDFs ohne Textebene (0 Zeichen extrahiert!) werden erkannt, Seiten als Canvas gerendert und automatisch per OCR gelesen; leere Extraktion wird nie mehr als „✓ fertig“ angezeigt | `app.js` (`ocrPdf()`), `ocr.js` (`ocrWorker` wiederverwendbar) |
| 14 | **Bugfix Übersetzen** — Modell plauderte auf Deutsch („Ich verstehe, dass du möchtest …") statt nach Vietnamesisch zu übersetzen; Übersetzungs-Prompt aus i18n herausgelöst und sprachunabhängig auf Englisch fixiert, Anweisung zusätzlich in der User-Nachricht wiederholt | `app.js` (`uebersetzen()`, `TRANS_ZIEL`), `i18n.js` (`prompt.transSys` entfernt) |
| 15 | **Bugfix falsche OCR-Warnung** — „Texterkennung war unvollständig" erschien auch bei sauberen Text-PDFs: Qualitätsheuristik lief auf JEDEM Dokument und `/(.)\1\1+/` schlug schon bei „…"/„---"/„www" an; jetzt nur noch für echten OCR-Text (`ausOcr`-Flag) + Regex nur Buchstaben 4x+ | `app.js` (`setzeDokument()`, `schaetzeOcrQualitaet()`) |
| 16 | **Auto-Load des Modells** — nach Seiten-Reload blieb Schritt 3 grau, bis man Schritt 1 manuell neu klickte, obwohl die Gewichte im Cache lagen; jetzt lädt das Modell automatisch, sobald ein Dokument bereit ist und `hasModelInCache` zutrifft | `app.js` (`autoLadeModell()`), `i18n.js` (`s1.autoLoad` ×3) |

### Lern-Highlights des Tages (mit Code)

**1. Worker-Fetches sind für den Hauptthread unsichtbar.** Das Signatur-Feature
(Netzwerk-Beweiszähler) wäre durch den Umzug der Engine in den Web Worker blind
geworden: `PerformanceObserver` sieht nur Requests des eigenen Kontexts. Lösung —
zweiter Observer **im Worker**, Meldung per `BroadcastChannel` (stört das
WebLLM-Message-Protokoll nicht, anders als eigene `postMessage`-Typen):

```js
// worker.js
const netChannel = new BroadcastChannel("dokucheck-net");
new PerformanceObserver(list => {
  for (const e of list.getEntries())
    if (e.initiatorType === "fetch") netChannel.postMessage({ kind: "net", url: e.name });
}).observe({ entryTypes: ["resource"] });
```

**2. Windows-Registry sabotiert ES-Module.** Flask/`mimetypes` liest Content-Types
aus der Registry — `.js` kommt dort oft als `text/plain`, und Browser verweigern
dann Module und Worker. Pflicht-Fix im Dashboard:

```python
import mimetypes
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("application/wasm", ".wasm")
```

**3. „Offline" ehrlich definieren.** WebLLM hat keinen WASM/CPU-Fallback (Kernels
sind WebGPU-only) und die Modellgewichte (0,8–2 GB) kommen zwingend einmalig von
HuggingFace. Der ehrliche Claim: *App-Shell + OCR 100 % lokal; Analyse nach
einmaligem Modell-Download offline.* Deshalb zeigt die Beweisleiste jetzt zwei
Zähler: „Modell-Download (einmalig)" vs. „Analyse-Anfragen: 0".

**4. Übersetzen ohne neue Abhängigkeit.** Statt einer Translation-Bibliothek
übersetzt das bereits geladene SLM abschnittsweise (Chunk für Chunk, gestreamt) —
ein System-Prompt genügt.

**5. i18n ohne Framework.** Ein flaches Schlüssel-Objekt pro Sprache + zwei
DOM-Attribute reichen: `data-i18n` (textContent) und `data-i18n-ph` (placeholder).
Der Kniff bei dynamischen Elementen: Das Ausgabefeld trägt anfangs `data-i18n`
für den Platzhalter — sobald eine echte Analyse drinsteht, wird das Attribut
per `removeAttribute` entfernt, sonst würde ein Sprachwechsel das Ergebnis
überschreiben. Gleiches Muster beim „Modell laden“→„Modell wechseln“-Button:
statt nur den Text zu setzen, wird das `data-i18n`-Attribut mit umgestellt.
Wichtig: Die Sprachwahl steuert auch die **Prompts** (`prompt.sys` etc.) —
so antwortet die KI in der UI-Sprache. Die BM25-Suchbegriffe des Risiko-Checks
bleiben dagegen mehrsprachig kombiniert, weil sie zum **Dokument** passen
müssen, nicht zur UI.

### Nachtrag 12.07. abends: DocuCheck-Reparatur nach Fremd-Edits

Ein anderer Agent (Agile Agent Canvas) hatte die App erweitert (Presets, Stepper,
Exporte, OCR-Vorverarbeitung, Umbenennung DokuCheck→DocuCheck) und dabei vier
Fehler eingebaut, die **Schritt 2 komplett lahmlegten**:

1. **`bm25Index` tokenisierte Chunk-Objekte statt `c.text`** → TypeError bei jedem
   Dokument-Upload („s.toLowerCase is not a function"). Der Killer-Bug.
2. **`procedural.js`: nicht geschlossener Blockkommentar in Zeile 1** verschluckte
   Import + alle 5 CRUD-Exports bis zum nächsten `*/` (Zeile 36) — syntaktisch
   gültig (!), daher von `node --check` unsichtbar. Routinen + „Prüfung:"-Preset tot.
3. **`semantic.js`: `return doc`** — Variable existiert nicht → jede Speicherung
   rejected nach dem Schreiben, Dokumentliste blieb leer.
4. **Preset-Modelle (Qwen2 0.5B, Phi 3.5 mini) fehlten im Modell-Dropdown** →
   Profilwahl lief ins Leere, falsches Modell wäre geladen worden.

Dazu repariert: OCR-Vorverarbeitung warf bei Canvas-Quellen (Scan-PDF-Fallback)
weg (`URL.createObjectURL(canvas)` ist illegal) + Object-URL-Leak + `\3`-Oktal-Regex.

**Lehre:** Ein offener Blockkommentar ist der fieseste „Syntaxfehler", weil er
keiner ist — Prüfung ab jetzt zusätzlich: erwartete Exports greppen, nicht nur
`node --check`.

### Nachtrag 12.07.: Übersetzen nach Vietnamesisch war kaputt

Symptom: Statt der Übersetzung kam deutsches Geplauder („Ich verstehe, dass du
möchtest, dass ich den Text vollständig übersetze …"). Ursache: Der
Übersetzungs-Prompt kam aus i18n und war damit in der **UI-Sprache** — ein
deutscher System-Prompt plus roher Text ohne Anweisung in der User-Nachricht
verleitet kleine Modelle dazu, auf Deutsch zu kommentieren statt zu übersetzen.

Fix in `uebersetzen()`: Prompt aus i18n herausgelöst und fest auf Englisch
(SLMs folgen englischen Instruktionen am zuverlässigsten), Zielsprache doppelt
benannt und die Anweisung in der User-Nachricht wiederholt:

```js
const TRANS_ZIEL = { de: "German (Deutsch)", en: "English", vi: "Vietnamese (Tiếng Việt)" };
// system: "You are a translation engine. Translate ... into Vietnamese (Tiếng Việt).
//          Reply with ONLY the translated text ..."
// user:   "Translate the following text into Vietnamese (Tiếng Việt). Output only the translation:\n\n" + chunk
```

**Lehre (korrigiert Highlight 5):** UI-Sprache darf die *Antwortsprache* steuern
(Zusammenfassen, Fragen) — aber nie einen Prompt, dessen Zielsprache der Nutzer
separat wählt. Task-Prompts für SLMs: englisch, Anweisung nah am Text wiederholen.

### Nachtrag 12.07.: v0.3 — Übersetzen ohne LLM (transformers.js + OPUS-MT)

Erkenntnis aus dem Übersetzungs-Bug: Reine Übersetzung ist keine LLM-Aufgabe.
Spezialisierte NMT-Modelle (OPUS-MT/MarianMT, ~45 MB int8 statt ~800 MB SLM)
übersetzen besser, schneller und ohne Geplauder — und laufen als ONNX/WASM
auf der **CPU**, brauchen also kein WebGPU.

**Architektur:**
- `trans-worker.js` — eigener Web Worker mit transformers.js 3.8.1 (gevendort
  inkl. 21-MB-ONNX-Runtime-WASM in `vendor/transformers/`), lazy eine
  `pipeline("translation", ...)` je Sprachpaar, Gewichte einmalig von
  HuggingFace → Browser-Cache (gleiche Beweis-Logik wie WebLLM-Downloads:
  eigener `PerformanceObserver` + BroadcastChannel, in app.js `netPhase="model"`).
- Sprachpaare: `Xenova/opus-mt-{de-en,en-de,en-vi,vi-en}` (auf HF verifiziert);
  **de↔vi existiert nicht** → Pivot über Englisch (de→en→vi).
- Quellsprache heuristisch: vietnamesische Diakritika sind eindeutig,
  Deutsch vs. Englisch per Stoppwort-Zählung.
- MarianMT verkraftet nur ~512 Tokens → Text absatzweise in Satzgruppen
  (~420 Zeichen) zerlegen, `absatzEnde`-Flag erhält die Absatzstruktur.

**UI-Konsequenz:** Übersetzen ist vom SLM entkoppelt — `runAktion(...,
brauchtEngine=false)`, `transBtn` nur noch an Dokument gebunden, Schritt 3
wird schon mit Dokument aktiv (nur Analyse-Buttons warten aufs Modell).
Damit funktioniert Übersetzen erstmals auch auf Geräten **ohne WebGPU**.

**Lehre:** Werkzeug nach Aufgabe wählen — ein 1B-Chat-SLM für Übersetzung
einzusetzen war v0.2-Pragmatismus („keine neue Bibliothek"); das dedizierte
Seq2Seq-Modell ist in jeder Dimension überlegen. Und: `.mjs`-MIME-Type war
im Dashboard zum Glück schon registriert — sonst wäre die ONNX-Runtime
(dynamischer Import von `ort-wasm-simd-threaded.jsep.mjs`) still gestorben.

### Stolpersteine
- `node --check` behandelt `.js` als CommonJS → für ES-Module-Check als `.mjs`-Kopie prüfen.
- Der cp1252-Print-Bug schlug wieder zu (Häkchen-Zeichen im Python-Check) → `PYTHONUTF8=1`.
- Flask-Teststart braucht >6 s (LLM-Router-Init) — nicht zu früh curlen.
- Auf dem Smartphone via LAN/Tailnet: Service Worker + WebGPU verlangen Secure Context —
  über `http://` (nicht localhost) läuft nur OCR; für volle Funktion HTTPS/Tunnel nötig.

---

## 2026-07-10 (Tag 2)

### Was heute entstanden ist

| # | Arbeit | Ort | Commit |
|---|--------|-----|--------|
| 1 | **Qdrant** als 2. Vector-Store (Phase 3b) | `backend/app/rag/qdrant_store.py` | `0ffc4a8` |
| 2 | **Lernguide** (Architektur-Diagramme, 8-Schritte-Bauplan) | `docs/AI-OS-Backend-Lernguide.html` | `cf2fa26` |
| 3 | **Hermes-Agent** — autonomer Mitarbeiter (learn/ask/work/status) | `backend/app/agents/hermes.py` | `b921941` |
| 4 | **Hermes Web-GUI** + Doppelklick-Start | `backend/app/static/hermes.html`, `backend/Hermes-Starten.bat` | `8d27f63` |
| 5 | **Hermes Desktop App** (v40.10.2) konfiguriert: Ollama-Anbindung, Auto-Routing, Deutsch | `~/.hermes/config.yaml`, `~/.hermes/SOUL.md`, `~/.hermes/skills/ai-os/` | — (außerhalb Repo) |
| 6 | **Lokale LLM-Fallbacks installiert**: LM Studio + Jan | `%LOCALAPPDATA%\Programs\{LM Studio, Jan}` | — |
| 7 | **Prompt-Board** (Trello-Stil, Modul 4 "Prompt Registry") | `backend/app/prompts/registry.py`, `/prompts` | siehe Git-Log |
| 8 | Pi-4B/Tailscale-Hosting-Anleitung | `docs/Hermes-Pi4-Tailscale-Setup.md` | `b921941` |

### Lern-Highlights des Tages (mit Code)

**1. Der Lohn des Interface-Schnitts (Qdrant).** Weil `RagService` nur den
`VectorStore`-**Protocol**-Vertrag kennt, brauchte die komplette Qdrant-Integration
**null Änderungen** an Services oder Routen — nur eine neue Klasse + 1 Zeile Verdrahtung:

```python
# vector_store.py — der Vertrag
class VectorStore(Protocol):
    def add_document(self, meta: DocumentMeta, chunks: list[ChunkRecord]) -> None: ...
    def search(self, query_embedding: list[float], top_k: int = 4) -> list[tuple[ChunkRecord, float]]: ...

# main.py — die einzige Stelle, die entscheidet (Composition Root)
def build_vector_store(settings: Settings) -> VectorStore:
    if settings.vector_backend == "qdrant":
        return QdrantVectorStore(settings.qdrant_url, settings.qdrant_collection)
    return JsonVectorStore(settings.data_dir / "vector_store.json")
```

Test-Trick: `QdrantClient(":memory:")` startet Qdrant im Prozess — die ganze
Test-Suite läuft per `@pytest.fixture(params=["json", "qdrant"])` gegen **beide**
Backends, ohne Server.

**2. Ein Agent, der aus eigener Arbeit lernt (Hermes).** `work()` ist der Kreislauf
Kontext holen → arbeiten → Ergebnis zurück in die Wissensbasis:

```python
async def work(self, briefing: str, top_k: int = 4) -> HermesWorkResult:
    sources = await self._rag.retrieve(briefing, top_k)      # 1. Kontext (nur Suche!)
    result = await self._pipeline.run(briefing_mit_kontext)  # 2. Planner→Developer→Reviewer
    await self._rag.ingest(journal_filename, journal, ...)   # 3. Journal → Wissensbasis
```

Wichtig dabei: `retrieve()` (Vektorsuche ohne LLM-Antwort) als eigene Methode
neben `query()` — sonst würde `work()` unnötig eine Antwort generieren.

**3. Frontmatter als Datenbank (Prompt-Board).** Das Trello-Board hat KEINE eigene
Datenbank — Status/Version/Tags leben als YAML-Frontmatter **in den Markdown-Dateien
selbst** (`04_Infrastruktur/Gateway/Prompts/*.md`). Das Board ist nur eine Sicht:

```markdown
---
title: CEO-Bild aus Dashboard entfernen
status: entwurf        # backlog | entwurf | test | freigegeben  ← Kanban-Spalte
version: 2             # erhöht sich automatisch bei Inhalts-Änderung
tags: [dashboard]
---
# Prompt-Inhalt wie gehabt ...
```

Vorteile: git-versionierbar, Obsidian-kompatibel, kein Lock-in. Alt-Dateien ohne
Frontmatter landen automatisch im Backlog und werden beim ersten Update migriert.

**4. Sicherheit bei Datei-APIs:** Der Registry-Pfad wird gegen Path-Escape geprüft
(`../../etc/passwd` → ValueError) — Pflicht, sobald ein API-Parameter zum Dateinamen wird.

**5. Hermes-App-Ökosystem:** Die Desktop-App (Nous Research) hat dieselbe
Skill-Struktur wie Claude Code. LLM-Routing = `fallback_providers`-Kette in
`~/.hermes/config.yaml` (verifiziert im Quellcode: `hermes_cli/fallback_config.py`),
Sprache = `display.language: "de"` (`agent/i18n.py`), Persona = `~/.hermes/SOUL.md`.
Kette jetzt: `llama3 → qwen3.5:9b → mistral → LM Studio (:1234) → Jan (:1337)`.

### Stolpersteine des Tages

- **Port-Zombie**: Alter uvicorn-Prozess hielt Port 8000 → neuer Server startete
  scheinbar, servierte aber 404. Deutsches Windows zeigt `ABHÖREN` statt
  `LISTENING` → `netstat`-Filter anpassen!
- **winget-Silent-Install von LM Studio schlägt fehl** (Exit 2, 3 Varianten
  probiert) → direkter Installer-Download von installers.lmstudio.ai + `/S` klappt.
- **`lms get <name>`** sucht nur "Staff Picks" — für beliebige Modelle die
  **volle HuggingFace-URL** übergeben.
- PocketPal AI / PalsHub / Locally AI sind Mobile-/Apple-Apps → auf Windows-PC
  nicht installierbar (PocketPal wäre was fürs Handy).

### Bedienung (Stand heute)

- **Hermes-Chat**: `backend/Hermes-Starten.bat` → http://localhost:8000/ui
- **Prompt-Board**: http://localhost:8000/prompts (Karten ziehen = Status ändern)
- **Swagger**: http://localhost:8000/docs
- **Hermes Desktop App**: Startmenü "Hermes" (Ollama llama3, deutsch, Auto-Fallback)

### Offene nächste Schritte

- [ ] Phase 4: LangGraph-Migration der Agent-Pipeline (QA-Schleife, Human Approval)
- [ ] Pi-Deployment nach `docs/Hermes-Pi4-Tailscale-Setup.md` (Schritte 2–5 per SSH)
- [ ] LiteLLM-Gateway dauerhaft betreiben → als Stufe 1 in Hermes-Fallback-Kette
- [ ] In Jan einmalig ein Modell laden + Local API Server aktivieren (Stufe 5 der Kette)
- [ ] Evaluation-Modul (Modul 5): RAG-Antworten protokollieren & bewerten

---

## 2026-07-09 (Tag 1)

### Was entstanden ist

**Das neue Backend** (`backend/`) nach dem 8-Phasen-Lernkonzept — Commit `85855f6`:
FastAPI + Pydantic v2 + asyncio, verwaltet mit uv, geprüft mit Ruff + MyPy strict
+ pytest (13 Tests). Funktionierend ab Tag 1: RAG-Pipeline (Upload → PDF/DOCX/TXT-Parsing
→ absatzbewusstes Chunking mit Überlappung → nomic-embed-text-Embeddings via Ollama
→ JSON-Vector-Store mit Kosinus-Suche → Antwort mit Quellen) und die
Agenten-Pipeline Planner → Developer → Reviewer.

### Lern-Highlights

**1. Dependency Injection ist DIE Kernidee der Architektur:**

```python
class RagService:
    def __init__(self, llm: LLMClient, store: VectorStore, ...):  # bekommt, erzeugt nicht
        self._llm = llm
```

Serverstart (`main.py` lifespan) steckt echte Teile zusammen; Tests stecken Fakes
hinein. Gleicher Code, andere Verkabelung → Tests ohne Netzwerk in 0,4 s.

**2. `typing.Protocol` statt Vererbung:** `FakeLLMClient` im Test erfüllt den
`LLMClient`-Vertrag ohne `import` der echten Klasse — strukturelle Typisierung.

**3. Deterministische Fake-Embeddings** (Wort-Hash-Histogramm) machen sogar die
semantische Suche testbar: gleiche Wörter → ähnliche Vektoren.

**4. Pydantic v2 an der Grenze:** `Field(min_length=1)`, `ge=1, le=20` — ungültige
Requests sterben als 422, bevor Logik läuft ("Parse, don't validate").

### Verifikation

End-to-End mit echtem Ollama getestet: Dokument hochgeladen, gefragt
"Auf welchem Port läuft der LiteLLM Gateway?" → korrekte Antwort mit Quelle (Score 0.66).

---

*Regel: Dieses Journal wird am Ende jedes Arbeitstages von Claude aktualisiert.*
*Zuletzt aktualisiert: 2026-07-15*
