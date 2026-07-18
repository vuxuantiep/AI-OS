# 💶 Wirtschaftlichkeitsprüfung: Broki AI (Browser-Extension als Produkt)

> Gate-Prüfung nach Regel 4, erstellt 18.07.2026 durch den Wirtschaftlichkeits-
> Prüfer-Agenten. Prüfgegenstand: Broki AI als eigenständig vermarktbares
> Produkt (Businessplan-docx + Landingpage-Konzept + gebaute Extension v0.1).
> Zeithorizont: 12 Monate.
> **UPDATE 18.07.2026 (Businessplan erweitert auf 118k Z.):** enthält jetzt
> ein explizites Erlösmodell, ROI-Kalkulation, Zielmarkt-Phasen und GTM —
> Zahlen unten aktualisiert. Prüfer-Hinweis bleibt: Plan-Zahlen sind
> UNVALIDIERT (keine Pilot-Verkäufe), realistische Spannen daher konservativer.

## Management-Summary (5 Sätze, Klartext)

Broki AI ist wirtschaftlich das stärkste Stück der Plattform, weil es als
einziges ein **wiederkehrendes** B2B-Modell trägt (Setup + Wartungsvertrag)
und die Kern-Software bereits gebaut ist (0 € Cash, Restaufwand ~5–7 Tage bis
pilotfähig: Pi-Gegenstück, vendor, Pilot). Der Engpass ist unverändert nicht
Technik, sondern **Vertriebszugang zu Kanzleien/Praxen** — darum ist der erste
„Kunde" das eigene AI-OS (Dogfooding als Referenz, null Vertriebsrisiko).
Konservativ (kein Kunde in 12 M) bleibt trotzdem ein internes Wiki-KI-Tool +
das beste Demo-Asset der Plattform übrig. Basis-Szenario: 2 Done-for-you-Setups
+ Wartung ≈ 10.000 €/Jahr bei ~60–80 €/h. Empfehlung: **GO_MIT_AUFLAGEN** —
Dogfooding-Pilot zuerst, hartes Zeitbudget, Preisliste erst nach Pilot-Feedback.

## 1. Marktbedarf — Score 7/10

- **Kaufdruck real:** DSGVO/Mandantengeheimnis verbietet Kanzleien/Praxen
  Cloud-KI faktisch; gleichzeitig Copilot-FOMO. Broki löst beides („Betriebsrat-
  Garantie": technisch prüfbar via host_permissions nur zur Pi-URL).
- **Referenz-Zahlungsbereitschaft:** ChatGPT Enterprise/Copilot ≈ 30–60 €/Nutzer/
  Monat (öffentliche Listenpreise) — der ROI-Rechner der Landingpage
  argumentiert genau gegen diese Benchmark.
- **Konkurrenz/Risiko:** Microsoft bündelt Copilot in M365 („fühlt sich gratis
  an"); lokale-KI-Startups (z. B. On-Prem-RAG-Anbieter) zielen auf denselben
  Schmerz, aber meist mit Server-Hardware — Broki's Pi+Browser-Ansatz ist
  günstiger und ohne Rollout-Aufwand (Extension statt Softwareverteilung).
- **Dämpfer:** erklärungsbedürftig; konservative Zielgruppe kauft Referenzen,
  nicht Technik.

## 1c. Businessplan-Zahlen (Stand 18.07.2026) — mit Prüfer-Einordnung

Der erweiterte Plan liefert jetzt konkrete Werte. Gegenüberstellung Plan ↔ Prüfer:

| Plan-Aussage | Beleg im Plan | Prüfer-Bewertung |
|---|---|---|
| **ROI: >380.000 €/Jahr Ersparnis @ 1.000 Nutzer** (Cloud ≈ 390k: 30 €/Seat + 2.500 €/M Server + API) | ROI-Tabelle | Rechnerisch plausibel, ABER: 1.000-Nutzer-Kunde ist für einen Solo-Anbieter Jahr 1 unerreichbar → als **Pitch-Argument** top, als Umsatz-Basis untauglich |
| **B2B SaaS-Light: 5–10 €/Seat/Monat, ~95 % Marge** | Erlösmodell | Marge realistisch (0 € Serverkosten). Preis plausibel, aber unvalidiert. **Wiederkehrend** = echter Pluspunkt ggü. Themen-Assistent |
| **B2C Premium 5 €/Monat** (Offline-Speicher, Vorlagen) | Erlösmodell | Reichweiten-abhängig, Jahr 1 vernachlässigbar (wie Themen-Assistent-Prüfung) |
| **GTM „Trojanisches Pferd"** (kostenloses Audit-Tool „wie oft kopieren MA Daten in ChatGPT?") | GTM-Strategie | **Stark** — löst das Zugangsproblem clever, konkret baubar (Mini-Extension), ehrlicher Aufhänger |
| **BSI-Zertifizierung** für Kanzleien/Behörden | GTM-Strategie | Türöffner, aber teuer + langwierig (Monate, 4-/5-stellig) → NICHT Jahr 1, später als Enterprise-Hebel |

## 1d. Nachtrag Businessplan-Erweiterung (133k Z., 18.07.2026 abends)

Neue Inhalte, Prüfer-Einordnung:

- **Neue Branchen — Logistik/Hafen + E-Commerce:** starke Usecases genau dort, wo
  Netzausfälle teuer sind (Hamburger Hafen: Funklöcher durch Stahlcontainer →
  Zoll-/Gefahrgut-Index offline im Browser). **Aber:** HHLA/EUROGATE = Großenterprise-
  Vertrieb (12–24 Monate, Ausschreibungen) → Jahr-1-unerreichbar für Solo, wie
  Medizin/Banken. Einordnung: **Phase-2-Narrativ**, nicht Startmarkt. Beachhead
  bleibt Kanzleien/Steuerberater.
- **IP-/Kopierschutz** (CEO-Kernfrage): senkt das Risiko „Konkurrent baut nach"
  deutlich — v.a. der **Lizenz-Wächter** (nutzt vorhandene Signaturkette, ~1 Tag)
  + Markenanmeldung (~ein paar hundert €). Details in `Architektur-Broki-Extension.md`
  §5c. Neue Auflage unten.
- **Hermes-Loop + Mesh-Schwarm** (autonome Workflows, serverlose Team-KI): das
  ist die **Investoren-Vision 2027/2028** — hebt die Valuation im Pitch, aber
  Prüfer-Warnung: NICHT als Jahr-1-Feature kalkulieren oder versprechen
  (Autonomie-Haftung, WebRTC-Mesh-Komplexität). Gehört ins Pitch-Deck, nicht in die 12-Monats-Rechnung.

## 2. Einnahmequellen-Inventar (Basis = Businessplan-Zahlen, konservativ gedeckelt)

| Quelle | Voraussetzung | Kennzahl (Herkunft) | fließt ab | konserv. | Basis | optim. |
|---|---|---|---|---|---|---|
| **B2B SaaS-Light-Lizenz** (5–10 €/Seat/M) | Pilot-Referenz + BSI/Datenschutzsiegel hilfreich | Businessplan: 5–10 €/Seat/M, ~95 % Marge | M5+ | 0 | 2 Firmen × 8 Seats × 7 €/M ab M6 ≈ 5.400 €/Jahr | 5 Firmen × 12 Seats × 8 €/M ≈ 23.000 € |
| **Done-for-you-Setup** (Pi + Extension + Wiki-Indexierung + Schulung) | Pilot-Referenz + Demo-Video | 2.500–8.000 €/Setup (IT-Tagessätze 800–1.200 € × 3–7 Tage) | M4+ | 0 | 2 Setups ≈ 8.000 € | 5 Setups ≈ 25.000 € |
| **Audit-Tool → Lead-Magnet** (Trojanisches Pferd) | Mini-Extension (~2 Tage) | kein Direktumsatz, aber Conversion-Treiber für die beiden oberen Zeilen | M4+ | 0 | (wirkt auf Setups/Lizenzen) | (Verstärker) |
| B2C Chrome-Store-Freemium (5 €/M) | Produktreife + Reichweite | Businessplan-Preis, aber reichweitenabhängig → 0 € Jahr 1 | M10+ | 0 | 0 | erste Umsätze p.m. |

## 3. Szenario-Rechnung (12 Monate, Anlaufkurve ehrlich)

- **Konservativ (P70):** kein zahlender Kunde (Vertriebszugang fehlt). Jahressumme
  ≈ 0 €. Restwert: internes Wiki-KI-Tool fürs AI-OS + stärkstes Demo-Asset.
- **Basis (P50):** M1–3 Bau/Dogfooding, M4 Audit-Tool + erster Pilot, M6+ zweites
  Setup + laufende SaaS-Light-Lizenzen. Setups ≈ 8.000 € + Lizenzen ≈ 5.400 €
  → Jahressumme ≈ **13.000 €** (die wiederkehrende Lizenz ist der Fortschritt ggü. der Erst-Prüfung).
- **Optimistisch (P20):** Audit-Tool/Referenz zieht, 5 Setups + Lizenzen. ≈ **45.000 €**.

**€/Arbeitsstunde (M12; ~50 h Restbau + 3 h/Woche laufend ≈ 200 h gesamt):**
konservativ 0 € ❌ · Basis ≈ 50–80 €/h ✓ · optimistisch ≈ 150 €/h ✓✓

## 4. Kosten & Break-even

- **Einmalig:** 0 € Cash (Pi vorhanden, Stack Open Source). Arbeitszeit-Rest:
  Pi-Gegenstück ~2–3 Tage, vendor/Polish ~1–2 Tage, Dogfooding-Pilot ~2 Tage.
- **Laufend:** ~0 € (Strom Pi); pro Kunde: dessen eigener Pi (≈ 100 € einmalig,
  zahlt Kunde — die „600 €/Jahr" der Landingpage sind Kunden-TCO, nicht unsere Kosten).
- **Break-even (Arbeitszeit zu 85 €/h ≈ 4.250 € Invest):** konservativ nie,
  Basis M7–9, optimistisch M5.

## 5. Top-Risiken

1. **Vertriebszugang** (größtes, bekannt aus Themen-Assistent-Prüfung) —
   Gegenmaßnahme: Dogfooding-Referenz + bestehende Kanäle, keine Kaltakquise-Illusion.
2. **Copilot-Bündelung** („ist doch schon in M365 drin") — Gegenargument im
   Pitch verankern: Mandantengeheimnis/Betriebsrat + 0 € Serverkosten.
3. **Ein-Personen-Support bei B2B-Wartungsverträgen** — Auflage: max. Reaktions-
   zeit „next business day" vertraglich, keine 24/7-Zusagen.
4. **Kommoditisierung durch Chrome Built-in AI** — mildert sich: Broki's Wert
   ist der signierte Firmen-Index + Rollout, nicht der Motor (Gateway ist agnostisch).
5. **Browser-API-Drift** (window.ai-Namensräume) — Gateway probt defensiv, Risiko klein.
6. **Haftung:** Wir verarbeiten KEINE Kundendaten (alles lokal beim Kunden) —
   AVV-Aufwand minimal, aber Beratungshaftung bei Setup sauber begrenzen (AGB).

## 6. Empfehlung: **GO_MIT_AUFLAGEN**

1. **Dogfooding zuerst:** Pi-Gegenstück wird als AI-OS-Komponente gebaut und
   Broki intern aufs eigene Wiki gesetzt (00_Wissen) — erst wenn das täglich
   genutzt wird, ist es demo-reif. Max. **7 Arbeitstage** bis dahin.
2. **Kein Vertrieb vor Referenz:** Demo-Video + Landingpage (Konzept liegt)
   erst NACH funktionierendem Dogfooding; Preisliste erst nach Pilot-Feedback.
3. **SaaS-Light/Wartung nur mit begrenzter SLA** (next business day, werktags) —
   keine 24/7-Zusagen als Einzelperson.
4. **Audit-Tool als Lead-Magnet** (Trojanisches Pferd) ist der GTM-Hebel:
   Mini-Extension (~2 Tage) NACH dem Dogfooding, vor aktivem Vertrieb.
5. **BSI-Zertifizierung NICHT Jahr 1** (teuer/langwierig) — als Enterprise-Hebel
   für Phase 2 vormerken, nicht in die Startkalkulation nehmen.
6. **Kopierschutz früh**: Lizenz-Wächter (Chef-Schlüssel, ~1 Tag, nutzt vorhandene
   Signaturkette) + Markenanmeldung „Broki AI" vor dem ersten Verkauf. WASM-
   Obfuskation erst bei zahlenden Kunden.
7. **Vision sauber trennen**: Hermes-Loop/Mesh-Schwarm nur im Pitch-Deck als
   „Vision 2027/2028", nie als Jahr-1-Zusage — sonst Haftungs-/Erwartungsfalle.
8. **Nachprüfung M3** nach Pilot: Prognose vs. Ist hier nachtragen.

```json
{
  "produkt": "Broki AI Browser-Extension (B2B: Kanzleien/Praxen/KMU)",
  "marktbedarf": {"score_0_10": 7, "begruendung": "DSGVO-Kaufdruck real + Copilot-FOMO; Engpass ist Vertriebszugang, nicht Technik"},
  "erloesmodell": {"b2b_saas_light_eur_seat_monat": "5-10 (Businessplan, unvalidiert)", "bruttomarge_prozent": 95, "done_for_you_setup_eur": "2500-8000", "b2c_premium_eur_monat": 5},
  "kosten": {"einmalig_eur": 0, "laufend_eur_monat": 0, "arbeitszeit_h_woche": 3, "restbau_h": 60},
  "break_even_monat": {"konservativ": null, "basis": 8, "optimistisch": 5},
  "jahresumsatz_eur": {"konservativ": 0, "basis": 13000, "optimistisch": 45000},
  "eur_pro_arbeitsstunde_monat12": {"konservativ": 0, "basis": 65, "optimistisch": 160},
  "empfehlung": "GO_MIT_AUFLAGEN",
  "auflagen": ["Dogfooding-Pilot aufs eigene AI-OS-Wiki zuerst (max 7 Arbeitstage)", "Audit-Tool als GTM-Lead-Magnet", "kein Vertrieb vor Referenz", "SLA begrenzen", "BSI erst Phase 2", "Nachpruefung M3"],
  "status": "FREIGEGEBEN_2026-07-18"
}
```

**Status: ✅ FREIGEGEBEN durch CEO am 18.07.2026** — Umsetzung des Pi-Gegenstücks
gestartet (= zugleich Dogfooding-Baustein, Auflage 1: erst aufs eigene 00_Wissen).
