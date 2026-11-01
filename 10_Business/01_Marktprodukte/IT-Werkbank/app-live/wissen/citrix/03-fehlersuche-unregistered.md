# Citrix-Fehlersuche: Server ist „Unregistered“

Ein Server mit Status Unregistered nimmt keine Sitzungen an. Sein VDA ist nicht beim Delivery Controller angemeldet. Offene Sitzungen können trotzdem weiterlaufen.

![Entscheidungsbaum für nicht registrierte Server](citrix-fehlerbaum-unregistered.svg)

## Der richtige Dienstname
Der VDA-Dienst heißt **Citrix Desktop Service**, technisch `BrokerAgent`. Daneben ist **Remotedesktopdienste** (`TermService`) wichtig: Ohne ihn gibt es keine Sitzungen. Einen Dienst namens „Desktop Courier“ gibt es nicht.

## Prüfen auf dem betroffenen Server
```powershell
# 1. Dienste
Get-Service BrokerAgent, TermService | Select-Object Name, Status, StartType

# 2. Domänenbeziehung
Test-ComputerSecureChannel -Verbose

# 3. Zeit (maximal 5 Minuten Abweichung zum Controller)
w32tm /query /status

# 4. Eingetragene Controller lesen
Get-ItemProperty "HKLM:\SOFTWARE\Citrix\VirtualDesktopAgent" | Select-Object ListOfDDCs

# 5. Controller erreichbar? Namen durch den echten FQDN ersetzen
Test-NetConnection controller.domaene.tld -Port 80

# 6. Letzte Meldungen des VDA
Get-WinEvent -FilterHashtable @{LogName='Application'; ProviderName='Citrix Desktop Service'} -MaxEvents 20 |
    Select-Object TimeCreated, Id, LevelDisplayName, Message | Format-List
```

Ohne `ListOfDDCs`-Treffer stammt der Eintrag oft aus einer Citrix-Richtlinie (Unterschlüssel `Policies`) oder aus der MCS-Konfiguration. Trage dann nichts von Hand ein, sondern prüfe die Quelle.

`Restart-Service BrokerAgent` ist ein einfacher nächster Schritt: Der Dienst versucht die Registrierung neu und schreibt dazu Ereignisse ins Protokoll. Offene Sitzungen vorher prüfen.

## Prüfen am Controller
```powershell
Get-BrokerMachine -MachineName "DOMAENE\SERVER01" |
    Select-Object RegistrationState, LastDeregistrationReason, LastDeregistrationTime, InMaintenanceMode, AgentVersion
```

## Häufige Ursachen
| Ursache | Hinweis |
|---|---|
| Uhrzeit weicht ab | Kerberos scheitert, Ereignis mit Hinweis auf Zeit |
| Controller fehlt in ListOfDDCs | Registrierung bei nur einem von mehreren Controllern, Sitzungsstart scheitert |
| Firewall oder Port gesperrt | Port 80 oder 443 zum Controller zu |
| Maschinenkonto kaputt | `Test-ComputerSecureChannel` gibt False |
| VDA zu alt oder Funktionsebene zu hoch | VDA-Version gegen Katalog prüfen |
| Protokollkonflikt WebSocket/WCF | VDA und Controller nutzen unterschiedliche Verfahren |
| Dienst startet, stoppt wieder | Virenschutz, fehlende Abhängigkeit, Ereignisprotokoll lesen |

## Wichtige Ereignis-IDs (Quelle Citrix Desktop Service)
| ID | Bedeutung | Weiter mit |
|---|---|---|
| 1017 | Keine Registrierung bei einem Controller möglich | Name, Port, ListOfDDCs |
| 1022 | Controller nicht erreichbar oder Ablehnung | Netz, Firewall |
| 1221 | Hinweis auf Uhrzeit | Zeitsynchronisation |

Die Texte unterscheiden sich je nach VDA-Version. Lies immer den vollen Ereignistext.

## Wann eskalieren?
Eskaliere, wenn mehrere Server gleichzeitig ausfallen (Hinweis auf Controller, DNS, Datenbank oder Lizenz) oder wenn ein Standort komplett betroffen ist. Nenne: Server, Uhrzeit, Status, Dienstzustand, Ereignis-ID, schon geprüfte Punkte.

Quellen: [CTX136668 VDA-Registrierung](https://support.citrix.com/external/article/CTX136668/how-to-troubleshoot-virtual-delivery-age.html), [Citrix-Doku VDA-Registrierung](https://docs.citrix.com/en-us/citrix-virtual-apps-desktops/2511/manage-deployment/vda-registration), [CTX695813 Server 2022 VDA Unregistered](https://support.citrix.com/external/article/CTX695813/citrix-virtual-apps-and-desktops-window.html)
