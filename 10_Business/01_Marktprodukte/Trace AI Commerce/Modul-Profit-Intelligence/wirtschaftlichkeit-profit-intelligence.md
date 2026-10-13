# Wirtschaftlichkeitsprüfung: Trace AI Commerce – Modul Profit-Intelligence (Amazon-Arbitrage)

> Erstellt vom [[../../../wirtschaftlichkeits-pruefer-agent|Wirtschaftlichkeits-Prüfer]] am 13.10.2026.
> **Status: FREIGEGEBEN** — CEO-Freigabe erteilt am 13.10.2026 (GO_MIT_AUFLAGEN, A1–A6 gelten).
> CEO-Zusatz bei Freigabe: Fokus auf Modul 6 (Einkaufskalkulation Amazon-Arbitrage),
> Daten über die **APIs der Online-Handelsplattformen** beziehen (SP-API, Keepa, eBay, Kaufland/Otto).
> Architektur-Bild: [[Plannung/Architektur-Modul6.png]]
> Produktplan: [[README|Profit-Intelligence]] · Architektur: [[Plannung/Architektur|Diagramm]]

## Management-Summary (5 Sätze)

Das Produkt ist **keine verkaufbare Software, sondern ein Werkzeug für ein eigenes
Handelsgeschäft** — Geld entsteht ausschließlich über Handelsmarge auf eingesetztes
Warenkapital, die Software selbst verdient nichts. Die Rechnung hängt deshalb an drei
Größen, die wir heute **nicht kennen**: wie viel Kapital du einsetzt, welchen Netto-ROI
pro Umschlag du in Deutschland real findest und wie viele Stunden Sourcing das kostet.
Bei realistischen Annahmen (1.500 € Kapital, 20 % ROI, 1 Umschlag/Monat) bleiben
≈ 240 €/Monat bei ≈ 9 €/Stunde — weit unter deinem IT-Stundensatz, und ab 15.10. startet
der EMVIA-Job, der deine freie Zeit verknappt. Zusätzlich gibt es für Kalkulation und
Preisverlauf fertige Tools (Keepa, Amazon-Gebührenrechner), die 80 % des MVP für
wenige €/Monat abdecken — ein 8-Wochen-Eigenbau ist erst gerechtfertigt, wenn der
Handel selbst bewiesen ist. **Empfehlung: GO_MIT_AUFLAGEN — erst 4 Wochen manueller
Praxistest mit max. 500 € Ware, Software-Bau nur bei bestandenem Meilenstein.**

## 1. Marktbedarf — Score: 5/10

- **Eigenbedarf statt Kundenmarkt:** Die Frage „lohnt sich dieser Einkauf?" ist echt,
  aber nur für dich als Händler. Ein späterer Verkauf als Tool träfe auf etablierte
  Konkurrenz (Keepa, SellerAmp, Helium 10, Jungle Scout — **Annahme**: Preise ~20–100 €/Monat,
  vor Nutzung aktuell prüfen).
- **Deutschland-spezifische Hürden für Arbitrage** (Annahme, vor Phase 0 verifizieren):
  viele Marken/Kategorien sind für Händler ohne Herstellerrechnung gesperrt („Ungating"),
  Kassenbons aus Retail-Arbitrage werden oft nicht als Nachweis akzeptiert, Amazon selbst
  ist häufig Buy-Box-Wettbewerber.
- **Differenzierung des Eigenbaus** (wenn überhaupt): Audit/Freigabe, Datenklassen,
  Rückführung eigener Ist-Daten — sinnvoll, aber erst wertvoll, wenn Ist-Daten existieren.

## 2. Einnahmequellen-Inventar

| # | Quelle | Voraussetzung | Kennzahl (Herkunft) | Fließt ab |
|---|---|---|---|---|
| E1 | **Handelsmarge Amazon (FBA/FBM)** | Gewerbe, Pro-Konto, verkaufsberechtigte Produkte | DB = Kapital × Netto-ROI × Umschläge (**Annahme**, Spannen unten) | Monat 2–3 (Einkauf → Einlagerung → Verkauf) |
| E2 | Handelsmarge TikTok Shop | Seller-Konto, Provision ~9 % EU (laut Plan, prüfen) | wie E1, andere Gebühren | frühestens Monat 6+ |
| E3 | Modul B (Seller-Growth, Beratung) | eigenes Konto mit Werbedaten, Fallstudie | — | nicht im Betrachtungszeitraum |
| E4 | Plattformwert AI-OS | — | Showcase für Decimal-Rechenkern, Audit, LLM-Bericht | kein Direktumsatz |

## 3. Szenario-Rechnung (Monat 12, eingeschwungen)

Fixkosten laufend ≈ **58 €/Monat** (Amazon-Pro-Tarif ~39 € netto + Keepa ~19 € —
beide **Annahme**, aktuelle Preise vor Start prüfen). Hosting = 0 € (Bestand).

| Szenario | Kapital | Netto-ROI/Umschlag | Umschläge/Mon | DB/Mon | − Fixkosten | Zeit/Mon | **€/h** |
|---|---|---|---|---|---|---|---|
| **Konservativ (P70)** | 500 € | 10 % | 0,7 | 35 € | **−23 €** | 17 h | **< 0** |
| **Basis (P50)** | 1.500 € | 20 % | 1,0 | 300 € | **242 €** | 26 h | **≈ 9 €** |
| **Optimistisch (P20)** | 3.000 € | 30 % | 1,3 | 1.170 € | **1.112 €** | 43 h | **≈ 26 €** |

- Anlaufkurve: Monat 1 = Einrichtung/Sourcing (≈ 0 €), erste Verkäufe Monat 2–3,
  Stressfall (Preis −10 %, mehr Retouren) frisst in Konservativ/Basis einen Großteil der Marge.
- ROI-Spannen sind **Annahmen** ohne belastbare DE-Benchmark — genau das soll Phase 0 messen.
- **Kapitalrisiko:** Totalverlust einzelner Positionen (Ladenhüter, gesperrte Listings) ist
  realistisch; deshalb Phase-0-Deckel 500 €.

## 4. Kosten & Break-even

| Posten | Betrag |
|---|---|
| Einmalig: Gewerbeanmeldung, ggf. LUCID/VerpackG, Kleinmaterial | ~50–150 € (**Annahme**) |
| Einmalig: Software-MVP Phase 1–3 | ~50–80 h Arbeitszeit |
| Laufend: Pro-Konto + Preisverlaufs-Tool | ~58 €/Monat |
| Laufend: Sourcing + Prep + Versand an FBA | 4–10 h/Woche |
| Gebunden: Warenkapital | 500–3.000 € |

**Break-even (Geld, ohne Arbeitszeit):** Konservativ nie · Basis Monat ~4 · Optimistisch Monat ~3.
**Break-even inkl. 60 h Entwicklung zu 50 €/h (3.000 € Opportunitätskosten):**
Konservativ nie · Basis > 12 Monate · Optimistisch ~Monat 6.

## 5. Risiken & Abhängigkeiten

1. **Zeit:** EMVIA-Start 15.10.2026 → realistische Kapazität ≤ 5 h/Woche. Sourcing ist der Engpass, nicht Software.
2. **Plattform:** Kontosperrung (Echtheitsbeschwerden der Markeninhaber, fehlende Rechnungen) trifft E1 vollständig — es gibt keine zweite Quelle.
3. **Recht/Steuer:** USt-Behandlung (Kleinunternehmer vs. Regelbesteuerung), GPSR-Pflichten, VerpackG/LUCID, ggf. ElektroG — **mit Steuerberater klären**, nicht vom System entscheiden lassen.
4. **Daten:** Konkurrenz-Absatz ist nicht direkt verfügbar; BSR→Absatz bleibt Schätzung (Datenklasse `GESCHAETZT`).
5. **Build-vs-Buy:** Eigenbau dupliziert vorhandene Tools; Wert entsteht erst mit eigenen Ist-Daten.
6. **Werbeversprechen Dritter** (z. B. Fischer & Habel „Schwungrad", 30–600 % Wachstum): Anbieter-Fallstudien, keine Planungsgrundlage; Umsatz ≠ Gewinn.

## 6. Empfehlung: `GO_MIT_AUFLAGEN`

| # | Auflage |
|---|---|
| **A1** | **Phase 0 zuerst (4 Wochen, kein Code):** manueller Test mit Keepa/Amazon-Gebührenrechner + Tabelle, **max. 500 € Warenkapital**. |
| **A2** | **Meilenstein für Software-Bau:** ≥ 5 Produkte gefunden, die du verkaufen *darfst*, mit Basis-ROI ≥ 20 % **und** Stressfall-DB > 0; davon ≥ 2 real verkauft. Nicht erreicht → `NO_GO` für den Eigenbau. |
| **A3** | Zeitdeckel **≤ 5 h/Woche** (EMVIA-Probezeit hat Vorrang). |
| **A4** | Vor dem ersten Einkauf: Gewerbe, USt-Status (Steuerberater), LUCID/GPSR-Pflichten geklärt. |
| **A5** | Keine Kurse/Beratung/Daten-Abos > 20 €/Monat bis A2 bestanden. Fischer-&-Habel-Fallstudie nur als Lernmaterial. |
| **A6** | Bei Bau: Modul im bestehenden `backend/` (FastAPI :8000) + Dashboard-Tab, keine neuen Frameworks (n8n/Streamlit entfallen). |

**Nachprüfung:** nach Phase 0 (≈ Mitte November 2026) Prognose vs. Ist eintragen.

```json
{
  "produkt": "Profit-Intelligence (Amazon-Arbitrage)",
  "marktbedarf": {"score_0_10": 5, "begruendung": "Eigenbedarf als Händler; als Tool starke Konkurrenz; DE-Arbitrage durch Markensperren erschwert", "belege": ["Annahme: Keepa/SellerAmp existieren", "Annahme: Ungating-Pflicht vieler Marken"]},
  "einnahmequellen": [
    {"quelle": "Handelsmarge Amazon", "voraussetzung": "Gewerbe, Pro-Konto, verkaufsberechtigte Produkte", "kennzahl": "Kapital x Netto-ROI x Umschlag (Annahme)", "fliesst_ab_monat": 2, "konservativ_eur_monat": -23, "basis_eur_monat": 242, "optimistisch_eur_monat": 1112},
    {"quelle": "Handelsmarge TikTok Shop", "voraussetzung": "Seller-Konto, Provision ~9% (prüfen)", "kennzahl": "wie oben", "fliesst_ab_monat": 6, "konservativ_eur_monat": 0, "basis_eur_monat": 0, "optimistisch_eur_monat": 0}
  ],
  "kosten": {"einmalig_eur": 150, "laufend_eur_monat": 58, "arbeitszeit_h_woche": 5},
  "break_even_monat": {"konservativ": null, "basis": 4, "optimistisch": 3},
  "eur_pro_arbeitsstunde_monat12": {"konservativ": 0, "basis": 9, "optimistisch": 26},
  "top_risiken": ["Zeit ab EMVIA-Start", "Kontosperrung/Markenbeschwerden", "Steuer/GPSR/VerpackG", "BSR-Absatz nur Schätzung", "Build-vs-Buy"],
  "empfehlung": "GO_MIT_AUFLAGEN",
  "auflagen": ["A1 Phase 0 manuell max 500 EUR", "A2 Meilenstein vor Software-Bau", "A3 max 5 h/Woche", "A4 Recht/Steuer vor Einkauf", "A5 keine Abos/Kurse > 20 EUR", "A6 im bestehenden backend/ bauen"],
  "status": "FREIGEGEBEN_2026-10-13"
}
```

#wichtig #wirtschaftlichkeit #gate
