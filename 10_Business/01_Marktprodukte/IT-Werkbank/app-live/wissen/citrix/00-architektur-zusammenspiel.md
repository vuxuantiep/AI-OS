# Citrix mit Windows Server 2022: Architektur und Zusammenspiel

Citrix Virtual Apps and Desktops (CVAD) stellt Anwendungen und Desktops zentral bereit. Die Programme laufen auf dem Server. Zum Endgerät gehen nur Bild und Ton, zurück kommen Tastatur und Maus. Windows Server 2022 hat dabei zwei Aufgaben:

- **Infrastruktur-Server:** trägt Delivery Controller, StoreFront, Lizenzserver und Director.
- **Sitzungs-Host:** trägt den Citrix VDA und die Sitzungen der Anwender (Multi-Session über die Rolle RDSH).

![Citrix auf Windows Server 2022: Architektur in fünf Bereichen](citrix-architektur.svg)

## Die Bausteine in einem Satz
- **Workspace App:** Client auf dem Endgerät, baut die Verbindung auf.
- **Citrix Gateway (NetScaler):** sicherer Zugang von außen, meist mit MFA.
- **StoreFront:** zeigt dem Anwender seine Apps und Desktops.
- **Delivery Controller:** vermittelt die Sitzung und kennt den Zustand aller Server.
- **Site-Datenbank (SQL Server):** hält die Konfiguration der Site.
- **Lizenzserver:** vergibt die Citrix-Lizenzen.
- **VDA (Virtual Delivery Agent):** Citrix-Software auf dem Sitzungs-Host. Er registriert den Server beim Controller und überträgt die Sitzung per HDX/ICA.

## Was macht Windows, was macht Citrix?
Citrix ersetzt Windows nicht, sondern setzt darauf auf. Windows liefert Anmeldung, Sitzungen, Dienste und Sicherheit. Citrix liefert Vermittlung, Protokoll, Verwaltung im großen Maßstab und Überwachung.

![Schichtmodell eines Sitzungs-Hosts und die drei nötigen Lizenzen](citrix-zusammenspiel.svg)

Merksatz für die Fehlersuche: **von unten nach oben prüfen**. Ist die VM, das Netz oder der Windows-Dienst gestört, hilft keine Citrix-Einstellung.

## Warum die Rolle RDSH nötig ist
Erst die Rolle Remote Desktop Session Host erlaubt mehrere Sitzungen auf einem Windows Server. Der VDA-Installer für Multi-Session kann sie mit einrichten; prüfe sie trotzdem im Server-Manager. Für jede Sitzung braucht man zusätzlich zur Citrix-Lizenz eine Microsoft RDS CAL.

## Was Windows Server 2022 beiträgt
- TLS 1.3 ist ab Werk aktiv. Das stärkt die Verbindungen zwischen den Komponenten, wenn sie per TLS abgesichert sind.
- Secured-core Server hängt von Hardware und Firmware ab. Bei VMs greift nur ein Teil davon, also im konkreten Fall prüfen statt annehmen.
- Windows Admin Center hilft bei der Serververwaltung. Es ersetzt weder Studio noch Director.

## Wie startet eine Sitzung?

![Acht Schritte vom Klick bis zur fertigen Sitzung](citrix-sitzungsablauf.svg)

Die Schritte zeigen, wo man sucht:

| Symptom | Bereich | Zuerst prüfen |
|---|---|---|
| Anmeldeseite kommt nicht | Schritt 1–2 | Gateway, Zertifikat, Internet |
| Apps fehlen nach der Anmeldung | Schritt 3–4 | Gruppenmitgliedschaft, Bereitstellungsgruppe |
| Klick auf App bewirkt nichts | Schritt 5–6 | Server im Wartungsmodus oder Unregistered, Auslastung |
| Verbindung bricht beim Aufbau ab | Schritt 7 | Ports 1494, 2598, Firewall |
| Anmeldung dauert sehr lange | Schritt 8 | GPO, Profil, Skripte (Director) |

## Netzwerk-Ports (Standard)
| Verbindung | Port |
|---|---|
| Endgerät zu StoreFront oder Gateway | 443 |
| Endgerät zu VDA (HDX/ICA) | 1494, mit Session Reliability 2598; bei EDT zusätzlich UDP |
| VDA zu Controller | 80 oder 443 |
| Controller zu Lizenzserver | 27000, 7279, Web Services 8083 |
| Controller zu SQL Server | 1433 (Standardinstanz) |

Maßgeblich ist die aktuelle Port-Übersicht von Citrix und das eigene Firewall-Konzept.

Quellen: [Citrix Systemanforderungen](https://docs.citrix.com/en-us/citrix-virtual-apps-desktops/system-requirements.html), [Citrix-Kommunikationsports](https://docs.citrix.com/en-us/tech-zone/build/tech-papers/citrix-communication-ports.html)
