# Wirtschaftlichkeitsprüfung: Praxis-IT-Check + Praxis-IT-Wächter

> Wirtschaftlichkeits-Prüfer, 24.11.2026 · **Status: WARTET_AUF_FREIGABE** (CEO)
> Produktplan: [[productized-service-praxis-it-check]] · Vorgänger: [[wirtschaftlichkeit-trace-it]] (Preis-Benchmarks, Kosten, Risiken dort weiter gültig)
> Zeithorizont 12 Monate, hauptberuflich aus Bürgergeld. Alle Preise/Mengen = **Annahmen**, Validierung über Pilot-Checks.

#wirtschaftlichkeit #gate #trace-it

## Management-Summary
Die Zuspitzung auf **eine Zielgruppe (Praxen) und ein Produkt** senkt Vertriebs- und Vorbereitungsaufwand deutlich gegenüber 3 bzw. 5 Angeboten.
Im Basis-Szenario ≈ **21.300 € Umsatz / ≈ 18.600 € Ergebnis vor Steuern** in Jahr 1 – leicht über dem Businessplan (19.946 €).
Wiederkehrend in Monat 12: ≈ 900 €/Monat; der Rest kommt aus Checks und Umsetzungstagen.
Größtes Risiko ist nicht die Technik, sondern ob Praxen **ohne akuten Vorfall** 790 € zahlen. **Empfehlung: GO_MIT_AUFLAGEN.**

## 1. Marktbedarf – Score 7/10 (vorläufig)
- Pflicht vorhanden: KBV-IT-Sicherheitsrichtlinie (§ 390 SGB V) gilt für alle vertrags(zahn)ärztlichen Praxen; Umsetzungsstand in kleinen Praxen gilt als lückenhaft. *Aktuelle Fassung + Prüfpraxis vor dem ersten Angebot an der Primärquelle (KBV/KZBV) prüfen.*
- Kaufanlass: Pflicht, Cyberversicherung, Ransomware-Fälle in Praxen, Datenschutz Art. 9 DSGVO.
- Konkurrenz: PVS-Händler und Praxis-IT-Betreuer (oft ohne strukturierte Prüfung), große Systemhäuser (zu teuer für Kleinpraxen), Online-Checklisten (kostenlos, aber ohne Technik-Prüfung).
- Abzug: noch kein Kundengespräch; Zahlungsbereitschaft ohne Vorfall unbelegt.

## 2. Einnahmequellen
| # | Quelle | Preis (Annahme) | ab Monat |
|---|---|---|---|
| 1 | Praxis-IT-Check | Ø 750 € (590/790/1.190) | 2–3 (Piloten 490 €) |
| 2 | Praxis-IT-Wächter | 129 €/Monat, 12 Mon. Mindestlaufzeit | 4 |
| 3 | Umsetzung (Upsell) | 760 €/Tag | 3 |
| 4 | Subunternehmer-Tage (Ventil) | 760 €/Tag | bei Bedarf, **nicht eingerechnet** |

## 3. Szenarien (12 Monate)
| | Konservativ (P70) | Basis (P50) | Optimistisch (P20) |
|---|---|---|---|
| Checks | 5 | 10 | 18 |
| Wächter-Kunden Monat 12 | 3 | 7 | 14 |
| Wächter-Kundenmonate gesamt | 12 | 36 | 70 |
| Umsetzungstage | 6 | 12 | 20 |
| Umsatz Checks | 3.500 € | 7.500 € | 13.500 € |
| Umsatz Wächter | 1.548 € | 4.644 € | 9.030 € |
| Umsatz Umsetzung | 4.560 € | 9.120 € | 15.200 € |
| **Umsatz** | **9.608 €** | **21.264 €** | **37.730 €** |
| − einmalig (Vorlagen, Gewerbe, Rechtstexte) | −300 € | −300 € | −300 € |
| − laufend (Haftpflicht, StB, Infrastruktur 12 × 200 €) | −2.400 € | −2.400 € | −2.400 € |
| **Ergebnis vor Steuern** | **6.908 €** | **18.564 €** | **35.030 €** |
| wiederkehrend Monat 12 | 387 €/Mo | 903 €/Mo | 1.806 €/Mo |
| abrechenbare Stunden (Check 10 h, Wächter 1,5 h/Mo, Tag 8 h) | ≈ 116 h | ≈ 250 h | ≈ 445 h |

Hardware (VTA-439/GPU) ist hier **nicht** nötig – Collector läuft beim Kunden, Bericht lokal auf vorhandenem PC. LES-Hardware bleibt Broki-AI zugeordnet.

**Anlaufkurve Basis (grob):** M1–2: 0 € · M3: 980 € (2 Piloten) · M4–6: ≈ 1.300 €/Mo · M7–12: ≈ 2.300 €/Mo.
→ Umsatzziel „2.000 €/Monat" wird im Basis-Szenario **ab etwa Monat 7** erreicht.

## 4. Break-even
Bargeld: Konservativ Monat 6 · Basis Monat 4 · Optimistisch Monat 3 (niedrige Fixkosten, keine Hardware).
Lebensunterhalt (Bedarf 1.065 €/Monat nach Steuern/KV) ist in Jahr 1 auch im Basis-Szenario **nicht voll** gedeckt → Einstiegsgeld + Subunternehmer-Tage als Ventil einplanen.

## 5. Risiken
1. **Zahlungsbereitschaft ohne Vorfall** → Gegenmittel: Pflicht/Versicherung als Aufhänger, kleiner Einstiegspreis 590 €.
2. **Haftung:** Bericht wird als „Bestätigung der Richtlinienkonformität" missverstanden → klar „Bestandsaufnahme, keine Zertifizierung/Rechtsberatung".
3. **Zugriff auf Gesundheitsdaten-Umgebung** → read-only-Skript, AVV, Verschwiegenheit, keine Kundendaten in Cloud-LLMs.
4. **Konflikt mit bestehenden Praxis-IT-Betreuern** → als Partner gewinnen (White-Label), nicht verdrängen.
5. **Wettbewerbs-/Kundenschutzklauseln** aus früheren Arbeitsverhältnissen prüfen.
6. **Fokus:** Broki-AI, Profit-Intelligence, Lab laufen parallel → max. 1 Tag/Woche für Nicht-Umsatz-Themen.

## 6. Empfehlung: GO_MIT_AUFLAGEN
- **P1** Bis Tag 60: 2 bezahlte Pilot-Checks, sonst PIVOT auf „AD-Security-Check für Systemhäuser" (gleiche Skripte).
- **P2** Vor Kunde 1: Haftpflicht, AVV, Prüffreigabe, Leistungsbeschreibung mit Haftungsbegrenzung.
- **P3** Kein 24/7, keine Entstörung im Abo.
- **P4** Preisuntergrenze effektiv ≥ 85 €/h; Pilotrabatt sichtbar ausweisen.
- **P5** Plattform/Automatisierung (TRACE AI) erst ab 5 Wächter-Kunden.
- **P6** Nachprüfung Prognose vs. Ist nach 3 Monaten.

## Freigabe
| Datum | Entscheidung | Notiz |
|---|---|---|
| – | ⏳ offen | |
