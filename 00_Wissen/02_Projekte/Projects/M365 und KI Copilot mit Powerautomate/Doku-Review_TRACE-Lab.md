# Doku-Review: TRACE Enterprise Lab

Durchsicht vom 14.11.2026. Ergebnis ist der Plan [[Project_TRACE-Enterprise-Lab]].

## Was im Ordner lag

| Datei | Inhalt | Bewertung |
|---|---|---|
| OneNote-Seite „IT Architektur M365 und KI" | Architekturbild, Zusammenspiel Copilot Studio / Power Automate / Zammad, 10-Schritte-Anleitung (4 Wochen) | guter Kern für die Helpdesk-Automatisierung, aber zu optimistisch im Zeitplan |
| OneNote-Seite „TRACE Enterprise Lab" | zwei aufeinanderfolgende Entwürfe: großer Entwurf (64 GB, 6 Phasen, Citrix/Omnissa) und 3-Monats-Bauplan (32 GB, 12 Wochen) | inhaltlich solide, aber beide Entwürfe stehen unaufgelöst untereinander |
| `Windows_11_und_Smartphone_Checkliste_Druckversion.docx` | Tastenkürzel-Spickzettel | **gehört nicht zum Projekt** – nicht verschoben, Vorschlag: nach `00_Wissen/04_Referenzen/` |

Das OneNote-Notizbuch wurde **nicht verändert**.

## Widersprüche in den Notizen und wie sie aufgelöst wurden

| Thema | Stand in den Notizen | Jetzt |
|---|---|---|
| Arbeitsspeicher | einmal 64 GB „16/32 sind zu wenig", einmal Plan für 32 GB | 32 GB für den Kern, 64 GB nur für Ausbaustufe VDI |
| Domänenname | `trace.lab` im Netzplan, `TRACE.LOCAL` in der Übung | Subdomain einer eigenen Domain (`lab.<eigene-domain>`) |
| Server-Version | Überschrift „Windows Server 2025", Text durchgehend 2022 | 2022, 2025 als Ausbaustufe |
| Umfang | Citrix/Omnissa/Wazuh erst als Ziel genannt, dann gestrichen | klar als Ausbaustufen B–D |
| Automatisierung | Seite 1: Power Automate + Copilot Studio; Seite 2: n8n + KI-Agent | Power Automate/Copilot Studio im Kern, anderes als Ausbaustufe |
| Zeitplan | 4 Wochen (Seite 1) vs. 12 Wochen ohne Zammad (Seite 2) | ein Plan, 10 Phasen, rund 15 Wochen |
| Zwei Projekte | Zammad-Helpdesk und TRACE Lab standen unverbunden nebeneinander | Helpdesk ist Phase 8 des einen Labs |
| Lizenzquelle | Seite 1 empfiehlt Developer Program als Standard, Seite 2 sagt „nur für Berechtigte" | Business-Premium-Testversion als Standard, Developer Program nur prüfen |

## Fachliche Lücken, die ergänzt wurden

1. **Erreichbarkeit:** Power Automate (Cloud) kann eine Zammad-Adresse im privaten Lab-Netz nicht aufrufen. Die Notiz nennt `http://<Zammad-IP>` – das funktioniert so nicht. Ergänzt: HTTPS-Tunnel oder Datengateway.
2. **Premium-Konnektor:** die HTTP-Aktion in Power Automate ist lizenzpflichtig.
3. **Notfall-Adminkonto** fehlte vor dem Schritt „Conditional Access einrichten".
4. **Conditional Access direkt scharf schalten** stand in Schritt 2 der Anleitung, also bevor ein Gerät überhaupt konform sein kann. Jetzt Phase 6, zuerst im Berichtsmodus.
5. **Entra Connect Sync** hatte keine eigene VM im RAM-Plan („separater Server" ohne Ressourcen). Jetzt auf LAB-SRV01.
6. **Zammad-VM mit 4 GB** ist zu knapp. Jetzt 6 GB, eigene Zeile im RAM-Plan.
7. **Testlizenz-Uhren:** die Notiz startet den Tenant in Woche 1. Jetzt erst nach dem lokalen Aufbau, Copilot Studio erst in Phase 8.
8. **Autonomer Ticket-Abschluss (Fall C)** hatte keinen Freigabeschritt. Jetzt Pflicht, mit fester Aktionsliste.
9. **Abnahmekriterien** gab es nur für Woche 1. Jetzt für jede Phase.
10. **Referenz-Gedanke** (Runbooks, festes Schema, Ordnerstruktur) fehlte ganz.

## Aufgeräumt

- Rückfragen und Angebote aus dem Chat-Verlauf („Möchtest du, dass ich …") entfernt.
- Fremde Bildunterschriften und Linktitel ohne Bezug entfernt.
- Doppelte Abschnitte (Projektvorschlag, Zieltechnologien standen zweimal) zusammengeführt.
- Unklarer Begriff „Euro-Office" durch neutrale „Win32-App" ersetzt – bitte ergänzen, welche Anwendung gemeint war.
- Auswahlfragen zur Hardware als „Offene Punkte" in den Plan übernommen.
