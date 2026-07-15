# Usecase 3: AI Business Checker

> YouTube-Kanal + TikTok-Shorts: Aktuelle „Geld verdienen mit KI"-Anbieter im Internet
> auf Seriosität prüfen — Warnung und Aufklärung für Zuschauer, bevor sie Geld verlieren.

## 1. Kanal-Konzept

| Punkt | Entscheidung |
|---|---|
| **Positionierung** | Der unabhängige Prüfer: „Wir testen, bevor du zahlst" |
| **Zielgruppe** | Deutschsprachige Einsteiger, die Angebote wie „500 €/Tag mit ChatGPT" sehen und unsicher sind |
| **Nutzenversprechen** | Pro Video eine klare, belegte Einschätzung: Welche Warnsignale gibt es? Was steckt wirklich dahinter? |
| **Format-Mix** | YouTube Long (8–12 min Deep-Dive) · YouTube Shorts + TikTok (45–60 s Warnung/Hook) · Community-Posts für Themenwünsche |
| **Stil** | **Animation statt Avatar** — Erklärvideo-Stil (Icons, Charts, Screenshots mit Markierungen, Sprecherstimme). Vorteil: keine HeyGen-Kosten, kein „KI-Gesicht"-Vertrauensproblem bei einem Prüf-Kanal |
| **Ton** | Sachlich, nüchtern, keine Häme — Glaubwürdigkeit ist DAS Kapital dieses Kanals |

### Wiederkehrende Formate
1. **„Seriös oder Abzocke?"** — Deep-Dive zu einem konkreten Anbieter (Long-Form)
2. **„Warnsignal der Woche"** — ein Muster erklärt (Fake-Testimonials, Countdown-Druck, Rendite-Versprechen) (Short)
3. **„Nachgeprüft"** — Follow-up: Was wurde aus Anbieter X nach 3 Monaten? (Long/Short)
4. **„Checkliste"** — 60-Sekunden-Prüfschema für die Zuschauer (Short, hohe Share-Rate)

## 2. Pipeline (angepasst gegenüber Usecase 1/2)

```
Research-Scan ──▶ Themen-Scoring ──▶ Dossier ──▶ Skript ──▶ Stimme ──▶ Animation ──▶ Edit ──▶ QA/Legal-Check ──▶ Posting
Market-Research-  Risiko/Trend/     Beweise +   Qwen3/     Kokoro-    Remotion/       FFmpeg   Compliance-Critic   n8n
Agent (SearXNG/   Beweislage        Quellen     Claude     TTS        Motion Canvas            + Äußerungsrecht
Reddit/Foren)                                                         (selbst gehostet)
```

**Wichtigste Änderungen zur Avatar-Pipeline:**
- **Trend-Scan → Research-Scan:** eigener [[../Konzept-KI Avatar/market-research-agent|Market-Research-Agent]] (siehe eigenes Dokument) durchsucht Reddit, Foren, Verbraucherportale und Bewertungsplattformen nach neuen KI-Geld-Angeboten und Beschwerden.
- **Neue Stufe „Dossier":** Pro Thema entsteht ein Beweis-Dossier (Quellen-URLs, Zitate, Screenshots, Datum) — Pflicht-Input für Skript UND Legal-Check. Ohne Dossier kein Video.
- **Avatar → Animation:** komplett selbst gehostet (Remotion oder Motion Canvas, gerendert auf dem eigenen Rechner). Damit fällt die einzige externe bezahlte API (HeyGen) für diesen Usecase weg.
- **QA-Check erweitert:** zusätzlich zur bestehenden Compliance-Prüfung ein **Äußerungsrecht-Check** (siehe Abschnitt 5) — für diesen Kanal der härteste Blocker.

## 3. Market-Research-Agent (Kurzfassung)

Vollständiger Prompt: [[../Konzept-KI Avatar/market-research-agent|market-research-agent.md]]

**Quellen (Start-Set):**
| Quelle | Was dort gesucht wird |
|---|---|
| Reddit (r/Scams, r/passive_income, r/Finanzen, r/kleinanzeigen) | frische Beschwerden, Erfahrungsberichte |
| https://blog.verbraucherdienst.com/ | dokumentierte Warnungen (RSS/Scrape) |
| Verbraucherzentrale.de + BaFin-Warnliste | **amtliche Quellen — höchste Beweiskraft** |
| Trustpilot / Google Reviews | Bewertungsmuster (viele 1★ + gekaufte 5★?) |
| Foren (gutefrage, ComputerBase, Finanzforen) | Fragen „Ist X seriös?" = Suchintention! |
| YouTube/TikTok selbst | welche Anbieter werben gerade aggressiv? |

**Technik:** SearXNG (selbst gehostet) für die Breitensuche, Qdrant für Dedup gegen schon behandelte Themen, Scheduled Run 1×/Tag über n8n oder LangGraph-Engine (:5500).

**Themen-Scoring (0–10 je Kriterium):**
1. **Aktualität/Trend** — wird gerade aggressiv beworben? Suchvolumen steigend?
2. **Publikums-Risiko** — wie viel Geld können Zuschauer verlieren?
3. **Beweislage** — wie viele unabhängige, zitierfähige Quellen? (unter 2 → kein Video, nur Beobachtungsliste)
4. **Konkurrenz-Lücke** — gibt es schon gute deutsche Videos dazu?

## 4. Video-Produktion (Animation)

| Baustein | Werkzeug | Anmerkung |
|---|---|---|
| Skript + Storyboard | Qwen3/Claude | Vorlage: Hook (Versprechen des Anbieters) → Prüfung (3–5 Warnsignale mit Belegen) → Einordnung → Checkliste für Zuschauer |
| Sprecherstimme | Kokoro-TTS | seriöse, ruhige Stimme; keine Hype-Betonung |
| Animation | **Remotion** (React-basiert, programmierbare Video-Templates) — Alternative: Motion Canvas | Ein Template-Satz: Intro, „Warnsignal"-Karte, Quellen-Einblendung, Score-Anzeige, Outro. Einmal bauen, für jedes Video nur Daten austauschen → echte Automatisierung |
| Screenshots/Belege | Playwright (headless) | Anbieter-Webseite + Quellen automatisch archivieren (mit Zeitstempel — dient zugleich als Beweissicherung!) |
| Schnitt/Untertitel | FFmpeg + Whisper | wie bestehende Pipeline |
| Shorts-Ableitung | FFmpeg-Crop 9:16 | pro Long-Video 3–5 Shorts: je 1 Warnsignal = 1 Short |

**Visuelle Kennzeichnung:** Jedes Video zeigt durchgehend eine Quellenleiste (unten) und einen Einschätzungs-Score. KI-Label gemäß Art. 50 EU-KI-VO bleibt Pflicht (synthetische Stimme!).

## 5. Recht — der kritischste Teil dieses Kanals ⚠️

Ein Kanal, der Anbieter „Abzocker" nennt, bewegt sich im Äußerungsrecht (§§ 185 ff. StGB, § 824 BGB, Verdachtsberichterstattung). Eine falsche Tatsachenbehauptung = Abmahnung/einstweilige Verfügung. Regeln (werden als **Check 7 im Compliance-Critic-Agent** erzwungen):

1. **Tatsache vs. Meinung sauber trennen.** Tatsachen („Firma X hat kein Impressum", „BaFin warnt seit 05/2026") nur mit Beleg im Dossier. Bewertungen immer als Einschätzung kennzeichnen („aus unserer Sicht riskant", „typische Warnsignale").
2. **Nie „Betrug"/„Betrüger" ohne rechtskräftiges Urteil.** Stattdessen: „Warnsignale", „intransparent", „wir raten zur Vorsicht". Das Wort „Abzocke" nur als erkennbare Meinungsäußerung mit Tatsachenkern.
3. **Mindestens 2 unabhängige Quellen** pro namentlicher Anbieter-Nennung, davon idealerweise 1 amtliche (BaFin, Verbraucherzentrale, Gericht).
4. **Stellungnahme anbieten:** Vor Veröffentlichung eines Deep-Dives Anfrage an den Anbieter (E-Mail genügt, Frist 5–7 Tage, im Video erwähnen: „Anbieter X hat auf unsere Anfrage nicht reagiert"). Das ist Kernpflicht der Verdachtsberichterstattung.
5. **Beweissicherung:** Dossier mit datierten Screenshots wird pro Video archiviert (`10_Business/KI-Avatar/dossiers/`), Aufbewahrung mindestens 3 Jahre.
6. **Kein Interessenkonflikt:** KEINE Affiliate-Links zu geprüften oder konkurrierenden Anbietern. Monetarisierung nur AdSense/Memberships — sonst ist die Unabhängigkeit (und damit der Meinungsschutz) angreifbar.

*Hinweis: Das ist eine Arbeitsgrundlage, keine Rechtsberatung — vor dem ersten Deep-Dive mit Namensnennung einmalig anwaltlich prüfen lassen (Medienrecht, ~200–400 €, gut investiert).*

## 6. Monetarisierung

| Phase | Quelle |
|---|---|
| Ab Start | YouTube AdSense (Shorts + Long), TikTok Creator Rewards |
| Ab 10k Abos | Kanal-Mitgliedschaften („Früh-Warnliste" als Perk) |
| Später | Eigenes Produkt: „KI-Anbieter-Checkliste" (PDF/Notion), Sponsoring nur von unabhängigen Tools (Passwort-Manager etc.), niemals von KI-Geld-Anbietern |

## 7. Roadmap

| Phase | Dauer | Meilenstein |
|---|---|---|
| **0 — Setup** | 1–2 Wochen | Remotion-Template-Satz bauen, Market-Research-Agent (v1: SearXNG + Reddit-RSS), Kanal-Branding, Impressum |
| **1 — MVP** | 4 Wochen | 4 Long-Videos + 12 Shorts halbmanuell (Agent liefert Dossier, Skript reviewed CEO, Rendering automatisch). Ziel: Format validieren |
| **2 — Automatisierung** | 4–8 Wochen | LangGraph-Pipeline Research→Dossier→Skript→Render, Board-Karten automatisch anlegen, Stellungnahme-Mails halbautomatisch |
| **3 — Skalierung** | ab Monat 3 | 2 Longs + 6 Shorts/Woche, Follow-up-Format „Nachgeprüft", ggf. EN-Ableger |

**KPIs:** Abo-Wachstum, Watchtime Long-Form (>40 %), Shorts-Share-Rate, 0 berechtigte Abmahnungen (harte Nebenbedingung).

## 8. Integration ins AI-OS

- **Pipeline-Board (:5310):** neuer Usecase „AI Business Checker" mit eigenem Filter — Karten durchlaufen dieselben Stufen; „Trend-Scan" heißt für diesen Usecase inhaltlich „Research-Scan".
- **Agenten:** Market-Research-Agent als Prompt-Dokument (später eigener Dienst im Agent-System :5300), Compliance-Critic-Agent um Check 7 (Äußerungsrecht) erweitert.
- **Ablage:** Dossiers unter `10_Business/KI-Avatar/dossiers/<anbieter-slug>/` (Screenshots + JSON + Skript).

#ki-avatar #ai-business-checker #youtube #tiktok
