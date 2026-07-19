# Broki-Designstil „Klar" — Konzept & Vergleichsvariante

*Stand: 19.07.2026 · Variante liegt als `Produkt/broki-landingpage/index-klar.html` neben der Hauptseite (`index.html`). Status: **Vergleich offen, CEO entscheidet.***

## Warum ein eigener Stil?

Der aktuelle Look der Hauptseite (dunkel, Neon-Grün, Glas/Blur, Partikel) ist der
Standard-Stil praktisch aller AI-Startups — er erzählt „Cloud, Hype, Magie".
Brokis Philosophie ist das Gegenteil: **lokal, ehrlich, klein, immer da.**
Die Zielgruppe (Kanzleien, Arztpraxen, Hausverwaltungen) sind konservative
Entscheider, für die helle, ruhige, solide Gestaltung Vertrauen schafft.

## Eigenschaft → Designentscheidung

| Broki-Eigenschaft | Designentscheidung im Stil „Klar" |
|---|---|
| **OFFLINE-Verfügbarkeit** (Kern-USP) | Grüner **Status-Punkt** als Markenzeichen: `● Offline bereit` — das vertraute „Online"-Symbol aus Chat-Apps, umgedeutet: *verfügbar gerade WEIL offline*. Im Hero-Badge, Footer, überall wiederholbar. |
| **Vertrautheit / Zielgruppe** | **Hell als Standard** (Papierweiß + ruhiges Grün), Dark-Mode bleibt als Option. Wirkt wie ein gut geführtes Dokument: seriös, prüfbar. |
| **Klein & Einfachheit** | Die Seite selbst als Beweis: Partikel entfernt, Blur entfernt, federleicht. Gag-Zeile im Hero: *„Diese Seite würde sogar offline funktionieren — genau wie Broki."* |
| **Vertrauen / Solidität** | **Opake Flächen statt Glas.** Transparenz signalisiert „flüchtig, durchlässig" — falsch für ein Produkt, dessen Versprechen ist: *Ihre Daten sind fest hier.* Weiße Karten, feine Linie, kleiner ehrlicher Schatten. |
| **Smart & Proaktiv** | Ein einziger bewegter Moment: die gelbe **Proaktiv-Hinweisblase** in der Geräte-Diashow („⚠ Rabatt laut Wiki-Update nicht mehr zulässig") mit sanfter Puls-Animation. Ruhiger Auftritt, ein kluger Moment — wie Broki selbst. |
| **Ehrlichkeit als Ästhetik** | JetBrains Mono **nur für prüfbare Fakten** (0 Bytes, F12, Preise) — wie Belege in einem Gutachten. Prinzip: **„Ehrlich wie F12."** |

## Technische Unterschiede der Variante

- `data-theme="light"` als Standard, eigener LocalStorage-Schlüssel `broki-theme-klar`
  (kollidiert nicht mit der Hauptseite).
- Kein `broki-particles.js`, kein Canvas, kein `backdrop-filter` auf Karten
  (nur die Nav behält ihren dezenten Standard-Blur).
- Body: flache Farbe `var(--bg-deep)` statt Verlaufs-Stack; Plus-Raster bleibt dezent.
- Zebra-Flächen/Stats/Footer im Light-Theme **opak** (`#f0f5f1`) statt halbtransparent.
- Erzeugt per Transform-Skript aus `index.html` — Inhalte beider Varianten sind identisch,
  nur die Gestaltungsschicht unterscheidet sich. Bei Inhaltsänderungen an `index.html`
  kann die Variante neu generiert werden.

## Vergleich & Entscheidung

Beide Dateien nebeneinander im Browser öffnen:
- `index.html` — dunkle Glow/Glas-Variante (Status quo)
- `index-klar.html` — helle Solid-Variante „Klar"

Entscheidungskriterium: Welche Version schafft bei der Kernzielgruppe
(Kanzlei-Partner, Praxis-Manager, Hausverwalter) in 5 Sekunden mehr Vertrauen?
Empfehlung: mit 2–3 Personen aus der Zielgruppe testen, nicht mit Entwicklern.

## Verwandt

- Design-System-Basis: `Broki-Design-System.md` (Farben/Fonts — Grün #00c758 bleibt Akzent in beiden Varianten)
- Landingpage-Plan: `Landingpage-Plan-Broki.md`
