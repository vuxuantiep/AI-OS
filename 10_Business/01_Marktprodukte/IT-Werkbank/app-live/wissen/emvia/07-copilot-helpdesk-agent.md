# Projekt: IT-Helpdesk-Agent mit Copilot Studio (Bauanleitung)

## Was soll der Agent können (v1)?
Er beantwortet IT-Standardfragen der Mitarbeitenden in Teams rund um die Uhr: Kennwort vergessen, Authenticator/MFA einrichten, neues Handy, verdächtige Mail, Outlook, Teams, Dienst-Tablet. Er antwortet nur aus geprüften Hilfeartikeln. Alles andere leitet er an die IT weiter (Ticket/Telefon).
Er ändert nichts an Konten, fragt nie nach Kennwörtern und hat keinen Zugriff auf Bewohner- oder Personaldaten.

## Was muss ich vorher klären?
- Freigabe durch die IT-Leitung, Datenschutz informieren, ggf. Betriebsrat (KI für Mitarbeitende, Gesprächsprotokolle).
- Kosten: Mitarbeitende ohne M365-Copilot-Lizenz verbrauchen bei jeder Agent-Nutzung Copilot Credits (Pay-as-you-go oder Credit-Packs). Pay-as-you-go mit Budget-Alarm einrichten und im Pilot den echten Verbrauch je Gespräch messen. Aktuelle Preise auf der Microsoft-Lizenzseite prüfen.
- Ist das Veröffentlichen von Agenten in Teams erlaubt (Teams Admin Center, Power Platform Admin Center)?
- Kontaktdaten der IT, Notfallnummer, Ticket-Mailadresse, ist SSPR aktiv?

## Wie baue ich ihn auf?
1. SharePoint-Website „IT-Hilfe“ mit Bibliothek „Artikel“. Nur die IT darf schreiben. Die Hilfeartikel als Word-Dateien hochladen, vorher die gelb markierten Platzhalter ersetzen.
2. https://copilotstudio.microsoft.com > eigene Umgebung (nicht Standard) > Neuer Agent „IT-Hilfe EMVIA“, Sprache Deutsch.
3. Anweisungen einfügen (Datei Agent-Anweisungen im Projektordner).
4. Wissen: SharePoint-Bibliothek hinzufügen. Websuche bzw. allgemeines Wissen ausschalten, nur eigene Quellen. Warten, bis alle Quellen „Bereit“ zeigen.
5. Themen anlegen: Notfall (Gerät verloren/Hackerverdacht), IT kontaktieren/Ticket, Mit Mensch sprechen. Das System-Thema „Eskalieren“ auf Ticket umleiten.
6. Authentifizierung: mit Microsoft (nur Mitarbeitende).
7. Mit den 18 Testfragen testen. Ziel: mindestens 80 % richtig und null Fehler bei Sicherheitsfragen.
8. In Teams und Microsoft 365 veröffentlichen, zuerst nur für eine Pilotgruppe (Sicherheitsgruppe).
9. Nach dem Veröffentlichen prüfen, ob die Wissensquellen im veröffentlichten Agenten auf „Bereit“ stehen. Jede Änderung neu veröffentlichen.

## Wie läuft der Pilot?
2–3 Wochen in einer Einrichtung mit 10–20 Personen. Danach Analysen auswerten: häufigste und unbeantwortete Fragen, Eskalationen, verbrauchte Credits. Neue Artikel für die Lücken schreiben, dann stufenweise ausrollen (Info-Mail, Aushang mit QR-Code).

## Wo liegen die Projektdateien?
Im AI-OS-Vault unter 00_Wissen/03_Aktuelles/Active/EMVIA-Helpdesk-Agent: Projektplan, Agent-Anweisungen, Themen, Testfragen, Hilfeartikel (Markdown und Word).
