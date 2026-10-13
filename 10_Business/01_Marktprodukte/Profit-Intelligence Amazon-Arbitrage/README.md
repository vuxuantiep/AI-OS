# Profit-Intelligence — Product Research & Einkaufskalkulation (Amazon-Arbitrage)

> Arbeitstitel (auch „Replenish-System"). Angelegt 13.10.2026.
> **Status: KONZEPT** — Umsetzung erst nach CEO-Freigabe der
> [[wirtschaftlichkeit-profit-intelligence|Wirtschaftlichkeitsprüfung]] (Pflicht-Gate).
> Architektur: [[Plannung/Architektur|Architekturdiagramm]]

## Kernidee in einem Satz

Nach Eingabe von **ASIN + Verkaufspreis + konkretem Lieferantenangebot** liefert das
System eine nachvollziehbare Antwort: *Wie viel verdiene ich unter diesen Annahmen,
welche Risiken bestehen, welche Daten fehlen, wie viel Geld riskiere ich?*
Es **kauft nie selbst** — jede Einkaufsentscheidung ist eine dokumentierte menschliche Freigabe.

**Leitsatz:** Erst die Wirtschaftlichkeit zuverlässig rechnen, dann KI und Automatisierung.
Eine Engine, die Gebühren falsch rechnet oder Schätzungen als Fakten ausgibt, ist
gefährlicher als eine Tabelle.

## MVP-Umfang

| Drin | Bewusst NICHT drin |
|---|---|
| Produkte/Angebote strukturiert erfassen (manuell + CSV) | Autonome Einkäufe/Bestellungen |
| Preise & Nachfrageindikatoren mit Quelle + Zeitstempel | Universeller Web-Scraper |
| Gebühren/USt/variable Kosten transparent (datierte Regeln) | „Präzise" Absatzprognose aus BSR |
| 3 Szenarien (optimistisch / Basis / Stress) | Mehrere Marktplätze gleichzeitig |
| Datenqualität getrennt von Profitabilität bewerten | Eigener LLM-Server / teure SaaS |
| Freigabe + Audit (Entscheidung reproduzierbar) | Änderungen am Verkäuferkonto |

## Datenklassen (Pflicht für jede Kennzahl)

`BEOBACHTET` (eigene Momentaufnahme) · `OFFIZIELL` (SP-API / eigenes Konto) ·
`GESCHAETZT` (Drittanbieter, nur mit Methode + Unsicherheit) · `UNBEKANNT`.
Ein unbekannter Compliance-Status gilt **nie** als bestanden.

## Berechnungskern (deterministisch, `Decimal`, kein LLM)

1. **Nettoerlös** = Brutto / (1 + USt-Satz) — z. B. 23,80 € / 1,19 = 20,00 €
   (Differenzbesteuerung/Kleinunternehmer separat modellieren).
2. **Deckungsbeitrag/Stück** = Nettoerlös − Wareneinsatz netto − Marktplatzgebühren
   − Versand/Fulfillment − Prep/Verpackung − erwartete Retouren-/Verlustkosten − sonstige.
3. **ROI** = Gesamt-DB / eingesetztes Warenkapital × 100 (z. B. 30 € / 80 € = 37,5 %) —
   vor Fixkosten und Ertragsteuern, *keine* Jahresrendite.
4. **Szenarien:** Stress = Preis −10 %, Gebühren ↑, Retouren ↑, längere Lagerdauer
   (Werte sind konfigurierbare Annahmen, später aus eigenen Ist-Daten).
5. **Vier getrennte Ergebnisse:** Profitabilität · Datenqualität · Risiko · Handlungsstatus.
   Kein undurchsichtiger KI-Score — harte Ausschlussregeln + erklärbare Teilwerte.

Gebühren (Amazon-Verkaufsprovision je Kategorie, FBA, TikTok-Shop-Provision) liegen
als **datierte Regeln** in `cost_profiles` (`valid_from/until`, `source_url`), nie im Code.

## Datenmodell (PostgreSQL bzw. vorhandene Backend-DB)

`products` · `marketplace_listings` · `observations` (historisch, nie überschreiben) ·
`supplier_offers` · `cost_profiles` · `profit_runs` (mit `rule_version`) ·
`purchase_decisions` (unveränderlich) · `audit_events` · `data_sources`
(Herkunft, Abrufzeit, Verwendungszweck, Ablaufdatum). Geld = `NUMERIC` / `Decimal`.

## Agenten/Services (die meisten deterministisch)

1. **Discovery** — Kandidaten aus CSV/erlaubten Quellen, Dublettenprüfung
2. **Market Research** — Preis, Verkäuferanzahl, Verlauf, jede Zahl mit Quelle + Alter
3. **Profit Engine** — reiner Python-Kern, keine freien LLM-Antworten
4. **Risk & Compliance** — Nachweise, Verkaufsbeschränkungen (Ungating), Marke, GPSR
5. **Decision Assistant** (LLM) — Bericht, Datenlücken, Vorschlag
   „weiter prüfen / beobachten / zur Freigabe vorlegen"

Externe Produkttexte/Webseiten = **nicht vertrauenswürdige Daten** (Prompt-Injection-Schutz).

## Einbettung ins AI-OS (Abweichungen vom Ursprungsvorschlag)

Der Ursprungsplan schlägt n8n/Activepieces + neues FastAPI + Streamlit vor. Im AI-OS
existiert das meiste schon — **nichts Neues installieren**:

| Vorschlag | AI-OS-Bestand | Entscheidung |
|---|---|---|
| n8n / Activepieces | Node-RED (läuft), Workflow-Engine :5200 | Node-RED bzw. einfacher Scheduler im Backend |
| Neues FastAPI | `backend/` (FastAPI + uv, :8000, Zielarchitektur) | als Modul `profit_intelligence` dort |
| LLM-Agent | LiteLLM :4000 (lokal/Cloud) | Decision Assistant über LiteLLM |
| LangGraph später | LangGraph-Engine :5500 vorhanden | erst wenn Ablauf zustandsbehaftet wird |
| Streamlit | Dashboard :5000 | eigener Tab, kein zweites UI-Framework |

## Fahrplan (nach Freigabe, angepasst an Gate-Auflagen)

- **Phase 0 (2–4 Wochen, kein Code außer Rechner):** manueller Praxistest mit
  Keepa/Seller-Central-Gebührenrechner + Tabelle, Kleinbudget. Beweist: gibt es in DE
  überhaupt Deals ≥ Mindest-ROI, die ich verkaufen *darf*?
- **Phase 1:** Profit Engine + ≥ 20 Testfälle mit unabhängig geprüften Sollwerten.
- **Phase 2:** CSV-Import (≥ 100 Datensätze, Dubletten), Datenqualität, Szenarien.
- **Phase 3:** Freigabe + Audit + Dashboard-Tab.
- **Phase 4:** SP-API (Product Fees, Catalog) — nur mit Pro-Konto und geprüften Rollen.
- **Phase 5:** Ist-Rückführung (echte Verkäufe → Stressannahmen kalibrieren).
- **Später:** TikTok Shop (nur offizielle Partner-APIs, kein Scraping) · Modul B.

## Abnahmekriterien MVP

- [ ] ≥ 100 CSV-Testdatensätze, Dubletten erkannt
- [ ] ≥ 20 Rechenfälle mit unabhängig geprüften Sollwerten grün
- [ ] Jede Gebühr: Quelle, Gültigkeitszeitraum, Status
- [ ] Basis- und Stressfall mit veränderbaren Annahmen sichtbar
- [ ] Veraltete/geschätzte/fehlende Werte markiert
- [ ] Keine Bestellung ohne dokumentierte menschliche Freigabe möglich
- [ ] Jede Entscheidung mit damaligem Datenstand reproduzierbar

## Modul B — Seller Growth Intelligence (geparkt)

Anderes Geschäftsmodell: bestehende Listings profitabler machen (Positionierung,
Amazon-SEO/Listing, PPC — vgl. „Schwungrad-Methode" der Agentur Fischer & Habel,
fischer-habel.com/de/amazon-agentur). Bewertung: deren Fallstudien (30–54 % / „bis 600 %")
sind **Anbieter-Werbung**, keine unabhängigen Belege; Umsatz ≠ Gewinn.
Voraussetzung für Modul B: eigenes Seller-Konto mit Werbe- und Verkaufsdaten
→ frühestens nach Phase 5. Fallstudie nur als Lernmaterial nutzen, keine Beratung kaufen.

#idee #amazon #arbitrage #profit-engine
