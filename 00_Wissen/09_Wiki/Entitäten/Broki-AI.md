# Broki AI (Produkt-Entität)

*Ingest-Quelle: Claude-Code-Sessions 18.–23.07.2026 (Bau, Design-Iteration,
Backend-Debugging). Verdichtet, nicht wörtliches Protokoll. Ausführliches
Session-Gedächtnis: `project-broki-ai` (Claude-Memory-System, siehe unten).*

## Was es ist

Manifest-V3-Browser-Extension: "Firmen-Wiki + KI-Berater", 100% lokal im
Browser lauffähig. Sidebar-Chat (Chrome Side Panel API), RAG gegen ein
Firmen-Wiki, das per Tailscale von einem Raspberry Pi (`broki-pi-server`)
signiert synchronisiert wird. Produktisierung der "Lokal-SML-Webassembly-
MultiMemory"-Plattform.

Code: `10_Business/01_Marktprodukte/Lokal-SML-Webassembly-MultiMemory/Produkt/broki-extension/`

## Architektur (Kernbausteine)

- **3-Stufen-Gedächtnis**: L1 Exact-Cache, L2 Semantic-Cache (Cosine ≥0.92),
  L3 RAG gegen den Pi-Wiki-Index. `modules/memory-manager.js`.
- **LLM-Gateway** (`modules/llm-gateway.js`): motor-agnostisch, probiert
  mehrere lokale KI-Engines der Reihe nach durch — siehe
  [[Lokale-LLM-Motoren-Browser]] für die technischen Details und die
  wichtigsten Bugs/Fixes.
- **Tailscale-Sync + ECDSA-Signaturprüfung** (`modules/tailscale-sync.js`):
  Wiki-Index vom Pi wird kryptografisch verifiziert, fail-closed bei
  Manipulation.
- **Privat-Tresor** (`modules/private-vault.js`): RAM-only-Modus, keine
  Persistenz sensibler Dokumente.
- **Crash-Rollback** (`modules/crash-rollback.js`): Formulareingaben
  überleben Tab-/Browser-Absturz.
- **Offscreen-Dokument** (`offscreen/offscreen.js`): DOM-Kontext für WebLLM/
  wllama, da Service Worker kein `import()` erlauben — siehe
  [[MV3-Offscreen-Dokumente-Debugging]] für das generische Muster.

## Produktvision / Positionierung

Zielgruppe: Kanzleien/Praxen (DSGVO-Nische) — Kernversprechen "keine Cloud,
Daten bleiben auf dem Gerät", USP gegenüber Merlin/Sider/Monica (die laut
UCL-Studie DSGVO-Verstöße haben). Verkaufsargument "Trojanisches Pferd,
einfach installieren" setzt voraus, dass NUR die Extension nötig ist (kein
Zusatz-Server/-Prozess) — siehe [[Lokale-LLM-Motoren-Browser]] für die
Geschichte, wie das technisch mal gefährdet war (Ollama-Pivot) und dann
wiederhergestellt wurde (wllama-Fix).

Gate-Status (Stand 18.07.2026): `GO_MIT_AUFLAGEN`, wartet auf CEO-Freigabe.
Auflage 1 = Dogfooding zuerst (Pi-Gegenstück als eigene AI-OS-Komponente,
kein Vertrieb vor Referenz).

Zukunfts-Vision (noch nicht gebaut): ein Broki-Agenten-*Team* — "Assistentin"
(Chat-Frontend, umgesetzt) + "Junge" (Hintergrund-Analyse-Agent, der lernt
WIE der Nutzer arbeitet, noch nicht gebaut).

## Wichtigste bisherige Design-Entscheidungen

- Design-System: echte, vom CEO gelieferte Illustrationen statt KI-generierte
  Bilder als Standard-Logo/Maskottchen, Farbpalette per Pixelmessung (nicht
  geraten) aus dem Logo abgeleitet.
- Alle sichtbaren UI-Rahmen entfernt (Apple/Perplexity-Minimalismus-Vorbild),
  Chat-Nachrichten als reiner Text-Transkript-Look statt Sprechblasen.

## Related

- Claude-Memory: `project-broki-ai` (vollständiges, chronologisches
  Session-Gedächtnis — Design-Iterationen, alle CEO-Entscheidungen im Detail)
- [[Lokale-LLM-Motoren-Browser]] — LLM-Gateway-Architektur + Ollama/wllama-Bugs
- [[MV3-Offscreen-Dokumente-Debugging]] — generisches Chrome-Extension-Wissen
- `Plannung/Broki-4-Saeulen-Framework.md` — Ist/Roadmap-Mapping
- `Plannung/Architektur-Broki-Extension.md` — Architekturdiagramm
