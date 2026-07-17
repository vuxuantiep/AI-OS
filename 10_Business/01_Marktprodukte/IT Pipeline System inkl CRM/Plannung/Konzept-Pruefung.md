# Konzept-Prüfung: IT Pipeline System inkl. CRM

> Geprüft am 16.07.2026 gegen `Konzept.png` + Screenshots im Plannung-Ordner.
> Gesamturteil: **Grundkonzept solide und angenehm schlank — aber 3 sachliche
> Fehler/Lücken, die vor dem Bau korrigiert werden müssen (F1–F3), plus eine
> strategische Empfehlung zur Reihenfolge (Eigennutzung vor Verkauf).**

## Was das Konzept richtig macht ✅

1. **Entscheidungs-Gate statt Overengineering:** CRM erst ab >10 Leads/Monat —
   genau richtig. Die meisten Freelancer-CRMs sterben an Wartungsaufwand für
   3 Leads im Monat.
2. **Bestehende Lead-Quellen nutzen** (Kontaktformular + Cal.com) statt neue zu
   erfinden.
3. **KI-Features bewusst nach hinten geschoben** („erst wenn Basis stabil,
   mit manueller Freigabe") — deckt sich mit unserer Compliance-Philosophie.
4. **Zwei Verwertungen angelegt:** Eigennutzung UND als Done-for-you-Paket
   verkaufbar (Screenshots: Positionierung + Paketpreis-Framework) — die
   Screenshots zeigen, dass der Markt dafür Pakete à 2.000–5.000 € akzeptiert.

## Gefundene Fehler & Lücken

### F1 — HubSpot Free kann die Stufe 3 NICHT (sachlicher Fehler) ⚠️
Das Konzept sagt: „Trigger-Mails im CRM eingebaut, kein Zusatztool nötig".
**HubSpot Free enthält aber keine Workflow-Automatisierung** — automatisierte
Sequenzen (Erinnerung bei fehlender Buchung, Follow-up nach Angebot) sind
Starter/Professional-Features (ab ~20–50 €/Monat, Preise vor Bau verifizieren).
Im Free-Tier gibt es nur einfache Formular-Follow-up-Mails.
**Optionen:**
- a) HubSpot Starter einplanen (laufende Kosten ins Budget) — Preis vorher prüfen
- b) **Self-hosted CRM (z. B. EspoCRM oder Twenty) + n8n für die 4 Trigger-Mails**
  — n8n läuft bereits in unserer Pipeline (KI-Avatar-Posting), passt zur
  AI-OS-Philosophie „selbst gehostet" und macht das Ganze erst zum echten
  **AI-OS-Modul** (und zum verkaufbaren Produkt ohne Fremdlizenz-Abhängigkeit)
- **Empfehlung: b)** — sonst ist das „Modul für AI-OS" in Wahrheit ein HubSpot-Tab.

### F2 — DSGVO/UWG fehlt komplett ⚠️
Leads = personenbezogene Daten. Vor dem Bau klären:
- **AV-Vertrag + Drittlandtransfer** falls US-CRM (HubSpot: Data Privacy Framework
  prüfen); bei Self-hosted entfällt das Problem elegant
- **Datenschutzerklärung** der Website um CRM-Verarbeitung ergänzen
- **§7 UWG bei Trigger-Mail 2 und 4:** Eingangsbestätigung (Mail 1) und Dankes-Mail
  (Mail 3) sind unkritisch (Vertragsanbahnung). „Erinnerung bei fehlender Buchung"
  und „Follow-up nach Angebot" sind als **einzelne 1:1-Nachrichten** okay, dürfen
  aber NICHT zu einer automatischen Drip-Serie werden (mehrfach nachfassen ohne
  Einwilligung = unzumutbare Belästigung). Regel: max. 1 automatische Erinnerung
  pro Anlass, danach manuell.
- Löschkonzept: verlorene Leads nach X Monaten anonymisieren/löschen.

### F3 — Der linke Pfad verschenkt den wertvollsten Hebel
Beim „Wenig"-Pfad gibt es NULL Automatisierung. Aber die mit Abstand
konversionsstärkste Automatisierung ist **Mail 1 (sofortige Eingangsbestätigung)**
— Antwortzeit entscheidet bei Freelancer-Anfragen über den Zuschlag, unabhängig
vom Volumen. Die kostet einen n8n-Flow (15 Minuten Aufwand) und gehört in BEIDE
Pfade.

### Kleinere Lücken
- **L1 — Dedup:** Kontaktformular + Cal.com erzeugen Dubletten (gleiche Person,
  zwei Wege) → beim Import auf E-Mail matchen.
- **L2 — Umschalt-Trigger fehlt:** Wann wird vom linken auf den rechten Pfad
  gewechselt? Vorschlag: 2 Monate in Folge >10 aktive Leads → Migration.
- **L3 — Keine KPIs:** Minimal messen: Antwortzeit bis Erstreaktion,
  Conversion je Pipeline-Stufe, Quelle je Lead (Formular vs. Cal.com).
- **L4 — „Trace-AI OS"-Einbindung** ist noch unspezifiziert — als Modul-Anforderung
  formulieren (welche Daten, welche API?), nicht als Nebensatz.

## Strategische Empfehlung: Reihenfolge

Die Screenshots zielen auf **Verkauf als Dienstleistung** („Wir setzen das CRM
FÜR DICH auf", Paketpreis 2.000–5.000 €). Das ist die eigentliche Umsatzchance —
ABER: Wer CRM-Setups verkauft, braucht ein vorzeigbares eigenes System.

**Phase A (Eigennutzung, ~2–3 Tage):** Schlanke Version selbst bauen —
Lead-Board als AI-OS-Modul (Muster: KI-Avatar-Board), n8n-Flows für Mail 1
(+ Mail 2 einfach), Cal.com-Webhook. Eigene Pipeline = Fallstudie.
**Phase B (Produktisierung):** Erst nach Phase A + erstem Monat Echtbetrieb:
Setup-Checkliste + Templates daraus ableiten, als Done-for-you-Paket anbieten
(Positionierung nach dem 3-Fragen-Framework aus den Screenshots).

→ Wirtschaftliche Bewertung + Freigabe-Gate: siehe
[[../wirtschaftlichkeit-it-pipeline-crm|Wirtschaftlichkeitsprüfung]].

#it-pipeline #crm #konzept-pruefung
