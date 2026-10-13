---
titel: Bauanleitung erster Agent „IT-Leitstand" (Ticket + Wiki + proaktives Monitoring) in Copilot Studio
erstellt: 2026-10-13
status: Anleitung — Übung privat ab sofort, EMVIA-Tenant erst nach Freigabe der IT-Leitung
tags: [emvia, copilot-studio, ki-agent, ticketsystem, monitoring, referenz, wichtig]
---

# Erster Agent: „IT-Leitstand" — Schritt für Schritt

> Baut auf [[Project_EMVIA-KI-Assistenten]] (Gesamtplan), [[Agenten-Anweisungen]] (Prompts)
> und [[Infosammlung-Woche-1]] auf. Diese Datei beantwortet nur: **Wie fange ich konkret an?**

## 0. Der Schnitt: EIN Agent, drei Fähigkeiten

Statt sechs Agenten auf einmal baue ich **einen** Agenten für das IT-Team, der drei Dinge kann.
Die Aufteilung in Fach-Agenten (Orchestrator) kommt erst, wenn dieser eine stabil läuft.

| Fähigkeit | Frage im Teams-Chat | Technik in Copilot Studio | KI-Anteil |
|---|---|---|---|
| **A · Wiki** | „Wie richte ich LAPS ein?" | Wissensquelle: SharePoint-Seite „IT-Wissen" | Antwort mit Quellenangabe |
| **B · Ticket** | „Fasse Ticket 4711 zusammen + Antwortentwurf" | Tool: Konnektor zum Ticketsystem (lesen) | Kategorie, Priorität, Entwurf |
| **C · Monitoring** | „Ist alles grün?" + **Alarm ohne Frage** | Power-Automate-Flow (ohne KI) alle 15 min → Teams-Kanal; Agent-Tool „Lage abfragen" | nur Zusammenfassung |

**Goldene Regel:** Alarmieren macht der Flow (billig, zuverlässig). Die KI erklärt und formuliert.
Der Agent liest nur, er ändert nichts (v1).

---

## 1. Jetzt sofort (vor dem 15.10.): Übungsumgebung, privat

Ziel: Die Handgriffe in Copilot Studio beherrschen, **bevor** ich im EMVIA-Tenant etwas anfasse.
Dort wird nichts gebaut, solange die IT-Leitung nicht zugestimmt hat.

1. **Test-Tenant beschaffen** (eine der Optionen, Kosten vor Abschluss prüfen):
   - eigener kleiner M365-Tenant (z. B. Business-Basic-Testversion) mit Arbeitskonto, oder
   - Microsoft-365-Entwicklerprogramm, falls ich berechtigt bin (Zugang ist eingeschränkt worden).
2. **Copilot-Studio-Testversion** mit diesem Arbeitskonto starten: `https://copilotstudio.microsoft.com`
   (Testphase für Copilot Studio, kein privates Microsoft-Konto möglich).
3. **Übungsdaten** aus diesem Ordner verwenden (nur erfundene Daten):
   - `Uebung/tickets-beispiel.csv` → als SharePoint-Liste „Tickets" importieren (simuliert das Ticketsystem)
   - die 8 Hilfeartikel aus `../EMVIA-Helpdesk-Agent/Wissen/docx/` + 2–3 eigene Runbooks → SharePoint-Seite „IT-Wissen"
4. Den Agenten nach Abschnitt 2 komplett einmal durchbauen. Zeitbedarf realistisch: 2–3 Abende.

**Lernziel:** Wissensquelle, Tool mit Konnektor, Agent-Flow, Teams-Kanal, Testbereich, Analysen.

---

## 2. Bau in Copilot Studio — Schritt für Schritt

> Menübezeichnungen ändern sich bei Microsoft häufig. Wenn ein Punkt anders heißt:
> sinngemäß suchen oder Microsoft Learn „Copilot Studio" prüfen.

### Schritt 1 · Umgebung (Power Platform Admin Center)
- Neue Umgebung **„IT-Agenten"** (Typ Sandbox für Test, später Produktion) — nicht die Standardumgebung.
- **DLP-Richtlinie** für diese Umgebung: nur benötigte Konnektoren erlaubt (SharePoint, Teams,
  Office 365 Outlook, Ticketsystem-Konnektor, HTTP mit Entra ID). Alles andere blockiert.
- Zugriff auf die Umgebung: nur Sicherheitsgruppe **„IT-Team"**.

### Schritt 2 · Agent anlegen
- *Erstellen → Neuer Agent* → Name **„IT-Leitstand"**, Sprache **Deutsch**.
- **Anweisungen:** Text „Admin-Cockpit" aus [[Agenten-Anweisungen]] einfügen, gekürzt auf die drei
  Fähigkeiten A/B/C, plus Ticket-Regeln aus „1 · Ticket-Assistent" (Kategorien, P1–P4).
- **Generative Orchestrierung** einschalten (der Agent wählt selbst Wissen oder Tool).
- **Authentifizierung:** „Mit Microsoft authentifizieren" — damit gelten die Rechte des fragenden
  Nutzers, z. B. bei SharePoint-Wissen.

### Schritt 3 · Fähigkeit A — Wiki
- *Wissen → Hinzufügen → SharePoint* → URL der Seite/Bibliothek „IT-Wissen".
- Optional: Websuche **aus** (Antworten nur aus eigenem Wissen = nachvollziehbar).
- Inhalt des Wikis: kurze Runbooks im Muster *Symptom → Ursache → Lösung → Prüfen*. Ein Thema pro Datei.
- **Test:** 10 Fragen aus `../EMVIA-Helpdesk-Agent/Testfragen.md` im Testbereich — antwortet er mit Quelle?
  Sagt er „weiß ich nicht", wenn nichts im Wiki steht?

### Schritt 4 · Fähigkeit B — Ticket (nur lesen)
- *Tools → Hinzufügen → Konnektor*:
  - Übung: **SharePoint „Elemente abrufen"** auf die Liste „Tickets".
  - EMVIA: Konnektor des echten Ticketsystems (Produkt in Woche 1 klären; viele haben fertige
    Konnektoren, sonst Outlook-Konnektor auf das IT-Postfach oder REST-API als eigener Konnektor).
- Beschreibung des Tools klar formulieren, z. B. *„Liest ein Ticket anhand der Ticketnummer. Nur lesen."*
  (die Orchestrierung entscheidet anhand dieser Beschreibung).
- Nur Lese-Aktionen hinzufügen. **Keine** Aktion „Ticket aktualisieren/schließen".
- **Test:** „Fasse Ticket 1003 zusammen" → Kategorie, Priorität mit Begründung, Rückfragen, Antwortentwurf.
  „Gibt es Häufungen heute?" → erkennt er die 3 WLAN-Tickets aus Haus Nord als „Verdacht auf Störung"?

### Schritt 5 · Fähigkeit C — proaktives Monitoring
**5a · Flow ohne KI (Power Automate), alle 15 min:**
1. Auslöser *Wiederholung* (15 min).
2. **M365-Dienststatus:** HTTP-Aufruf Microsoft Graph `GET /admin/serviceAnnouncement/healthOverviews`
   (Berechtigung `ServiceHealth.Read.All`, eigene App-Registrierung, Zertifikat statt Kennwort).
3. **Fachanwendungen:** je Anwendung HTTP-GET auf die Web-Adresse → Statuscode + Antwortzeit.
4. **Ticket-Häufung:** Tickets der letzten 30 min nach Kategorie/Standort zählen, ≥ 3 → Auffälligkeit.
5. Nur **wenn etwas auffällig ist** → Nachricht (adaptive Karte) in Teams-Kanal „IT-Leitstand".
   Sonst nichts senden (spart Nerven und Credits).
6. Ergebnis zusätzlich in SharePoint-Liste „Lage" schreiben (Zeit, Quelle, Status, Text).

**5b · Morgenbericht 07:00:** zweiter Flow liest „Lage" + offene P1/P2-Tickets → ruft den Agenten /
eine KI-Aktion zum Zusammenfassen auf → Ampelbericht (Rot/Gelb/Grün) in den Kanal.

**5c · Agent-Tool „Lage abfragen":** Agent-Flow, der die letzten Einträge aus „Lage" zurückgibt →
auf „Ist alles grün?" antwortet der Agent mit Ampel + nächstem Schritt.

**Erste Ablaufüberwachung (Pflicht, sobald Zugriff besteht):** Apple-MDM-Push-Zertifikat,
ABM/VPP-Token, Ablauf von App-Secrets/Zertifikaten in Entra → Warnung bei < 30 / < 7 Tagen.

### Schritt 6 · Veröffentlichen in Teams (nur IT-Team)
- *Kanäle → Teams und Microsoft 365 Copilot* → Verfügbarkeit nur für Sicherheitsgruppe „IT-Team".
- Begrüßungstext mit Hinweis: **„Ich bin ein KI-Assistent. Ich lese nur und mache Vorschläge."**

### Schritt 7 · Messen
- *Analysen* in Copilot Studio: Sitzungen, gelöste Fragen, Eskalationen, Verbrauch an Credits.
- Eigene Tabelle (siehe Abschnitt 5) wöchentlich füllen.

---

## 3. Fahrplan bei EMVIA (passt zu Phase 0–3 im Gesamtplan)

| Woche | Was | Ergebnis |
|---|---|---|
| 1–2 (ab 15.10.) | Ankommen, [[Infosammlung-Woche-1]]: Ticketsystem, MDM, Lizenzen (Copilot Studio vorhanden?), Fachanwendungen, Ansprechpartner Datenschutz/Betriebsrat | Systemlandkarte, Schmerzpunkte |
| 3–4 | **Ohne KI:** Monitoring-Flow 5a + Ablaufüberwachung + Wiki „IT-Wissen" anfangen (mit Einverständnis der IT-Leitung) | erster sichtbarer Nutzen ohne Zusatzkosten |
| 5 | Pitch (3 Sätze im Gesamtplan) + Datenschutz-Check (Abschnitt 4) | Freigabe für Pilot |
| 6–9 | Agent „IT-Leitstand" mit A + B + C nur für IT-Team | Messwerte |
| 10+ | Auswertung → Ausbau: Helpdesk für Mitarbeitende, Orchestrator, JML | Referenz |

**Probezeit-Regel:** Im ersten Monat zuerst zuhören und den Alltag lernen. Die Idee bringe ich
erst, wenn ich die echten Schmerzpunkte kenne — dann passt der Pitch zu EMVIA, nicht zu meinem Plan.

---

## 4. „Rechte und Datenschutz sauber gelöst" — die Checkliste (das ist die Referenz!)

| # | Punkt | Nachweis |
|---|---|---|
| R1 | Eigene Umgebung „IT-Agenten" mit DLP-Richtlinie | Screenshot DLP |
| R2 | Agent nur für Sicherheitsgruppe „IT-Team" freigegeben | Kanal-Einstellung |
| R3 | Authentifizierung über Microsoft; Wissen respektiert SharePoint-Rechte | Test mit Nutzer ohne Recht |
| R4 | Eigene App-Registrierung, nur Leserechte (`ServiceHealth.Read.All`, …), Zertifikat, Ablauf überwacht | Entra-Bericht |
| R5 | Agent hat **keine** schreibenden Aktionen | Tool-Liste |
| R6 | Keine Personal-/Bewohnerdaten (Art. 9 DSGVO) in Wissen, Tickets für KI oder Prompts | Anweisung + Stichprobe |
| R7 | Datenschutzbeauftragte/r informiert, Eintrag im Verzeichnis der Verarbeitungstätigkeiten | VVT-Eintrag |
| R8 | Betriebsrat eingebunden, Zweck schriftlich: „IT-Betrieb, keine Leistungskontrolle" | Protokoll/Vereinbarung |
| R9 | Transparenz: Nutzer sehen, dass es eine KI ist (EU-KI-Verordnung) | Begrüßungstext |
| R10 | Aufbewahrung der Gesprächsprotokolle festgelegt, Datenresidenz der Umgebung geprüft | Admin-Center |
| R11 | Kosten: Budget-Alarm, Verbrauch je Monat dokumentiert | Analysen |

---

## 5. Messwerte für die Referenz

| Kennzahl | Vorher (Woche 1–4 messen!) | Nach Pilot |
|---|---|---|
| Erstreaktionszeit Tickets | | |
| Störungen erkannt, bevor jemand anruft | | |
| Zeit für Morgen-Lagebild | | |
| Antworten aus dem Wiki mit richtiger Quelle (Testfragen) | | |
| Copilot Credits / Monat | | |

**Ohne Vorher-Werte keine Referenz.** Deshalb in Woche 1–4 schon still mitzählen.

**Referenz-Text (später, nur mit Erlaubnis von EMVIA und ohne interne Details):**
> „KI-Assistent für den IT-Betrieb eines Pflegeunternehmens (ca. 55 Standorte) mit Copilot Studio
> eingeführt: Ticket-Vorsortierung, Wiki-Antworten mit Quellen, proaktive Störungswarnung.
> Least-Privilege-Berechtigungen, eigene Umgebung mit DLP, Datenschutz und Betriebsrat eingebunden.
> Ergebnis: Erstreaktion −X %, Y Störungen vor dem ersten Anruf erkannt."

---

## 6. Typische Stolperfallen

- **Agent erfindet Antworten** → Websuche aus, Anweisung „wenn nicht im Wissen: sagen, dass du es nicht weißt".
- **Tool wird nicht genutzt** → Tool-Beschreibung präziser schreiben, Beispielfragen im Testbereich prüfen.
- **Kosten steigen** → zeitgesteuerte KI-Ausführungen sind teuer; Flows filtern vorher, KI nur bei Auffälligkeit.
- **Lizenz fehlt** → Copilot Studio, Premium-Konnektoren (HTTP mit Entra ID) und Teams-Veröffentlichung
  vorab mit der IT-Leitung/Lizenzverwaltung klären.
- **Zu viel auf einmal** → erst A (Wiki), dann B (Ticket), dann C (Monitoring). Jede Stufe einzeln testen.
