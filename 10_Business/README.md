# 💼 10_Business — Produkte & Geschäftsprojekte

Jedes Produkt folgt derselben Struktur (Stand 17.07.2026):

```
10_Business/<Produktname>/
├── README.md                      ← Idee, Elevator-Pitch, Status
├── Plannung/                      ← Konzept.md + Material (PDFs, Screenshots, Recherche)
├── wirtschaftlichkeit-<name>.md   ← PFLICHT vor Umsetzung (Gate-Regel 4, CLAUDE.md)
└── app/                           ← der Code (sobald Umsetzung freigegeben)
```

Nur `.md`-Dateien wandern ins KI-Gedächtnis (RAG-Index) — Konzepte deshalb
immer als Markdown schreiben, PDFs/Screenshots sind nur Beilage.

## Produkte

| Ordner | Was | Status |
|---|---|---|
| `IT Pipeline System inkl CRM/` | LeadPilot CRM + Lead-Radar (Port 5330) | In Betrieb (Phase A) |
| `KI-Avatar/` | Video-Pipeline YouTube/TikTok + AI-Business-Checker | In Betrieb (Board :5310, Checker :5320) |
| `Lokal-SML-Webassembly-MultiMemory/` | DokuCheck Lokal (Browser-KI) + Ausblick Self-Evolving Agent | v0.2, unter `/produkte/dokucheck/` |
| `CEO-Dashboard/` | Next.js-Dashboard mit 3D-Bots + AI-OS-Chat | Prototyp |
| `Lokal-Private-LLM-App/` | Mobile Gateway-App (Expo, On-Device-LLM + Tailscale-Routing) | Konzept — Gate ausstehend |

Hinweis: „Client-Side Self-Evolving AI" wurde am 17.07.2026 in
`Lokal-SML-Webassembly-MultiMemory/Plannung/Konzept-Self-Evolving-Agent.md`
eingegliedert (gleiche Nische, gleicher Stack — Stufe 2 der Plattform).

## Keine Produkte (Infrastruktur/Output — Pfade werden von Code referenziert, NICHT verschieben)

| Ordner | Zweck | Referenziert von |
|---|---|---|
| `KI-Fabrik-Auftraege/` | Auto-Ablage der KI-Fabrik-Ergebnisse | `ai_os_dashboard.py` (FACTORY_RESULTS_DIR) |
| `content/videos/` | Video-Downloads | `higgsfield_agent.py` |
| `wirtschaftlichkeits-pruefer-agent.md` | Gate-Agent (Regel 4) | `CLAUDE.md` |

Ebenfalls von Code referenziert (in den Produkten): `KI-Avatar/board/`,
`KI-Avatar/research-agent/`, `IT Pipeline System inkl CRM/app/`,
`Lokal-SML-Webassembly-MultiMemory/Produkt/` — Umbenennen nur zusammen mit
`ai_os_dashboard.py`.
