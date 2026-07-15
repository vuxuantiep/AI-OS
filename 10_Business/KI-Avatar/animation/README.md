# AI Business Checker — Animations-Templates (Remotion)

Datengetriebene Video-Templates: **ein Dossier-JSON rein → fertiges Video raus.**
Kein HeyGen, keine externe API — gerendert wird lokal (Remotion + Headless Chrome).

## Kompositionen

| ID | Format | Aufbau |
|---|---|---|
| `CheckerLong` | 1920×1080 (YouTube) | Intro → alle Warnsignale (je 6 s) → Risiko-Score → Outro/Checkliste. Dauer wächst automatisch mit der Anzahl Warnsignale |
| `CheckerShort` | 1080×1920 (Shorts/TikTok) | Kompakt: Intro → 1 Warnsignal → Score → Outro (14 s) |

Eingebaute Pflicht-Bausteine: **KI-Label ab Sekunde 1** (Art. 50 EU-KI-VO),
durchlaufende **Quellenleiste**, Score-Einordnung als gekennzeichnete **Meinungsäußerung**.

## Benutzung

```bash
cd 10_Business/KI-Avatar/animation
npm install                # einmalig

npm run studio             # Vorschau/Editor im Browser
npm run render-long        # rendert mit Beispiel-Dossier
npm run render-short

# Mit echtem Dossier (aus Research-Agent + Skript-Stufe):
npx remotion render CheckerLong out/video.mp4 --props=./pfad/zum/dossier.json
```

## Dossier-JSON (Schnittstelle zur Pipeline)

Siehe `src/data/beispiel-dossier.json` — Felder: `titel`, `anbieter`, `claim`,
`warnsignale[] {code, name, zitat, quelle}`, `score` (0–10), `einschaetzung`,
`stellungnahme`, `datum`. Erzeugt wird das Dossier vom
[[../Konzept-KI Avatar/market-research-agent|Market-Research-Agent]] (Belege!)
plus Skript-Stufe; TTS-Audio (Kokoro) wird in einer späteren Version als
`<Audio>`-Spur eingebunden.

## Design anpassen

Farben/Schrift zentral in `src/theme.js`, Szenen in `src/scenes/`,
Szenen-Längen in `src/CheckerVideo.jsx` (`TIMING`).
