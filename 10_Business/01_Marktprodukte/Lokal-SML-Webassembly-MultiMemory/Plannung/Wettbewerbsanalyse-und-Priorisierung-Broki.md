# 🥊 Broki AI — Wettbewerbsanalyse & Priorisierungs-Empfehlung

> Erstellt 18.07.2026 auf CEO-Frage „Ist Broki stärker als andere? Wenn ja,
> zum vollständigen Produkt entwickeln und priorisieren." Recherche-gestützt
> (Quellen unten). Verwandt: [[Architektur-Broki-Extension]], [[wirtschaftlichkeit-broki-ai]].

## Kernantwort (ehrlich)

**In seiner Nische — regulierte Branchen mit DSGVO-Zwang (Kanzleien, Praxen,
Steuerberater) — ist Broki nicht nur vergleichbar, sondern strukturell
überlegen.** Nicht weil es technisch raffinierter wäre, sondern weil die
bequeme, ausgereifte Konkurrenz dort **rechtlich disqualifiziert** ist.
Für den Massenmarkt (Nutzer ohne Datenschutz-Zwang) ist Broki dagegen NICHT
stärker — dort gewinnt Bequemlichkeit (kein Pi, kein Setup, kein GB-Download).
→ **Empfehlung: JA, vollständig entwickeln — aber scharf auf die Nische
fokussiert, nicht als „Merlin-Killer für alle".**

## Das Wettbewerbsfeld (Stand 2026)

### Gruppe A — Cloud-Browser-Assistenten (die bequemen)
Merlin, Sider, Monica, TinaMind, HARPA AI. Ausgereift, poliert, große Nutzerbasis,
viele Features. **Aber: massives Datenschutzproblem — für Broki der Steilpass.**
- UCL/unabhängige Studien 2025: verletzen wahrscheinlich DSGVO; zeichnen z. T.
  auch im Privatmodus weiter auf.
- **Merlin wurde erwischt, wie es eine Sozialversicherungsnummer aus einem
  IRS-Formular exfiltrierte.** Sider/TinaMind teilen Nutzerfragen + IP mit
  Google Analytics (Cross-Site-Tracking).
- Studien-Fazit wörtlich sinngemäß: **„ungeeignet für Enterprise-Nutzung"**
  wegen HIPAA/DSGVO-Risiken.
- → In Kanzleien/Praxen ist der Einsatz dieser Tools ein Compliance-Verstoß.
  Genau hier ist Broki (100 % lokal, nichts verlässt das Gerät) konkurrenzlos.

### Gruppe B — Lokale In-Browser-Tech (die Bausteine)
WebLLM (MLC), WebML, Transformers.js, ONNX Runtime Web, LiteRT.js, Chrome
Prompt API (Gemini Nano). **Sind Technologien / Tech-Demos, keine Produkte.**
- WebLLM hat Beispiel-Chrome-Extensions — aber das ist ein Chat-Fenster, kein
  Firmen-RAG, keine proaktive Assistenz, kein Pi-Sync, kein kollektives Wissen.
- Broki NUTZT diese Bausteine (WebLLM/wllama/Transformers.js) und baut das
  Produkt darüber. Der Abstand „Demo → verkaufbares Enterprise-Produkt" ist
  genau Brokis Wertschöpfung.

### Gruppe C — Der Enterprise-Elefant
Microsoft 365 Copilot. Mächtig, tief integriert, aber Cloud (Daten zu MS
hochgeladen), ~30 €/Seat, nur im MS-Ökosystem. Brokis Gegenargumente stehen
schon im [[Architektur-Broki-Extension]] §5b: lokal, plattformübergreifend, 0 €/Seat.

## Brokis echter, verteidigbarer USP (was keiner der drei hat)

1. **100 % lokal + Firmen-RAG** — die Cloud-Assistenten sind lokal-schwach,
   die lokalen Tech-Demos haben kein Firmen-Wissen. Broki verbindet beides.
2. **Pi + Tailscale-Sync mit signiertem Index** — kollektives Firmengehirn ohne
   Server, kryptografisch manipulationsgeschützt. Gibt es so bei keinem.
3. **Proaktive Assistenz** (siehe Frontend-Mockup) — nicht ein Chat-Fenster, das
   man fragen muss, sondern warnt aktiv („USt-IdNr. ungültig", „2 Pflichtangaben
   fehlen"). Das ist der Sprung von „Chatbot" zu „Intelligenzschicht".
4. **IT-Crash-Rollback** — verkauft sich als „Lebensversicherung", hat kein Konkurrent.

## Ehrliche Schwächen (nicht verschweigen)

- **Reifegrad:** Merlin/Sider sind fertige Politur; Broki ist Kern + Pi-Server,
  Frontend/vendor fehlen. Monate Arbeit bis Mockup-Niveau.
- **Setup-Hürde:** Pi + Tailscale + Modell-Download ist für den Kunden mehr
  Aufwand als „Extension installieren". Muss durch Done-for-you-Setup abgefedert werden.
- **Ein-Personen-Team:** Feature-Wettlauf gegen finanzierte Startups ist nicht
  gewinnbar → NICHT auf Feature-Breite konkurrieren, sondern auf die eine Sache,
  die nur Broki kann (lokal + Firmen-RAG + proaktiv, für regulierte Branchen).

## Priorisierungs-Empfehlung: JA — mit dieser MVP-Reihenfolge

Das Frontend-Mockup (`Broki Ai-Frontend.png`) ist das Nordstern-Ziel (Vollprodukt).
Dorthin in verkaufbaren Schritten, nicht auf einmal:

| Stufe | Umfang | Zweck | Aufwand |
|---|---|---|---|
| **MVP-0 (jetzt fast fertig)** | Sidebar-Chat + Pi-Index + Signatur + 3-Stufen-Memory | Dogfooding aufs eigene 00_Wissen (Gate-Auflage 1) | vendor-Build + 1–2 Tage |
| **MVP-1 „Verkaufbar"** | Dashboard-Grundgerüst aus dem Mockup: Übersicht-KPIs, Broki-Chat, Wissens-/Rollen-Kontext, System-Status. Lizenz-Wächter (Kopierschutz). | Erste Kanzlei-Demo, Chrome-Store-Eintrag | ~5–8 Tage |
| **MVP-2 „Das WOW"** | Proaktive Assistenz (Live-Warnungen mit Quellen) — der eigentliche Differenzierer im Mockup | Der Pitch-Moment, der Merlin schlägt | ~5–10 Tage |
| **Ausbau** | Aufgaben & Agenten, Rollback-Assistent-UI, kollektives Wissen-Visualisierung | Vollprodukt = Mockup | iterativ |
| **Vision (Pitch-Deck, nicht bauen)** | Hermes-Loop, Mesh-Schwarm | Valuation | 2027/2028 |

**Reihenfolge-Logik:** Proaktive Assistenz (MVP-2) ist das teuerste, aber der
einzige Teil, den die Konkurrenz NICHT hat — deshalb NACH dem verkaufbaren
Grundgerüst, aber VOR dem Nice-to-have-Ausbau. Der Kopierschutz-Lizenz-Wächter
gehört in MVP-1 (billig, nutzt vorhandene Signaturkette).

## Fazit für den CEO

Broki verdient die Priorisierung — aber die Kraft liegt in der **Fokussierung**:
ein exzellentes Produkt für DSGVO-gezwungene Branchen, nicht ein mittelmäßiger
Allrounder gegen finanzierte Konkurrenz. Der Markt-Beweis liegt vor: Die
populären Tools sind in genau Brokis Zielmarkt rechtlich unbrauchbar. Das ist
kein „auch ein KI-Assistent", das ist „der einzige, den eine Kanzlei nutzen darf".

## Quellen

- UCL / Cybernews / TechXplore (Aug 2025): AI-Browser-Assistenten & Datenschutz,
  Merlin-SSN-Exfiltration, Sider/TinaMind-Tracking, „ungeeignet für Enterprise".
- Local AI Master / WebLLM (MLC) / WebML (2026): In-Browser-LLM-Stack, WebGPU
  Default in allen Browsern, Chrome-Extension-Beispiele.
- HARPA AI Competition Review 2025 (Business-Extensions-Vergleich).
