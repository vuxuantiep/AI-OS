# Product Requirement Document: DokuCheck Lokal v0.3–v0.5
**Technische Roadmap & Architektur-Spezifikation**

**Status:** Entwurf  
**Gültig ab:** 2026-07-12  
**Zielplattform:** Browser (Chrome/Edge ≥113, Android Chrome ≥121, iOS 18+) — 100 % lokal, kein Server, DSGVO by Design

---

## 1. Executive Summary

DokuCheck Lokal ist eine browser-native Anwendung zur KI-gestützten Analyse von Verträgen, Behördenbriefen und Dokumentfotos. Das Produkt kombiniert drei lokale Technologien: **WebLLM/WebGPU** (SLM-Inferenz), **WebAssembly** (OCR/PDF-Parsing) und **IndexedDB** (persistenter Speicher). Das Alleinstellungsmerkmal ist der **Netzwerk-Beweis** (externe Requests = 0 während der Analyse) und das **Multi-Memory-System** (Working, Episodic, Semantic, Procedural Memory) — beides ausschließlich client-seitig.

v0.2 ist produktionsreif (BM25-Retrieval, PWA, Kamera-OCR). v0.3–v0.5 erweitern das System um **RAG-Light mit echten Embeddings**, **Use-Case-Presets**, **professionelle Export-Formate** und optional **GraphRAG**.

---

## 2. Technical Architecture: Browser-Based RAG-Light

### 2.1 Chunking Strategy

**Ziel:** Dokumente in semantisch sinnvolle Einheiten zerlegen, die präzise abgerufen werden können, ohne den Kontext des LLM zu überschwemmen.

#### Chunk-Größen
| Segment-Typ | Token-Ziel | Überlappung | Begründung |
|---|---|---|---|
| Absatz / Klausel | 256–512 Tokens | 0–50 Tokens | Vertragsklauseln sind oft <200 Wörter; präzise Zuordnung zu Fristen/Kosten. |
| Abschnitts-Gruppe | 512–1024 Tokens | 100–200 Tokens | Für Map-Reduce-Zusammenfassungen und thematische Suche. |
| Seite (PDF) | 800–1200 Tokens | 150 Tokens | Layout-Erhaltung; pdf.js liefert Texte pro Seite. |

**Implementierung:**
- Eingabe: Rohtext aus `handleFile()` (`app.js`) → Whitespace-Normalisierung → Segmentierung nach Absätzen (`\n\n`) oder pdf.js-Seitengrenzen.
- Absatzweises Chunking mit Absatz-ID und Seitenzahl-Metadaten (für Zitate im Output).
- Speicherung als Array of Objects in IndexedDB (`chunks`-Store).

**Skill-spezifische Auswahl:**
Jeder Skill (z. B. `vertrag`, `mietvertrag`, `versicherung`) definiert **Schlüsselwort-Cluster** (Fristen: `"kündigung"`, `"frist"`, `"monat"`; Kosten: `"gebühr"`, `"preis"`, `"euro"`). Der Retriever priorisiert Chunks, die maximal viele Cluster-Treffer enthalten.

### 2.2 Context Management

**Problem:** Ein 3B-Modell hat ein Context Window von ~4096–8192 Tokens. Das gesamte Dokument darf nicht hereingereicht werden.

**Lösung: Top-k-Chunk-Auswahl mit Skill-Filter**

1. **Retrieval Phase:**
   - Embedding des Query-Textes (Skill-Prompt + User-Frage).
   - Ähnlichkeitssuche über lokale Vektor-DB → Top-k Chunks (k = 3–5).
   - Bonus: Chunks aus derselben Seite wie ein explizit genanntes Datum werden aufgewertet.

2. **Zusammenbau:**
   - Template: `<DOKUMENT_META>\n<CHUNK_1 mit Quellenangabe>\n---\n<CHUNK_2>\n---\n<CHUNK_3>\n\n<SYSTEM_PROMPT aus Skill>\n<USER_QUERY>`
   - System-Prompt enthält die Struktur-Vorgabe (Zusammenfassung / Risiko-Check / Fristen-Tabelle).
   - Max. 2048 Tokens für den Prompt reservieren; Rest für LLM-Antwort.

3. **Streaming & Antwort-Kontrolle:**
   - `temperature: 0.2–0.3` (wenig Halluzination).
   - `max_tokens: 700` für kurze Analysen, 1200 für vollständige Vertragsprüfung.
   - Jede Antwort wird mit den verwendeten Chunk-IDs gespeichert (Episodic Memory).

### 2.3 Local Vector Search

**Constraint:** Kein Server, kein externer API-Call für Embeddings.

**Option A — Precomputed Hashing (v0.3 MVP, kein zusätzliches Modell nötig):**
- Nutze **Sparse-Embeddings via BM25** (bereits in v0.2 vorhanden in `memory/semantic.js`).
- Erweitere um **TF-IDF-Weighting** mit mehrsprachigem Vokabular (DE/EN/VI).
- Vorteil: Kein zusätzliches Modell, funktioniert offline sofort.
- Nachteil: Semantische Ähnlichkeit nur approximativ.

**Option B — Tiny-Embedding-Modell (v0.3+ , empfohlen für 2026):**
- Lade `transformers.js` mit `Xenova/all-MiniLM-L6-v2` oder `Xenova/paraphrase-multilingual-MiniLM-L12-v2` (~23 MB, quantisiert).
- Embedding-Berechnung im Web Worker (blockiert UI nicht).
- Speicherung der Vektoren in IndexedDB (`chunks`-Store, Feld `embedding` als Float32Array).
- Ähnlichkeit: **Cosine Similarity** über alle Vektoren im Browser (für 1000 Chunks ~10–30 ms).

**Schema-Erweiterung für Chunks:**

```javascript
// In IndexedDB: Store "chunks" im DB "dokucheck"
{
  id: "chunk_001",
  docId: "doc_abc",
  reihe: 1,               // Absatznummer im Dokument
  seite: 3,               // PDF-Seite
  text: "Die Vertragslaufzeit beträgt 24 Monate...",
  tokens: 87,
  embedding: Float32Array, // Option B: 384-dim
  bm25Terms: ["laufzeit", "monat", "kündigung"], // Option A: Sparse
  skillTags: ["fristen", "laufzeit"],             // vom Skill-Preset vergeben
  ts: "2026-07-12T14:00:00Z"
}
```

**Cross-Document Semantic Query:**
- Der Nutzer fragt: *"Finde alle Dokumente mit automatischer Verlängerung"*
- Query wird embeddet → Suche über alle Chunks aller Dokumente → Ranking nach Similarity + Skill-Tag `"verlaengerung"`.
- Ergebnis: Liste von `(docId, chunkId, similarity)` mit Link zum Dokument.

---

## 3. Product UX & Trust Engineering

### 3.1 Trust Indicators

**Prinzip:** Privacy by Design muss sichtbar sein, nicht nur versprochen.

#### UI-Elemente
| Element | Position | Verhalten |
|---|---|---|
| **Netzwerk-Beweis-Counter** | Fixierte Leiste oben oder Footer | Zeigt `externe Requests: 0` während Analyse. Klickbar → öffnet Mini-Panel mit Erklärung: *"WebLLM läuft im Web Worker, Modellgewicht liegt im Cache, OCR ist WASM — keine Daten verlassen das Gerät."* |
| **Modell-Cache-Badge** | Schritt 1 | *"Dieses Modell ist schon auf dem Gerät — Laden geht ohne Download."* (bereits implementiert in `zeigeCacheStatus()`). |
| **Storage-Meter** | Einstellungen / Info | Zeigt belegten IndexedDB-Speicher (Dokumente + Cache) in MB. |
| **Tech-Stack-Tooltip** | Footer oder Info-Button | Kurze Erklärung: WebGPU (was es ist, welche GPUs), WebLLM (Open-Source, lokal), IndexedDB (Browser-Speicher, kein Upload). |
| **Safe-Context-Badge** | Oben rechts | Zeigt `🔒 Lokal` (HTTP) oder `🌐 HTTPS` bei Deployment. Grün = sicher, Gelb = lokales HTTP ohne WebGPU-Funktion. |

**Erklärungstexte (i18n.js):**
```javascript
"trust.webgpu": "WebGPU ist eine Browser-Schnittstelle für GPU-Berechnungen. Das Modell läuft auf deiner Grafikkarte — es gibt keine Cloud.",
"trust.weballm": "WebLLM bringt Sprachmodelle direkt in den Browser. Die Modellgewichte werden einmal heruntergeladen und im Cache gespeichert.",
"trust.indexeddb": "IndexedDB ist eine Datenbank im Browser. Deine Dokumente und Analysen bleiben auf diesem Gerät."
```

### 3.2 Use-Case Presets

**Konzept:** Presets sind Bundles aus `Skill-Prompt + Mini-Checkliste + LLM-Parametern`, die den Nutzer durch den Workflow führen.

#### Preset-Definition (JSON)

```json
{
  "id": "mietvertrag_privat",
  "name": "Mietvertrag (privat)",
  "icon": "🏠",
  "sprachen": ["de", "en"],
  "skillPrompt": "Du bist ein juristischer Assistent für Mietverträge...",
  "checkliste": [
    "Kautionshöhe und Verwendung",
    "Kündigungsfristen (Mieter/Vermieter)",
    "Betriebskosten und deren Aufschlüsselung",
    "Schönheitsreparaturen",
    "Haustier-Klausel"
  ],
  "temperature": 0.2,
  "maxTokens": 900,
  "chunkPriority": ["fristen", "kosten", "kündigung"]
}
```

**Preset-System:**
- Auswahl **vor** dem Dokument-Upload oder danach.
- Speicherung in IndexedDB (`routinen`-Store mit Typ `preset`).
- Beim Start einer Analyse: Skill-Prompt + Checkliste werden geladen, der Retriever priorisiert `chunkPriority`-Tags.
- UI: Dropdown oder Cards mit Icons. Suchfeld für Presets.

**MVP-Presets:**
1. `mietvertrag_privat` — deutsch
2. `mobilfunk_vertrag` — deutsch
3. `versicherung_bedingungen` — deutsch
4. `dienstvertrag_firma` — deutsch/englisch
5. `generic` — Fallback ohne Spezialisierung

### 3.3 Export Ecosystem

**Ziel:** Professionelle Reports für E-Mail, Ablage oder weiterverarbeitung.

#### Export-Formate

| Format | Use Case | Implementierung |
|---|---|---|
| **Markdown** | Notizen, Obsidian/Vault-Export | `marked.js` bereits vorhanden oder Template-String. |
| **HTML** | Browser-Ansicht, Drucken | Strukturiertes HTML mit CSS-Print-Media. |
| **JSON** | API-Import, maschinelle Weiterverarbeitung | `{ docMeta, analysen: [...], chunks: [...] }` |
| **DOCX** | Word-Bericht | `docx.js` (client-side, ~200 kB). Sectionen: Titel, Zusammenfassung, Risikotabelle, Fristen, Quellen. |
| **PDF** | Finales Dokument | Option A: Browser-Print → `window.print()` mit Print-CSS. Option B: `pdf-lib` oder `jsPDF` für programmatische Erstellung (empfohlen für v0.4). |

**Export-Workflow:**
1. Nutzer klickt Export-Button nach Analyse.
2. Modal wählt Format + Optionen (z. B. "mit Quellenangaben", "nur Zusammenfassung").
3. Download wird ausgelöst (`Blob` + `URL.createObjectURL`).
4. Bei DOCX/PDF: kurzer Ladebalken, da Serialisierung CPU-intensiv sein kann.

**Export-Schema (JSON-Beispiel):**

```json
{
  "version": "0.3",
  "doc": { "name": "mietvertrag.pdf", "seiten": 12, "datum": "2026-07-12" },
  "analyse": {
    "preset": "mietvertrag_privat",
    "modell": "Llama-3.2-3B-Instruct-q4f16_1-MLC",
    "zusammenfassung": "...",
    "risiken": [
      { "kategorie": "Kündigung", "text": "...", "quelle": "Seite 3, Abs. 2" }
    ],
    "fristen": [
      { "ereignis": "Kündigung", "datum": "unbekannt", "frist": "3 Monate", "quelle": "Seite 5" }
    ]
  },
  "meta": {
    "externeRequests": 0,
    "tokenVerwendet": 1847,
    "dauer": "12.4s"
  }
}
```

---

## 4. Modern Tech Stack Specification (2026 Readiness)

### 4.1 LLM Layer — WebLLM Integration

**Basis:** WebLLM 0.2.79 (aktuell gevendort). Ziel für v0.3: Update auf aktuellste stabile Version (erfordert gemeinsames Update von `web-llm.js` + WASM-Libs).

**Model-Presets:**

| Preset | Modell-ID | Größe | GPU-Anforderung | Use Case |
|---|---|---|---|---|
| `schnell` | `Qwen2-0.5B-Instruct-q4f16_1-MLC` | ~400 MB | Integrierte GPU / Smartphone | OCR-Ergebnis-Vorprüfung, kurze Q&A |
| `standard` | `Llama-3.2-1B-Instruct-q4f16_1-MLC` | ~0,8 GB | Integrierte GPU | Default; allgemeine Vertragsanalyse |
| `praezise` | `Llama-3.2-3B-Instruct-q4f16_1-MLC` | ~2 GB | Dedizierte GPU (Desktop) | Gründliche Prüfung, längere Reports |
| `experimental` | `Phi-3.5-mini-instruct-q4f16_1-MLC` | ~2,2 GB | Dedizierte GPU | Alternativ zu Llama-3.2-3B; testen auf Reasoning-Qualität |

**Engine-Parameter (pro Preset):**
```javascript
const PRESETS = {
  schnell:   { temperature: 0.3, max_tokens: 500, repetition_penalty: 1.1 },
  standard:  { temperature: 0.25, max_tokens: 800, repetition_penalty: 1.15 },
  praezise:  { temperature: 0.2, max_tokens: 1200, repetition_penalty: 1.2 },
  experimental: { temperature: 0.2, max_tokens: 1000, repetition_penalty: 1.1 }
};
```

**Worker-Architektur:**
- `worker.js`: Hostet `WebWorkerMLCEngineHandler` von WebLLM.
- Kommunikation mit Hauptthread über `postMessage` (Streaming) + `BroadcastChannel` (Netzwerk-Monitoring).
- Bei Modellwechsel: Worker wird neu erstellt (`Terminate` + `new Worker`), Engine-State wird zurückgesetzt.

### 4.2 OCR & Document Processing

**Pipeline:**

```
Eingabe (PDF/Bild) 
    → Preprocessing (Rotation, Binarisierung) 
    → Layout-Segmentierung (pdf.js → Seiten/Blöcke) 
    → OCR (Tesseract.js, sprachspezifisch) 
    → Nachverarbeitung (Whitespace, Rechtschreib-Korrektur-Plugin) 
    → Text + Metadaten (Seite, Block, Koordinaten)
```

**Preprocessing (Client-seitig, Canvas):**
1. **Auto-Rotation:** EXIF-Orientierung lesen → Canvas drehen.
2. **Kontrastverbesserung:** `ctx.filter = 'contrast(1.5) brightness(1.1)'` oder manuelle Pixel-Manipulation für Scans mit schlechter Qualität.
3. **Binarisierung:** Otsu-Schwellwert oder fest `threshold = 160` (adaptiv bei stark beleuchteten Fotos).
4. **Rauschreduzierung:** Einfacher Median-Filter (3x3) über Pixeldaten, falls Tesseract viel Rauschen erkennt.

**Layout-Segmentierung (pdf.js):**
- Statt `page.getTextContent()` → flachen String zu erzeugen, werden `items` nach Y-Koordinate gruppiert (Absätze) und X-Koordinate (Spalten bei mehrspaltigen Dokumenten).
- Ergebnis: Array von Blöcken mit `{ seite, y, text, font }`.
- Für OCR-Bilder: Tesseract liefert `bbox`-Koordinaten → gleiche Segmentierung möglich.

**Sprach-Profile für OCR:**
```javascript
const OCR_PROFILE = {
  de: { lang: 'deu', psm: '6', dictionary: 'de' },
  en: { lang: 'eng', psm: '6', dictionary: 'en' },
  vi: { lang: 'vie', psm: '6', dictionary: 'vi' },
  mixed_de_en: { lang: 'deu+eng', psm: '6', dictionary: 'de+en' }
};
```
- `psm: 6` (Assume a single uniform block of text) für Verträge.
- Erst-Draft OCR mit `deu+eng`, dann Language Detection auf Ergebnis → ggf. Re-OCR mit spezifischem Profil (nur bei >10 % Unsicherheit).

### 4.3 Storage — IndexedDB Schema

**Datenbank:** `dokucheck`  
**Versionierung:** Schema-Version im `metadata`-Store; bei Upgrade Migration durchführen.

#### Store 1: `dokumente`
```javascript
{
  id: "doc_001",                    // UUID
  name: "mietvertrag.pdf",
  typ: "pdf|txt|md|image",
  groesse: 245000,                  // Bytes
  seiten: 12,
  sprache: "de",
  eingelesenAm: "2026-07-12T14:00:00Z",
  text: "...",                      // Rohtext (optional, für BM25-Index)
  preview: "Kautionshöhe: 2 Nettokaltmieten...", // Erste 200 Zeichen
  presets: ["mietvertrag_privat"],  // Zugewiesene Presets
  chunkIds: ["chunk_001", ...],     // Referenz zu chunks
  embeddingModell: null             // v0.3: "Xenova/all-MiniLM-L6-v2"
}
```

#### Store 2: `chunks` (v0.3+ erweitert)
```javascript
{
  id: "chunk_001",
  docId: "doc_001",
  reihe: 1,
  seite: 3,
  blockX: 0,                        // Layout-X (mehrspaltig)
  blockY: 150,                      // Layout-Y
  text: "Die Vertragslaufzeit beträgt 24 Monate...",
  tokens: 87,
  embedding: Float32Array,          // Optional, v0.3+
  bm25Terms: ["laufzeit", "monat"], // Sparse Repräsentation
  skillTags: ["fristen", "laufzeit"],
  ts: "2026-07-12T14:00:00Z"
}
```

#### Store 3: `analysen` (Episodic Memory)
```javascript
{
  id: "ana_001",
  docId: "doc_001",
  docName: "mietvertrag.pdf",
  aktion: "zusammenfassung|risiko|fragen|translation",
  frage: "Was sind die Kündigungsfristen?",
  modell: "Llama-3.2-3B-Instruct-q4f16_1-MLC",
  preset: "mietvertrag_privat",
  antwort: "...",
  chunksVerwendet: ["chunk_001", "chunk_005"],
  tokenVerwendet: 1847,
  dauerMs: 12400,
  ts: "2026-07-12T14:05:00Z"
}
```

#### Store 4: `routinen` (Procedural + Skill Memory)
```javascript
{
  id: "routine_001",
  typ: "preset|skill|vorlage",
  name: "Mietvertrag privat",
  inhalt: { /* JSON: skillPrompt, checkliste, parameter */ },
  system: false,                    // false = Nutzer-definiert, true = Default
  ts: "2026-07-12T14:00:00Z"
}
```

#### Store 5: `session` (Working + Tool Memory)
```javascript
{
  id: "session",
  modell: "Llama-3.2-1B-Instruct-q4f16_1-MLC",
  sprache: "de",
  netzwerkPhase: "watch",           // boot | model | watch
  netzwerkAnfragen: 0,
  letzteAktion: "risiko"
}
```

### 4.4 Frontend Workflow — State Machine

**High-Level State Diagram:**

```
[BOOT] → Initialisierung (Sprache, GPU-Check, Modell-Cache)
    ↓
[IDLE] → Warte auf Benutzeraktion
    ↓
[PRESET_WAHL] → Preset auswählen (optional, kann später erfolgen)
    ↓
[UPLOAD] → Dokument hochladen / Kamera starten
    ↓
[TEXT_EXTRACTION] → PDF parsen / OCR laufen
    ↓
[CHUNKING] → Rohtext → Chunks → Indexierung (v0.3: Embeddings berechnen)
    ↓
[MODELL_BEREIT] → Schritt 1 abgeschlossen
    ↓
[ANALYSE_BEREIT] → Schritt 2 abgeschlossen (Dokument geladen)
    ↓
[GENERIERUNG] → LLM-Streaming läuft
    ↓
[ERGEBNIS] → Antwort anzeigen, speichern, Export-Optionen
    ↓
[IDLE] oder [ANALYSE_BEREIT] (nächste Frage)
```

**State-Variablen in `app.js`:**
```javascript
let state = {
  phase: 'boot',          // boot | idle | preset_wahl | upload | extraction | chunking | modell_bereit | analyse_bereit | generierung | ergebnis
  engine: null,           // WebLLM Engine
  aktivesModell: '',
  presets: [],            // Geladene Presets
  aktivesPreset: null,    // Aktuell gewähltes Preset
  docText: '',
  docName: '',
  docMeta: null,          // { seiten, sprache, typ }
  chunks: [],
  chunkIndex: null,       // Vektor-Index oder BM25-Index
  generating: false,
  stopFlag: false
};
```

**State-Transitions (vereinfacht):**
- `boot → idle` nach `initLang()`, `zeigeGpuBadge()`, Auto-Load-Check.
- `idle → preset_wahl` wenn Nutzer Preset-Klick.
- `preset_wahl → upload` wenn Dokument vorhanden, sonst zurück zu `idle`.
- `upload → extraction` bei Datei-Event.
- `extraction → chunking` nach erfolgreicher Textextraktion.
- `chunking → modell_bereit` wenn Modell geladen, sonst → `idle` mit Hinweis.
- `modell_bereit → analyse_bereit` wenn Chunks bereit.
- `analyse_bereit → generierung` bei Button-Klick (Zusammenfassung / Risiko / Frage).
- `generierung → ergebnis` bei Stream-Ende.
- `ergebnis → analyse_bereit` (weitere Fragen) oder `idle`.

**UI-Sichtbarkeit:**
- Jeder State steuert Sichtbarkeit von `#sec1`, `#sec2`, `#sec3`.
- `statusFlow()` (bereits vorhanden) wird um Preset-Indicator erweitert.

---

## 5. Migration Plan v0.2 → v0.3 → v0.4 → v0.5

| Version | Fokus | Aufwand | Risiko |
|---|---|---|---|
| **v0.2** | Basis produktionsreif (BM25, PWA, OCR) | — | — |
| **v0.3** | Embeddings (transformers.js), Chunk-Store, Preset-System, Export (MD/HTML/JSON) | 2–3 Wochen | Mittel: Modell-Größe im Worker, Speicher-Overhead |
| **v0.4** | CPU-Fallback (wllama/llama.cpp-WASM), DOCX/PDF-Export, Layout-Segmentierung | 2–3 Wochen | Hoch: CPU-Fallback ist langsam, WASM-Kompatibilität |
| **v0.5** | GraphRAG / Knowledge-Graph, Hybrid-Sync zum FastAPI-RAG (Opt-in) | 3–4 Wochen | Hoch: Komplexität der Graph-Logik |

**Kernentscheidungen vor v0.3:**
1. Embedding-Modell festlegen (Empfehlung: `Xenova/paraphrase-multilingual-MiniLM-L12-v2` für DE/EN/VI).
2. WebLLM-Version aktualisieren oder bleiben? (Empfehlung: Update auf ≥0.3.x falls verfügbar, sonst 0.2.79 mit neuen Modell-Presets).
3. PDF-Layout-Segmentierung priorisieren (sofort) oder deferred (v0.4)?

---

## 6. Nicht-Ziele (Out of Scope)

- **Kein Server-Backend für Inferenz:** Alle LLM-Aufrufe bleiben im Browser.
- **Keine Cloud-Synchronisation standardmäßig:** Opt-in Hybrid-Sync erst in v0.5.
- **Keine multi-user / account-Funktionalität:** DSGVO-by-Design schließt Nutzerkonten aus.
- **Keine automatische Rechtsberatung:** System liefert Ersteinschätzung mit Disclaimer; keine Haftung.

---

## 7. Erfolgsmetriken

| Metrik | Ziel | Messmethode |
|---|---|---|
| Erstnutzung: Modell geladen | < 30 s auf Desktop mit GPU | `performance.now()` in `ladeModell()` |
| OCR-Genauigkeit (deutsche Scans) | > 90 % Zeichenerkennungsrate | manuelle Stichprobe, Tesseract `confidence`-Score |
| Analyse-Qualität (Fristen-Check) | > 80 % relevante Klauseln erkannt | Golden-Set-Test mit 20 Verträgen |
| Externe Requests während Analyse | 0 | Netzwerk-Beweis-Counter |
| Token-Nutzung pro Analyse | < 3000 Tokens (Prompt + Antwort) | Logging in `analysen`-Store |
| PWA-Install-Rate | > 20 % (Mobile Nutzer) | Service-Worker-Install-Event |

---

*Dokument abgeschlossen. Nächste Schritte: Review der Architektur-Entscheidungen, Festlegung der Embedding-Strategie, Sprint-Planung für v0.3.*
