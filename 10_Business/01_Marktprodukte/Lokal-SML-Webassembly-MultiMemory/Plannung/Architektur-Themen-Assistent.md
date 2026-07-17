# 🏗️ Architektur-Plan: Themen-Assistent (Self-Evolving Stufe 2)

> Erstellt 17.07.2026 zur Gate-Freigabe. Pflege-Regel: Bei jeder Änderung/
> Erweiterung dieses Diagramm MITaktualisieren — es ist die Referenz für
> Fehlersuche und spätere Anpassungen. Verwandt: [[Bauplan-Feed-Scraper-Wasm]],
> [[Analyse-Browser-vs-Native]], [[wirtschaftlichkeit-themen-assistent]]

## 1. Systemübersicht — eine Komponente, zwei Laufzeiten

```mermaid
flowchart TB
    subgraph KOMP["📦 feed-scraper.wasm (EINE Codebasis, JS → componentize-js)"]
        WIT["WIT-Interface:<br/>fetch-feed(url) → list&lt;item&gt;"]
        PARSE["RSS/Atom-Parser<br/>+ Text-Bereinigung"]
    end

    subgraph DESKTOP["🖥️ Desktop / AI-OS (Agenten-Seite)"]
        WASSETTE["Wassette-Runtime (MCP)<br/>🔒 deny-by-default"]
        POLICY["Policy: Netzwerk NUR<br/>für erlaubte Feed-Hosts"]
        WASSETTE --> POLICY
    end

    subgraph PHONE["📱 Smartphone / PWA (Endnutzer)"]
        JCO["jco transpile<br/>→ ES-Modul im Browser"]
        ALLOW["Feed-Allowlist im Code<br/>+ CORS / Proxy-Fallback"]
        JCO --> ALLOW
    end

    KOMP --> WASSETTE
    KOMP --> JCO

    subgraph MEMORY["🧠 Multi-Memory (IndexedDB, DB dokucheck)"]
        WISSEN["Store 'wissen'<br/>Chunks + Embeddings + Quelle"]
        SESSION["Store 'session'<br/>(Working Memory, existiert)"]
    end

    subgraph KI["🤖 KI-Schicht (existiert aus DokuCheck)"]
        EMB["transformers.js<br/>multilingual-e5-small (Embeddings)"]
        SLM["WebLLM Worker<br/>Llama 3.2 1B / Qwen3 1.7B"]
    end

    POLICY -->|"Feed-Items"| EMB
    ALLOW -->|"Feed-Items"| EMB
    EMB --> WISSEN
    WISSEN -->|"Top-K Kontext"| SLM
    SLM -->|"Antwort + Quellen"| UI["PWA-UI: Themen wählen ·<br/>Aktualisieren · Fragen stellen"]
```

## 2. Der Self-Evolving-Loop (Ablauf pro Aktualisierung/Frage)

```mermaid
sequenceDiagram
    participant N as 👤 Nutzer
    participant UI as PWA-UI
    participant S as feed-scraper.wasm
    participant A as Agenten-Loop (SLM)
    participant M as Memory (IndexedDB)

    N->>UI: Thema wählen / "Aktualisieren"
    UI->>S: fetch-feed(url) je Feed der Allowlist
    S-->>UI: Items (Titel, Link, Datum, Text)
    UI->>A: Items in Batches
    A->>A: Hebel 3a: Relevanz-Filter<br/>"relevant fürs Thema? ja/nein"
    A->>M: relevante Items → Embeddings → Store 'wissen'<br/>(Dedup per Link-Hash)
    N->>UI: Frage stellen
    UI->>M: Embedding der Frage → Top-K Chunks
    M-->>A: Kontext + Quellen
    A->>A: Hebel 1: Antwort NUR aus Kontext
    A->>A: Hebel 3b: Selbstkorrektur-Pass
    A-->>N: Antwort mit Quellenangaben
```

## 3. Modul- und Dateistruktur (geplant)

| Pfad | Inhalt | Status |
|---|---|---|
| `Produkt/scraper-komponente/wit/world.wit` | WIT-Interface der Komponente | Phase 1 |
| `Produkt/scraper-komponente/src/scraper.js` | fetch + RSS/Atom-Parser + Bereinigung | Phase 1 |
| `Produkt/scraper-komponente/package.json` | componentize-js + jco als devDeps, Build-Skripte | Phase 1 |
| `Produkt/scraper-komponente/feed-scraper.wasm` | Build-Artefakt (gitignored, reproduzierbar) | Phase 1 |
| `Produkt/themen-assistent/` | PWA-Modul (UI + Loop), nutzt Vendor-Libs von dokucheck-lokal | Phase 2–4 |
| `Produkt/dokucheck-lokal/vendor/` | WebLLM, transformers.js, pdf.js — WIRD MITGENUTZT, nicht dupliziert | existiert |
| Dashboard-Route `/produkte/themen-assistent/` | Auslieferung wie dokucheck (PRODUCTS-Dict) | Phase 2 |
| Dashboard-Route `/feeds/<id>` | CORS-Proxy für Feeds ohne CORS-Header (Whitelist) | Phase 2, nur bei Bedarf |

## 4. Erweiterungspunkte (für später — hier ansetzen!)

| Erweiterung | Wo ändern | Was NICHT anfassen |
|---|---|---|
| Neues Thema / neue Feeds | Feed-Allowlist (Einstellungen der PWA) + ggf. Proxy-Whitelist | Komponente bleibt gleich |
| Neue Branche (Kanzlei, KMU…) | eigene Feed-/Dokument-Liste + UI-Texte; später Branchen-Finetune-Modell in Modellliste | Loop, Memory, Komponente identisch |
| Besseres Retrieval | Embedding-Modell in KI-Schicht tauschen; Hybrid BM25+Vektor | Stores bleiben (Re-Embedding-Migration nötig) |
| Hintergrund-Sync / Push / NPU | → Trigger T1–T3: Native-App-Stufe (`Plannung/Native-App/`) | PWA bleibt Hauptkanal |
| Heim-Ollama-Anbindung („Stufe 2.5") | neuer Provider in der KI-Schicht (fetch auf Tailnet-Endpunkt) | Rest unverändert |
| Weitere Quellen-Typen (z. B. Sitemaps) | NUR neue Export-Funktion in der Wasm-Komponente + WIT-Eintrag | Rechte-Modell bleibt Feed-only pro Host |

## 5. Sicherheits-Grundsätze (nicht verhandelbar)

1. Netzwerkrechte der Komponente: **nur explizit erlaubte Feed-Hosts** (Wassette-Policy bzw. Allowlist in der PWA) — niemals Wildcard.
2. Alle Nutzdaten (Feeds, Embeddings, Fragen) bleiben im Gerät (IndexedDB) — kein Server-Speicher; Proxy reicht nur durch, loggt keine Inhalte.
3. Beweisbarkeit wie DokuCheck: Netzwerk-Zähler/Beweisleiste auch im Themen-Assistenten.
