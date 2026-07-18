# 🎨 Broki AI — Design-System (Corporate Identity)

> Erstellt 18.07.2026. Ziel (CEO): Broki einheitlich mit der Marke
> **vuxuantiep.de** — gleiche Farben, Fonts, Ästhetik, damit alles als EIN
> Unternehmen erkennbar ist. Tokens direkt aus der Live-Website extrahiert.
> Gilt für: Landingpage ([[Landingpage-Plan-Broki]]) UND das Produkt-Frontend
> (`Broki Ai-Frontend.png` — Akzent dort von Lila auf Grün umstellen!).

## 1. Farbpalette (exakt aus vuxuantiep.de)

```css
:root {
  /* Hintergründe — tiefes Schwarz, leicht abgestuft */
  --bg:          #0a0a0a;   /* Seiten-Basis */
  --bg-deep:     #000000;   /* Hero / tiefste Ebene */
  --bg-card:     #0d0d0f;   /* Karten */
  --bg-elevated: #111114;   /* erhöhte Karten / Hover */
  --border:      #27272a;   /* dünne Ränder */

  /* Grün — die Marken-Signatur */
  --accent:      #00c758;   /* Primär-Grün (Buttons, Highlights) */
  --accent-mint: #00d294;   /* Mint-Türkis (Verläufe, sekundär) */
  --accent-teal: #00bb7f;   /* Grün-Türkis (Akzent-Nuance) */
  --accent-soft: #4ade80;   /* helles Grün (Text-Highlights, Links) */

  /* Text */
  --text:        #ffffff;
  --text-dim:    #cccccc;
  --text-muted:  #888890;

  /* Status */
  --ok:    #4ade80;
  --warn:  #facc15;
  --danger:#f87171;
}
```

Verlauf-Signatur (Hero-Hintergrund, dezent): radial/linear von `#0a0a0a` mit
einem leisen grünen Schimmer oben (`rgba(0,199,88,0.06)`).

## 2. Typografie

- **Headlines & Text:** `"Inter", system-ui, sans-serif` — fett (700/800) für
  H1/H2, groß und knapp.
- **Code / Tech-Details / Zahlen-Labels:** `"JetBrains Mono", ui-monospace, monospace`.
- **Signatur-Move:** wichtige Wörter in der Headline farbig hervorheben —
  wie „skaliert." / „liefert." in Grün. Für Broki z. B.:
  „Die KI, die im Browser **bleibt.** Zu 100 % **privat.**" (grün = bleibt/privat).

⚠️ **Fonts LOKAL vendorn** (Inter + JetBrains Mono als .woff2 mitliefern), NICHT
von Google-Fonts-CDN laden — sonst widerspricht die Landingpage der eigenen
„keine Cloud / keine Datenübertragung"-Botschaft (und die Extension-CSP verbietet
externe Quellen ohnehin).

## 3. Komponenten-Stil

| Element | Stil |
|---|---|
| **Primär-Button** | Grün gefüllt (`--accent`), schwarze Schrift, Radius ~8px, dezenter Glow beim Hover |
| **Sekundär-Button** | transparent, 1px `--border`, weißer Text (wie „Erstgespräch buchen") |
| **Card** | `--bg-card`, 1px `--border`, Radius ~14px, viel Innenabstand, kein harter Schatten |
| **Badge/Pill** | klein, `--bg-elevated`, Monospace, grüner Punkt für „aktiv/online" |
| **Trust-Leiste** | Zeile aus Icon+Text, grüne Häkchen (100 % lokal · DSGVO · keine Cloud) |
| **Tag/Chip** | grau-transparent, kleiner Text (wie „AWS CDK · Terraform · K8s") |
| **Code-Fenster** | dunkler Block, Mac-Ampel-Punkte oben, Monospace, `//`-Kommentare in Grau, Werte in Grün — das ist die stärkste Wiedererkennung der Marke |

## 4. Ton & Signatur-Elemente (aus der Website)

- **Terminal/Code-Ästhetik:** `//`-Kommentare, `KEY: VALUE`-Zeilen, grüner
  „Status: …"-Text. Broki hat das im Mockup schon (System-Status-Liste) — im
  vuxuantiep-Grün ausführen.
- **Roboter-Maskottchen:** die Website hat den grün-blauen Robot ("LEGO AI-OS"),
  das Broki-Mockup einen ähnlichen Kumpel → **gleiche Maskottchen-Familie**,
  verstärkt die Wiedererkennung. Broki-Robot in denselben Grün/Cyan-Tönen halten.
- **Knappe, technische Sprache**, deutsche Hauptsprache, Sprach-Umschalter DE/EN/VI
  (die Website hat ihn — für Broki-Landingpage übernehmen, passt zur Migranten-B2C-Zielgruppe).

## 5. Was sich ggü. dem bisherigen Mockup ändert

Das Frontend-Mockup (`Broki Ai-Frontend.png`) nutzt **Lila (#7c5cff)** als
Akzent. → **Auf Grün (`#00c758`) umstellen.** Konkret:
- Lila Buttons/Aktiv-Zustände/Icons → Grün.
- Lila „Kein Chatbot"-Banner → dunkle Card mit grünem Rand/Text.
- Sidebar-Aktiv-Markierung (war lila) → grüner Balken/Text.
- Robot-Maskottchen: von Lila-Anteilen auf Grün/Cyan (wie Website-Robot).
Layout, Struktur, Komponenten des Mockups bleiben — nur die Farbwelt wechselt.

## 5b. Hintergrund-Signatur: Partikel-Netzwerk (Constellation)

Gebaut 18.07.2026 (CEO-Wunsch, Vorbild itsupporthh.de). Verbundene, langsam
driftende Punkte + Linien im Broki-Grün, reagiert dezent auf die Maus.
**Self-contained Canvas, KEINE Fremd-Library** (kein particles.js/jQuery) —
CSP-konform für die MV3-Extension + passt zur „keine Cloud"-Botschaft.

- Datei: `Produkt/broki-landingpage/assets/broki-particles.js`
  (`BrokiParticles.init("canvas-id", {optionaleConfig})`).
- Performance: pausiert bei unsichtbarem Tab, respektiert `prefers-reduced-motion`,
  Partikelzahl skaliert mit Fläche (Deckel 140), devicePixelRatio-bewusst.
  Die CPU gehört dem LLM — die Deko darf sie nicht fressen.
- Farben aus dem Design-System: helle Punkte, Linien im Grün `#00c758`.
- Live-Beispiel: `Produkt/broki-landingpage/index.html` (Hero mit Animation).
- Einsatz: Hintergrund der Landingpage-Hero UND optional des Produkt-Frontends
  (Übersicht-Header), dezent hinter dem Inhalt.

## 6. Wiederverwendung im AI-OS

Diese Tokens eignen sich als gemeinsame Marken-Palette für ALLE Marktprodukte
(DokuCheck, Themen-Assistent, LeadPilot-Kundenansicht), damit das ganze
Portfolio als „ein Haus" auftritt. Optional später: eine geteilte
`brand.css` mit diesen `:root`-Variablen, die jedes Produkt einbindet.
