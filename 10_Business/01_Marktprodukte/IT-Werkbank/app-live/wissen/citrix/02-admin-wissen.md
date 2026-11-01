# Citrix-Admin: Was man sicher können muss

## Täglicher Rundgang im Director
1. **Dashboard:** fehlgeschlagene Verbindungen, fehlerhafte Maschinen, Lizenzstatus.
2. **Trends:** Anmeldedauer und Sitzungen im Vergleich zu gestern.
3. **Filter > Maschinen:** Server mit dauerhaft hoher CPU- oder RAM-Last, nicht registrierte Server.
4. Auffälligkeit dokumentieren, bevor sie weg ist: Server, Uhrzeit, Benutzer, Fehlertext.

## Einem Anwender helfen (Director)
- **Benutzer suchen:** Name eingeben, offene Sitzung öffnen.
- **Spiegeln (Shadowing):** Der Anwender sieht einen Hinweis und muss zustimmen. Bei Gesundheits- oder Personaldaten vorher klären, was sichtbar sein darf.
- **Prozess beenden:** hängende Anwendung gezielt schließen.
- **Abmelden oder trennen:** Abmelden beendet alles und kann ungesicherte Arbeit kosten. Vorher fragen.

## Anmeldezeit lesen
Director zerlegt die Anmeldedauer in Phasen. Die längste Phase zeigt die Richtung:

| Phase | Lang bedeutet meist | Maßnahme |
|---|---|---|
| Brokering | Controller oder Datenbank langsam | Controller prüfen |
| VM-Start | Server war aus | Neustartplan, Reserve an Servern |
| HDX-Verbindung | Netz oder Ports | Leitung, Firewall |
| Authentifizierung | DC langsam oder DNS falsch | DC-Erreichbarkeit |
| GPOs | zu viele oder langsame Richtlinien | gpresult lesen, aufräumen |
| Anmeldeskripte | Skripte warten auf Netzlaufwerke | Skripte verkürzen |
| Profil laden | Fileserver langsam oder Container groß | FSLogix und Fileserver prüfen |
| Interaktive Sitzung | Autostarts, Shell | Autostarts reduzieren |

## FSLogix-Profile
Anwender melden sich jedes Mal an einem anderen Server an. Deshalb liegt das Profil als VHDX-Container auf einem Fileserver und wird beim Anmelden eingehängt. Für den Anwender sieht es wie ein lokales Profil aus.

Typische Störungen:
- **Temporäres Profil:** Fileserver nicht erreichbar, Rechte falsch oder Container noch an einer anderen Sitzung angehängt.
- **Speicher voll:** Container hat die Maximalgröße erreicht oder der Fileserver ist voll.
- **Langsame Anmeldung:** Fileserver überlastet oder Virenscanner prüft VHDX-Dateien. Ausnahmen laut Hersteller setzen.

Protokolle: `C:\ProgramData\FSLogix\Logs`. Prüfwerkzeug auf dem Server: `frx list-redirects`.

## Windows Server 2022 für Multi-User optimieren
- Citrix Optimizer als Grundlage nutzen, nicht jede Einstellung blind übernehmen.
- Per GPO: visuelle Effekte reduzieren, OneDrive-Autostart nur dort, wo gebraucht, Hintergrunddienste einzelner Anwendungen deaktivieren.
- Virenschutz: Ausnahmen für Citrix und FSLogix nach Herstellerliste.
- RAM und CPU je Benutzer im Echtbetrieb messen, statt zu schätzen.

## Lizenzen
| Lizenz | Wofür | Wo sichtbar |
|---|---|---|
| Windows Server + CAL | Betriebssystem und Zugriff | Microsoft-Vertrag |
| RDS CAL | jede RDSH-Sitzung | RDS-Lizenzserver |
| Citrix | Citrix-Nutzung, Modell laut Vertrag | Citrix-Lizenzserver, Director |

Der RDS-Lizenzserver wird auf den Sitzungs-Hosts per GPO hinterlegt. Fehlt er, greift nach der Karenzzeit eine Sperre neuer Sitzungen.

## Golden Rules
- Immer zuerst die Infrastruktur prüfen, dann die Anwendung.
- Keine Änderung am Klon, nur am Image.
- Wartungsmodus vor Arbeiten, Rückweg vor Änderungen.
- Änderungen an Richtlinien und GPOs nach dem Change-Verfahren des Betriebs.
- Zu jeder Eskalation: Server, Uhrzeit, Benutzer, genauer Fehlertext.
