# 📋 Aktuelle Arbeiten — Arbeitsjournal

> Tägliche Dokumentation der kompletten Arbeit am AI-OS (von Claude geführt).
> Zweck: Überblick behalten + aus dem Code lernen. Neuester Tag oben.
> Details zur Architektur: [[../../docs/AI-Engineering-Roadmap|Roadmap]] · Lernguide: `docs/AI-OS-Backend-Lernguide.html`

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
*Zuletzt aktualisiert: 2026-07-10*
