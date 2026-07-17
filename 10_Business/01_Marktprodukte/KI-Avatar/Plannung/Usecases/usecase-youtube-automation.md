# Usecase 1: YouTube-Automation

## Ziel
Vollautomatische Produktion von KI-Avatar-Videos (Shorts + Long-Form) für drei Kanäle:
- **Deutsch Dễ Hiểu** — Deutsch lernen für Vietnamesisch-Sprecher
- **KI-News Redakteur** — tagesaktuelle KI-News
- **KI für Business** — KI-Anwendung für Unternehmer

## Pipeline-Belegung

| Stufe | Tool | Hosting | Aufgabe |
|---|---|---|---|
| Trend-Scan | SearXNG + Qdrant | selbst (AI Factory) | Themenrecherche, Duplikat-Check gegen Vektor-DB |
| Skript | Qwen3 / Claude | selbst / API | Hook + Skript + Caption + Hashtags |
| Stimme | Kokoro-TTS | selbst | Voiceover (DE, VI) |
| Avatar | HeyGen / Arcads | **extern, bezahlt** | Lippensynchrones Avatar-Video |
| Edit | FFmpeg | selbst | Schnitt, Untertitel, KI-Wasserzeichen einbrennen |
| QA-Check | Compliance-Critic-Agent | selbst (LLM) | Freigabe/Block, siehe Agenten-Prompt |
| Posting | n8n Scheduler | selbst | Upload + natives KI-Label setzen, Zeitplan |

## Formate
- `youtube_shorts`: ≤ 180 s, Hochformat, 1–2/Tag pro Kanal
- `youtube_long`: 5–12 min, wöchentlich, Art.-50-Kennzeichnung am Anfang der Beschreibung

## KPIs (Start)
- 30 Shorts/Monat pro Kanal, < 15 min manuelle Arbeit pro Video
- Kosten-Deckel: nur Avatar-API kostet Geld → Budget pro Video tracken

#ki-avatar #youtube
