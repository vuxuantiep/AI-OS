# 🌐 Broki AI — Landingpage-Plan (baubar)

> Erstellt 18.07.2026. Konkretisiert das Struktur-Konzept aus
> `offizielle Landingpage von Broki AI.docx` zu einem umsetzbaren Bauplan.
> Basis: [[Wettbewerbsanalyse-und-Priorisierung-Broki]] (das Datenschutz-Argument
> ist der Kern) + Frontend-Mockup (`Broki Ai-Frontend.png`, Design-Sprache).

## Ziel & Rahmen

- **Zweck:** B2B-Leadgenerierung für regulierte Branchen (Kanzleien, Praxen,
  Steuerberater, Hausverwaltungen) → CTA „B2B-Demo vereinbaren".
- **Sekundär:** Chrome-Store-Download für die kostenlose Basisversion (B2C-Trichter).
- **Gate-Einordnung:** Bauen erst NACH Dogfooding (Gate-Auflage 2 „kein Vertrieb
  vor Referenz"). Dieser PLAN ist vom Gate ausgenommen.
- **Technik:** statische Single-Page (HTML/CSS/JS, keine Cloud-Abhängigkeit —
  passt zur Botschaft!). Deploybar über das AI-OS-Dashboard (`/produkte/broki-lp/`)
  oder Cloudflare Pages. Design-Sprache = Mockup (dunkel, Lila-Akzent #7c5cff,
  Trust-Grün, moderne Cards).

## Sektionsplan (Reihenfolge = Scroll-Fluss)

### 1. Hero — „Über der Falz"
- **H1:** „Die KI, die im Browser bleibt. Unendlich skalierbar. Zu 100 % privat."
- **Sub:** kollektives Firmenwissen + KI-Berater in jedem Tab, lokal via
  WebGPU/WASM, vernetzt über Tailscale + Raspberry Pi. Null Serverkosten. DSGVO.
- **Trust-Leiste** (aus Mockup): 🔒 100 % lokal · ✅ DSGVO-konform · ☁️🚫 Keine Cloud · Keine Datenübertragung
- **CTAs:** [Kostenlos testen (Chrome Store)] (primär) · [B2B-Demo vereinbaren] (sekundär)
- **Visual:** animiertes Browser-Mockup (Sidebar blendet proaktiv Warnung/Wiki-Zitat ein) — als Loop-GIF/CSS.

### 2. Der Schock — Datenschutz-Pain (NEU, aus Wettbewerbsanalyse!)
Der stärkste Hebel, den die docx noch nicht hatte. Belegbar:
- **Headline:** „Ihre Mitarbeiter nutzen längst KI im Browser. Nur leider die falsche."
- 3 harte Fakten (mit Quellenlink, seriös): Studien zeigen — populäre KI-Browser-
  Assistenten verletzen wahrscheinlich die DSGVO; ein bekanntes Tool exfiltrierte
  eine Steuer-ID aus einem Formular; andere teilen Prompts + IP mit Trackern.
- **Punchline:** „Für eine Kanzlei ist das ein Compliance-Verstoß. Broki ist die
  einzige KI, die Ihre Mandantendaten nie sieht."

### 3. ROI-Rechner (interaktiv)
- Slider „Wie viele Mitarbeiter nutzen KI?" (10–5.000).
- Live: Cloud-KI-Kosten (≈ 30 €/Seat/M + Server) vs. Broki (≈ 600 €/Jahr Pi-Fixkosten).
- Ausgabe „Ihre jährliche Ersparnis: X €". (Zahlen aus Businessplan-ROI-Tabelle.)
- 3 Fakten-Boxen: 0 € Server-Skalierung · Betriebsrat-Garantie (100 % lokal) ·
  Unzerstörbares Backup (Crash-Rollback).

### 4. Zielgruppen-Matrix (Tab-Umschalter)
- **Tab Kanzleien/Steuerberater** (Beachhead zuerst!): 500-Seiten-Verträge lokal
  prüfen, kein Mandantengeheimnis-Bruch, GoBD/DSGVO-Rollen-Wiki.
- **Tab Arztpraxen/Kliniken:** Befund-Abgleich mit Leitlinien offline.
- **Tab Hausverwaltung:** Mietverträge/BGH-Urteile beim Schreiben prüfen.
- **Tab Privat/Migranten (B2C):** Behördenbrief fotografieren → lokal übersetzen.
- Jeweils 1 konkretes Vorher/Nachher-Szenario.

### 5. Wie es funktioniert (3-Schritte-Grafik)
Verteilen (Pi baut signierten Index) → Erinnern (3-Stufen-Gedächtnis im Browser)
→ Denken (LLM-Gateway wählt lokalen Motor). Vereinfachtes Architektur-Diagramm
aus dem Mockup (Browser ↔ Pi ↔ kollektives Netz).

### 6. IT-Leiter-Sicherheits-Zertifikat (Vertrauens-Anker)
Harte Specs für die technische Zielperson: 🔒 Manifest V3 Sandbox · 🔑 SHA-256/
ECDSA-Integrität (Data-Poisoning-Schutz) · 📦 plattformunabhängig · 🔐 Lizenz-
Wächter. „Von Administratoren geliebt."

### 7. Vergleichstabelle (NEU — direkter Konkurrenz-Konter)
Broki vs. Cloud-Assistenten (Merlin/Sider) vs. M365 Copilot: Datenhaltung,
DSGVO, Serverkosten, Offline, Firmen-RAG. Broki = einzige volle grüne Spalte.

### 8. Footer + Schluss-CTA
Banner „Bereit für KI ohne Cloud-Risiko?" · [Jetzt zu Ihrem AI-OS hinzufügen] ·
Links: Datenschutz (Betriebsrat-Konformität als PDF), Impressum, GitHub (Open-Source-Transparenz).

## Assets, die noch entstehen müssen

- 60-Sek-Explainer-Video (Skript liegt in der docx: „Das unzerstörbare Firmengehirn").
- Broki-Logo (freundlicher Roboter-Kumpel, Lila) — im Mockup schon angelegt.
- Screenshots/GIF aus dem echten Frontend (→ erst nach MVP-1).
- Betriebsrat-Konformitätserklärung (PDF, rechtlich prüfen lassen).

## Bau-Reihenfolge (wenn Gate-Freigabe für Vertrieb kommt)

1. Statisches Gerüst (Sektionen 1, 3, 4, 5, 8) — ~1 Tag.
2. Datenschutz-Schock + Vergleichstabelle (2, 7) — der Konversionskern — ~0,5 Tag.
3. ROI-Rechner-JS interaktiv — ~0,5 Tag.
4. Echte Screenshots einsetzen, sobald MVP-1-Frontend steht.
→ Gesamt ~2–3 Tage für eine überzeugende v1, ohne Video/Logo (die parallel).

## Wichtige Ehrlichkeits-Regel (Prüfer)

Der Datenschutz-Schock (Sektion 2) und die Vergleichstabelle (7) müssen mit
**seriösen Quellen** verlinkt sein (UCL-Studie etc.) und dürfen NICHT
verleumderisch werden — Fakten zitieren, keine Behauptungen über konkrete
Wettbewerber ohne Beleg. Sonst Abmahnrisiko.
