# 🧠 Gedächtnis (Memory-Layer)

Das Wissensmodell ist bewusst in getrennte Kategorien aufgeteilt, damit nicht alles in einem einzigen
Vektorindex landet:

| Ordner | Inhalt |
|---|---|
| `Business-Knowledge/` | Produkte, Kunden, Strategien |
| `Technical-Knowledge/` | APIs, Docker, FastAPI, Python |
| `Agent-Knowledge/` | Rollen, Fähigkeiten, Grenzen |
| `Project-Knowledge/` | Entscheidungen, ADRs, Architektur |
| `Memory/Short-Memory/` | Kurzfristiger Kontext (aktuelle Session/Aufgabe) |
| `Memory/Long-Memory/` | Dauerhaftes, konsolidiertes Wissen |
| `Memory/Episodic-Memory/` | Konkrete vergangene Ereignisse/Interaktionen |
| `Prompt-Library/` | Wiederverwendbare Prompts |
| `SOP-Library/` | Standard Operating Procedures |
| `Vector-Database/` | Vektor-Index (`vector_store.json`), separat pro Kategorie einzubetten |

`knowledge_agent.py` (Indexer/RAG-Service) liegt hier als technische Komponente, die diese Kategorien
verarbeitet. Der eigentliche Obsidian-Vault mit den Rohnotizen bleibt in `00_Wissen/` — dieser Ordner ist
die technische Memory-Schicht *auf* diesem Wissen, nicht das Wissen selbst.

## Status
🟡 Struktur angelegt, Inhalte noch nicht kategorisiert/migriert.
