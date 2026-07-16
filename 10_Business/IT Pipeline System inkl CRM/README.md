# IT Pipeline System inkl. CRM — „LeadPilot"

> Eigenes schlankes Lead-CRM + Lead-Radar für das IT-Freelancer-Business.
> Self-contained Modul für **AI-OS und Trace-AI OS** (siehe [app/INSTALL.md](app/INSTALL.md)).
> Konzept-Review: [Plannung/Konzept-Pruefung.md](Plannung/Konzept-Pruefung.md) ·
> Wirtschaftlichkeit: [wirtschaftlichkeit-it-pipeline-crm.md](wirtschaftlichkeit-it-pipeline-crm.md) (freigegeben 16.07.2026)

## Was es kann (Phase A)

| Bereich | Funktion |
|---|---|
| **Lead-Erfassung** | Webhooks für Website-Kontaktformular, eingebaute Terminbuchung, manuell, Radar-Übernahme — Dedup per E-Mail (Cal.com-Webhook wird weiter unterstützt, ist aber nicht mehr nötig) |
| **📅 Eigene Terminbuchung** | Cal.com-Ersatz ohne Fremdabhängigkeit: öffentliche Buchungsseite `/buchen` (per iframe auf vuxuantiep.de einbettbar, Snippet in den Einstellungen), konfigurierbare Slots (Wochentage/Zeiten/Vorlauf), Kollisionsprüfung, Terminbestätigungs-Mail, **ICS-Kalender-Feed** `/api/termine.ics` zum Abonnieren in Thunderbird/Outlook/Google |
| **Pipeline** | Kanban: Neu → Qualifiziert → Erstgespräch → Angebot → Gewonnen/Verloren (Drag & Drop), Pipeline-Wert |
| **F3: Trigger-Mails** | Mail 1 = sofortige Eingangsbestätigung bei JEDEM Lead · Mail 2 = genau EINE Buchungs-Erinnerung (systemseitig begrenzt — kein Drip, §7 UWG) · Postausgang-Ansicht, funktioniert auch ohne SMTP |
| **F2: DSGVO** | Export je Lead (Art. 15), Löschen (Art. 17), Anonymisieren, automatisches Löschkonzept für verlorene Leads (Frist konfigurierbar), Verlaufs-Protokoll |
| **Lead-Radar** | Scannt öffentliche Projektbörsen (RemoteOK, WeWorkRemotely, Remotive-API + eigene Feeds) nach Keyword-Relevanz, 1 Klick → Lead in Pipeline |
| **Einstellungen** | Mail-Templates, Buchungs-Regeln, Keywords, eigene Radar-Quellen, DSGVO-Frist — alles in der UI |
| **Design** | Helles Corporate-Theme (Standard, angelehnt an Trace-AI OS/CorporateLLM) + Dunkel-Umschalter in der Sidebar |

Start: `python app/app.py` → http://localhost:5330 · im AI-OS: Produktion-Tab oder `/produkte/it-pipeline/`

## Bewusste Entscheidungen

- **Eigenes CRM statt EspoCRM** (liegt als Referenz unter `Plannung/EspoCRM-10.0.2/`):
  EspoCRM braucht PHP + MySQL und bringt 90 % Funktionen mit, die hier nicht
  gebraucht werden. Das eigene Modul ist exakt zugeschnitten, self-hosted und
  in beide Plattformen kopierbar. Wechsel-Pfad bleibt offen, falls Anforderungen wachsen.
- **Radar scannt Projektbörsen, keine Personendaten:** „Relevanteste Kunden aus
  dem Netz" heißt hier: öffentlich ausgeschriebene Projekte/Aufträge, die zu den
  eigenen Skills passen — nicht das Scrapen privater Kontaktdaten (DSGVO) und
  keine automatisierte Kaltakquise-Mails (§7 UWG). Deutsche Börsen (freelancermap
  etc.) als eigene Feed-Quellen in den Einstellungen ergänzbar.

## Phase B (Gate: erst nach 4 Wochen Echtbetrieb + Nutzen-Nachweis)

Produktisierung als Done-for-you-Angebot: Setup-Checkliste, Kunden-Templates,
Angebotsseite mit Paketpreis (siehe Wirtschaftlichkeitsprüfung, Auflage B1).

#it-pipeline #crm #leadpilot #wichtig
