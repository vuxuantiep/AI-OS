---
titel: Informationssammlung EMVIA – Woche 1 (Ergänzung zur Werkbank-Fragenliste)
start: 2026-10-15
tags: [emvia, onboarding, checkliste]
---

# Informationssammlung Woche 1 – was die KI-Assistenten brauchen

Die Grundfragen (Zugang, Identität, Lizenzen, Exchange, MDM, Betrieb) stehen in der Werkbank-Vorlage
**`emvia-doku-erste-woche`**. Diese Liste ergänzt nur, was für [[Project_EMVIA-KI-Assistenten]]
zusätzlich nötig ist. Antworten → Werkbank-Steckbrief `emvia-steckbrief` (keine Passwörter,
keine Personal-/Bewohnerdaten).

**Grundsatz:** Woche 1–2 nur lesen, fragen, dokumentieren. Nichts ändern, nichts bauen.

## 1. rexx systems (HR)
- [ ] Welche rexx-Module sind im Einsatz (Personalakte, Recruiting, Mitarbeiter-Self-Service, Zeitwirtschaft)?
- [ ] Wie erfährt die IT heute von Ein-/Austritten/Wechseln? (Mail, Formular, Ticket, rexx-Workflow?) Vorlaufzeit?
- [ ] Gibt es eine Schnittstelle rexx → Entra ID / Active Directory (SCIM, REST-API, CSV-Export, LDAP)? Wer betreut rexx (HR intern, rexx-Support)?
- [ ] Welche Felder sind zuverlässig gepflegt: Personalnummer, Einrichtung/Kostenstelle, Funktion, Eintritt, Austritt, Vorgesetzte:r?
- [ ] Meldet sich jemand per SSO (Entra) an rexx an? → Enterprise-App in Entra prüfen
- [ ] Ansprechpartner:in HR für einen späteren Pilot „automatischer Eintritt“

## 2. Ticketsystem
- [ ] Produkt + Version, Cloud oder On-Premises? Gibt es eine API / einen Power-Automate-Konnektor?
- [ ] Eingangskanäle (Mail, Portal, Telefon) — welches Postfach?
- [ ] Kategorien, Prioritäten, SLAs vorhanden? Wer ist 1st/2nd Level, welche Dienstleister?
- [ ] Ticketvolumen pro Woche, Top-10-Themen der letzten 3 Monate (Export/Bericht)
- [ ] Wissensdatenbank im Ticketsystem? Wo liegen Anleitungen heute?

## 3. MDM
- [ ] Produkt (Intune / anderes), Plattformen und Stückzahlen (Windows, iPad, iPhone, Android)
- [ ] Apple: ABM/ASM, **Ablaufdatum Apple-MDM-Push-Zertifikat**, VPP-/DEP-Token — wer hat die Apple-ID dazu?
- [ ] Android: Zero-Touch / Knox, Dedicated Devices (Kiosk) für Pflege-Tablets?
- [ ] Ablauf bei Verlust/Diebstahl, wer darf Wipe auslösen?

## 4. Fachanwendungen und Dienste (für Verfügbarkeits-Monitoring)
Für jede Anwendung: Name, Zweck, Hersteller, Cloud/On-Prem, URL/Server, Anmeldung (SSO?),
Ansprechpartner/Support-Hotline, kritisch ja/nein, Wartungsfenster.
- [ ] Pflegedokumentation
- [ ] Dienstplanung / Zeiterfassung
- [ ] Abrechnung / Bewohnerverwaltung
- [ ] rexx (HR)
- [ ] Finanzbuchhaltung / ERP
- [ ] Telefonie, Schwesternruf-Anbindung, WLAN, Drucker/Scanner
- [ ] Gibt es schon ein Monitoring (PRTG, Zabbix, Checkmk, Azure Monitor)? Wer bekommt Alarme?

## 5. Copilot, Power Platform, Sicherheit
- [ ] Habe ich (bzw. das IT-Team) eine **Microsoft-365-Copilot-Lizenz**? Wer sonst?
- [ ] Copilot Studio / Power Platform: Wer ist Admin, welche Umgebungen gibt es, DLP-Richtlinien, gibt es schon Agenten oder Flows?
- [ ] Ist Pay-as-you-go-Abrechnung in Azure möglich (Abonnement, Kostenstelle)?
- [ ] Lizenzstufe Sicherheit: Business Premium / E3 / E5? Defender XDR? Security Copilot? Log Analytics Workspace vorhanden?
- [ ] Datenschutzbeauftragte:r, Betriebsrat: bestehende Vereinbarungen zu IT/KI/Protokollierung?

## 6. Kommunikation
- [ ] Wie werden Störungen heute an die Einrichtungen gemeldet (Mail-Verteiler, Teams, Intranet, Telefon)?
- [ ] Gibt es Vorlagen/Corporate Wording, Signatur, Du/Sie-Kultur?
- [ ] Welche Sprachen spricht die Belegschaft häufig (für einfache Sprache/Übersetzung)?

## Ergebnis Ende Woche 2
1. Steckbrief ausgefüllt
2. Systemlandkarte (Anwendungen + Abhängigkeiten) → Diagramm in Werkbank/SharePoint
3. Liste „Top-5-Schmerzpunkte“ mit Zeitaufwand → Grundlage für Phase 1 (Quick Wins)
