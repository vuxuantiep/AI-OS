# feed-scraper — Wasm-Komponente (Themen-Assistent, Phase 1)

Holt RSS/Atom-Feeds als sandboxed WebAssembly-Komponente. Netzwerkzugriff nur
auf explizit freigegebene Hosts (Wassette-Policy, deny-by-default).
Architektur: `../../Plannung/Architektur-Themen-Assistent.md`

## Testen (einfachster Weg)

```bash
python test-scraper.py
```

Erwartung: Test 1 liefert ~50 Tagesschau-Items ✅, Test 2 (fremder Host) wird
von der Sandbox verweigert ✅. Das Skript startet/stoppt den Wassette-Server selbst.

## Testen über Claude Code (MCP)

In einer NEUEN Claude-Code-Sitzung stehen die Wassette-Tools bereit — einfach fragen:
> „Rufe das Tool local_feed-scraper_scraper_fetch-feed mit
> https://www.tagesschau.de/index~rss2.xml auf"

## Neu bauen / neu laden

```bash
npm install          # einmalig (componentize-js + jco)
npm run build        # → feed-scraper.wasm
wassette component load file://C:/…/scraper-komponente/feed-scraper.wasm
wassette permission grant network feed-scraper www.tagesschau.de
```

⚠️ Pfadformat: `file://C:/...` (zwei Slashes) — `file:///C:/` lehnt Wassette ab.
Weitere Feed-Hosts: je ein weiterer `permission grant network`-Aufruf — niemals Wildcards.

## Rechte ansehen / entziehen

```bash
wassette policy get feed-scraper
wassette permission revoke network feed-scraper <host>
```
