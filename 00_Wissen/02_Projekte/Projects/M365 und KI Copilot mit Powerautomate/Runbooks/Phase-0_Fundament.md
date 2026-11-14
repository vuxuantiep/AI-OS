# Runbook Phase 0: Fundament (Lab-Host)

Teil von [[Project_TRACE-Enterprise-Lab]] · Status: **Entwurf, noch nicht selbst durchgeführt**

## 1. Ziel

Der Mini-PC kann VMs in einem eigenen, abgeschotteten Netz betreiben, die trotzdem ins Internet kommen.

## 2. Voraussetzungen

- Mini-PC mit **Windows 11 Pro** (Home hat kein Hyper-V), 32 GB RAM
- Im BIOS/UEFI ist Virtualisierung eingeschaltet (Intel VT-x bzw. AMD-V/SVM)
- ISO-Dateien: Windows Server 2022 Evaluation (Microsoft Evaluation Center), Windows 11
- Alle Befehle in **PowerShell als Administrator** auf dem Host

> Annahme: Die VMs liegen unter `D:\Lab`. Bei nur einer Platte `C:\Lab` nehmen.

## 3. Schritte

### 3.1 Prüfen, ob der PC virtualisieren kann

```powershell
# Zeigt u. a. "Virtualisierung in Firmware aktiviert: Ja"
systeminfo | Select-String "Hyper-V","Virtualisierung"
```

Warum: Ohne aktivierte Virtualisierung im BIOS startet später keine VM.

### 3.2 Hyper-V einschalten

```powershell
# Installiert Hyper-V samt Verwaltungswerkzeugen, danach Neustart
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
Restart-Computer
```

### 3.3 Ordner anlegen

```powershell
# VMs = laufende Maschinen, ISO = Installationsmedien, Export = Sicherungen
New-Item -ItemType Directory -Path D:\Lab\VMs, D:\Lab\ISO, D:\Lab\Export
```

Warum: Eine feste Ablage, damit man eine VM später wiederfindet und sichern kann.

### 3.4 Eigenes Lab-Netz mit NAT bauen

```powershell
# 1) Interner Schalter: VMs und Host sehen sich, das Heimnetz bleibt außen vor
New-VMSwitch -SwitchName "TRACE-LAB" -SwitchType Internal

# 2) Der Host bekommt in diesem Netz die Adresse .1 und wird damit zum Gateway
New-NetIPAddress -IPAddress 10.10.10.1 -PrefixLength 24 -InterfaceAlias "vEthernet (TRACE-LAB)"

# 3) NAT: Der Host übersetzt Lab-Adressen, damit die VMs ins Internet kommen
New-NetNat -Name "TRACE-LAB-NAT" -InternalIPInterfaceAddressPrefix 10.10.10.0/24
```

Warum intern + NAT statt „Extern": Ein eigener DHCP-/DNS-Server im Lab darf das
Heimnetz nicht stören. Mit dem internen Schalter kann er das gar nicht.

Wichtig: NAT liefert **kein DHCP und kein DNS**. Bis der Domänencontroller steht,
brauchen VMs eine feste Adresse.

### 3.5 Erste VM anlegen (Muster für alle weiteren)

```powershell
# Generation 2 = UEFI + Secure Boot (Pflicht für Windows 11, sinnvoll für Server)
New-VM -Name "LAB-DC01" -Generation 2 -MemoryStartupBytes 4GB `
       -Path D:\Lab\VMs -NewVHDPath D:\Lab\VMs\LAB-DC01\LAB-DC01.vhdx -NewVHDSizeBytes 80GB `
       -SwitchName "TRACE-LAB"

# 2 Prozessorkerne zuweisen
Set-VMProcessor -VMName "LAB-DC01" -Count 2

# ISO als DVD einlegen und von dort starten
Add-VMDvdDrive -VMName "LAB-DC01" -Path D:\Lab\ISO\WindowsServer2022.iso
Set-VMFirmware -VMName "LAB-DC01" -FirstBootDevice (Get-VMDvdDrive -VMName "LAB-DC01")

# Automatische Prüfpunkte aus – wir setzen sie bewusst selbst
Set-VM -Name "LAB-DC01" -AutomaticCheckpointsEnabled $false
```

Die Platte ist „dynamisch": 80 GB ist die Obergrenze, belegt wird nur, was die VM wirklich nutzt.

### 3.6 Zusatz für Windows-11-VMs: virtuelles TPM

```powershell
# Windows 11 und später Autopilot/BitLocker verlangen ein TPM
Set-VMKeyProtector -VMName "LAB-W11-01" -NewLocalKeyProtector
Enable-VMTPM -VMName "LAB-W11-01"
```

### 3.7 Prüfpunkt-Regel

```powershell
# Vor jedem größeren Schritt einen benannten Prüfpunkt setzen
Checkpoint-VM -Name "LAB-DC01" -SnapshotName "vor-AD-Installation"

# Zurück zum Prüfpunkt, wenn etwas schiefgeht
Restore-VMSnapshot -VMName "LAB-DC01" -Name "vor-AD-Installation" -Confirm:$false
```

Regel: Name sagt immer, **wovor** der Prüfpunkt entstand. Alte Prüfpunkte nach erfolgreicher
Phase löschen, sonst wächst die Platte.

Achtung beim Domänencontroller: Prüfpunkte nur im Ein-DC-Lab zurückspielen. In echten
Umgebungen mit mehreren DCs ist das tabu.

## 4. Prüfung

```powershell
Get-VMSwitch                     # TRACE-LAB, Typ Internal
Get-NetNat                       # TRACE-LAB-NAT mit 10.10.10.0/24
Get-NetIPAddress -IPAddress 10.10.10.1
```

In einer VM mit fester Adresse `10.10.10.x`, Gateway `10.10.10.1`:

```powershell
Test-NetConnection 10.10.10.1    # Host erreichbar?
Test-NetConnection 9.9.9.9       # Internet erreichbar? (ohne DNS)
```

**Abnahme:** VM im Lab-Netz erreicht das Internet, im Heimnetz hat sich nichts geändert.

## 5. Fehlerbilder

Typische Fälle aus der Praxis (noch nicht selbst erlebt – eigene Fälle unten ergänzen):

| Symptom | Ursache | Lösung |
|---|---|---|
| VM startet nicht, Hinweis auf Hypervisor | Virtualisierung im BIOS aus | im UEFI einschalten |
| VM pingt Host, aber kein Internet | NAT fehlt oder falsches Präfix | `Get-NetNat` prüfen, neu anlegen |
| `New-NetNat` meldet Fehler | es gibt schon ein NAT (z. B. von Docker/WSL) | `Get-NetNat` ansehen; Windows erlaubt praktisch nur eines |
| Windows-11-Setup: „PC erfüllt Anforderungen nicht" | TPM fehlt oder unter 4 GB RAM / 2 Kerne | Schritt 3.6, Ressourcen erhöhen |

Eigene Fälle:

| Datum | Symptom | Ursache | Lösung |
|---|---|---|---|
| | | | |

## 6. Bezug zur Praxis

- Interne/externe virtuelle Schalter und NAT begegnen einem bei jedem Hyper-V-Host und in Azure als VNet/NAT-Gateway wieder.
- Prüfpunkt vor Änderung = dieselbe Denkweise wie Snapshot vor Patch im Serverbetrieb.
