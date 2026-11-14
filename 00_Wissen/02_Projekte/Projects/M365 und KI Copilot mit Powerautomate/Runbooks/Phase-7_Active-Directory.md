# Runbook Phase 7: Active Directory (Erweiterung)

Teil von [[Project_TRACE-Enterprise-Lab]] · Vorher: [[Phase-0_Fundament]] · Status: **Entwurf, noch nicht selbst durchgeführt**

## 1. Ziel

Die TRACE GmbH hat eine eigene Domäne: Ein neuer Benutzer wird angelegt, bekommt
seine Gruppe und kann sich am Windows-11-Client anmelden.

## 2. Voraussetzungen

- Phase 0 abgenommen (Netz `TRACE-LAB`, NAT läuft)
- VM `LAB-DC01` mit installiertem Windows Server 2022 (Desktopdarstellung)
- VM `LAB-W11-01` mit installiertem Windows 11 Pro
- Domänenname festgelegt. Hier als Platzhalter: **`lab.example.de`** – überall durch die eigene Subdomain ersetzen

Alle Befehle in **PowerShell als Administrator**. Wo nichts anderes steht: auf `LAB-DC01`.

## 3. Schritte

### 3.1 Server vorbereiten: Name und feste Adresse

```powershell
# Name setzen – nach der Hochstufung zum DC ist Umbenennen mühsam
Rename-Computer -NewName "LAB-DC01" -Restart
```

```powershell
# Wie heißt die Netzwerkkarte? Meist "Ethernet"
Get-NetAdapter

# Feste Adresse: ein Domänencontroller darf seine Adresse nie wechseln
New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress 10.10.10.10 -PrefixLength 24 -DefaultGateway 10.10.10.1

# Vorläufig ein öffentlicher DNS, damit Updates gehen (wird in 3.3 ersetzt)
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses 9.9.9.9
```

Jetzt Prüfpunkt: `vor-AD-Installation` (auf dem Host, siehe Phase 0).

### 3.2 Active Directory installieren und Domäne erzeugen

```powershell
# Rolle installieren (nur die Dateien, noch keine Domäne)
Install-WindowsFeature AD-Domain-Services -IncludeManagementTools

# Neue Gesamtstruktur anlegen; fragt nach dem Wiederherstellungskennwort (DSRM) und startet neu
Install-ADDSForest -DomainName "lab.example.de" -DomainNetbiosName "TRACE" -InstallDns
```

Warum `-InstallDns`: Active Directory findet seine Dienste über DNS. Ohne eigenen
DNS-Server funktioniert keine Anmeldung.

Das DSRM-Kennwort in den Kennwortmanager – man braucht es nur im Notfall, dann aber dringend.

### 3.3 DNS fertig machen

```powershell
# Der DC fragt ab jetzt sich selbst
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses 10.10.10.10

# Alles, was nicht zur eigenen Domäne gehört, weiterreichen
Add-DnsServerForwarder -IPAddress 9.9.9.9
```

### 3.4 DHCP für die Clients

```powershell
# Rolle installieren und im AD berechtigen (sonst verteilt er nichts)
Install-WindowsFeature DHCP -IncludeManagementTools
Add-DhcpServerInDC -DnsName "LAB-DC01.lab.example.de" -IPAddress 10.10.10.10

# Adressbereich für Clients
Add-DhcpServerv4Scope -Name "Clients" -StartRange 10.10.10.150 -EndRange 10.10.10.199 -SubnetMask 255.255.255.0

# Was der Client mitbekommt: Gateway, DNS-Server, Domänenname
Set-DhcpServerv4OptionValue -ScopeId 10.10.10.0 -Router 10.10.10.1 -DnsServer 10.10.10.10 -DnsDomain "lab.example.de"
```

Der entscheidende Wert ist der DNS-Server: Zeigt ein Client auf einen fremden DNS,
findet er die Domäne nicht.

### 3.5 OU-Struktur

```powershell
# Abkürzung für den Domänenpfad, damit die Befehle lesbar bleiben
$dom = "DC=lab,DC=example,DC=de"

# Ober-OU der Firma
New-ADOrganizationalUnit -Name "TRACE" -Path $dom

# Zweite Ebene
"Benutzer","Computer","Gruppen","Dienstkonten" | ForEach-Object {
    New-ADOrganizationalUnit -Name $_ -Path "OU=TRACE,$dom"
}

# Dritte Ebene: Abteilungen und Gerätearten
"IT","HR","Management","Office" | ForEach-Object {
    New-ADOrganizationalUnit -Name $_ -Path "OU=Benutzer,OU=TRACE,$dom"
}
"Workstations","Server" | ForEach-Object {
    New-ADOrganizationalUnit -Name $_ -Path "OU=Computer,OU=TRACE,$dom"
}
```

Warum eigene OUs statt der Standardordner `Users`/`Computers`: Das sind Container,
keine OUs – an ihnen lassen sich keine Gruppenrichtlinien verknüpfen.

### 3.6 Gruppen

```powershell
# Eine Sicherheitsgruppe je Abteilung; Rechte hängen später an der Gruppe, nie am Benutzer
"SG-IT","SG-HR","SG-Management","SG-Office" | ForEach-Object {
    New-ADGroup -Name $_ -GroupScope Global -GroupCategory Security -Path "OU=Gruppen,OU=TRACE,$dom"
}
```

### 3.7 Benutzer anlegen (ein Beispiel, die anderen genauso)

```powershell
# Startkennwort verdeckt eingeben – nie im Klartext ins Skript schreiben
$pw = Read-Host "Startkennwort" -AsSecureString

New-ADUser -Name "IT User01" -GivenName "IT" -Surname "User01" `
    -SamAccountName "it.user01" `
    -UserPrincipalName "it.user01@lab.example.de" `
    -Department "IT" `
    -Path "OU=IT,OU=Benutzer,OU=TRACE,$dom" `
    -AccountPassword $pw -Enabled $true `
    -ChangePasswordAtLogon $true          # Benutzer muss beim ersten Anmelden ändern

# In die Abteilungsgruppe aufnehmen
Add-ADGroupMember -Identity "SG-IT" -Members "it.user01"
```

| Benutzer | OU | Gruppe |
|---|---|---|
| it.user01 | IT | SG-IT |
| hr.user01 | HR | SG-HR |
| ceo.user01 | Management | SG-Management |
| office.user01 | Office | SG-Office |
| admin01 | IT | SG-IT + `Domänen-Admins` |

`admin01` ist das Verwaltungskonto. Damit wird nicht gesurft und keine Mail gelesen –
für Alltagsarbeit gibt es `it.user01`.

### 3.8 Kennwortrichtlinie

```powershell
# Gilt für die ganze Domäne
Set-ADDefaultDomainPasswordPolicy -Identity "lab.example.de" `
    -MinPasswordLength 12 -ComplexityEnabled $true `
    -LockoutThreshold 10 -LockoutDuration "00:15:00" -LockoutObservationWindow "00:15:00"
```

Lernpunkt: Kennwortregeln für Domänenkonten wirken **nur auf Domänenebene**. Eine
Kennwort-GPO an einer OU bleibt wirkungslos. (Der ursprüngliche Plan nannte das eine
gewöhnliche GPO.) Abweichende Regeln für einzelne Gruppen gehen nur über
„Fine-Grained Password Policies".

### 3.9 Gruppenrichtlinie: Bildschirmsperre nach 10 Minuten

```powershell
# Leere Richtlinie anlegen
New-GPO -Name "TRACE-Bildschirmsperre"

$key = "HKCU\Software\Policies\Microsoft\Windows\Control Panel\Desktop"

# Bildschirmschoner an, nach 600 Sekunden, mit Kennwortabfrage
Set-GPRegistryValue -Name "TRACE-Bildschirmsperre" -Key $key -ValueName "ScreenSaveActive"    -Type String -Value "1"
Set-GPRegistryValue -Name "TRACE-Bildschirmsperre" -Key $key -ValueName "ScreenSaveTimeOut"   -Type String -Value "600"
Set-GPRegistryValue -Name "TRACE-Bildschirmsperre" -Key $key -ValueName "ScreenSaverIsSecure" -Type String -Value "1"

# An die Benutzer-OU hängen – erst die Verknüpfung macht die Richtlinie wirksam
New-GPLink -Name "TRACE-Bildschirmsperre" -Target "OU=Benutzer,OU=TRACE,$dom"
```

Das ist eine **Benutzer**einstellung (HKCU), also gehört sie an die OU mit den Benutzern,
nicht an die mit den Computern.

### 3.10 Client in die Domäne aufnehmen (auf `LAB-W11-01`)

```powershell
# Bekommt der Client Adresse und den richtigen DNS (10.10.10.10)?
ipconfig /all

# Findet er die Domäne?
Resolve-DnsName lab.example.de

# Umbenennen, beitreten und direkt in die richtige OU legen; fragt nach admin01
Rename-Computer -NewName "LAB-W11-01"
Add-Computer -DomainName "lab.example.de" `
    -OUPath "OU=Workstations,OU=Computer,OU=TRACE,DC=lab,DC=example,DC=de" `
    -Options JoinWithNewName -Restart
```

Vorher auf dem Host: Prüfpunkt `vor-Domaenenbeitritt`.

## 4. Prüfung

Auf `LAB-DC01`:

```powershell
Get-ADDomain | Select-Object DNSRoot, NetBIOSName      # Domäne da?
dcdiag /q                                              # keine Ausgabe = keine Fehler
Get-ADUser -Filter * -SearchBase "OU=TRACE,DC=lab,DC=example,DC=de" | Select-Object SamAccountName
Get-ADGroupMember "SG-IT"                              # Mitglieder stimmen?
Get-DhcpServerv4Lease -ScopeId 10.10.10.0              # Client hat Adresse bekommen?
```

Auf `LAB-W11-01`, angemeldet als `it.user01`:

```powershell
whoami                     # trace\it.user01
whoami /groups             # SG-IT ist dabei
gpresult /r                # TRACE-Bildschirmsperre unter "Angewendete Gruppenrichtlinienobjekte"
nltest /dsgetdc:lab.example.de   # zeigt LAB-DC01
```

**Abnahme:** Einen sechsten Benutzer ohne Blick ins Runbook anlegen, einer Abteilung und
Gruppe zuweisen und die Anmeldung am Client zeigen.

Zum Schluss: VM herunterfahren und auf dem Host sichern.

```powershell
Export-VM -Name "LAB-DC01" -Path D:\Lab\Export
```

## 5. Fehlerbilder

Typische Fälle aus der Praxis (noch nicht selbst erlebt – eigene Fälle unten ergänzen):

| Symptom | Ursache | Lösung |
|---|---|---|
| Client: „Domäne konnte nicht kontaktiert werden" | Client nutzt falschen DNS | `ipconfig /all`; DNS muss 10.10.10.10 sein |
| Client bekommt 169.254.x.x | DHCP nicht autorisiert oder Bereich fehlt | `Add-DhcpServerInDC`, `Get-DhcpServerv4Scope` |
| Internetnamen lösen im Lab nicht auf | Weiterleitung fehlt | `Get-DnsServerForwarder`, Schritt 3.3 |
| Richtlinie kommt nicht an | an falscher OU verknüpft oder Benutzer liegt woanders | `gpresult /r`, dann `gpupdate /force` |
| Anmeldung scheitert nach Stunden Pause | Uhrzeit von Client und DC weicht über 5 Minuten ab | Zeit prüfen; Kerberos ist da streng |
| „Kennwort erfüllt die Richtlinien nicht" | Startkennwort kürzer als 12 Zeichen | längeres Kennwort |

Eigene Fälle:

| Datum | Symptom | Ursache | Lösung |
|---|---|---|---|
| | | | |

## 6. Bezug zur Praxis

- Benutzeranlage mit OU, Gruppe und Startkennwort ist das tägliche Brot im Benutzer-Support.
- „Erst DNS prüfen" löst den größten Teil aller Anmelde- und Domänenprobleme.
- Die saubere OU-Struktur zahlt sich in Phase 8 aus: Dort wird gezielt nur `OU=TRACE` in die Cloud synchronisiert.
- Aus Schritt 3.7 lässt sich das Eintritts-Skript aus Phase 6 um das lokale AD erweitern.
