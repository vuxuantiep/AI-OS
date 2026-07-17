# 🛠️ Bauplan: Feed-Scraper als Wasm-Komponente (Self-Evolving Stufe 2, Schritt 1)

> Erstellt 17.07.2026. Planungs-/Vorbereitungsdokument — Umsetzung ab Phase 1
> erst nach CEO-Freigabe (Gate-Regel 4; Wirtschaftlichkeits-Update siehe unten).
> Verwandt: [[Konzept-Self-Evolving-Agent]], [[PRD_DokuCheck-Lokal]]

## 1. Endnutzer-Fokus: Smartphone-Verbraucher zuerst

**Usecase „Persönlicher Themen-Assistent":** Nutzer wählt in der PWA Themen
(z. B. Gesundheit, Verbraucher-News, Hobby) → der Agent zieht **RSS/Atom-Feeds**
(bewusst NUR Feeds: technisch sauber abgrenzbare Rechte, und rechtlich die
saubere Linie — Feeds sind zur Syndication gedacht, kein Scraping fremder Seiten;
gleiche Entscheidung wie beim Lead-Radar) → filtert agentisch → speichert lokal
als Embeddings → beantwortet Fragen **offline, mit Quellenangabe**.

Warum PWA und nicht native App zuerst: Zero-Install (Link öffnen statt App-Store),
DokuCheck-Infrastruktur (WebLLM-Worker, IndexedDB-Memory, PWA-Shell) existiert
schon und läuft auf Smartphones (WebGPU: Android Chrome ≥ 121, iOS 18+; Default-
Modell Llama 3.2 1B ~0,8 GB). Die native App ist Ausbaustufe 3 (`Plannung/Native-App/`).

## 2. Architektur — EINE Komponente, zwei Laufzeiten

```
                 feed-scraper.wasm (Wasm-Komponente, aus JS gebaut)
                 WIT-Interface: fetch-feed(url) → list<item{titel,link,datum,text}>
                        │
        ┌───────────────┴────────────────┐
        ▼ Desktop / AI-OS (Agenten)      ▼ Smartphone (PWA)
  Wassette-Runtime (MCP)           jco transpile → Browser-Modul
  Rechte: grant-network-permission  Browser-Sandbox + Feed-Allowlist im Code;
  NUR für die Feed-Hosts            CORS-Realität: Feeds ohne CORS-Header →
  (deny-by-default verifiziert ✓)   winziger Feed-Proxy am Dashboard (Whitelist)
        │                                │
        └───────────────┬────────────────┘
                        ▼
          Chunks → Embeddings (transformers.js, multilingual-e5-small)
          → IndexedDB Store (Semantic/RAG Memory des Multi-Memory-Panels)
                        ▼
          SLM (WebLLM) antwortet NUR aus geliefertem Kontext + Quellen
```

## 3. Einbindung der 3 SLM-Qualitäts-Hebel

| Hebel | Umsetzung in diesem Projekt | Phase |
|---|---|---|
| **1. Lokales RAG** | Feed-Items → Embeddings → IndexedDB; SLM bekommt Top-K-Chunks als Kontext und fasst NUR zusammen (Anti-Halluzination) | 3 |
| **3. Agentic Loop** | (a) Relevanz-Filter: SLM bewertet jedes Item „relevant fürs Thema? ja/nein"; (b) Selbstkorrektur-Pass über die Antwort („Fehler? korrigieren") | 4 |
| **2. QLoRA-Finetuning** | NICHT auf dem Smartphone — später optional feingetuntes Themen-Modell ausliefern (gleiches WebLLM-Format). Bewusst hinter RAG+Loop zurückgestellt | später |

## 4. Phasenplan mit konkreten Schritten

**Phase 0 — Vorbereitung ✅ (17.07.2026 erledigt)**
- Wassette v0.4.0 installiert, deny-by-default verifiziert, OCI-Load getestet
- Toolchain geprüft: Node v24.15.0, componentize-js 0.21.0, jco 1.25.2
- Fusion Lokal-Private-LLM-App → Plattform (siehe unten)

**Phase 1 — Wasm-Komponente bauen (Desktop, ~1 Tag)**
1. Projekt `scraper-komponente/` (WIT-Datei + JS): `world feed-scraper { export fetch-feed: func(url: string) -> result<list<item>, string> }`
2. JS-Implementierung: `fetch()` + Feed-Parsing (RSS/Atom, ohne externe Lib oder mit
   kleinem Vendored-Parser), Text-Bereinigung
3. Build: `npx componentize-js` → `feed-scraper.wasm`
4. `wassette component load file://...` + `wassette permission grant network`
   NUR für 2–3 Test-Feed-Hosts (z. B. tagesschau.de)
5. **Sicherheitstest:** Zugriff auf NICHT freigegebenen Host muss fehlschlagen

**Phase 2 — Browser-Transpile (PWA, ~0,5 Tag)**
1. `npx jco transpile feed-scraper.wasm -o pwa/` → ES-Modul für den Browser
2. CORS-Test gegen reale Feeds; für Feeds ohne CORS: Mini-Proxy-Route am
   AI-OS-Dashboard (`/feeds/<whitelist-id>`, analog DokuCheck-Proxy)
3. Feed-Allowlist als Nutzer-Einstellung (Themen → kuratierte Feed-Liste)

**Phase 3 — Memory-Anbindung (~1 Tag)**
1. Embeddings per transformers.js (multilingual-e5-small, int8 — deckt gleichzeitig
   den offenen v0.3-Punkt von DokuCheck ab!)
2. Neuer IndexedDB-Store `wissen` im Multi-Memory-Schema (Semantic/RAG Memory)
3. Dedup per Link-Hash, Lösch-/Aufbewahrungsregel (Speicherbudget am Smartphone)

**Phase 4 — Agentic Loop + UI (~1–2 Tage)**
1. Relevanz-Filter-Prompt (ja/nein je Item, Batch)
2. Q&A-Flow: Frage → Top-K aus `wissen` → Antwort mit Quellen → Selbstkorrektur-Pass
3. UI in der PWA: Themen wählen, „Aktualisieren", Fragen stellen, Quellen anzeigen

**Gate vor Phase 1:** Wirtschaftlichkeits-Update der Plattform (Erweiterungs-
Prüfung: Zielgruppe Endverbraucher-Smartphone, Monetarisierung z. B. Freemium-PWA /
Themen-Pakete / B2B-Ableger) → CEO-Freigabe. Phase 0 war Vorbereitung, vom Gate ausgenommen.

## 5. Risiken / offene Punkte

- **CORS bei Feeds** → Proxy-Fallback nötig (dann nicht mehr 100 % serverlos;
  ehrlich in der UI ausweisen wie beim DokuCheck-Modell-Download)
- **componentize-js `fetch()`-Support in Wassette** prüfen (Wassette-Beispiele
  fetch-rs/get-weather-js als Referenz) — Plan B: Rust-Komponente für den Fetcher
- **Speicher am Smartphone** (Modell 0,8 GB + Embeddings) → Budget-Anzeige
- iOS-WebGPU erst ab iOS 18 → OCR-/BM25-Fallback-Pfad wie bei DokuCheck
