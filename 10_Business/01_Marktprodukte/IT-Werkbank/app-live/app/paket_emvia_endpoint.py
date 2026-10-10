"""
Vorlagen-Paket "EMVIA · Intune/Endpoint-Werkzeuge".

Ideen nach github.com/tomwechsler/Microsoft_Endpoint_Manager (Ordner Scripts),
dort ohne Lizenz veroeffentlicht -> NICHT kopiert, sondern neu geschrieben:
statt der abgekuendigten Module Microsoft.Graph.Intune/AzureAD und App-Secrets
im Code nur Microsoft.Graph (Connect-MgGraph, delegierte Scopes), Berichte
aendern nichts. Einspielen wie paket_emvia_betrieb: eigene PAKET_ID, genau
einmal je Instanz.
"""

MODUL = "emvia"
PAKET_ID = "emvia-endpoint-v1"

# Gemeinsamer Helfer fuer Graph-Listen mit Seitenumbruch (@odata.nextLink).
_ALLE_SEITEN = r"""function Get-GraphAlle([string]$Uri) {
    $Ergebnis = @()
    while ($Uri) {
        $Antwort  = Invoke-MgGraphRequest -Method GET -Uri $Uri -OutputType PSObject
        $Ergebnis += $Antwort.value
        $Uri      = $Antwort.'@odata.nextLink'
    }
    $Ergebnis
}
"""

VORLAGEN: tuple[dict, ...] = (
    {
        "id": "emvia-skript-intune-sicherung",
        "typ": "skript",
        "titel": "Intune-Konfiguration sichern (JSON-Export aller Richtlinien, Profile, Apps-Liste)",
        "sprache": "powershell",
        "inhalt": r"""# Nur lesend. Sicherung VOR jeder groesseren Aenderung + woechentlich (Runbook). Ersetzt das
# alte IntuneBackupAndRestore/Connect-MSGraph (abgekuendigt). Rolle: Intune-Leser.
param([string]$Ziel = ".\intune-sicherung\$(Get-Date -Format 'yyyy-MM-dd_HHmm')")
Connect-MgGraph -Scopes 'DeviceManagementConfiguration.Read.All','DeviceManagementApps.Read.All' -NoWelcome
""" + _ALLE_SEITEN + r"""
$Bereiche = [ordered]@{
    'Konformitaet'        = 'https://graph.microsoft.com/beta/deviceManagement/deviceCompliancePolicies?$expand=assignments,scheduledActionsForRule($expand=scheduledActionConfigurations)'
    'Konfigurationsprofile' = 'https://graph.microsoft.com/beta/deviceManagement/deviceConfigurations?$expand=assignments'
    'Einstellungskatalog' = 'https://graph.microsoft.com/beta/deviceManagement/configurationPolicies?$expand=assignments,settings'
    'Admin-Vorlagen'      = 'https://graph.microsoft.com/beta/deviceManagement/groupPolicyConfigurations?$expand=assignments'
    'Skripte'             = 'https://graph.microsoft.com/beta/deviceManagement/deviceManagementScripts?$expand=assignments'
    'Korrekturen'         = 'https://graph.microsoft.com/beta/deviceManagement/deviceHealthScripts?$expand=assignments'
    'Apps'                = 'https://graph.microsoft.com/beta/deviceAppManagement/mobileApps?$expand=assignments'
}
foreach ($Name in $Bereiche.Keys) {
    $Ordner = Join-Path $Ziel $Name
    New-Item -ItemType Directory -Path $Ordner -Force | Out-Null
    $Eintraege = Get-GraphAlle $Bereiche[$Name]
    foreach ($E in $Eintraege) {
        $Titel = if ($E.displayName) { $E.displayName } else { $E.name }
        $Datei = ($Titel -replace '[\\/:*?"<>|]', '_') + '.json'
        $E | ConvertTo-Json -Depth 20 | Set-Content (Join-Path $Ordner $Datei) -Encoding UTF8
    }
    '{0,-22} {1,4} Eintraege' -f $Name, @($Eintraege).Count
}
"Sicherung: $Ziel   (enthaelt keine Geheimnisse wie WLAN-PSKs/Zertifikate im Klartext -- trotzdem nur intern ablegen)"
# Wiederherstellen: bewusst KEIN automatischer Import (legt Duplikate an, ueberschreibt Zuweisungen).
# Einzelne Richtlinie aus der JSON im Portal nachbauen oder gezielt per Graph POST -- vorher Testgruppe.""",
    },
    {
        "id": "emvia-skript-intune-vergleich",
        "typ": "skript",
        "titel": "Intune-Sicherungen vergleichen: was wurde seit der letzten Sicherung geaendert?",
        "sprache": "powershell",
        "inhalt": r"""# Nur lesend, offline (kein Graph). Vergleicht zwei Ordner aus "Intune-Konfiguration sichern".
# Typische Frage im Ticket: "Seit gestern geht X nicht mehr -- hat jemand eine Richtlinie geaendert?"
param(
    [Parameter(Mandatory)][string]$Alt,
    [Parameter(Mandatory)][string]$Neu
)
# Felder, die sich bei jeder Sicherung aendern und nichts bedeuten
$Ignorieren = 'lastModifiedDateTime','createdDateTime','version','@odata.context','settingCount'

function Normalisieren([string]$Pfad) {
    $Obj = Get-Content $Pfad -Raw | ConvertFrom-Json
    foreach ($F in $Ignorieren) { $Obj.PSObject.Properties.Remove($F) }
    $Obj | ConvertTo-Json -Depth 20 -Compress
}

$AltDateien = Get-ChildItem $Alt -Recurse -Filter *.json | ForEach-Object { $_.FullName.Substring($Alt.Length) }
$NeuDateien = Get-ChildItem $Neu -Recurse -Filter *.json | ForEach-Object { $_.FullName.Substring($Neu.Length) }

Compare-Object $AltDateien $NeuDateien | ForEach-Object {
    [pscustomobject]@{ Aenderung = if ($_.SideIndicator -eq '=>') { 'NEU' } else { 'GELOESCHT' }; Datei = $_.InputObject }
}
$AltDateien | Where-Object { $_ -in $NeuDateien } | ForEach-Object {
    if ((Normalisieren (Join-Path $Alt $_)) -ne (Normalisieren (Join-Path $Neu $_))) {
        [pscustomobject]@{ Aenderung = 'GEAENDERT'; Datei = $_ }
    }
}
# Wer hat geaendert? -> Skript "Intune-Aenderungsprotokoll" bzw. Intune > Mandantenverwaltung > Ueberwachungsprotokolle""",
    },
    {
        "id": "emvia-skript-intune-gruppe-zuweisungen",
        "typ": "skript",
        "titel": "Was bekommt diese Gruppe? Alle Intune-Zuweisungen (Richtlinien, Profile, Apps, Skripte) einer Entra-Gruppe",
        "sprache": "powershell",
        "inhalt": r"""# Nur lesend. Beantwortet "Warum hat Geraet/Benutzer X diese Einstellung/App (nicht)?"
# Rolle: Intune-Leser. Beruecksichtigt Einschluss UND Ausschluss.
param([Parameter(Mandatory)][string]$Gruppenname)
Connect-MgGraph -Scopes 'DeviceManagementConfiguration.Read.All','DeviceManagementApps.Read.All','Group.Read.All' -NoWelcome
""" + _ALLE_SEITEN + r"""
$Gruppe = Get-MgGroup -Filter "displayName eq '$($Gruppenname -replace "'", "''")'"
if (@($Gruppe).Count -ne 1) { throw "Gruppe '$Gruppenname' nicht eindeutig gefunden ($(@($Gruppe).Count) Treffer)." }
"Gruppe: $($Gruppe.DisplayName)  ($($Gruppe.Id))"

$Bereiche = [ordered]@{
    'Konformitaet'          = 'https://graph.microsoft.com/beta/deviceManagement/deviceCompliancePolicies?$expand=assignments'
    'Konfigurationsprofil'  = 'https://graph.microsoft.com/beta/deviceManagement/deviceConfigurations?$expand=assignments'
    'Einstellungskatalog'   = 'https://graph.microsoft.com/beta/deviceManagement/configurationPolicies?$expand=assignments'
    'Admin-Vorlage'         = 'https://graph.microsoft.com/beta/deviceManagement/groupPolicyConfigurations?$expand=assignments'
    'Skript'                = 'https://graph.microsoft.com/beta/deviceManagement/deviceManagementScripts?$expand=assignments'
    'Korrektur'             = 'https://graph.microsoft.com/beta/deviceManagement/deviceHealthScripts?$expand=assignments'
    'App'                   = 'https://graph.microsoft.com/beta/deviceAppManagement/mobileApps?$filter=isAssigned eq true&$expand=assignments'
}
$Treffer = foreach ($Art in $Bereiche.Keys) {
    foreach ($E in (Get-GraphAlle $Bereiche[$Art])) {
        foreach ($Z in $E.assignments) {
            $Typ = $Z.target.'@odata.type'
            $Art2 = switch -Wildcard ($Typ) {
                '*exclusionGroupAssignmentTarget' { if ($Z.target.groupId -eq $Gruppe.Id) { 'AUSGESCHLOSSEN' } }
                '*groupAssignmentTarget'          { if ($Z.target.groupId -eq $Gruppe.Id) { 'zugewiesen' + $(if ($Z.intent) { " ($($Z.intent))" }) } }
            }
            if ($Art2) {
                [pscustomobject]@{ Art = $Art; Name = $(if ($E.displayName) { $E.displayName } else { $E.name }); Zuweisung = $Art2 }
            }
        }
    }
}
$Treffer | Sort-Object Art, Name | Format-Table -AutoSize
"Hinweis: Zuweisungen an 'Alle Benutzer'/'Alle Geraete' sowie Filter gelten zusaetzlich und sind hier nicht aufgefuehrt." """,
    },
    {
        "id": "emvia-skript-laps-bitlocker",
        "typ": "skript",
        "titel": "Ticket: lokales Admin-Kennwort (Windows LAPS) oder BitLocker-Wiederherstellungsschluessel abrufen",
        "sprache": "powershell",
        "inhalt": r"""# Jeder Abruf wird im Entra-Ueberwachungsprotokoll protokolliert -- Grund im Ticket dokumentieren!
# BitLocker-Schluessel nur nach Identitaetspruefung herausgeben (Rueckruf), nie per Mail/Chat.
# Rollen: Cloudgeraeteadministrator bzw. Helpdesk-/Intune-Admin (LAPS), BitLocker: Helpdesk-Admin o. ae.
param(
    [Parameter(Mandatory)][string]$Geraetename,
    [ValidateSet('LAPS','BitLocker')][string]$Was = 'BitLocker'
)
Connect-MgGraph -Scopes 'Device.Read.All','DeviceLocalCredential.Read.All','BitlockerKey.Read.All' -NoWelcome

$Geraet = Get-MgDevice -Filter "displayName eq '$Geraetename'" -Property Id,DeviceId,DisplayName,OperatingSystem
if (@($Geraet).Count -ne 1) { throw "Geraet '$Geraetename' nicht eindeutig gefunden ($(@($Geraet).Count) Treffer)." }

if ($Was -eq 'LAPS') {
    $Kopf = @{ 'ocp-client-name' = 'EMVIA-Werkbank'; 'ocp-client-version' = '1.0' }
    $Info = Invoke-MgGraphRequest -Method GET -Headers $Kopf -OutputType PSObject `
        -Uri "https://graph.microsoft.com/v1.0/directory/deviceLocalCredentials/$($Geraet.DeviceId)?`$select=credentials"
    $Neueste = $Info.credentials | Sort-Object backupDateTime -Descending | Select-Object -First 1
    "Konto: $($Neueste.accountName)   gesichert: $($Neueste.backupDateTime)"
    'Kennwort: ' + [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($Neueste.passwordBase64))
    'Nach Gebrauch in Intune > Geraet > "Lokales Administratorkennwort rotieren" ausloesen.'
} else {
    $Schluessel = Get-MgInformationProtectionBitlockerRecoveryKey -Filter "deviceId eq '$($Geraet.DeviceId)'"
    if (-not $Schluessel) { 'Kein BitLocker-Schluessel in Entra gesichert -- Geraet pruefen (Intune > Datentraegerverschluesselung).' }
    foreach ($S in $Schluessel) {
        $Voll = Get-MgInformationProtectionBitlockerRecoveryKey -BitlockerRecoveryKeyId $S.Id -Property key
        [pscustomobject]@{ SchluesselID = $S.Id; Erstellt = $S.CreatedDateTime; Wiederherstellungsschluessel = $Voll.Key }
    }
    'Am Geraet: die ersten 8 Zeichen der angezeigten Schluessel-ID mit SchluesselID vergleichen.'
}""",
    },
    {
        "id": "emvia-skript-intune-aenderungen",
        "typ": "skript",
        "titel": "Intune-Aenderungsprotokoll: wer hat in den letzten X Tagen Richtlinien/Apps/Geraete geaendert?",
        "sprache": "powershell",
        "inhalt": r"""# Nur lesend. Erste Frage bei "seit gestern geht X nicht mehr". Rolle: Intune-Leser.
param([int]$Tage = 7)
Connect-MgGraph -Scopes 'DeviceManagementApps.Read.All','DeviceManagementConfiguration.Read.All' -NoWelcome
""" + _ALLE_SEITEN + r"""
$Seit = (Get-Date).ToUniversalTime().AddDays(-$Tage).ToString('yyyy-MM-ddTHH:mm:ssZ')
Get-GraphAlle "https://graph.microsoft.com/v1.0/deviceManagement/auditEvents?`$filter=activityDateTime ge $Seit" |
    Select-Object @{n='Zeit';  e={ $_.activityDateTime }},
                  @{n='Wer';   e={ $_.actor.userPrincipalName }},
                  @{n='Aktion';e={ $_.activity }},
                  @{n='Ziel';  e={ ($_.resources | ForEach-Object displayName) -join ', ' }},
                  @{n='Ergebnis'; e={ $_.activityResult }} |
    Sort-Object Zeit -Descending | Format-Table -AutoSize -Wrap
# Aenderungen an Entra-Geraeten/Gruppen stehen zusaetzlich im Entra-Ueberwachungsprotokoll (Get-MgAuditLogDirectoryAudit).""",
    },
    {
        "id": "emvia-skript-legacy-anmeldungen",
        "typ": "skript",
        "titel": "Alte Anmeldeprotokolle finden (POP/IMAP/SMTP-Auth, ActiveSync, EWS) -- vor Abschaltungen",
        "sprache": "powershell",
        "inhalt": r"""# Nur lesend. Findet Geraete/Programme, die alte Protokolle nutzen -- Kandidaten fuer Tickets nach
# Abschaltungen (EWS seit 01.10.2026 blockiert). Braucht Entra ID P1 (Anmeldeprotokolle, max. 30 Tage).
param([int]$Tage = 7)
Connect-MgGraph -Scopes 'AuditLog.Read.All' -NoWelcome
$Seit = (Get-Date).ToUniversalTime().AddDays(-$Tage).ToString('yyyy-MM-ddTHH:mm:ssZ')
$Modern = 'Browser','Mobile Apps and Desktop clients',''

$Alt = Get-MgAuditLogSignIn -Filter "createdDateTime ge $Seit" -All |
    Where-Object { $_.ClientAppUsed -notin $Modern }

"== Nach Protokoll"
$Alt | Group-Object ClientAppUsed -NoElement | Sort-Object Count -Descending | Format-Table -AutoSize
"== Nach Benutzer/Programm (Top 30)"
$Alt | Group-Object UserPrincipalName, ClientAppUsed, AppDisplayName -NoElement |
    Sort-Object Count -Descending | Select-Object -First 30 Count, Name | Format-Table -AutoSize
# Achtung Datenmenge: bei vielen Nutzern $Tage klein halten oder die KQL-Variante im Log Analytics Workspace nutzen.""",
    },
)
