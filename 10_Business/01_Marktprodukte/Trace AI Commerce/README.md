# Trace AI Commerce

> Produktordner angelegt 13.10.2026. Bisher existierte das Produkt nur als KI-Fabrik-Auftrag:
> - v1: [[../../KI-Fabrik-Auftraege/ord_20260703_222059_Trace_AI_Commerce|ord_20260703_222059]] (03.07.2026)
> - v2: [[../../KI-Fabrik-Auftraege/ord_20260706_221950_Trace_AI_Commerce_v2|ord_20260706_221950]] (06.07.2026, im Sprint Review vom CEO abgenommen)
> - Klickbarer Prototyp v2: `../../KI-Fabrik-Auftraege/Prototypen/ord_20260706_221950.html`

## Zielgruppe

Onlinehändler · Content-Creator · Online-Kurs-Anbieter

## Module

| # | Modul | Quelle | Status |
|---|---|---|---|
| 1 | Marktanalyse | Fabrik-Auftrag v1/v2 | Konzept |
| 2 | Lead-Automation | Fabrik-Auftrag v1/v2 (Überschneidung mit LeadPilot CRM :5330) | Konzept |
| 3 | Marketing / AIVO / GEO-Agent | Fabrik-Auftrag v1/v2 | Konzept |
| 4 | API-Connector-Agent | Fabrik-Auftrag v1/v2 | Konzept |
| 5 | Avatar für Digitalprodukte (YouTube-Content, E-Books) | Fabrik-Auftrag v1/v2 (Überschneidung mit KI-Avatar :5310) | Konzept |
| **6** | **[[Modul-Profit-Intelligence/README\|Profit-Intelligence]]**: Produktrecherche + Einkaufskalkulation (Amazon-Arbitrage, später TikTok Shop) | Plan vom 13.10.2026 | **FREIGEGEBEN 13.10.2026** |
| 7 | Seller-Growth (Listing/PPC, „Schwungrad"-Ansatz) | Plan vom 13.10.2026 | geparkt, siehe Modul 6 |

## Einordnung

Modul 6 konkretisiert die Punkte „Marktanalyse" und „API-Connector" aus dem Fabrik-Auftrag
für Onlinehändler, verschiebt aber den Schwerpunkt: Statt Leads/Content steht die
**Wirtschaftlichkeit eines Einkaufs** im Mittelpunkt. Der Fabrik-Tech-Stack
(Node.js/React/MongoDB) wird für Modul 6 **nicht** übernommen: Es baut auf dem AI-OS-Bestand
(`backend/` FastAPI, Dashboard, LiteLLM) auf, siehe Gate-Auflage A6.

#trace-ai-commerce #produkt

## Werbung in KI-Assistenten (Recherche 13.10.2026) — für Modul 3 (AIVO/GEO) und Modul 7

Stand laut Sekundärquellen (Fachblogs, nicht OpenAI/Google selbst) – vor Budgetentscheidungen auf den offiziellen Seiten prüfen:

| Plattform | Status DE | Kurzinfo |
|---|---|---|
| **ChatGPT Ads** (OpenAI) | **Self-Serve offen** seit Ende Aug. 2026 (ads.openai.com) | Anzeigen unter Antworten für Free/Go-Nutzer; in EWR nur **kontextbezogen** (keine Personalisierung); Mindestbudget lt. einer Quelle 15 €/Kampagne; Finanz-/Gesundheits-/Rechtswerbung außerhalb USA eingeschränkt; Produkt-Feeds im Ads Manager möglich |
| **Google AI Mode / AI Overviews** | Tests v. a. USA, DE unklar | Gemini-Formate (Conversational Discovery, Highlighted Answers) laufen über **bestehende Google-Ads-Kampagnen**; keine eigene GA/Reporting angekündigt |
| **Gemini-App** | keine bestätigten Anzeigen | Google schließt es nicht aus („2026" gegenüber Werbekunden genannt) |
| **Microsoft Copilot** | Pilot, englischsprachige Märkte | über Microsoft-Advertising-Kampagnen, Retail zuerst |
| **Perplexity** | kein Anzeigenprogramm | Sponsored Follow-ups wieder eingestellt |

**Einordnung für Trace AI Commerce:**
- **Modul 6 (Arbitrage):** Verkauf läuft über Amazon → externe KI-Ads sind dort **kein Hebel**. Werbekosten aber als variable Kosten vorsehen (`cost_profiles.fee_type = "werbung"`, z. B. Amazon-PPC/ACoS), damit DB nicht geschönt wird.
- **Modul 3 (AIVO/GEO):** Zwei Wege in KI-Antworten: *organisch* (GEO: zitierfähige Inhalte, strukturierte Produktdaten, Feeds) und *bezahlt* (ChatGPT Ads, später Google AI Mode). Vorbereitung: sauberer Produkt-Feed (GTIN, Preis, Verfügbarkeit), Landingpages mit klaren Fakten, Conversion-Tracking.
- **Modul 7 (Seller-Growth):** ChatGPT-Ads als Testkanal mit Mini-Budget erst, wenn eigenes Produkt/eigene Marke existiert. Erfolg in **Deckungsbeitrag**, nicht Umsatz messen.

Quellen: dataiads.io/en/blog/chatgpt-ads-manager-europe-flux-produit · inpromptads.com/chatgpt-ads/germany · enterprisedna.co (ChatGPT Ads 31 EU-Märkte) · leapbuzz.com/blog/does-gemini-have-ads · trylapis.com (Guide Advertising in AI Assistants) · grailstar.com/blog/conversational-ads-landscape-2026
