# DokuCheck Lokal — Edge Cognitive AI Platform

**Produkt 1 der Nische: SLM + WebAssembly/WebGPU + Multi-Memory · 100 % lokal · DSGVO by Design**

DokuCheck Lokal analysiert Verträge, Behördenbriefe und Fotos von Dokumenten direkt im
Browser des Nutzers. Ein kleines Sprachmodell (SLM) läuft per **WebGPU** auf dem Gerät,
die Texterkennung (**OCR**) per **WebAssembly** — es gibt keinen Server, kein Konto,
keinen Upload. Signatur-Feature: eine **Live-Beweisleiste**, die externe Netzwerk-Anfragen
zählt und damit das Datenschutz-Versprechen überprüfbar macht (F12 → Netzwerk).

## Was bedeutet „offline" hier — ehrlich erklärt

| Bestandteil | Woher | Internet nötig? |
|---|---|---|
| App-Shell (HTML/CSS/JS) | lokal vom AI-OS-Dashboard (Flask) | nein |
| Bibliotheken (WebLLM, pdf.js, Tesseract) | lokal gevendort in `vendor/` | nein |
| OCR-Sprachdaten (deu/eng/vie) | lokal gevendort in `vendor/tessdata/` | nein |
| **Modellgewichte (0,8–2 GB)** | HuggingFace-CDN, **einmalig** beim ersten Laden | **nur beim ersten Mal** |

Nach dem ersten Modell-Download liegt alles im Browser-Cache — Analyse, OCR und
Übersetzung funktionieren dann komplett offline. Die Dokumente selbst verlassen das
Gerät **nie**.

## Funktionen (v0.2)

- **Zusammenfassen** — auch lange Dokumente (Map-Reduce über Abschnittsgruppen)
- **Risiko-Check** — Fristen, Kosten, Kündigungsklauseln, nachteilige Klauseln (mit Zitat)
- **Freie Fragen** — BM25-Retrieval über die Dokument-Abschnitte
- **OCR (Bild → Text)** — Tesseract.js/WASM, läuft auf jedem Gerät (auch ohne WebGPU);
  Kamera-Aufnahme auf dem Smartphone (`📷 Foto aufnehmen`); Sprachen: Deutsch, Englisch, Vietnamesisch
- **Übersetzen** — das geladene SLM übersetzt nach Deutsch, Englisch oder Vietnamesisch
- **PWA** — auf dem Smartphone installierbar („Zum Startbildschirm hinzufügen"),
  App-Shell offline dank Service Worker
- **🧠 Multi-Memory-Panel** — siehe unten

## Multi-Memory: das Alleinstellungsmerkmal

Umsetzung der 8 Memory-Typen aus dem Konzept-PDF (`Idee und Plannung/`), alles in der
**IndexedDB des Browsers** (DB `dokucheck`):

| App-Feature | Memory-Typ (Konzept) | Store |
|---|---|---|
| Aktuelles Dokument + Sitzung | Working Memory | `session` |
| Analyse-Verlauf mit „Anzeigen" | Episodic Memory | `analysen` |
| Gespeicherte Dokumente + Chunks | Semantic + RAG Memory | `dokumente` (+ `chunks` reserviert für v0.3-Embeddings) |
| Prüfroutinen (Prompt-Vorlagen, CRUD, JSON-Export/Import) | Procedural + Skill Memory | `routinen` |
| Gemerkte Modellwahl | Tool Memory | `session` |
| Knowledge Graph / GraphRAG | — Ausblick v0.5 | — |

## Starten

**Über das AI-OS-Dashboard (empfohlen):**
1. Dashboard starten: `python 04_Infrastruktur/Gateway/ai_os_dashboard.py`
2. Im Browser: `http://127.0.0.1:5000/produkte/dokucheck/`
   (oder Nav-Button „🛡️ DokuCheck Lokal" im Dashboard)

**Standalone (Entwicklung):**
```bash
cd "Produkt/dokucheck-lokal"
python -m http.server 8080
# → http://localhost:8080
```
Direktes Öffnen per Doppelklick (`file://`) funktioniert **nicht** — ES-Module und
Worker brauchen einen HTTP-Server.

**Auf dem Smartphone:** gleiche Tailnet/LAN-Adresse des Dashboards öffnen
(z. B. `http://tiep-laptop.tailed32d1.ts.net:5000/produkte/dokucheck/`), dann
„Zum Startbildschirm hinzufügen". Hinweis: Service Worker und WebGPU verlangen
einen *Secure Context* — `localhost` gilt immer als sicher, HTTP über LAN/Tailnet
nicht; dort OCR-only oder HTTPS (z. B. Cloudflare Tunnel) verwenden.

## Modelle

| Modell | Größe | Empfehlung |
|---|---|---|
| Llama 3.2 1B Instruct (q4f16) | ~0,8 GB | Default; Smartphones und schwache iGPUs |
| Qwen3 1.7B (q4f16) | ~1,2 GB | bestes Deutsch in dieser Klasse |
| Llama 3.2 3B Instruct (q4f16) | ~2 GB | Desktop mit ordentlicher GPU |

## Technik-Stack

- **WebLLM 0.2.79** (MLC AI, Apache 2.0) — im Web Worker (`worker.js`), UI bleibt responsiv.
  Version ist gepinnt: das gevendorte JS und die Model-Lib-WASMs sind versionsgekoppelt —
  bei einem Upgrade beides zusammen testen.
- **transformers.js 3.8.1** (HuggingFace) + **OPUS-MT** (Helsinki-NLP, MarianMT) — neuronale
  Übersetzung ohne LLM im eigenen Worker (`trans-worker.js`), ONNX/WASM auf der CPU, läuft
  ohne WebGPU. Paare de↔en und en↔vi; de↔vi als Pivot über Englisch. Gewichte (~45 MB/Paar,
  int8) einmalig von HuggingFace, danach im Browser-Cache.
- **Tesseract.js 5.1.1** (OCR, WASM, Single-File-Core mit eingebettetem Binary)
- **pdf.js 4.4.168** (lokales PDF-Parsing)
- **BM25-Retrieval** (vanilla JS, deutsche Stoppwörter) statt Embeddings — bewusste
  v0.2-Entscheidung; Embeddings kommen in v0.3 (transformers.js, multilingual-e5-small)
- **Kein Build-Toolchain** — reines HTML/CSS/JS, direkt editierbar
- Netzwerk-Beweis: `PerformanceObserver` im Hauptthread **und** im LLM-Worker
  (Worker-Fetches sind sonst unsichtbar; Meldung per `BroadcastChannel`)

## Roadmap (gemappt auf das Konzept-PDF)

| Version | Inhalt | PDF-Roadmap-Schritt |
|---|---|---|
| v0.1 | Prototyp (CDN, ein HTML) | 1 SLM einsetzen ✓ |
| **v0.2** | **Vendoring, Worker, OCR, Übersetzen, PWA, BM25, Multi-Memory-Panel** | 2 Memory + 4 WASM + 5 WebGPU ✓ |
| **v0.3** | **NMT-Übersetzung ohne LLM (transformers.js + OPUS-MT, WASM/CPU, de↔en↔vi mit Pivot) ✓** — noch offen: echte Embeddings für Q&A + Semantic Memory (gleiche Lib) | 3 RAG (teilweise) |
| v0.4 | CPU-Fallback ohne WebGPU (wllama/llama.cpp-WASM), Self-Hosting der Modellgewichte | — |
| v0.5 | GraphRAG / Knowledge-Graph über Dokumente; optionaler Hybrid-Sync zum FastAPI-RAG (`backend/app/rag/`, Port 8000, Opt-in, default aus) | 3b GraphRAG + 6 AI-OS ✓ |

## Ausblick: Self-Evolving Research Agent (Stufe 2 der Plattform)

Konzept in `Plannung/Konzept-Self-Evolving-Agent.md` (eingegliedert 17.07.2026,
vorher eigener Ordner „Client-Side Self-Evolving AI"): gleicher Stack wie
DokuCheck, erweitert um **Agenten-Loop** (Planung → Ausführung → Selbstkorrektur)
und **selbstwachsendes Gedächtnis** (autonome Web-Recherche → Embeddings →
IndexedDB/OPFS). Synergie: nutzt exakt die v0.3-Embedding-Technik und füllt das
Multi-Memory-Panel. ⚠️ Wirtschaftlichkeits-Gate vor Umsetzung nötig.

**Konkreter Bauplan:** `Plannung/Bauplan-Feed-Scraper-Wasm.md` — Feed-Scraper
als Wasm-Komponente (eine Komponente, zwei Laufzeiten: Wassette am Desktop mit
Feed-only-Netzwerkrechten, jco-Transpile für die Smartphone-PWA), Usecase
„Persönlicher Themen-Assistent" für Endverbraucher, 3 SLM-Qualitäts-Hebel
eingeplant. Phase 0 (Toolchain + Wassette) ✅ erledigt.
**Gate:** `wirtschaftlichkeit-themen-assistent.md` → **GO_MIT_AUFLAGEN**,
Status WARTET_AUF_FREIGABE (max. 4 Bautage, Monetarisierung Trigger-basiert,
B2B-Demo als wahrscheinlichster Geldweg).

## Ausbaustufe 3: Native Mobile App — ZURÜCKGESTELLT (Trigger-basiert)

Analyse `Plannung/Analyse-Browser-vs-Native.md` (17.07.2026): **Antwortqualität
im Browser identisch** (gleiche Gewichte + RAG + Loop); Unterschiede sind nur
Tempo/Komfort. Browser-first gewinnt strategisch (Distribution per Link, eine
Codebase, 0 €, Datenschutz per F12 beweisbar). Native App (`Plannung/Native-App/`,
ehemals „Lokal-Private-LLM-App": Expo + Inferenz-Router zum Heim-Ollama) wird
erst bei Trigger gebaut: T1 Nutzer fordern Hintergrund-Sync/Push · T2 Modelle
>3B mobil (NPU) · T3 App-Store als Vertriebskanal nötig. Der Inferenz-Router
ist als PWA-Feature umsetzbar (Kandidat „Stufe 2.5").

## Grenzen / Hinweise

- **Keine Rechtsberatung** — Ersteinschätzung durch ein kleines Modell, Disclaimer in der App.
- WebGPU nötig für Analyse/Übersetzung (Chrome/Edge ≥ 113, Android Chrome ≥ 121, iOS 18+);
  **OCR läuft überall** (WASM).
- Erster Modell-Download kann hinter Firmen-Proxys scheitern (HuggingFace-CDN).
