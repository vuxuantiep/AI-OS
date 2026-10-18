# EmviaAdmin: PowerShell-Modul für die Benutzerverwaltung

Lern- und Arbeitsmodul für die Einarbeitung bei EMVIA (Abnahme M1 am 29.10.2026).
Jede Funktion ist ausführlich kommentiert: was sie tut **und warum**.

## Installation (auf dem Admin-PC bzw. Exchange-Server)

```powershell
# 1. Ordner EmviaAdmin z. B. nach C:\EmviaAdmin\ kopieren
# 2. Konfiguration anlegen und mit den echten OUs füllen (KEINE Kennwörter!)
Copy-Item .\EmviaAdmin\EmviaAdmin.config.example.json .\EmviaAdmin\EmviaAdmin.config.json
notepad .\EmviaAdmin\EmviaAdmin.config.json
# 3. Laden
Import-Module .\EmviaAdmin\EmviaAdmin.psd1
Get-Command -Module EmviaAdmin
Get-Help Disable-EmviaBenutzer -Full
```

Die `EmviaAdmin.config.json` ist per `.gitignore` ausgeschlossen. Sie enthält interne OU-Pfade von EMVIA und gehört nicht ins Repo.

## Goldene Regel

```powershell
New-EmviaBenutzer ... -WhatIf      # 1. Probelauf: zeigt nur, was passieren würde
New-EmviaBenutzer ...              # 2. echt
Get-EmviaProtokoll -Ticket T-4711  # 3. Nachweis fürs Ticket
```

## Befehle und M1-Checkliste

| M1-Punkt | Befehle |
|---|---|
| 3 Neuanlagen | `New-EmviaBenutzer` (inkl. `-Fremdpersonal`) |
| 3 Änderungen | `Set-EmviaBenutzer`, `Add-/Remove-EmviaGruppenmitglied` |
| 3 Austritte | `Disable-EmviaBenutzer`, später `Remove-EmviaBenutzer` |
| Kennwort nach Regeln | `Get-EmviaKontoStatus`, `Reset-EmviaKennwort -Pruefweg ... -Nachweis ...`, `Unlock-EmviaKonto`, `Get-EmviaSperrquelle` |
| Funktionspostfach-Rechte | `New-EmviaFunktionspostfach`, `Grant-/Revoke-EmviaPostfachRecht`, `Get-EmviaPostfachRechte` |
| Lizenz und MFA | `Set-EmviaLizenz`, `Get-EmviaMfaStatus`, `Reset-EmviaMfa -TapAusstellen` |
| Vollständig dokumentiert | automatisch: `Get-EmviaProtokoll` |

Die Erklärungen zu jedem Befehl stehen im Wiki unter `wissen/emvia/13-benutzerverwaltung-ad-exchange.md`.

**Vor dem ersten echten Einsatz:** Abläufe mit dem Paten abgleichen. Die Richtlinien IT.10.0x haben Vorrang vor diesem Modul.
