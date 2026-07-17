# 💼 10_Business — Produkte & Geschäftsprojekte

Aufteilung (Stand 17.07.2026): **`01_Marktprodukte/`** = verkaufbare Produkte,
**`02_Interne-Tools/`** = eigene Werkzeuge (kein Wirtschaftlichkeits-Gate nötig).
Jedes Produkt folgt derselben Struktur:

```
10_Business/01_Marktprodukte/<Produktname>/
├── README.md                      ← Idee, Elevator-Pitch, Status
├── Plannung/                      ← Konzept.md + Material (PDFs, Screenshots, Recherche)
├── wirtschaftlichkeit-<name>.md   ← PFLICHT vor Umsetzung (Gate-Regel 4, CLAUDE.md)
└── app/                           ← der Code (sobald Umsetzung freigegeben)
```

Nur `.md`-Dateien wandern ins KI-Gedächtnis (RAG-Index) — Konzepte deshalb
immer als Markdown schreiben, PDFs/Screenshots sind nur Beilage.

## 01_Marktprodukte (verkaufbar)

| Ordner | Was | Status |
|---|---|---|
| `IT Pipeline System inkl CRM/` | LeadPilot CRM + Lead-Radar (Port 5330) | In Betrieb (Phase A) |
| `KI-Avatar/` | Video-Pipeline YouTube/TikTok + AI-Business-Checker | In Betrieb (Board :5310, Checker :5320) |
| `Lokal-SML-Webassembly-MultiMemory/` | Plattform „Souveräne lokale KI": DokuCheck (Stufe 1) + Self-Evolving Agent (Stufe 2, Bauplan liegt) + Native App (Stufe 3) | v0.2, unter `/produkte/dokucheck/` |

Hinweis: Am 17.07.2026 wurden „Client-Side Self-Evolving AI" (→ Stufe 2) und
„Lokal-Private-LLM-App" (→ Stufe 3, `Plannung/Native-App/`) in die
Lokal-SML-Plattform eingegliedert — gleiche Nische, gleiche Zielgruppe,
ein Gate statt drei.

## 02_Interne-Tools (Eigenbedarf)

| Ordner | Was | Status |
|---|---|---|
| `CEO-Dashboard/` | Next.js-Dashboard mit 3D-Bots + AI-OS-Chat | Prototyp |

Das AI-OS-Dashboard selbst (Port 5000) ist Infrastruktur und liegt in
`04_Infrastruktur/Gateway/` — nicht hier.

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
