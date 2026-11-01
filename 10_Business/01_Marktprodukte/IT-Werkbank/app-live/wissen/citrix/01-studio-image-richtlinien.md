# Citrix Studio: Kataloge, Gruppen, Richtlinien und Image

Citrix Studio (in neueren Versionen Web Studio) ist die zentrale Verwaltung einer Site. Die Grundlogik passt auf ein Bild:

![Vom Golden Image über Katalog und Bereitstellungsgruppe zum Benutzer, dazu der Ablauf eines Image-Updates](citrix-studio-objekte.svg)

## Die vier Grundbegriffe
- **Golden Image:** eine vorbereitete Windows-Server-2022-VM mit VDA und Anwendungen. Alle Sitzungs-Hosts sind Kopien davon.
- **Maschinenkatalog:** eine Sammlung gleicher Server. Hier wählst du Betriebssystem-Typ (Multi-Session) und Klonverfahren.
- **Bereitstellungsgruppe:** verbindet Server mit Benutzern. Hier stehen Zuweisung, Veröffentlichung und Neustartplan.
- **Richtlinien:** steuern das Verhalten der Citrix-Sitzung.

## MCS oder PVS?
| | MCS (Machine Creation Services) | PVS (Provisioning Services) |
|---|---|---|
| Prinzip | klont virtuelle Festplatten über den Hypervisor | streamt das Image über das Netz |
| Infrastruktur | kein eigener Server nötig | eigene PVS-Server, Stream-Netz |
| Passt für | kleine bis mittlere Umgebungen, einfacher Einstieg | große Farmen, viele Images |

## Citrix-Richtlinien und GPOs
Beide ergänzen sich:

- **GPOs** regeln Windows: Sicherheit, Ordnerumleitung, FSLogix, Oberfläche.
- **Citrix-Richtlinien** regeln die HDX-Sitzung: Zwischenablage, Laufwerks- und Druckerzuordnung, USB, Bandbreite, Audio.

Citrix-Richtlinien lassen sich in Studio oder über die Gruppenrichtlinien-Verwaltung pflegen. Bei gegensätzlichen Einstellungen entscheidet die Priorität. Prüfe das Ergebnis mit dem Citrix Group Policy Modeling oder im Director.

Gute Regeln:
- Richtlinien klar benennen und nach Zweck trennen (Drucker, USB, Bandbreite).
- Zuerst in einer Testgruppe wirken lassen.
- Zwischenablage und Laufwerke zwischen Sitzung und Endgerät nur so weit öffnen wie nötig. Gerade dort fließen Daten ab.

## Image vorbereiten (Versiegelung)
1. VM mit Windows Server 2022 aufsetzen und Updates einspielen.
2. Rolle RDSH, VDA und Anwendungen installieren.
3. FSLogix installieren. Die Konfiguration kommt per GPO.
4. Citrix Optimizer laufen lassen. Vorlage für Server 2022 wählen, Änderungen vorher ansehen.
5. Autostarts und Update-Dienste der Anwendungen abschalten, die in den Klonen stören.
6. VM herunterfahren und Snapshot anlegen.
7. Katalog aktualisieren, zuerst auf Testservern, danach im Neustartfenster.

**Wichtig:** Änderungen an einem einzelnen Klon sind beim Neustart verloren. Dauerhaft ändern nur im Image.

## Nützliche Befehle am Controller
Die Cmdlets kommen mit den Citrix-PowerShell-Modulen (Windows PowerShell 5.1, ab 7.x-Versionen `Citrix.Broker.Admin.V2`). Lesebefehle sind ungefährlich. Änderungen nur im Wartungsfenster.

```powershell
# Citrix-Snap-ins laden (je nach Version nicht mehr nötig)
Add-PSSnapin Citrix*

# Nicht registrierte Server auflisten
Get-BrokerMachine -RegistrationState Unregistered |
    Select-Object MachineName, InMaintenanceMode, LastDeregistrationReason

# Server, die im Wartungsmodus hängen geblieben sind
Get-BrokerMachine -InMaintenanceMode $true | Select-Object MachineName, DesktopGroupName

# Sitzungen je Server zählen
Get-BrokerSession | Group-Object MachineName | Sort-Object Count -Descending

# Server vor Arbeiten in den Wartungsmodus nehmen: keine neuen Sitzungen
Set-BrokerMachine -MachineName "DOMAENE\SERVER01" -InMaintenanceMode $true
```
