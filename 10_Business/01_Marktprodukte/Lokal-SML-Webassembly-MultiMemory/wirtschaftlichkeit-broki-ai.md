# 💶 Wirtschaftlichkeitsprüfung: Broki AI (Browser-Extension als Produkt)

> Gate-Prüfung nach Regel 4, erstellt 18.07.2026 durch den Wirtschaftlichkeits-
> Prüfer-Agenten. Prüfgegenstand: Broki AI als eigenständig vermarktbares
> Produkt (Businessplan-docx + Landingpage-Konzept + gebaute Extension v0.1).
> Zeithorizont: 12 Monate. Hinweis: Der Businessplan ist primär Technik-
> Recherche — **alle Preiszahlen hier sind gekennzeichnete Annahmen-Spannen.**

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

## 2. Einnahmequellen-Inventar (Preise = ANNAHMEN, Spannen)

| Quelle | Voraussetzung | Kennzahl (Herkunft) | fließt ab | konserv. | Basis | optim. |
|---|---|---|---|---|---|---|
| **Done-for-you-Setup** (Pi + Extension + Wiki-Indexierung + Schulung) | Pilot-Referenz + Demo-Video | 2.500–8.000 €/Setup (ANNAHME: IT-Dienstleister-Tagessätze 800–1.200 € × 3–7 Tage; LeadPilot-Recherche als Untergrenze) | M4+ | 0 | 2 Setups ≈ 8.000 €/Jahr | 5 Setups ≈ 25.000 € |
| **Wartungsvertrag** (Index-Pflege, Updates, Support) | bestehendes Setup | 100–300 €/Monat/Firma (ANNAHME: üblicher KMU-IT-Wartungssatz) | M5+ | 0 | 2 × 150 €/M ab M6 ≈ 2.000 € | 5 × 200 €/M ≈ 7.000 € |
| Per-Seat-Lizenz / Chrome-Store-Freemium | Produktreife + Reichweite | nicht seriös bezifferbar → 0 € angesetzt | M10+ | 0 | 0 | erste Umsätze p.m. |

## 3. Szenario-Rechnung (12 Monate, Anlaufkurve ehrlich)

- **Konservativ (P70):** kein zahlender Kunde (Vertriebszugang fehlt). Jahressumme
  ≈ 0 €. Restwert: internes Wiki-KI-Tool fürs AI-OS + stärkstes Demo-Asset.
- **Basis (P50):** M1–3 Bau/Dogfooding, M4 erster Pilot (ggf. vergünstigt),
  M6+ zweites Setup + 2 Wartungsverträge. Jahressumme ≈ **10.000 €**.
- **Optimistisch (P20):** Referenz zieht, 5 Setups + Wartung. ≈ **30.000 €**.

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
3. **Wartungsverträge nur mit begrenzter SLA** (next business day, werktags).
4. **Nachprüfung M3** nach Pilot: Prognose vs. Ist hier nachtragen.

```json
{
  "produkt": "Broki AI Browser-Extension (B2B: Kanzleien/Praxen/KMU)",
  "marktbedarf": {"score_0_10": 7, "begruendung": "DSGVO-Kaufdruck real + Copilot-FOMO; Engpass ist Vertriebszugang, nicht Technik"},
  "kosten": {"einmalig_eur": 0, "laufend_eur_monat": 0, "arbeitszeit_h_woche": 3, "restbau_h": 50},
  "break_even_monat": {"konservativ": null, "basis": 8, "optimistisch": 5},
  "eur_pro_arbeitsstunde_monat12": {"konservativ": 0, "basis": 65, "optimistisch": 150},
  "empfehlung": "GO_MIT_AUFLAGEN",
  "auflagen": ["Dogfooding-Pilot aufs eigene AI-OS-Wiki zuerst (max 7 Arbeitstage)", "kein Vertrieb vor Referenz", "SLA begrenzen", "Nachpruefung M3"],
  "status": "WARTET_AUF_FREIGABE"
}
```

**Status: WARTET_AUF_FREIGABE** — nach CEO-Freigabe startet das Pi-Gegenstück
(= zugleich Dogfooding-Baustein, Auflage 1).
