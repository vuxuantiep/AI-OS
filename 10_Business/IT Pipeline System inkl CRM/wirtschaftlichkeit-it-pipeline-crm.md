# Wirtschaftlichkeitsprüfung: IT Pipeline System inkl. CRM

> Erstellt vom [[../wirtschaftlichkeits-pruefer-agent|Wirtschaftlichkeits-Prüfer]] am 16.07.2026.
> **Status: FREIGEGEBEN** — CEO-Freigabe erteilt am 16.07.2026 (GO_MIT_AUFLAGEN, A1–A3 + B1 gelten).
> CEO-Zusatz bei Freigabe: Modul muss in AI-OS UND Trace-AI OS (getrennte Repos)
> installierbar sein → als self-contained Modul gebaut; Ziel-UX „professionelles SaaS";
> eigenes schlankes CRM statt EspoCRM; Lead-Radar für relevante Kundenprojekte.
> Konzept-Review: [[Plannung/Konzept-Pruefung|Konzept-Prüfung]] (3 Pflicht-Korrekturen F1–F3).

## Management-Summary (5 Sätze)

Dieses Produkt ist anders als der AI Business Checker: Der Wert entsteht zuerst
**indirekt** (eigene Lead-Konversion + gesparte Zeit) und erst in Phase B direkt
(Done-for-you-Setups für Kunden à 1.500–3.500 €). Phase A kostet nur 2–3 Tage
Arbeit, nutzt vorhandene Bausteine (n8n, Flask-Board-Muster, Self-hosted-Stack)
und liefert selbst im schlechtesten Fall ein funktionierendes eigenes Lead-System
plus wiederverwendbares AI-OS-Modul. Die Verkaufs-Chance (Phase B) ist real —
der Markt zahlt für CRM-Einrichtung nachweislich Paketpreise —, hängt aber daran,
dass erst die eigene Fallstudie existiert und Akquise-Aufwand entsteht. Größtes
Risiko ist nicht Technik, sondern dass Phase B ohne eigene Lead-Basis zum
Luftschloss wird. **Empfehlung: GO für Phase A sofort, Phase B nur nach
Meilenstein-Check.**

## 1. Marktbedarf — Score: 7/10 (Phase B) / 9/10 (Phase A)

- **Phase A (Eigenbedarf):** unmittelbar belegt — Kontaktformular + Cal.com existieren
  bereits auf der Website, jede unbeantwortete Anfrage ist verlorener Umsatz.
- **Phase B (Verkauf):** Kleinunternehmen/Freelancer zahlen nachweislich für
  Done-for-you-Automatisierung (Paketpreis-Framework aus der Recherche: 2.000–5.000 €
  bei quantifiziertem Wert „20 h/Monat + 1.000 € Personalkosten gespart").
  Konkurrenz existiert (Agenturen, Fiverr), Differenzierung nötig: **self-hosted +
  DSGVO-sauber ohne US-Cloud** ist ein echtes Verkaufsargument im DACH-Markt.
- Unsicherheit: eigene Reichweite für Akquise fehlt noch (**Annahme**, Gegenmittel:
  eigene Fallstudie + bestehende IT-Kunden als Erstzielgruppe).

## 2. Einnahmequellen-Inventar

| # | Quelle | Voraussetzung | Kennzahl (Herkunft) | Fließt ab |
|---|---|---|---|---|
| E1 | **Eigene Lead-Konversion** (indirekt) | Phase A live | +1 gewonnener Auftrag/Quartal durch schnellere Reaktion = 1.500–5.000 € (**Annahme**, typische Freelancer-Projektgröße) | Monat 1–2 |
| E2 | **Zeitersparnis** (indirekt) | Phase A live | ~2–4 h/Monat manuelles Lead-Handling entfällt | Monat 1 |
| E3 | **Done-for-you-Setup-Pakete** | Phase B: Fallstudie + Angebotsseite | 1.500–3.500 €/Paket (Marktspanne aus Recherche-Screenshots, konservativ angesetzt) | Monat 3+ |
| E4 | **Wartungs-Retainer** | ≥3 verkaufte Setups | 50–150 €/Monat/Kunde (**Branchenüblich**) | Monat 6+ |
| E5 | AI-OS-/Trace-AI-OS-Modul | Phase A | kein Direktumsatz — Plattformwert + Demo-Material | — |

## 3. Szenario-Rechnung (12 Monate)

| Szenario | Phase-B-Verkäufe Jahr 1 | Einnahmen Jahr 1 (direkt + indirekt) |
|---|---|---|
| **Konservativ (P70)** | 0 Pakete | ~1.500–3.000 € (nur E1/E2: 1 Zusatzauftrag + Zeit) |
| **Basis (P50)** | 2–3 Pakete | ~6.000–12.000 € (E1 + 2–3 × ~2.500 €) |
| **Optimistisch (P20)** | 6–8 Pakete + 3 Retainer | ~20.000–30.000 € |

Anlaufkurve ehrlich: Phase-B-Umsatz frühestens Monat 3–4 (Fallstudie braucht
einen Monat Echtbetrieb). Der konservative Fall ist hier — anders als beim
Checker — **nicht negativ**: selbst 0 Verkäufe lassen ein nützliches eigenes
System zurück.

## 4. Kosten & Break-even

| Posten | Betrag |
|---|---|
| Phase A Arbeitszeit | 2–3 Tage einmalig (~16–24 h) + ~1 h/Monat Pflege |
| Phase B Arbeitszeit | ~1 Tag Produktisierung (Checkliste, Templates, Angebotsseite) + ~1–2 Tage pro Kundensetup |
| Cash laufend | ~0 € (self-hosted: EspoCRM/Twenty + n8n auf eigener Infrastruktur); nur falls HubSpot-Weg: ~20–50 €/Mon. (F1 der Konzept-Prüfung!) |
| **Break-even** | Phase A: sofort (Zeitersparnis > Pflegeaufwand ab Monat ~3). Phase B: mit dem **ersten verkauften Paket** ist die gesamte Bauzeit bezahlt (~2.500 € / ~30 h ≈ 80 €/h) |

**€/Arbeitsstunde:** konservativ ~30–60 €/h (nur E1), Basis ~80–150 €/h — deutlich
über dem Checker, weil Dienstleistung sofort bezahlt wird statt über Werbe-RPM.

## 5. Top-Risiken

1. **Phase B ohne Nachfrage-Beweis:** CRM-Setups verkaufen erfordert Akquise —
   wenn die eigene Pipeline <10 Leads/Monat hat, gilt das erst recht für das
   neue Angebot. Gegenmittel: Auflage B1 (Meilenstein vor Phase B).
2. **Scope-Kriechen:** aus „schlankes Konzept" wird ein CRM-Eigenbau.
   Gegenmittel: Phase A hart auf Board + 2 n8n-Flows + Webhook begrenzt (A1).
3. **DSGVO-Fehler beim Kundenprojekt** (F2 der Konzept-Prüfung) — beim Verkauf
   haftet man für saubere Einrichtung; Checkliste Pflichtteil des Pakets.
4. **Fremd-Plattform-Falle:** HubSpot-Free-Annahme ist falsch (F1) — ohne Korrektur
   platzt das Nutzenversprechen „keine Zusatzkosten".

## 6. Empfehlung: **GO_MIT_AUFLAGEN**

- **A1 — Phase A zuerst, hart begrenzt:** max. 3 Arbeitstage. Umfang: Lead-Board
  (AI-OS-Modul, Muster KI-Avatar-Board), n8n-Flow Mail 1 (+ einfache Erinnerung),
  Cal.com-Webhook, Dedup auf E-Mail. Self-hosted, kein HubSpot.
- **B1 — Phase-B-Gate:** Produktisierung erst wenn (a) Phase A 4 Wochen im
  Echtbetrieb UND (b) mindestens 1 dokumentierter Nutzen-Nachweis (schnellere
  Antwortzeit / gewonnener Auftrag). Sonst bleibt es ein internes Werkzeug —
  auch okay.
- **A2 — DSGVO-Basics vor Golive:** Datenschutzerklärung ergänzen, Löschregel,
  Trigger-Mails 2/4 nur als einzelne 1:1-Erinnerung (kein Drip).
- **A3 — Cash-Deckel:** 0 € (self-hosted); jede kostenpflichtige Alternative
  braucht neue Freigabe.

```json
{"empfehlung": "GO_MIT_AUFLAGEN", "status": "WARTET_AUF_FREIGABE"}
```

> ✍️ **Freigabe CEO:** ☑ erteilt am: **16.07.2026** · ☐ abgelehnt · ☐ Pivot angefordert
> Review-Termin (Prognose vs. Ist): 3 Monate nach Phase-A-Golive.

#wirtschaftlichkeit #it-pipeline #crm
