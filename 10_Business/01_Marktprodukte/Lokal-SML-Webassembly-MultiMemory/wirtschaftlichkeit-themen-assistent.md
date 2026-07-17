# 💶 Wirtschaftlichkeitsprüfung: Themen-Assistent (Self-Evolving Stufe 2)

> Erweiterungs-Prüfung der Plattform „Souveräne lokale KI" nach Gate-Regel 4,
> erstellt 17.07.2026 durch den Wirtschaftlichkeits-Prüfer-Agenten.
> Prüfgegenstand: [[Bauplan-Feed-Scraper-Wasm]] (Phasen 1–4, ~3–4 Arbeitstage).
> Zeithorizont: 12 Monate. Zielgruppe: deutschsprachige Smartphone-Endverbraucher.

## Management-Summary (5 Sätze, Klartext)

Der Themen-Assistent kostet 0 € Cash und ~3–4 Arbeitstage, weil er komplett auf
vorhandener Infrastruktur (DokuCheck-PWA, WebLLM, Multi-Memory) aufsetzt und
Phase 3 nebenbei den offenen v0.3-Embedding-Punkt von DokuCheck erledigt.
Als reines Endverbraucher-Verkaufsprodukt trägt er sich im Jahr 1 **nicht** —
ohne Reichweite konvertiert eine Consumer-PWA praktisch nicht (Monat 1–6 ≈ 0 €,
konservativ auch Monat 12 nahe 0 €). Der belastbare Geldpfad ist derselbe wie
bei LeadPilot: das Produkt als **B2B-Demo-Asset** („lokale KI, die Ihr
Fachwissen lernt — ohne Cloud") für Done-for-you-Setups à 1.500–5.000 €.
Der Endverbraucher-Kanal ist Marketing und Nutzer-Feedback-Quelle (Freemium
erst ab echtem Nutzungssignal, vorher kein Payment-Aufwand). Empfehlung:
**GO_MIT_AUFLAGEN** — striktes Zeitbudget, Monetarisierung Trigger-basiert,
Vertrieb über vorhandene Kanäle (KI-Avatar/Checker, vuxuantiep.de).

## 1. Marktbedarf — Score 6/10

- **Problem real:** Nachrichten-/Themen-Müdigkeit + Datenschutz-Bedenken bei
  Cloud-KI sind belegt (DSGVO-Diskussion, Apple/Samsung bewerben „On-Device AI"
  massiv — der Markt wird von den Geräteherstellern selbst erzogen).
- **Konkurrenz:** Feedly/Inoreader (Cloud, Abo 6–9 €/Monat — beweist
  Zahlungsbereitschaft für Feed-Kuration), Perplexity/ChatGPT (Cloud, generisch).
  **Lücke:** niemand bietet „dein Themen-Wissen bleibt auf deinem Gerät" als
  Consumer-Produkt — Alleinstellung glaubwürdig, aber erklärungsbedürftig.
- **Dämpfer:** Erklärungsbedürftige Produkte konvertieren bei Endverbrauchern
  schlecht ohne Reichweite; 0,8–1,2 GB Modell-Download ist eine echte Hürde.

## 1b. Usecase-Analyse nach Branchen (Ergänzung 17.07.2026)

Das Konzept-Dokument (docx, „Part 2: Nutzen für spezifische Branchen") nennt
drei Leuchtturm-Usecases. Prüfer-Bewertung: **alle drei sind technisch dieselbe
Plattform** (lokales SLM + Multi-Memory + Agenten-Loop in der PWA) — aber ihre
Erreichbarkeit für einen Solo-Freelancer unterscheidet sich dramatisch:

| Usecase (Quelle) | Bedarf | Blocker für Solo-Einstieg | Erreichbarkeit Jahr 1 | Rolle |
|---|---|---|---|---|
| 🏥 Medizin: OP-/Ultraschall-Diagnostik (docx) | sehr hoch | **Medizinprodukt-Regulierung (MDR/CE)**, Haftung, Klinik-Sales 12–24 Monate | ❌ nicht erreichbar | Fernziel/Marketing-Narrativ |
| 🏦 Banken: lokale Betrugserkennung (docx) | hoch | BaFin/DORA-Compliance, Enterprise-Vendor-Onboarding — kauft nicht bei Einzelpersonen | ❌ nicht erreichbar | Fernziel/Marketing-Narrativ |
| 🏭 Industrie: Offline-Wartungs-Assistent (docx) | hoch | kein Regulierungs-Blocker; Zugang über regionale KMU/Maschinenbau mühsam, aber möglich | ⚠️ mittelfristig (M6+) | **B2B-Ziel #2**: „10.000-Seiten-Handbuch als Offline-PWA" = Done-for-you-Setup |
| ⚖️ Kanzleien/Steuerberater/Notare (eigene Ableitung) | hoch | keiner — DSGVO-Druck ist dort KAUFGRUND; dokumentenlastig = exakt DokuCheck-Terrain | ✅ **Beachhead** | **B2B-Ziel #1**: „Mandanten-Dokumente lokal prüfen + Kanzlei-Wissen lokal" |
| 🔧 KMU/Handwerk: interner Wissens-Assistent (eigene Ableitung) | mittel | keiner; kleine Budgets, aber kurze Entscheidungswege | ✅ ab M4 | B2B-Ziel #3 (Industrie-Usecase „light") |
| 📱 Endverbraucher Themen-Assistent (Kern Stufe 2) | mittel | Reichweite (siehe Abschnitt 1) | ✅ sofort baubar | Produkt-Kern + Demo-Vehikel für alle B2B-Ziele |

**Konsequenz für die Strategie:** Die docx-Leuchttürme (Medizin, Banken) sind
Jahr-1-Vertriebsziele **nicht** — aber sie sind das perfekte Marketing-Narrativ
(„dieselbe Technik, die im OP funktionieren könnte, prüft Ihre Mandanten-Akten").
Der realistische Einstieg ist **Kanzleien/Steuerberater** (DSGVO als Kaufgrund,
DokuCheck-Risiko-Check existiert schon als Basis) und danach der
**Industrie-Wartungs-Usecase als KMU-Variante** — beide bedienen das bestehende
Done-for-you-Modell (1.500–5.000 €/Setup). Der Endverbraucher-Themen-Assistent
bleibt der Kern: Er ist das öffentlich vorführbare Demo-Vehikel, aus dem jede
Branchen-Variante nur durch **andere Feeds/Dokumente + anderes Finetuning**
entsteht (gleiche Codebasis — das ist der eigentliche Plattform-Hebel).

## 2. Einnahmequellen-Inventar

| Quelle | Voraussetzung | Kennzahl (Herkunft) | fließt ab | konserv. €/M (M12) | Basis €/M (M12) | optim. €/M (M12) |
|---|---|---|---|---|---|---|
| Freemium-Premium (mehr Themen/Routinen, einmalig 19–29 € o. 3–5 €/M) | >500 aktive Gratis-Nutzer (Trigger!) | Conversion Free→Paid 1–3 % (Branchenspanne Freemium-Apps; ANNAHME, keine eigene Historie) | M7+ | 0–30 | 60–150 | 300–600 |
| B2B Done-for-you („Firmen-Wissens-Assistent lokal", Intranet-Feeds) | 1 Demo-Video + Landingpage; Akquise über bestehende Kanäle | 1.500–5.000 €/Setup (eigene LeadPilot-Recherche, belegt) | M4+ | 0 | 125–250 (=1–2 Setups/Jahr anteilig) | 400–800 |
| Indirekt: Freelancer-Aufträge durch Kompetenz-Nachweis | Portfolio-Eintrag + Fachartikel | nicht seriös bezifferbar → bewusst 0 € angesetzt | — | 0 | 0 | 0 |

## 3. Szenario-Rechnung (12 Monate, Anlaufkurve ehrlich)

- **Konservativ (P70):** M1–12 ≈ 0–30 €/M gesamt. Consumer-Conversion bleibt aus,
  kein B2B-Abschluss. Jahressumme ≈ 0–200 €.
- **Basis (P50):** M1–6 ≈ 0 € (Bau + Gratis-Phase), ab M7 Freemium 60–150 €/M,
  1–2 B2B-Setups im Jahr (3.000–6.000 € einmalig). Jahressumme ≈ 3.500–7.500 €.
- **Optimistisch (P20):** Viral-Moment über KI-Avatar-Kanäle, 3+ B2B-Setups.
  Jahressumme ≈ 10.000–15.000 €.

**€/Arbeitsstunde (Monat 12, bei ~2 h/Woche laufend + 30 h Bau):**
konservativ ≈ 0–2 €/h ❌ · Basis ≈ 25–55 €/h ✓ · optimistisch ≈ 75–110 €/h ✓✓

## 4. Kosten & Break-even

- **Einmalig:** 0 € Cash (Toolchain frei, Infrastruktur vorhanden); ~30 h Arbeit (Phasen 1–4)
- **Laufend:** 0 € (kein Server; Feed-Proxy läuft auf vorhandenem Dashboard);
  Payment-Gebühren erst bei Premium (LemonSqueezy/Stripe ~5 % + 0,50 €)
- **Break-even (Cash):** sofort (keine Cash-Kosten). **Break-even (Arbeitszeit
  zu 85 €/h Referenzsatz ≈ 2.550 € Invest):** konservativ nie, Basis M9–12, optimistisch M6–8
- **Doppelnutzen senkt echte Kosten:** Phase 3 (Embeddings) stünde für DokuCheck
  v0.3 ohnehin an — ~1/3 der Bauzeit wäre so oder so investiert worden.

## 5. Top-Risiken

1. **Reichweiten-Risiko (größtes):** ohne Marketing-Kanal konvertiert nichts —
   Gegenmaßnahme: Content über die bestehenden KI-Avatar/Checker-Kanäle, kein neuer Kanal.
2. **Modell-Download-Hürde** (0,8+ GB) schreckt Casual-Nutzer ab — Gegenmaßnahme:
   OCR-/BM25-Modus ohne LLM als Einstieg (existiert in DokuCheck bereits).
3. **Browser-Plattform-Risiko:** iOS-WebGPU-Reife, Storage-Eviction — siehe
   [[Analyse-Browser-vs-Native]]; Trigger-Kriterien für native App definiert.
4. **Ein-Personen-Risiko:** Zeitbudget-Deckel als Auflage (s. u.).
5. **Feed-Verfügbarkeit:** Verlage drosseln RSS — Gegenmaßnahme: kuratierte
   Feed-Listen pro Thema pflegbar in den Einstellungen.

## 6. Empfehlung: **GO_MIT_AUFLAGEN**

Auflagen:
1. **Zeitbudget Phasen 1–4: max. 4 Arbeitstage**, danach harter Stopp-Punkt mit
   Review (funktioniert der Loop? Nutzt es jemand?).
2. **Kein Payment-/Premium-Aufwand vor Trigger** „>500 aktive Gratis-Nutzer ODER
   erste konkrete B2B-Anfrage" — vorher ist Monetarisierungs-Arbeit verschwendet.
3. **B2B-Pfad ab Phase 4 mitdenken:** 1 Demo-Video + Abschnitt auf vuxuantiep.de
   (max. 0,5 Tage) — das ist der wahrscheinlichste Geldweg. **Zielbranche zuerst:
   Kanzleien/Steuerberater** (Beachhead laut Usecase-Analyse 1b), danach
   KMU-Wartungs-/Wissens-Assistent; Medizin/Banken nur als Narrativ nutzen.
4. **Nachprüfung M3** nach Launch: Prognose vs. Ist in diesem Dokument nachtragen.

```json
{
  "produkt": "Themen-Assistent (Self-Evolving Stufe 2, Plattform-Erweiterung)",
  "marktbedarf": {"score_0_10": 6, "begruendung": "echte Luecke (lokal statt Cloud), aber erklaerungsbeduerftig + Reichweiten-abhaengig"},
  "kosten": {"einmalig_eur": 0, "laufend_eur_monat": 0, "arbeitszeit_h_woche": 2, "bau_h_einmalig": 30},
  "break_even_monat": {"konservativ": null, "basis": 10, "optimistisch": 7},
  "eur_pro_arbeitsstunde_monat12": {"konservativ": 1, "basis": 40, "optimistisch": 90},
  "usecase_prioritaet": ["1. Kanzleien/Steuerberater (Beachhead)", "2. Industrie/KMU-Wartung (M6+)", "3. Endverbraucher (Demo-Vehikel)", "Fernziel-Narrativ: Medizin, Banken"],
  "empfehlung": "GO_MIT_AUFLAGEN",
  "auflagen": ["max 4 Arbeitstage Phasen 1-4", "Monetarisierung erst ab Trigger", "B2B-Demo ab Phase 4 (Zielbranche: Kanzleien/Steuerberater)", "Nachpruefung M3"],
  "status": "WARTET_AUF_FREIGABE"
}
```

**Status: WARTET_AUF_FREIGABE** — Umsetzung Phase 1 startet erst nach expliziter CEO-Freigabe.
