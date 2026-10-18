<#
================================================================================
  EmviaAdmin -- Benutzerverwaltung EMVIA (AD, Exchange, M365) als Lern-Modul
================================================================================
  Zweck: Die typischen Aufgaben aus der Einarbeitung (Abnahme M1, 29.10.2026)
  richtlinienkonform und NACHVOLLZIEHBAR erledigen:

    Neuanlage ............ New-EmviaBenutzer        (auch Fremdpersonal)
    Aenderung ............ Set-EmviaBenutzer        (Name, Stelle, Einrichtungswechsel)
    Austritt ............. Disable-EmviaBenutzer    (sperren, Gruppen sichern+entfernen)
    Endgueltig loeschen .. Remove-EmviaBenutzer     (erst nach Aufbewahrungsfrist)
    Kennwort / Sperre .... Get-EmviaKontoStatus, Reset-EmviaKennwort, Unlock-EmviaKonto,
                           Get-EmviaSperrquelle
    Gruppen/Rechte ....... Add-/Remove-EmviaGruppenmitglied, Get-EmviaBenutzerGruppen
    Funktionspostfach .... New-EmviaFunktionspostfach, Grant-/Revoke-EmviaPostfachRecht,
                           Get-EmviaPostfachRechte
    M365 (Graph) ......... Get-EmviaMfaStatus, Reset-EmviaMfa, Set-EmviaLizenz
    Dokumentation ........ jede Aenderung landet automatisch in der Protokoll-CSV

  LERN-GRUNDREGELN, die sich durch alle Funktionen ziehen:
  1. -WhatIf ZUERST. Jede aendernde Funktion unterstuetzt -WhatIf (Probelauf,
     zeigt nur an, was passieren wuerde) und -Confirm. Das ist der
     PowerShell-Standard (SupportsShouldProcess) -- dieselben Schalter wie bei
     Remove-Item, Set-ADUser usw.
  2. Jede Aenderung braucht -Ticket. Ohne Ticketnummer keine Aenderung ->
     "Anliegen vollstaendig dokumentiert" (M1) ist automatisch erfuellt.
  3. Keine Passwoerter/Secrets im Code. Die Konfiguration (Domain, OUs) liegt in
     EmviaAdmin.config.json und enthaelt NUR Strukturdaten.
  4. Erst lesen, dann aendern: zu jeder Aenderung gibt es eine Get-Funktion.

  Voraussetzungen:
    - RSAT: Active-Directory-Modul (Import-Module ActiveDirectory)
    - Exchange: Exchange Management Shell (lokal/Hybrid) ODER
      ExchangeOnlineManagement (Connect-ExchangeOnline)
    - M365-Funktionen: Microsoft.Graph-Module (Connect-MgGraph)
  Laden:
    Import-Module .\EmviaAdmin\EmviaAdmin.psd1
    Get-Command -Module EmviaAdmin            # alle Befehle
    Get-Help New-EmviaBenutzer -Full          # Hilfe inkl. Beispiele
================================================================================
#>

# Strikter Modus: Tippfehler in Variablennamen werden zu Fehlern statt still
# zu $null. Spart viel Fehlersuche.
Set-StrictMode -Version Latest

# ------------------------------------------------------------------------------
#  Konfiguration
# ------------------------------------------------------------------------------
# $script: = Variable gilt im ganzen Modul, ist aber von aussen nicht sichtbar.
# $PSScriptRoot = Ordner, in dem diese .psm1 liegt.
$script:KonfigPfad = Join-Path $PSScriptRoot 'EmviaAdmin.config.json'
$script:Konfig = $null

function Get-EmviaKonfig {
    <#
    .SYNOPSIS
    Liest EmviaAdmin.config.json (einmal, dann aus dem Zwischenspeicher).
    #>
    [CmdletBinding()]
    param([switch]$NeuLaden)

    if ($script:Konfig -and -not $NeuLaden) { return $script:Konfig }
    if (-not (Test-Path $script:KonfigPfad)) {
        throw "Konfiguration fehlt: $script:KonfigPfad -- EmviaAdmin.config.example.json kopieren und ausfuellen."
    }
    # ConvertFrom-Json macht aus dem JSON-Text ein Objekt mit Eigenschaften.
    $script:Konfig = Get-Content $script:KonfigPfad -Raw -Encoding UTF8 | ConvertFrom-Json
    return $script:Konfig
}

# ------------------------------------------------------------------------------
#  Interne Hilfsfunktionen (werden NICHT exportiert, siehe .psd1)
# ------------------------------------------------------------------------------

function Initialize-EmviaAD {
    # Laedt das AD-Modul erst, wenn es gebraucht wird. So laesst sich das Modul
    # auch auf einem PC ohne RSAT laden (z. B. nur fuer die Graph-Funktionen).
    if (-not (Get-Module ActiveDirectory)) {
        Import-Module ActiveDirectory -ErrorAction Stop
    }
}

function Assert-EmviaBefehl {
    # Prueft, ob ein Cmdlet in der aktuellen Sitzung existiert (z. B.
    # Enable-RemoteMailbox gibt es nur in der Exchange Management Shell).
    param([Parameter(Mandatory)][string]$Name, [Parameter(Mandatory)][string]$Hinweis)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Befehl '$Name' nicht verfuegbar. $Hinweis"
    }
}

function Write-EmviaProtokoll {
    <#
    .SYNOPSIS
    Schreibt eine Zeile in die Protokoll-CSV (wer, wann, Ticket, was, an wem).
    .DESCRIPTION
    Wird von allen aendernden Funktionen aufgerufen, NACHDEM die Aenderung
    erfolgreich war. Bei -WhatIf wird nichts protokolliert, weil nichts passiert.
    Die CSV laesst sich in Excel oeffnen und als Nachweis fuers Ticket nutzen.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Ticket,
        [Parameter(Mandatory)][string]$Aktion,
        [Parameter(Mandatory)][string]$Ziel,
        [string]$Details = '',
        [string]$Pruefweg = ''
    )
    $k = Get-EmviaKonfig
    $pfad = $k.ProtokollPfad
    $ordner = Split-Path $pfad -Parent
    if ($ordner -and -not (Test-Path $ordner)) { New-Item -ItemType Directory -Path $ordner -Force | Out-Null }

    [pscustomobject]@{
        Zeit     = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
        Admin    = "$env:USERDOMAIN\$env:USERNAME"   # wer hat es getan
        Ticket   = $Ticket
        Aktion   = $Aktion
        Ziel     = $Ziel
        Details  = $Details
        Pruefweg = $Pruefweg                         # Identitaetspruefung (nur bei Kennwort/MFA)
    } | Export-Csv -Path $pfad -Append -NoTypeInformation -Delimiter ';' -Encoding UTF8
    # -Delimiter ';' -> deutsches Excel oeffnet die Datei direkt in Spalten.
}

function New-EmviaStartkennwort {
    # Zufallskennwort ohne verwechselbare Zeichen (0/O, 1/l/I), 14 Zeichen.
    # RandomNumberGenerator ist kryptografisch sicher -- Get-Random ist es nicht.
    param([int]$Laenge = 14)
    $zeichen = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!$%&?#+'
    $bytes = [byte[]]::new($Laenge)
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    -join ($bytes | ForEach-Object { $zeichen[$_ % $zeichen.Length] })
}

function Resolve-EmviaEinrichtungsOU {
    <#
    .SYNOPSIS
    Findet die OU einer Einrichtung anhand der OENR.
    .DESCRIPTION
    Reihenfolge: 1) feste Zuordnung in der Konfig (EinrichtungsOUs),
    2) Suche unter BenutzerBasisOU nach einer OU, deren Name oder Beschreibung
    die OENR enthaelt. Es muss GENAU EINE Treffer-OU geben -- bei 0 oder 2+
    Treffern bricht die Funktion ab, statt zu raten.
    #>
    param([Parameter(Mandatory)][string]$OENR)
    Initialize-EmviaAD
    $k = Get-EmviaKonfig

    $fest = $k.EinrichtungsOUs.PSObject.Properties[$OENR]
    if ($fest) { return $fest.Value }

    # -SearchBase = nur unterhalb dieser OU suchen (schneller, kein Fehlgriff
    # in Admin- oder Server-OUs).
    $treffer = @(Get-ADOrganizationalUnit -SearchBase $k.BenutzerBasisOU -Filter * -Properties Description |
        Where-Object { $_.Name -like "*$OENR*" -or $_.Description -like "*$OENR*" })
    if ($treffer.Count -ne 1) {
        throw "OU fuer OENR $OENR nicht eindeutig ($($treffer.Count) Treffer). In der Konfig unter EinrichtungsOUs fest eintragen."
    }
    return $treffer[0].DistinguishedName
}

function Get-EmviaEinrichtungsgruppe {
    # Gruppenschema laut Einarbeitung: G_<OENR>, z. B. G_0350.
    param([Parameter(Mandatory)][string]$OENR)
    $k = Get-EmviaKonfig
    return ($k.EinrichtungsGruppenMuster -f $OENR)   # -f = Platzhalter {0} ersetzen
}

# ==============================================================================
#  1. NEUANLAGE
# ==============================================================================

function New-EmviaBenutzer {
    <#
    .SYNOPSIS
    Legt einen Benutzer richtlinienkonform an: Konto, Einrichtungs- und
    Rollengruppe, Postfach, Protokoll.
    .DESCRIPTION
    Ablauf (das ist der Teil, den man verstehen sollte):
      1. Pruefen, ob Kennung/UPN schon existiert  -> keine Doppelanlage.
      2. OU der Einrichtung aus der OENR ermitteln.
      3. Konto mit Einmalkennwort anlegen, "bei naechster Anmeldung aendern".
      4. In G_<OENR> + Rollengruppe aufnehmen     -> daraus folgen die Rechte.
      5. Postfach: Hybrid = Enable-RemoteMailbox (Postfach in Exchange Online),
         lokal = Enable-Mailbox, Keins = z. B. Fremdpersonal ohne Mail.
      6. Protokoll schreiben, Startkennwort EINMAL anzeigen.
    Fremdpersonal: -Fremdpersonal verlangt -Ablaufdatum und -Firma. Das Konto
    laeuft dann automatisch ab (AccountExpirationDate) -- niemand muss daran denken.
    .EXAMPLE
    New-EmviaBenutzer -Kennung DE123456 -Vorname Anna -Nachname Muster -OENR 0350 `
        -Rollengruppe 'G_0350_Pflege' -Stelle 'Pflegefachkraft' -Ticket 'T-4711' -WhatIf
    .EXAMPLE
    New-EmviaBenutzer -Kennung EXT00042 -Vorname Max -Nachname Leih -OENR 0350 `
        -Rollengruppe 'G_0350_Pflege' -Stelle 'Leasingkraft' -Fremdpersonal -Firma 'Pflege-Zeit GmbH' `
        -Ablaufdatum '2026-12-31' -Postfach Keins -Ticket 'T-4712'
    #>
    # SupportsShouldProcess = aktiviert -WhatIf/-Confirm. ConfirmImpact Medium:
    # fragt nur nach, wenn der Nutzer -Confirm angibt.
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
    param(
        # ValidatePattern: Kennung muss dem EMVIA-Schema entsprechen (Regex in
        # der Konfig waere flexibler; hier bewusst sichtbar zum Lernen).
        [Parameter(Mandatory)][ValidatePattern('^[A-Z]{2,3}\d{4,8}$')][string]$Kennung,
        [Parameter(Mandatory)][string]$Vorname,
        [Parameter(Mandatory)][string]$Nachname,
        [Parameter(Mandatory)][ValidatePattern('^\d{3,5}$')][string]$OENR,
        [Parameter(Mandatory)][string]$Rollengruppe,
        [Parameter(Mandatory)][string]$Stelle,
        [Parameter(Mandatory)][string]$Ticket,
        [ValidateSet('Remote', 'Lokal', 'Keins')][string]$Postfach,
        [switch]$Fremdpersonal,
        [string]$Firma,
        [datetime]$Ablaufdatum,
        [string[]]$WeitereGruppen = @()
    )
    Initialize-EmviaAD
    $k = Get-EmviaKonfig
    if (-not $Postfach) { $Postfach = $k.PostfachStandard }   # Standard aus Konfig

    # --- Plausibilitaet Fremdpersonal: ohne Ablaufdatum KEIN Konto
    if ($Fremdpersonal) {
        if (-not $Ablaufdatum) { throw 'Fremdpersonal braucht -Ablaufdatum (Konto laeuft automatisch ab).' }
        if (-not $Firma)       { throw 'Fremdpersonal braucht -Firma (wer ist der Vertragspartner?).' }
        if ($Ablaufdatum -gt (Get-Date).AddDays($k.FremdpersonalMaxTage)) {
            throw "Ablaufdatum liegt mehr als $($k.FremdpersonalMaxTage) Tage in der Zukunft -- Richtlinie pruefen."
        }
    }

    $upn = "$Kennung@$($k.UpnDomain)"
    # AD-Konvention bei EMVIA: Anzeigename "Nachname, Vorname".
    # Das Komma maskiert AD im DN selbst (CN=Muster\, Anna) -- nichts zu tun.
    $anzeige = "$Nachname, $Vorname"

    # --- 1. Doppelanlage verhindern
    # -Filter mit Variablen: AD-Filter-Syntax, nicht PowerShell-Where-Object.
    $vorhanden = Get-ADUser -Filter "SamAccountName -eq '$Kennung' -or UserPrincipalName -eq '$upn'" -ErrorAction SilentlyContinue
    if ($vorhanden) { throw "Konto existiert bereits: $($vorhanden.DistinguishedName)" }

    # --- 2. Ziel-OU und Gruppen pruefen, BEVOR irgendetwas angelegt wird
    $ou = if ($Fremdpersonal -and $k.FremdpersonalOU) { $k.FremdpersonalOU } else { Resolve-EmviaEinrichtungsOU -OENR $OENR }
    $gruppen = @(Get-EmviaEinrichtungsgruppe -OENR $OENR) + $Rollengruppe + $WeitereGruppen
    foreach ($g in $gruppen) {
        # Get-ADGroup wirft einen Fehler, wenn es die Gruppe nicht gibt -> Abbruch vor der Anlage.
        $null = Get-ADGroup -Identity $g -ErrorAction Stop
    }

    $beschreibung = "$Stelle $OENR"
    if ($Fremdpersonal) { $beschreibung = "FREMD $Firma bis $($Ablaufdatum.ToString('dd.MM.yyyy')) - $beschreibung" }

    # --- 3. Konto anlegen. Parameter als Hashtable ("Splatting", @param):
    # uebersichtlicher als eine Riesenzeile mit Backticks, und man kann
    # Werte bedingt ergaenzen.
    $kennwort = New-EmviaStartkennwort
    $param = @{
        Name                  = $anzeige
        DisplayName           = $anzeige
        GivenName             = $Vorname
        Surname               = $Nachname
        SamAccountName        = $Kennung          # Anmeldename "alt" (max. 20 Zeichen)
        UserPrincipalName     = $upn              # Anmeldename "neu", auch fuer M365
        Path                  = $ou
        Title                 = $Stelle
        Department            = $OENR
        Description           = $beschreibung
        AccountPassword       = (ConvertTo-SecureString $kennwort -AsPlainText -Force)
        ChangePasswordAtLogon = $true             # Einmalkennwort -> Nutzer setzt eigenes
        Enabled               = $true
    }
    if ($Fremdpersonal) {
        $param.Company = $Firma
        # Ablauf am Ende des Tages: AD meint "abgelaufen AB diesem Zeitpunkt".
        $param.AccountExpirationDate = $Ablaufdatum.Date.AddDays(1)
    }

    # ShouldProcess(Ziel, Aktion): bei -WhatIf wird nur der Text ausgegeben
    # und $false zurueckgegeben -> der Block wird uebersprungen.
    if (-not $PSCmdlet.ShouldProcess("$anzeige ($upn) in $ou", 'Benutzer anlegen')) { return }

    New-ADUser @param -ErrorAction Stop
    Write-Host "[1] Konto angelegt: $upn" -ForegroundColor Green

    # --- 4. Gruppen. Rechte NIE direkt ans Konto, immer ueber Gruppen
    # (G_<OENR> + Rollengruppe) -> beim Austritt/Wechsel reicht Gruppenpflege.
    foreach ($g in $gruppen) {
        Add-ADGroupMember -Identity $g -Members $Kennung -ErrorAction Stop
        Write-Host "    + $g"
    }

    # --- 5. Postfach
    switch ($Postfach) {
        'Remote' {
            # Hybrid: Postfach liegt in Exchange Online, das lokale AD-Objekt
            # bekommt nur die Weiterleitungsadresse (RemoteRoutingAddress).
            Assert-EmviaBefehl Enable-RemoteMailbox 'In der Exchange Management Shell ausfuehren oder -Postfach Keins und spaeter nachholen.'
            Enable-RemoteMailbox -Identity $Kennung -RemoteRoutingAddress "$Kennung@$($k.RoutingDomain)" | Out-Null
            Write-Host '[2] Remote-Postfach aktiviert (sichtbar nach Sync + Lizenz)'
        }
        'Lokal' {
            Assert-EmviaBefehl Enable-Mailbox 'In der Exchange Management Shell ausfuehren.'
            Enable-Mailbox -Identity $Kennung | Out-Null
            Write-Host '[2] Lokales Postfach angelegt'
        }
        'Keins' { Write-Host '[2] Kein Postfach (laut Parameter)' }
    }

    Write-EmviaProtokoll -Ticket $Ticket -Aktion 'Neuanlage' -Ziel $upn `
        -Details "OU=$ou; Gruppen=$($gruppen -join ','); Postfach=$Postfach; Fremd=$([bool]$Fremdpersonal)"

    Write-Host ''
    Write-Host "Einmalkennwort: $kennwort" -ForegroundColor Yellow
    Write-Host 'Uebergabe nur nach Richtlinie (nicht per Mail an den Nutzer selbst). Fenster danach schliessen/leeren.' -ForegroundColor Yellow
}

# ==============================================================================
#  2. AENDERUNG
# ==============================================================================

function Set-EmviaBenutzer {
    <#
    .SYNOPSIS
    Aendert Stammdaten oder fuehrt einen Einrichtungswechsel durch.
    .DESCRIPTION
    Namensaenderung (z. B. Heirat): Vorname/Nachname -> Anzeige- und CN-Name
    werden mitgezogen (Rename-ADObject). Die Kennung/UPN bleibt gleich, deshalb
    bleiben Postfach und M365-Konto unberuehrt.
    Einrichtungswechsel (-NeueOENR): Konto in die neue OU verschieben,
    alte G_<OENR> raus, neue rein. Die Rollengruppe wird nur getauscht, wenn
    -NeueRollengruppe angegeben ist -- bewusst, weil die Rolle oft gleich bleibt.
    .EXAMPLE
    Set-EmviaBenutzer -Kennung DE123456 -Nachname Neumann -Ticket T-4720 -WhatIf
    .EXAMPLE
    Set-EmviaBenutzer -Kennung DE123456 -NeueOENR 0412 -NeueRollengruppe G_0412_Pflege -AlteRollengruppe G_0350_Pflege -Ticket T-4721
    #>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
    param(
        [Parameter(Mandatory)][string]$Kennung,
        [Parameter(Mandatory)][string]$Ticket,
        [string]$Vorname,
        [string]$Nachname,
        [string]$Stelle,
        [ValidatePattern('^\d{3,5}$')][string]$NeueOENR,
        [string]$NeueRollengruppe,
        [string]$AlteRollengruppe
    )
    Initialize-EmviaAD
    $u = Get-ADUser -Identity $Kennung -Properties Department, Title, DisplayName -ErrorAction Stop
    $aenderungen = [System.Collections.Generic.List[string]]::new()

    # --- Stammdaten
    $set = @{}
    if ($Vorname)  { $set.GivenName = $Vorname }
    if ($Nachname) { $set.Surname   = $Nachname }
    if ($Stelle)   { $set.Title     = $Stelle }
    if ($Vorname -or $Nachname) {
        $vn = if ($Vorname) { $Vorname } else { $u.GivenName }
        $nn = if ($Nachname) { $Nachname } else { $u.Surname }
        $set.DisplayName = "$nn, $vn"
    }
    if ($set.Count -and $PSCmdlet.ShouldProcess($u.UserPrincipalName, "Stammdaten aendern: $($set.Keys -join ', ')")) {
        # -Replace waere fuer Spezialattribute; fuer Standardfelder gibt es eigene Parameter.
        Set-ADUser -Identity $u @set
        if ($set.DisplayName) {
            # Der CN (Name im AD-Baum) aendert sich NICHT automatisch mit dem DisplayName.
            Rename-ADObject -Identity $u.DistinguishedName -NewName $set.DisplayName
        }
        $aenderungen.Add("Stammdaten: $(($set.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join '; ')")
    }

    # --- Einrichtungswechsel
    if ($NeueOENR) {
        $alteOENR = $u.Department
        $neueOU = Resolve-EmviaEinrichtungsOU -OENR $NeueOENR
        $alteG = if ($alteOENR) { Get-EmviaEinrichtungsgruppe -OENR $alteOENR } else { $null }
        $neueG = Get-EmviaEinrichtungsgruppe -OENR $NeueOENR

        if ($PSCmdlet.ShouldProcess($u.UserPrincipalName, "Wechsel $alteOENR -> $NeueOENR ($neueOU)")) {
            # Erst Gruppen, dann verschieben: Move-ADObject aendert den DN, die
            # Kennung ($Kennung) funktioniert aber weiter als Identity.
            if ($alteG) { Remove-ADGroupMember -Identity $alteG -Members $Kennung -Confirm:$false -ErrorAction SilentlyContinue }
            Add-ADGroupMember -Identity $neueG -Members $Kennung
            if ($NeueRollengruppe) {
                if ($AlteRollengruppe) { Remove-ADGroupMember -Identity $AlteRollengruppe -Members $Kennung -Confirm:$false }
                Add-ADGroupMember -Identity $NeueRollengruppe -Members $Kennung
            }
            Set-ADUser -Identity $Kennung -Department $NeueOENR
            Move-ADObject -Identity (Get-ADUser $Kennung).DistinguishedName -TargetPath $neueOU
            $aenderungen.Add("Wechsel $alteOENR->$NeueOENR; $alteG->$neueG; Rolle $AlteRollengruppe->$NeueRollengruppe")
        }
    }

    if ($aenderungen.Count) {
        Write-EmviaProtokoll -Ticket $Ticket -Aktion 'Aenderung' -Ziel $u.UserPrincipalName -Details ($aenderungen -join ' | ')
        Write-Host "Geaendert: $($aenderungen -join ' | ')" -ForegroundColor Green
    }
}

# ==============================================================================
#  3. AUSTRITT  /  LOESCHEN
# ==============================================================================

function Disable-EmviaBenutzer {
    <#
    .SYNOPSIS
    Austritt: Konto sperren, Gruppen SICHERN und entfernen, verschieben,
    aus dem Adressbuch ausblenden -- aber NICHT loeschen.
    .DESCRIPTION
    Warum nicht sofort loeschen? Ein geloeschtes Konto bekommt beim
    Wiederanlegen eine neue SID -> alle Dateirechte sind weg, das Postfach
    haengt in der Luft. Deshalb: deaktivieren, Aufbewahrungsfrist abwarten
    (Konfig AustrittAufbewahrungTage), erst dann Remove-EmviaBenutzer.

    Die Gruppenliste wird VOR dem Entfernen ins Protokoll geschrieben. Kommt
    die Person zurueck (Elternzeit-Irrtum, Wiedereinstellung), steht dort,
    was sie hatte.

    Hybrid-Hinweis: Die Sperre im lokalen AD wird per Entra Connect nach M365
    synchronisiert (bis ~30 Min). Fuer SOFORTIGE Sperre (Kuendigung mit
    Risiko) zusaetzlich -SitzungenWiderrufen (braucht Graph-Verbindung).
    .EXAMPLE
    Disable-EmviaBenutzer -Kennung DE123456 -Austrittsdatum 2026-10-31 -Ticket T-4730 -WhatIf
    .EXAMPLE
    Disable-EmviaBenutzer -Kennung DE123456 -Ticket T-4731 -PostfachZuFreigegeben -SitzungenWiderrufen
    #>
    # ConfirmImpact High: fragt IMMER nach (ausser -Confirm:$false).
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
    param(
        [Parameter(Mandatory)][string]$Kennung,
        [Parameter(Mandatory)][string]$Ticket,
        [datetime]$Austrittsdatum = (Get-Date),
        [switch]$PostfachZuFreigegeben,
        [switch]$SitzungenWiderrufen
    )
    Initialize-EmviaAD
    $k = Get-EmviaKonfig
    $u = Get-ADUser -Identity $Kennung -Properties MemberOf, Description, PrimaryGroup -ErrorAction Stop

    # MemberOf enthaelt die DNs aller direkten Gruppen -- OHNE die primaere
    # Gruppe ("Domaenen-Benutzer"), die kann man ohnehin nicht entfernen.
    $gruppen = @($u.MemberOf | ForEach-Object { (Get-ADGroup $_).Name })
    Write-Host "Gruppen von $($u.Name): $($gruppen -join ', ')"

    if (-not $PSCmdlet.ShouldProcess($u.UserPrincipalName, "Austritt zum $($Austrittsdatum.ToString('dd.MM.yyyy')): sperren, $($gruppen.Count) Gruppen entfernen, nach $($k.AustrittOU)")) { return }

    # Sicherung zuerst -- falls danach etwas abbricht, ist die Liste schon da.
    Write-EmviaProtokoll -Ticket $Ticket -Aktion 'Austritt-Gruppensicherung' -Ziel $u.UserPrincipalName -Details ($gruppen -join ',')

    Disable-ADAccount -Identity $Kennung
    Write-Host '[1] Konto deaktiviert' -ForegroundColor Green

    foreach ($g in $u.MemberOf) {
        Remove-ADGroupMember -Identity $g -Members $Kennung -Confirm:$false
    }
    Write-Host "[2] $($gruppen.Count) Gruppen entfernt (Lizenzgruppen eingeschlossen -> Lizenz wird frei)"

    # Beschreibung mit Datum + Ticket -> spaeter sieht jeder, warum das Konto gesperrt ist.
    $neu = "AUSTRITT $($Austrittsdatum.ToString('yyyy-MM-dd')) $Ticket | $($u.Description)"
    # -Replace @{ attribut = wert } setzt beliebige LDAP-Attribute.
    # msExchHideFromAddressLists blendet das Konto im Adressbuch aus (wird bei Hybrid synchronisiert).
    Set-ADUser -Identity $Kennung -Description $neu -Replace @{ msExchHideFromAddressLists = $true }
    Write-Host '[3] Beschreibung gesetzt, aus Adressbuch ausgeblendet'

    Move-ADObject -Identity $u.DistinguishedName -TargetPath $k.AustrittOU
    Write-Host "[4] Verschoben nach $($k.AustrittOU)"

    if ($PostfachZuFreigegeben) {
        # Postfach bleibt fuer Vorgesetzte/Vertretung erreichbar, braucht als
        # freigegebenes Postfach (bis 50 GB) keine Lizenz.
        # Hybrid: in Exchange Online Set-Mailbox -Type Shared, danach lokal
        # Set-RemoteMailbox -Type Shared (Exchange 2016 CU-aktuell), damit das AD stimmt.
        Assert-EmviaBefehl Set-Mailbox 'Exchange-Verbindung fehlt (Connect-ExchangeOnline oder EMS).'
        Set-Mailbox -Identity $u.UserPrincipalName -Type Shared
        if (Get-Command Set-RemoteMailbox -ErrorAction SilentlyContinue) { Set-RemoteMailbox -Identity $Kennung -Type Shared }
        Write-Host '[5] Postfach -> freigegebenes Postfach'
    }
    if ($SitzungenWiderrufen) {
        Assert-EmviaBefehl Revoke-MgUserSignInSession 'Connect-MgGraph -Scopes User.RevokeSessions.All ausfuehren.'
        Revoke-MgUserSignInSession -UserId $u.UserPrincipalName | Out-Null
        Write-Host '[6] Alle M365-Sitzungen widerrufen (Handy-Outlook/Teams fliegen sofort raus)'
    }

    Write-EmviaProtokoll -Ticket $Ticket -Aktion 'Austritt' -Ziel $u.UserPrincipalName `
        -Details "Datum=$($Austrittsdatum.ToString('yyyy-MM-dd')); Shared=$([bool]$PostfachZuFreigegeben); Sitzungen=$([bool]$SitzungenWiderrufen)"
    Write-Host 'Offen (manuell): Geraete zurueck, Fachanwendungen (SAP/Vivendi...) laut Checkliste, Ticket schliessen.' -ForegroundColor Yellow
}

function Remove-EmviaBenutzer {
    <#
    .SYNOPSIS
    Loescht ein ausgetretenes Konto ENDGUELTIG -- nur, wenn es deaktiviert ist,
    in der Austritt-OU liegt und die Aufbewahrungsfrist abgelaufen ist.
    .DESCRIPTION
    Die drei Pruefungen sind Absicht: Ein Tippfehler in der Kennung soll nie
    ein aktives Konto loeschen. Mit aktiviertem AD-Papierkorb laesst sich das
    Objekt noch 180 Tage wiederherstellen (Restore-ADObject), sonst nicht.
    .EXAMPLE
    Remove-EmviaBenutzer -Kennung DE123456 -Ticket T-4800 -WhatIf
    #>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
    param(
        [Parameter(Mandatory)][string]$Kennung,
        [Parameter(Mandatory)][string]$Ticket
    )
    Initialize-EmviaAD
    $k = Get-EmviaKonfig
    $u = Get-ADUser -Identity $Kennung -Properties whenChanged, Enabled -ErrorAction Stop

    if ($u.Enabled) { throw 'Konto ist noch AKTIV -- erst Disable-EmviaBenutzer.' }
    if ($u.DistinguishedName -notlike "*$($k.AustrittOU)") { throw "Konto liegt nicht in $($k.AustrittOU)." }
    $tage = ((Get-Date) - $u.whenChanged).Days
    if ($tage -lt $k.AustrittAufbewahrungTage) {
        throw "Erst $tage von $($k.AustrittAufbewahrungTage) Tagen Aufbewahrung vergangen."
    }

    if ($PSCmdlet.ShouldProcess($u.UserPrincipalName, 'ENDGUELTIG loeschen')) {
        Remove-ADUser -Identity $Kennung -Confirm:$false
        Write-EmviaProtokoll -Ticket $Ticket -Aktion 'Loeschung' -Ziel $u.UserPrincipalName -Details "Aufbewahrung $tage Tage"
        Write-Host 'Geloescht.' -ForegroundColor Green
    }
}

# ==============================================================================
#  4. KENNWORT, SPERRE, DIAGNOSE
# ==============================================================================

function Get-EmviaKontoStatus {
    <#
    .SYNOPSIS
    Nur lesen: Ist das Konto aktiv, gesperrt, abgelaufen? Wann zuletzt angemeldet?
    .DESCRIPTION
    IMMER zuerst ausfuehren, bevor man ein Kennwort zuruecksetzt -- oft ist
    das Konto nur gesperrt oder abgelaufen (Fremdpersonal!), und ein Reset
    waere unnoetig.
    LastLogonDate (lastLogonTimestamp) wird nur alle 9-14 Tage repliziert,
    ist also ungenau -- fuer "ist der Account noch in Benutzung" reicht das.
    .EXAMPLE
    Get-EmviaKontoStatus DE123456
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory, Position = 0)][string]$Kennung)
    Initialize-EmviaAD
    $u = Get-ADUser -Identity $Kennung -Properties Enabled, LockedOut, BadLogonCount, LastBadPasswordAttempt,
        PasswordLastSet, PasswordExpired, AccountExpirationDate, LastLogonDate, Description, Department, MemberOf
    [pscustomobject]@{
        Name             = $u.Name
        UPN              = $u.UserPrincipalName
        Aktiv            = $u.Enabled
        Gesperrt         = $u.LockedOut
        Fehlversuche     = $u.BadLogonCount            # pro DC! Get-EmviaSperrquelle fuer die Quelle
        LetzterFehler    = $u.LastBadPasswordAttempt
        KennwortGesetzt  = $u.PasswordLastSet          # leer = "bei naechster Anmeldung aendern" aktiv
        KennwortAbgelauf = $u.PasswordExpired
        KontoLaeuftAb    = $u.AccountExpirationDate
        LetzteAnmeldung  = $u.LastLogonDate
        OENR             = $u.Department
        Beschreibung     = $u.Description
        Gruppen          = ($u.MemberOf | ForEach-Object { ($_ -split ',')[0] -replace '^CN=' }) -join ', '
    }
}

function Unlock-EmviaKonto {
    <#
    .SYNOPSIS
    Entsperrt ein gesperrtes AD-Konto (Kennwort bleibt unveraendert).
    .DESCRIPTION
    Sperrt sich das Konto immer wieder, steckt fast immer ein ALTES Kennwort
    irgendwo fest (Handy-Mail, gespeicherte Anmeldeinformation, Netzlaufwerk,
    zweiter PC). Dann zuerst Get-EmviaSperrquelle -- Entsperren allein hilft
    nur Minuten.
    .EXAMPLE
    Unlock-EmviaKonto -Kennung DE123456 -Ticket T-4740
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$Kennung,
        [Parameter(Mandatory)][string]$Ticket
    )
    Initialize-EmviaAD
    $u = Get-ADUser -Identity $Kennung -Properties LockedOut
    if (-not $u.LockedOut) { Write-Host 'Konto ist nicht gesperrt -- nichts zu tun.'; return }
    if ($PSCmdlet.ShouldProcess($u.UserPrincipalName, 'Entsperren')) {
        Unlock-ADAccount -Identity $Kennung
        Write-EmviaProtokoll -Ticket $Ticket -Aktion 'Entsperren' -Ziel $u.UserPrincipalName
        Write-Host 'Entsperrt.' -ForegroundColor Green
    }
}

function Get-EmviaSperrquelle {
    <#
    .SYNOPSIS
    Findet heraus, VON WELCHEM RECHNER die Kontosperre ausgeloest wurde.
    .DESCRIPTION
    Jede Sperre wird auf dem PDC-Emulator als Ereignis 4740 protokolliert.
    Im Feld "Aufrufername" (TargetDomainName im XML) steht der Rechner, der
    das falsche Kennwort geschickt hat. Braucht Leserechte auf das
    Sicherheitsprotokoll des DCs (Ereignisprotokollleser).
    .EXAMPLE
    Get-EmviaSperrquelle -Kennung DE123456 -Stunden 24
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Kennung, [int]$Stunden = 24)
    Initialize-EmviaAD
    $pdc = (Get-ADDomain).PDCEmulator
    # FilterHashtable filtert AUF dem Server -- viel schneller als Where-Object.
    Get-WinEvent -ComputerName $pdc -FilterHashtable @{
        LogName = 'Security'; Id = 4740; StartTime = (Get-Date).AddHours(-$Stunden)
    } -ErrorAction SilentlyContinue |
        Where-Object { $_.Properties[0].Value -eq $Kennung } |
        Select-Object TimeCreated,
            @{ n = 'Konto';  e = { $_.Properties[0].Value } },
            @{ n = 'Quelle'; e = { $_.Properties[1].Value } }   # Rechnername
}

function Reset-EmviaKennwort {
    <#
    .SYNOPSIS
    Setzt ein Kennwort zurueck -- NUR nach dokumentierter Identitaetspruefung.
    .DESCRIPTION
    EMVIA-Regel (Einarbeitung, M1): Kennwort-Resets ausschliesslich
      a) auf Anforderung aus dem Funktionspostfach der Einrichtungsleitung, oder
      b) mit Rueckruf an die bekannte Durchwahl (aus dem Telefonverzeichnis,
         NICHT die Nummer, die der Anrufer nennt).
    Deshalb sind -Pruefweg und -Nachweis Pflicht. Ohne sie startet die
    Funktion gar nicht -- man KANN die Regel nicht vergessen.
    Das neue Kennwort ist ein Einmalkennwort (aendern bei naechster Anmeldung).
    Ein gesperrtes Konto wird gleich mit entsperrt.
    Hybrid: Das Kennwort wird ins lokale AD geschrieben und per
    Kennwort-Hash-Sync nach M365 uebertragen (ca. 2 Minuten).
    .EXAMPLE
    Reset-EmviaKennwort -Kennung DE123456 -Ticket T-4741 -Pruefweg RueckrufDurchwahl `
        -Nachweis 'Rueckruf 040-1234-567 (Telefonliste), 10:42, Identitaet bestaetigt'
    #>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
    param(
        [Parameter(Mandatory)][string]$Kennung,
        [Parameter(Mandatory)][string]$Ticket,
        [Parameter(Mandatory)][ValidateSet('FunktionspostfachEL', 'RueckrufDurchwahl')][string]$Pruefweg,
        [Parameter(Mandatory)][ValidateLength(15, 500)][string]$Nachweis   # min. 15 Zeichen -> kein "ok"
    )
    Initialize-EmviaAD
    $u = Get-ADUser -Identity $Kennung -Properties LockedOut, Enabled
    if (-not $u.Enabled) { throw 'Konto ist deaktiviert (Austritt?) -- kein Reset, erst Ticket klaeren.' }

    if (-not $PSCmdlet.ShouldProcess($u.UserPrincipalName, "Kennwort zuruecksetzen (Pruefweg: $Pruefweg)")) { return }

    $kennwort = New-EmviaStartkennwort
    # -Reset = Admin-Reset ohne altes Kennwort. Ohne -Reset wuerde das alte verlangt.
    Set-ADAccountPassword -Identity $Kennung -Reset -NewPassword (ConvertTo-SecureString $kennwort -AsPlainText -Force)
    Set-ADUser -Identity $Kennung -ChangePasswordAtLogon $true
    if ($u.LockedOut) { Unlock-ADAccount -Identity $Kennung; Write-Host 'Konto war gesperrt -> entsperrt.' }

    Write-EmviaProtokoll -Ticket $Ticket -Aktion 'Kennwort-Reset' -Ziel $u.UserPrincipalName -Pruefweg "$Pruefweg | $Nachweis"
    Write-Host "Einmalkennwort: $kennwort" -ForegroundColor Yellow
    Write-Host 'Mitteilung nur ueber den geprueften Weg (Rueckruf / Antwort an Funktionspostfach EL).' -ForegroundColor Yellow
}

# ==============================================================================
#  5. GRUPPEN / RECHTE (AD)
# ==============================================================================

function Get-EmviaBenutzerGruppen {
    <#
    .SYNOPSIS
    Zeigt direkte UND verschachtelte Gruppen eines Benutzers.
    .DESCRIPTION
    MemberOf zeigt nur direkte Gruppen. Rechte kommen oft ueber
    Verschachtelung (Benutzer -> G_0350 -> Fileshare-Gruppe). Der LDAP-Filter
    mit der OID 1.2.840.113556.1.4.1941 ("LDAP_MATCHING_RULE_IN_CHAIN")
    loest die ganze Kette auf -- das ist der Standardtrick dafuer.
    .EXAMPLE
    Get-EmviaBenutzerGruppen DE123456
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory, Position = 0)][string]$Kennung)
    Initialize-EmviaAD
    $u = Get-ADUser -Identity $Kennung -Properties MemberOf
    $direkt = @($u.MemberOf)
    Get-ADGroup -LDAPFilter "(member:1.2.840.113556.1.4.1941:=$($u.DistinguishedName))" |
        Sort-Object Name |
        Select-Object Name, @{ n = 'Art'; e = { if ($direkt -contains $_.DistinguishedName) { 'direkt' } else { 'verschachtelt' } } }
}

function Add-EmviaGruppenmitglied {
    <#
    .SYNOPSIS
    Nimmt einen Benutzer in eine Gruppe auf (mit Protokoll).
    .EXAMPLE
    Add-EmviaGruppenmitglied -Kennung DE123456 -Gruppe G_0350_PDL -Ticket T-4750
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$Kennung,
        [Parameter(Mandatory)][string]$Gruppe,
        [Parameter(Mandatory)][string]$Ticket
    )
    Initialize-EmviaAD
    $null = Get-ADGroup $Gruppe -ErrorAction Stop
    if ($PSCmdlet.ShouldProcess("$Kennung -> $Gruppe", 'Gruppenmitgliedschaft hinzufuegen')) {
        Add-ADGroupMember -Identity $Gruppe -Members $Kennung
        Write-EmviaProtokoll -Ticket $Ticket -Aktion 'Gruppe+' -Ziel $Kennung -Details $Gruppe
        Write-Host "+ $Gruppe (wirkt erst nach neuer Anmeldung -- Kerberos-Ticket enthaelt die Gruppen)" -ForegroundColor Green
    }
}

function Remove-EmviaGruppenmitglied {
    <#
    .SYNOPSIS
    Entzieht eine Gruppenmitgliedschaft (= Recht entziehen), mit Protokoll.
    .EXAMPLE
    Remove-EmviaGruppenmitglied -Kennung DE123456 -Gruppe G_0350_PDL -Ticket T-4751
    #>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
    param(
        [Parameter(Mandatory)][string]$Kennung,
        [Parameter(Mandatory)][string]$Gruppe,
        [Parameter(Mandatory)][string]$Ticket
    )
    Initialize-EmviaAD
    if ($PSCmdlet.ShouldProcess("$Kennung aus $Gruppe", 'Gruppenmitgliedschaft entfernen')) {
        Remove-ADGroupMember -Identity $Gruppe -Members $Kennung -Confirm:$false
        Write-EmviaProtokoll -Ticket $Ticket -Aktion 'Gruppe-' -Ziel $Kennung -Details $Gruppe
        Write-Host "- $Gruppe" -ForegroundColor Green
    }
}

# ==============================================================================
#  6. FUNKTIONSPOSTFAECHER (freigegebene Postfaecher) und RECHTE
# ==============================================================================
#  Drei verschiedene Rechte -- die Unterscheidung wird gern gefragt:
#    Vollzugriff (FullAccess) .... Postfach oeffnen, lesen, loeschen
#    Senden als (SendAs) ......... Mail kommt "von it@emvia.de", Empfaenger sieht
#                                  den Absender NICHT
#    Senden im Auftrag (SendOnBehalf) "Anna Muster im Auftrag von it@emvia.de"
#  Wo wird das Recht gesetzt?
#    Postfach in Exchange Online -> in der EXO-Shell (Connect-ExchangeOnline)
#    Postfach lokal              -> in der Exchange Management Shell
#  Senden als heisst in EXO Add-RecipientPermission, lokal Add-ADPermission.
# ------------------------------------------------------------------------------

function Get-EmviaPostfachUmgebung {
    # Erkennt an den verfuegbaren Befehlen, wo wir verbunden sind.
    if (Get-Command Add-RecipientPermission -ErrorAction SilentlyContinue) { return 'Online' }
    if (Get-Command Add-ADPermission -ErrorAction SilentlyContinue)        { return 'Lokal' }
    throw 'Keine Exchange-Verbindung. Connect-ExchangeOnline oder Exchange Management Shell starten.'
}

function New-EmviaFunktionspostfach {
    <#
    .SYNOPSIS
    Legt ein Funktionspostfach (freigegebenes Postfach) an, z. B. el-0350@emvia.de.
    .DESCRIPTION
    Freigegebene Postfaecher haben ein deaktiviertes AD-Konto, man meldet sich
    nie direkt an -- Zugriff nur ueber Rechte. Bis 50 GB ohne Lizenz.
    Hybrid: New-RemoteMailbox -Shared auf dem lokalen Exchange (Objekt entsteht
    im AD und wird synchronisiert). Cloud: New-Mailbox -Shared in EXO.
    .EXAMPLE
    New-EmviaFunktionspostfach -Alias el-0350 -Anzeigename 'Einrichtungsleitung 0350' -OENR 0350 -Ticket T-4760 -WhatIf
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][ValidatePattern('^[a-z0-9\-\.]+$')][string]$Alias,
        [Parameter(Mandatory)][string]$Anzeigename,
        [Parameter(Mandatory)][string]$Ticket,
        [string]$OENR,
        [ValidateSet('Hybrid', 'Cloud', 'Lokal')][string]$Art = 'Hybrid'
    )
    $k = Get-EmviaKonfig
    $adresse = "$Alias@$($k.MailDomain)"
    if (-not $PSCmdlet.ShouldProcess($adresse, "Funktionspostfach anlegen ($Art)")) { return }

    switch ($Art) {
        'Hybrid' {
            Assert-EmviaBefehl New-RemoteMailbox 'Auf dem lokalen Exchange (EMS) ausfuehren.'
            $ou = if ($OENR) { Resolve-EmviaEinrichtungsOU -OENR $OENR } else { $k.FunktionspostfachOU }
            New-RemoteMailbox -Shared -Name $Anzeigename -Alias $Alias -UserPrincipalName $adresse `
                -PrimarySmtpAddress $adresse -RemoteRoutingAddress "$Alias@$($k.RoutingDomain)" -OnPremisesOrganizationalUnit $ou | Out-Null
        }
        'Cloud' {
            Assert-EmviaBefehl New-Mailbox 'Connect-ExchangeOnline fehlt.'
            New-Mailbox -Shared -Name $Anzeigename -Alias $Alias -PrimarySmtpAddress $adresse | Out-Null
        }
        'Lokal' {
            Assert-EmviaBefehl New-Mailbox 'Exchange Management Shell fehlt.'
            New-Mailbox -Shared -Name $Anzeigename -Alias $Alias -PrimarySmtpAddress $adresse `
                -OrganizationalUnit $k.FunktionspostfachOU | Out-Null
        }
    }
    Write-EmviaProtokoll -Ticket $Ticket -Aktion 'Funktionspostfach-Neu' -Ziel $adresse -Details "Art=$Art"
    Write-Host "Angelegt: $adresse. Rechte jetzt mit Grant-EmviaPostfachRecht vergeben." -ForegroundColor Green
}

function Grant-EmviaPostfachRecht {
    <#
    .SYNOPSIS
    Vergibt Vollzugriff, Senden als oder Senden im Auftrag auf ein Postfach.
    .DESCRIPTION
    Best Practice: Rechte an eine Gruppe (z. B. P_el-0350) statt an Personen
    vergeben -- dann ist Rechtepflege = Gruppenpflege. Achtung: AutoMapping
    (Postfach erscheint automatisch in Outlook) funktioniert NUR bei direkt
    berechtigten Benutzern, nicht ueber Gruppen.
    .EXAMPLE
    Grant-EmviaPostfachRecht -Postfach el-0350@emvia.de -Benutzer DE123456@emvia.de -Recht Vollzugriff,SendenAls -Ticket T-4761 -WhatIf
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$Postfach,
        [Parameter(Mandatory)][string]$Benutzer,
        [Parameter(Mandatory)][ValidateSet('Vollzugriff', 'SendenAls', 'SendenImAuftrag')][string[]]$Recht,
        [Parameter(Mandatory)][string]$Ticket,
        [bool]$AutoMapping = $true
    )
    $umg = Get-EmviaPostfachUmgebung
    foreach ($r in $Recht) {
        if (-not $PSCmdlet.ShouldProcess("$Benutzer auf $Postfach", "$r vergeben ($umg)")) { continue }
        switch ($r) {
            'Vollzugriff' {
                Add-MailboxPermission -Identity $Postfach -User $Benutzer -AccessRights FullAccess -InheritanceType All -AutoMapping $AutoMapping | Out-Null
            }
            'SendenAls' {
                if ($umg -eq 'Online') {
                    Add-RecipientPermission -Identity $Postfach -Trustee $Benutzer -AccessRights SendAs -Confirm:$false | Out-Null
                } else {
                    Add-ADPermission -Identity $Postfach -User $Benutzer -ExtendedRights 'Send As' | Out-Null
                }
            }
            'SendenImAuftrag' {
                # @{Add=...} ergaenzt die Liste, statt sie zu ueberschreiben!
                Set-Mailbox -Identity $Postfach -GrantSendOnBehalfTo @{ Add = $Benutzer }
            }
        }
        Write-EmviaProtokoll -Ticket $Ticket -Aktion "Postfachrecht+ $r" -Ziel $Postfach -Details $Benutzer
        Write-Host "+ $r fuer $Benutzer auf $Postfach" -ForegroundColor Green
    }
    Write-Host 'Hinweis: In Outlook sichtbar nach bis zu 60 Min (AutoMapping), Senden als ggf. erst nach Outlook-Neustart.'
}

function Revoke-EmviaPostfachRecht {
    <#
    .SYNOPSIS
    Entzieht Postfachrechte (Gegenstueck zu Grant-EmviaPostfachRecht).
    .DESCRIPTION
    Ohne -Recht werden ALLE drei Rechte entzogen -- typisch bei Stellenwechsel.
    Nach dem Entzug von Vollzugriff bleibt das Postfach in Outlook manchmal
    sichtbar (Cache), bis Outlook neu startet.
    .EXAMPLE
    Revoke-EmviaPostfachRecht -Postfach el-0350@emvia.de -Benutzer DE123456@emvia.de -Ticket T-4762 -WhatIf
    #>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
    param(
        [Parameter(Mandatory)][string]$Postfach,
        [Parameter(Mandatory)][string]$Benutzer,
        [Parameter(Mandatory)][string]$Ticket,
        [ValidateSet('Vollzugriff', 'SendenAls', 'SendenImAuftrag')][string[]]$Recht = @('Vollzugriff', 'SendenAls', 'SendenImAuftrag')
    )
    $umg = Get-EmviaPostfachUmgebung
    foreach ($r in $Recht) {
        if (-not $PSCmdlet.ShouldProcess("$Benutzer auf $Postfach", "$r entziehen ($umg)")) { continue }
        switch ($r) {
            'Vollzugriff' {
                Remove-MailboxPermission -Identity $Postfach -User $Benutzer -AccessRights FullAccess -InheritanceType All -Confirm:$false -ErrorAction SilentlyContinue
            }
            'SendenAls' {
                if ($umg -eq 'Online') {
                    Remove-RecipientPermission -Identity $Postfach -Trustee $Benutzer -AccessRights SendAs -Confirm:$false -ErrorAction SilentlyContinue
                } else {
                    Remove-ADPermission -Identity $Postfach -User $Benutzer -ExtendedRights 'Send As' -Confirm:$false -ErrorAction SilentlyContinue
                }
            }
            'SendenImAuftrag' {
                Set-Mailbox -Identity $Postfach -GrantSendOnBehalfTo @{ Remove = $Benutzer }
            }
        }
        Write-EmviaProtokoll -Ticket $Ticket -Aktion "Postfachrecht- $r" -Ziel $Postfach -Details $Benutzer
        Write-Host "- $r fuer $Benutzer auf $Postfach" -ForegroundColor Green
    }
}

function Get-EmviaPostfachRechte {
    <#
    .SYNOPSIS
    Nur lesen: Wer hat welche Rechte auf ein Postfach?
    .DESCRIPTION
    Filtert System-Eintraege (NT AUTHORITY\SELF, geerbte Admin-Rechte) heraus,
    damit nur die echten, vergebenen Rechte uebrig bleiben. Vor jedem Entzug
    ausfuehren und als Nachweis ins Ticket kopieren.
    .EXAMPLE
    Get-EmviaPostfachRechte el-0350@emvia.de
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory, Position = 0)][string]$Postfach)
    $umg = Get-EmviaPostfachUmgebung

    Get-MailboxPermission -Identity $Postfach |
        Where-Object { -not $_.IsInherited -and $_.User -notlike 'NT AUTHORITY\*' -and $_.User -notlike 'S-1-5-*' } |
        ForEach-Object { [pscustomobject]@{ Recht = 'Vollzugriff'; Wer = "$($_.User)" } }

    if ($umg -eq 'Online') {
        Get-RecipientPermission -Identity $Postfach |
            Where-Object { $_.Trustee -notlike 'NT AUTHORITY\*' } |
            ForEach-Object { [pscustomobject]@{ Recht = 'SendenAls'; Wer = "$($_.Trustee)" } }
    } else {
        Get-ADPermission -Identity $Postfach |
            Where-Object { $_.ExtendedRights -like '*Send-As*' -and -not $_.IsInherited -and $_.User -notlike 'NT AUTHORITY\*' } |
            ForEach-Object { [pscustomobject]@{ Recht = 'SendenAls'; Wer = "$($_.User)" } }
    }

    (Get-Mailbox -Identity $Postfach).GrantSendOnBehalfTo |
        ForEach-Object { [pscustomobject]@{ Recht = 'SendenImAuftrag'; Wer = "$_" } }
}

# ==============================================================================
#  7. MICROSOFT 365 (Graph): MFA und Lizenzen
# ==============================================================================
#  Rolle laut Einarbeitung: "Authentifizierungs- und Benutzeradministrator".
#  Verbinden mit minimalen Rechten (Least Privilege):
#    Connect-MgGraph -Scopes 'UserAuthenticationMethod.ReadWrite.All','User.ReadWrite.All','Organization.Read.All'
# ------------------------------------------------------------------------------

function Get-EmviaMfaStatus {
    <#
    .SYNOPSIS
    Nur lesen: Welche Anmeldemethoden hat ein Benutzer registriert?
    .EXAMPLE
    Get-EmviaMfaStatus DE123456@emvia.de
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory, Position = 0)][string]$Upn)
    Assert-EmviaBefehl Get-MgUserAuthenticationMethod 'Microsoft.Graph installieren und Connect-MgGraph ausfuehren.'
    Get-MgUserAuthenticationMethod -UserId $Upn | ForEach-Object {
        # Der Methodentyp steckt im OData-Typ, z. B. #microsoft.graph.phoneAuthenticationMethod
        # Kein "??"-Operator: der existiert erst ab PowerShell 7, die Exchange
        # Management Shell laeuft aber unter Windows PowerShell 5.1.
        $detail = $_.AdditionalProperties['displayName']
        if (-not $detail) { $detail = $_.AdditionalProperties['phoneNumber'] }
        [pscustomobject]@{
            Methode = $_.AdditionalProperties['@odata.type'] -replace '#microsoft.graph.', '' -replace 'AuthenticationMethod$', ''
            Detail  = $detail
            Id      = $_.Id
        }
    }
}

function Reset-EmviaMfa {
    <#
    .SYNOPSIS
    MFA-Reset (z. B. neues Handy): alte Methoden entfernen, optional einen
    befristeten Zugriffspass (TAP) ausstellen. Identitaetspruefung Pflicht.
    .DESCRIPTION
    Warum TAP statt Methoden einfach loeschen? Ohne Methode kann sich der
    Nutzer zwar neu registrieren -- aber das koennte auch ein Angreifer mit
    dem Kennwort. Der TAP (60 Min, einmalig) geht ueber den geprueften Weg an
    die Person, damit registriert sie Authenticator/Passkey selbst neu.
    Die Kennwort-Methode (password) wird nie entfernt.
    .EXAMPLE
    Reset-EmviaMfa -Upn DE123456@emvia.de -Ticket T-4770 -Pruefweg RueckrufDurchwahl `
        -Nachweis 'Rueckruf 040-1234-567 laut Telefonliste, 11:05' -TapAusstellen -WhatIf
    #>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
    param(
        [Parameter(Mandatory)][string]$Upn,
        [Parameter(Mandatory)][string]$Ticket,
        [Parameter(Mandatory)][ValidateSet('FunktionspostfachEL', 'RueckrufDurchwahl')][string]$Pruefweg,
        [Parameter(Mandatory)][ValidateLength(15, 500)][string]$Nachweis,
        [switch]$TapAusstellen,
        [ValidateRange(10, 480)][int]$TapMinuten = 60
    )
    Assert-EmviaBefehl Get-MgUserAuthenticationMethod 'Connect-MgGraph -Scopes UserAuthenticationMethod.ReadWrite.All'

    # Je Methodentyp gibt es ein eigenes Loesch-Cmdlet -- Zuordnungstabelle:
    $loeschen = @{
        'microsoftAuthenticatorAuthenticationMethod'  = { param($u, $id) Remove-MgUserAuthenticationMicrosoftAuthenticatorMethod -UserId $u -MicrosoftAuthenticatorAuthenticationMethodId $id }
        'phoneAuthenticationMethod'                   = { param($u, $id) Remove-MgUserAuthenticationPhoneMethod -UserId $u -PhoneAuthenticationMethodId $id }
        'fido2AuthenticationMethod'                   = { param($u, $id) Remove-MgUserAuthenticationFido2Method -UserId $u -Fido2AuthenticationMethodId $id }
        'softwareOathAuthenticationMethod'            = { param($u, $id) Remove-MgUserAuthenticationSoftwareOathMethod -UserId $u -SoftwareOathAuthenticationMethodId $id }
        'emailAuthenticationMethod'                   = { param($u, $id) Remove-MgUserAuthenticationEmailMethod -UserId $u -EmailAuthenticationMethodId $id }
        'windowsHelloForBusinessAuthenticationMethod' = { param($u, $id) Remove-MgUserAuthenticationWindowsHelloForBusinessMethod -UserId $u -WindowsHelloForBusinessAuthenticationMethodId $id }
        'temporaryAccessPassAuthenticationMethod'     = { param($u, $id) Remove-MgUserAuthenticationTemporaryAccessPassMethod -UserId $u -TemporaryAccessPassAuthenticationMethodId $id }
    }

    $methoden = Get-MgUserAuthenticationMethod -UserId $Upn
    $entfernt = @()
    foreach ($m in $methoden) {
        $typ = $m.AdditionalProperties['@odata.type'] -replace '#microsoft.graph.', ''
        if ($typ -eq 'passwordAuthenticationMethod') { continue }
        if (-not $loeschen.ContainsKey($typ)) { Write-Warning "Unbekannter Typ $typ -- im Portal pruefen."; continue }
        if ($PSCmdlet.ShouldProcess($Upn, "Methode entfernen: $typ")) {
            & $loeschen[$typ] $Upn $m.Id      # & = Skriptblock ausfuehren
            $entfernt += $typ
        }
    }

    $tapText = ''
    if ($TapAusstellen -and $PSCmdlet.ShouldProcess($Upn, "TAP ausstellen ($TapMinuten Min, einmalig)")) {
        $tap = New-MgUserAuthenticationTemporaryAccessPassMethod -UserId $Upn -BodyParameter @{
            lifetimeInMinutes = $TapMinuten
            isUsableOnce      = $true
        }
        $tapText = $tap.TemporaryAccessPass
    }

    if ($entfernt -or $tapText) {
        Write-EmviaProtokoll -Ticket $Ticket -Aktion 'MFA-Reset' -Ziel $Upn `
            -Details "Entfernt=$($entfernt -join ','); TAP=$([bool]$tapText)" -Pruefweg "$Pruefweg | $Nachweis"
        Write-Host "Entfernt: $($entfernt -join ', ')" -ForegroundColor Green
        if ($tapText) {
            Write-Host "TAP: $tapText  (gueltig $TapMinuten Min, nur ueber den geprueften Weg mitteilen)" -ForegroundColor Yellow
            Write-Host 'Nutzer: https://aka.ms/mysecurityinfo -> mit TAP anmelden -> Authenticator neu einrichten.'
        }
    }
}

function Set-EmviaLizenz {
    <#
    .SYNOPSIS
    Weist eine M365-Lizenz direkt zu oder entzieht sie.
    .DESCRIPTION
    ZUERST klaeren: Vergibt EMVIA Lizenzen ueber Gruppen? Dann ist das der
    richtige Weg (Add-EmviaGruppenmitglied mit der Lizenzgruppe), und direkte
    Zuweisungen erzeugen nur Wildwuchs. Diese Funktion ist fuer Ausnahmen.
    Ohne UsageLocation (Nutzungsstandort) schlaegt jede Zuweisung fehl --
    deshalb wird sie bei Bedarf auf 'DE' gesetzt.
    SkuPartNumber ist der technische Name, z. B. SPE_E3, SPE_F1, ENTERPRISEPACK.
    Get-MgSubscribedSku | Select SkuPartNumber, ConsumedUnits zeigt den Bestand.
    .EXAMPLE
    Set-EmviaLizenz -Upn DE123456@emvia.de -SkuPartNumber SPE_F1 -Ticket T-4780 -WhatIf
    .EXAMPLE
    Set-EmviaLizenz -Upn DE123456@emvia.de -SkuPartNumber SPE_F1 -Entziehen -Ticket T-4781
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$Upn,
        [Parameter(Mandatory)][string]$SkuPartNumber,
        [Parameter(Mandatory)][string]$Ticket,
        [switch]$Entziehen
    )
    Assert-EmviaBefehl Set-MgUserLicense 'Connect-MgGraph -Scopes User.ReadWrite.All,Organization.Read.All'
    $sku = Get-MgSubscribedSku | Where-Object SkuPartNumber -eq $SkuPartNumber
    if (-not $sku) { throw "Lizenz $SkuPartNumber nicht im Mandanten. Get-MgSubscribedSku zeigt die vorhandenen." }

    $frei = $sku.PrepaidUnits.Enabled - $sku.ConsumedUnits
    if (-not $Entziehen -and $frei -le 0) { throw "Keine freien $SkuPartNumber-Lizenzen ($($sku.ConsumedUnits) belegt)." }

    $u = Get-MgUser -UserId $Upn -Property Id, UsageLocation
    $aktion = if ($Entziehen) { 'entziehen' } else { "zuweisen (frei: $frei)" }
    if (-not $PSCmdlet.ShouldProcess($Upn, "$SkuPartNumber $aktion")) { return }

    if (-not $Entziehen -and -not $u.UsageLocation) {
        Update-MgUser -UserId $u.Id -UsageLocation 'DE'
        Write-Host 'Nutzungsstandort DE gesetzt (Pflicht fuer Lizenzen).'
    }
    if ($Entziehen) {
        Set-MgUserLicense -UserId $u.Id -AddLicenses @() -RemoveLicenses @($sku.SkuId) | Out-Null
    } else {
        Set-MgUserLicense -UserId $u.Id -AddLicenses @(@{ SkuId = $sku.SkuId }) -RemoveLicenses @() | Out-Null
    }
    Write-EmviaProtokoll -Ticket $Ticket -Aktion "Lizenz $(if ($Entziehen) { '-' } else { '+' })" -Ziel $Upn -Details $SkuPartNumber
    Write-Host "$SkuPartNumber $aktion -- erledigt." -ForegroundColor Green
}

# ==============================================================================
#  8. NACHWEIS fuer die Abnahme / das Ticket
# ==============================================================================

function Get-EmviaProtokoll {
    <#
    .SYNOPSIS
    Zeigt das Aenderungsprotokoll, gefiltert nach Ticket, Ziel oder Zeitraum.
    .EXAMPLE
    Get-EmviaProtokoll -Ticket T-4711
    .EXAMPLE
    Get-EmviaProtokoll -Seit (Get-Date).AddDays(-14) | Group-Object Aktion | Select Name, Count
    # -> Nachweis fuer M1: "je 3 Neuanlagen, Aenderungen, Austritte"
    #>
    [CmdletBinding()]
    param([string]$Ticket, [string]$Ziel, [datetime]$Seit)
    $k = Get-EmviaKonfig
    if (-not (Test-Path $k.ProtokollPfad)) { Write-Host 'Noch kein Protokoll.'; return }
    $eintraege = Import-Csv $k.ProtokollPfad -Delimiter ';' -Encoding UTF8
    if ($Ticket) { $eintraege = $eintraege | Where-Object Ticket -eq $Ticket }
    if ($Ziel)   { $eintraege = $eintraege | Where-Object Ziel -like "*$Ziel*" }
    if ($Seit)   { $eintraege = $eintraege | Where-Object { [datetime]$_.Zeit -ge $Seit } }
    $eintraege
}
