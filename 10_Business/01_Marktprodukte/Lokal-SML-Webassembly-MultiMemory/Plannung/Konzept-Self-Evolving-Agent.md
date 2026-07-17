# 🧬 Konzept: Client-Side Self-Evolving AI (Ausbaustufe der Plattform)

> Destillat aus dem Chat-Export „Die Kombination dieser fünf Technologien ergibt
> ein ultramodernes.docx" (liegt daneben). Eingeordnet 17.07.2026: Das ist
> **Stufe 2 / Produkt 2** der Nische „SLM + WebAssembly + Multi-Memory" —
> gleicher Stack wie DokuCheck Lokal, erweitert um Agentik + selbstwachsendes Gedächtnis.

## Die 5 Technologien (Architektur „Local-First AI")

1. **Edge AI + Browser-SLM** — kleines Modell läuft im Browser auf dem Endgerät (WebLLM/MLC)
2. **WebAssembly + WebGPU** — nahezu native Geschwindigkeit, GPU-Zugriff (bei uns: DokuCheck v0.2 ✓)
3. **Multimodale LLMs** — Text + Bilder + Kamera + Dokumente lokal analysieren
4. **Agentic AI** — Agenten-Loop: Planung → Ausführung → Selbstkorrektur
5. **Self-Evolving Memory** — Agent recherchiert autonom und erweitert sein eigenes Gedächtnis

## 3-Säulen-Architektur des Self-Evolving-Loops

1. **Autonomer Web-Scraper (Tool-Use):** `fetch()` + CORS-Proxy (oder Extension),
   Bereinigung mit Readability.js → Rohtext ans SLM.
2. **Agentische Filterung:** SLM bewertet gescrapte Chunks („relevant für die
   Forschungsfrage? ja/nein") — schützt kleine Modelle vor Kontext-Überlauf.
3. **Lokales Langzeit-Gedächtnis:** Embedding via Transformers.js (z. B. bge-small),
   Vektoren in **IndexedDB / OPFS** — überlebt Tab-Refresh, bleibt auf dem Gerät.

Workflow: Wissenslücke erkennen → Suchbegriffe generieren → scrapen → Kernpunkte
extrahieren (mit Selbstkorrektur) → als Vektoren ins lokale Gedächtnis → beim
nächsten Mal Antwort direkt aus dem eigenen Gedächtnis.

## SLM-Qualität — die 3 Hebel (wichtigste Erkenntnis)

SLMs nie als „allwissendes Genie" einsetzen, sondern als **spezialisierten Experten**:

| Hebel | Wirkung |
|---|---|
| **Lokales RAG** | Halluzinationen fast eliminiert — Modell fasst nur noch gelieferten Kontext zusammen |
| **QLoRA-Finetuning** auf Fachdaten | 3B-Modell wird im Spezialgebiet präziser als generisches GPT-4 |
| **Agentic Workflows** (Planung → Ausführung → Reflexion) | kleines Modell schlägt per Reflexions-Loop oft größere Modelle |

## Warum die Chance groß ist

- Cloud-Riesen (OpenAI/Google/MS) vernachlässigen Browser-lokal — sie verkaufen Server-Abos
- NPUs in Smartphones werden jährlich drastisch stärker → heutige Ruckler sind in 12–24 Monaten weg
- **B2B-USP:** Firmen-Agent scrapt nur Intranet/Fachportale; Gelerntes bleibt in der
  IndexedDB des einen Geräts — kein Abfluss in Cloud-Training (DSGVO-Argument wie bei DokuCheck)

## Bezug zur bestehenden Roadmap (DokuCheck / Plattform)

- v0.3 Embeddings (transformers.js) = **identische Technik** wie Säule 3 hier → Synergie
- Multi-Memory-Panel (8 Memory-Typen, IndexedDB) = Fundament, das der Self-Evolving-Loop befüllt
- v0.5 GraphRAG = passt als Struktur für das selbst aufgebaute Wissen
- Werkzeuge aus dem Dokument, die wir noch nicht nutzen: Readability.js, OPFS,
  BrowserOS/BrowserClaw (Agent-Loop im Browser), Microsoft Wassette (Wasm-Sandbox + MCP)

## Status

Konzeptphase. ⚠️ Wirtschaftlichkeits-Gate (Regel 4) vor Umsetzung nötig —
sinnvoll als Erweiterungs-Prüfung der bestehenden Plattform, nicht als neues Produkt.
Verwandt: [[PRD_DokuCheck-Lokal]], [[2026-07-17_Lernpfad_SLM-und-Webtechnologie]]
