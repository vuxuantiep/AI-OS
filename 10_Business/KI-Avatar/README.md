# KI-Avatar — Content-Produkt

Automatisierte KI-Avatar-Video-Pipeline mit zwei Usecases:

| Usecase | Kanäle/Projekte | Monetarisierung | Details |
|---|---|---|---|
| **YouTube-Automation** | "Deutsch Dễ Hiểu", "KI-News Redakteur", "KI für Business" | AdSense, Affiliate | [[01_Usecases/usecase-youtube-automation]] |
| **TikTok-Shop** | Shoppable Videos mit Produktlinks | Shop-Provision, Affiliate | [[01_Usecases/usecase-tiktok-shop]] |
| **AI Business Checker** | Prüf-Kanal: "Geld verdienen mit KI"-Anbieter auf Seriosität testen (Animation statt Avatar) | AdSense, Memberships (bewusst KEINE Affiliates) | [[01_Usecases/usecase-ai-business-checker]] |

## Pipeline (7 Stufen)

```
Trend-Scan ──▶ Skript ──▶ Stimme ──▶ Avatar ──▶ Edit ──▶ QA-Check ──▶ Posting
SearXNG/      Qwen3/     Kokoro-    HeyGen/    FFmpeg-   KI-Label-    n8n
Qdrant        Claude     TTS        Arcads     Schnitt   Check        Scheduler
```

- **Grau** = Ein-/Ausgabe (Trend-Scan, Posting)
- **Türkis** = selbst gehostet in der AI Factory (Skript, Stimme, Edit, QA-Check)
- **Koralle** = einzige externe bezahlte API (Avatar: HeyGen/Arcads)

## Verwaltung: Pipeline-Board (Trello-artig)

Zentrale Verwaltungsseite als AI-OS-Erweiterung — jedes Video ist eine Karte,
die per Drag & Drop durch die 7 Pipeline-Stufen wandert.

```bash
python 10_Business/KI-Avatar/board/app.py
# → http://localhost:5310
```

- Spalten = Pipeline-Stufen (+ "Veröffentlicht")
- Karten = Videos mit Usecase, Plattform, Compliance-Status, Notizen
- Filter nach Usecase (YouTube / TikTok-Shop)
- Persistenz: `board/data/board.json` (wird automatisch angelegt)

## Ordnerstruktur

```
KI-Avatar/
├── README.md                    ← diese Datei
├── 01_Usecases/                 ← Usecase-Beschreibungen
├── Konzept-KI Avatar/           ← Konzeptdokumente + Agenten-Prompts
│   └── compliance-critic-agent.md  ← QA-Check-Agent (letzte Instanz vor Posting)
└── board/                       ← Pipeline-Board (Flask, Port 5310)
    ├── app.py
    ├── templates/board.html
    └── data/board.json
```

## Compliance (Kurzfassung)

Kein Video geht raus ohne Freigabe durch den [[Konzept-KI Avatar/compliance-critic-agent|Compliance-Critic-Agent]]:
KI-Kennzeichnung (Art. 50 EU-KI-VO, gilt ab 02.08.2026), Werbekennzeichnung (§5a UWG),
Impressum, verbotene Claims, Wiederholungsrate, Plattform-Limits — und für den
AI Business Checker zusätzlich Äußerungsrecht (Belegpflicht, 2-Quellen-Minimum,
Stellungnahme-Pflicht bei Deep-Dives). Themen-Recherche für den Checker:
[[Konzept-KI Avatar/market-research-agent|Market-Research-Agent]].

#wichtig #ki-avatar #business
