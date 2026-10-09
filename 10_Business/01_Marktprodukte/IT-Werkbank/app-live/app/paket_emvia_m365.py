"""
Vorlagen-Paket "EMVIA · M365-Verwaltung".

Wird von store.vorlagen_pakete_einspielen() genau EINMAL je Instanz in die
editierbare vorlage-Tabelle uebernommen (Marker in vorlage_paket). Danach
gehoeren die Vorlagen dem Nutzer: Aendern/Loeschen in der UI bleibt erhalten,
ein Neustart spielt nichts erneut ein.

Grundsaetze aller Skripte:
- Berichte aendern nichts (nur Get-*/Export-Csv).
- Aendernde Skripte laufen standardmaessig als Testlauf ($Testlauf = $true)
  und zeigen nur an, was passieren wuerde.
- Minimal noetige Graph-Scopes je Skript, Rollen nach Least Privilege.
- KEINE Zugangsdaten, Tenant-IDs oder Kundendomains im Code -- die kommen aus
  dem EMVIA-Steckbrief bzw. werden beim Aufruf als Parameter uebergeben.
"""

MODUL = "emvia"
PAKET_ID = "emvia-m365-v1"

STECKBRIEF_ID = "emvia-steckbrief"

VORLAGEN: tuple[dict, ...] = (
    # ------------------------------------------------------------------ Doku
    {
        "id": STECKBRIEF_ID,
        "typ": "doku",
        "titel": "EMVIA-Steckbrief (wird automatisch in jeden EMVIA-Chat geladen)",
        "sprache": "",
        "inhalt": """EMVIA-STECKBRIEF -- bitte ausfuellen. KEINE Passwoerter, Schluessel oder Tenant-Secrets eintragen!
Dieser Text wird bei jeder Frage im Modul "EMVIA · M365" als Kundenkontext mitgeschickt.

Identitaetsquelle:      [Cloud-only | Hybrid mit Entra Connect / Cloud Sync]
  Bei Hybrid: Sync-Server: [Name]   Ziel-OU fuer neue Benutzer: [OU=...,DC=...]
Primaere Domain(s):     [z. B. firma.de]  weitere: [...]
UPN-/Namensschema:      [vorname.nachname@domain | v.nachname@... ] Umlaute: [ae/oe/ue]
Standorte/Einrichtungen:[Liste der Haeuser/Standorte + Kuerzel]
Lizenzmodell:           [z. B. M365 Business Premium / E3 / F3 fuer Pflegekraefte]
Lizenzvergabe:          [gruppenbasiert ueber Gruppe ... | direkt]
Standard-Gruppen neu:   [Alle Mitarbeiter, Standort-Gruppe, Teams ...]
MFA / Conditional Access: [Methode (Authenticator/FIDO2), Ausnahmen, Break-Glass vorhanden ja/nein]
Geraeteverwaltung:      [Intune / anderes MDM, Pflege-Tablets im Kiosk-Modus ja/nein]
Freigegebene Postfaecher: [Namensschema, wer genehmigt Zugriff]
Offboarding-Regeln:     [Aufbewahrung Postfach (Tage), Weiterleitung erlaubt ja/nein, Freigabe durch ...]
Genehmigungen:          [Wer darf Zugriff auf fremde Postfaecher freigeben? Betriebsrat/DSB?]
Meine Admin-Rollen:     [z. B. Benutzeradministrator, Exchange-Administrator -- nicht Global Admin]
Ticketsystem/Kontakte:  [...]
Besonderheiten:         [...]
""",
    },
    {
        "id": "emvia-doku-erste-woche",
        "typ": "doku",
        "titel": "Start 15.10.2026: Fragenliste fuer die ersten Tage (Antworten in den Steckbrief)",
        "sprache": "",
        "inhalt": """ERSTE WOCHE -- was ich klaeren muss, bevor ich etwas aendere

ZUGANG & ROLLEN
[ ] Eigenes Admin-Konto getrennt vom Alltagskonto? Welche Rollen (Benutzeradmin, Exchange-Admin, Intune-Admin)? PIM?
[ ] Break-Glass-Konten vorhanden, wer verwahrt sie?
[ ] Wer genehmigt was (neue Konten, Postfachzugriff, Wipe)? Gibt es Betriebsrat-/Datenschutz-Vereinbarungen zur IT?

IDENTITAET
[ ] Cloud-only oder Hybrid (Entra Connect / Cloud Sync)? Wo laeuft der Sync, welche OUs werden synchronisiert?
[ ] Namensschema UPN/E-Mail, Umgang mit Doppelnamen/Umlauten
[ ] MFA-Methode, Conditional-Access-Richtlinien (erst lesen: Skript "CA-Richtlinien dokumentieren" im Modul Entra ID)

LIZENZEN
[ ] Welche Plaene (z. B. Business Premium / E3 / F-Lizenzen fuer Pflegekraefte)? Gruppenbasiert?
[ ] Lizenzbericht laufen lassen (Skript "Lizenzbericht") -> Ueberblick + Einsparpotenzial

EXCHANGE / TEAMS
[ ] Freigegebene Postfaecher je Standort? Namensschema? Verteiler?
[ ] Externe Weiterleitungen erlaubt? (Skript "Weiterleitungen nach extern" als Bestandsaufnahme)

MDM
[ ] Welches MDM (Intune oder anderes)? Plattformen: Windows, iOS/iPadOS, Android?
[ ] Pflege-Tablets: Kiosk-Modus? Wer registriert neue Geraete? Autopilot / Apple Business Manager / Zero-Touch?
[ ] Compliance-Richtlinien + Ablauf bei Verlust/Diebstahl

BETRIEB
[ ] Ticketsystem, Eskalationswege, Dienstleister (wer macht Server/Netz?)
[ ] Dokumentation: wo liegt sie, was ist veraltet?
[ ] Wiederkehrende Aufgaben (Ein-/Austritte pro Monat, Standortwechsel)

Grundsatz Woche 1-2: lesen, Berichte ziehen, dokumentieren -- Aenderungen erst nach Ruecksprache.
""",
    },
    {
        "id": "emvia-onboarding-checkliste",
        "typ": "doku",
        "titel": "Onboarding-Checkliste neuer Mitarbeiter",
        "sprache": "",
        "inhalt": """ONBOARDING -- Checkliste (Reihenfolge einhalten)

[ ] Auftrag/Freigabe liegt vor (Name, Eintritt, Standort, Funktion, Vorgesetzte/r)
[ ] Identitaetsquelle pruefen: Hybrid -> Konto im lokalen AD (richtige OU) anlegen, NICHT in Entra
[ ] Konto anlegen (Generator im Werkzeug "On-/Offboarding" oder Skript-Vorlage)
[ ] UsageLocation = DE gesetzt (sonst schlaegt die Lizenzzuweisung fehl)
[ ] Lizenzgruppe + Standard-/Standortgruppen zugewiesen
[ ] Lizenzstatus nach ~15 Min pruefen: admin.microsoft.com > Benutzer > Lizenzen und Apps
[ ] Postfach vorhanden (Exchange Admin Center), ggf. Zugriff auf Team-/Standortpostfach
[ ] Startkennwort GETRENNT von der Benutzerkennung uebermitteln (z. B. Kennung per Mail an Vorgesetzte, Kennwort persoenlich/telefonisch)
[ ] MFA-Einrichtung beim ersten Anmelden begleiten (E-Mail-Vorlage "MFA einrichten")
[ ] Geraet zuweisen / in MDM registrieren, bei Pflege-Tablet: Kiosk-Profil
[ ] Ticket dokumentieren (wer, was, wann, Freigabe von wem)
""",
    },
    {
        "id": "emvia-offboarding-checkliste",
        "typ": "doku",
        "titel": "Offboarding-Checkliste Austritt",
        "sprache": "",
        "inhalt": """OFFBOARDING -- Checkliste (Reihenfolge ist wichtig!)

[ ] Schriftliche Freigabe: Austrittsdatum, wer bekommt Postfach-/OneDrive-Zugriff, wie lange
[ ] Anmeldung sperren (Hybrid: im lokalen AD deaktivieren, sonst setzt der Sync es zurueck)
[ ] Alle Sitzungen widerrufen (Revoke-MgUserSignInSession)
[ ] Postfach in freigegebenes Postfach umwandeln -- VOR dem Lizenzentzug
    (sonst wird das Postfach 30 Tage nach Lizenzentzug geloescht)
    Achtung: freigegebenes Postfach ohne Lizenz max. 50 GB, kein Archiv-Postfach
[ ] Abwesenheitsnotiz (intern/extern) setzen
[ ] Zugriff fuer Vertretung (FullAccess) -- nur mit Freigabe, Vier-Augen-Prinzip, dokumentieren
[ ] Aus Gruppen entfernen (Lizenzgruppen zuletzt), direkte Lizenzen entziehen
[ ] OneDrive: Vorgesetzte/n Zugriff geben bzw. Daten sichern (Standard-Aufbewahrung nach Loeschung: 30 Tage)
[ ] Geraete zuruecknehmen, im MDM zuruecksetzen/abmelden
[ ] Konto nach Aufbewahrungsfrist loeschen (Papierkorb Entra: 30 Tage wiederherstellbar)
[ ] Ticket mit allen Schritten + Freigaben dokumentieren
""",
    },
    # ------------------------------------------------------------- Skripte
    {
        "id": "emvia-skript-onboarding-cloud",
        "typ": "skript",
        "titel": "Onboarding Cloud-only: Benutzer anlegen, Gruppen, Vorgesetzte/r (Testlauf zuerst)",
        "sprache": "powershell",
        "inhalt": r"""<#
  EMVIA · Onboarding (nur Cloud-only-Konten! Bei Hybrid: Vorlage "Onboarding Hybrid")
  Modul:  Install-Module Microsoft.Graph -Scope CurrentUser
  Rolle:  Benutzeradministrator (+ Gruppenbesitzer/Gruppenadministrator fuer Gruppen)
  Ablauf: erst mit -Testlauf $true pruefen, dann mit -Testlauf $false ausfuehren.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Vorname,
    [Parameter(Mandatory)][string]$Nachname,
    [Parameter(Mandatory)][string]$Domain,      # aus dem EMVIA-Steckbrief
    [string]$Abteilung = '',
    [string]$Standort  = '',
    [string]$Position  = '',
    [string]$VorgesetzteUpn = '',
    [string[]]$Gruppen = @(),                   # Anzeigenamen (Lizenz-, Standort-, Teams-Gruppen)
    [bool]$Testlauf = $true
)

function Normalisieren([string]$t) {
    $t = $t.Trim().ToLower() -replace 'ä','ae' -replace 'ö','oe' -replace 'ü','ue' -replace 'ß','ss'
    # uebrige Akzente auf den Grundbuchstaben (Zoë -> zoe, José -> jose) statt sie zu verlieren
    $t = $t.Normalize([Text.NormalizationForm]::FormD) -replace '\p{Mn}',''
    $t = $t -replace '\s+','-'
    return ($t -replace '[^a-z0-9\-]', '')
}
$Alias = '{0}.{1}' -f (Normalisieren $Vorname), (Normalisieren $Nachname)
$Upn   = "$Alias@$Domain"

Connect-MgGraph -Scopes 'User.ReadWrite.All','Group.ReadWrite.All' -NoWelcome

if (Get-MgUser -Filter "userPrincipalName eq '$Upn'" -ErrorAction SilentlyContinue) {
    throw "Konto $Upn existiert bereits -- Namensschema/Steckbrief pruefen (z. B. zweiter Vorname)."
}

# Startkennwort: 16 Zeichen, muss bei der ersten Anmeldung geaendert werden
$Zeichen  = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!$%&?#'
$Kennwort = -join (1..16 | ForEach-Object { $Zeichen[(Get-Random -Maximum $Zeichen.Length)] })

$Konto = @{
    AccountEnabled    = $true
    DisplayName       = "$Vorname $Nachname"
    GivenName         = $Vorname
    Surname           = $Nachname
    MailNickname      = $Alias
    UserPrincipalName = $Upn
    UsageLocation     = 'DE'     # Pflicht fuer Lizenzzuweisung
    PasswordProfile   = @{ Password = $Kennwort; ForceChangePasswordNextSignIn = $true }
}
if ($Abteilung) { $Konto.Department     = $Abteilung }
if ($Standort)  { $Konto.OfficeLocation = $Standort }
if ($Position)  { $Konto.JobTitle       = $Position }

Write-Host "Geplant: $Upn ($Vorname $Nachname) Abteilung='$Abteilung' Standort='$Standort'"
Write-Host "Gruppen: $($Gruppen -join ', ')"
if ($Testlauf) { Write-Warning 'TESTLAUF -- nichts angelegt. Mit -Testlauf $false ausfuehren.'; return }

$Neu = New-MgUser -BodyParameter $Konto
Write-Host "Angelegt: $($Neu.UserPrincipalName) (Id $($Neu.Id))"

if ($VorgesetzteUpn) {
    $Vg = Get-MgUser -UserId $VorgesetzteUpn
    Set-MgUserManagerByRef -UserId $Neu.Id -BodyParameter @{
        '@odata.id' = "https://graph.microsoft.com/v1.0/users/$($Vg.Id)"
    }
}

foreach ($Name in $Gruppen) {
    $G = Get-MgGroup -Filter "displayName eq '$Name'"
    if (-not $G)              { Write-Warning "Gruppe '$Name' nicht gefunden"; continue }
    if ($G.Count -gt 1)       { Write-Warning "Gruppe '$Name' ist nicht eindeutig"; continue }
    New-MgGroupMember -GroupId $G.Id -DirectoryObjectId $Neu.Id
    Write-Host "  + $Name"
}

Write-Host ''
Write-Host "Startkennwort (GETRENNT von der Kennung uebermitteln!): $Kennwort"
Disconnect-MgGraph | Out-Null""",
    },
    {
        "id": "emvia-skript-onboarding-hybrid",
        "typ": "skript",
        "titel": "Onboarding Hybrid: Benutzer im lokalen AD anlegen + Delta-Sync",
        "sprache": "powershell",
        "inhalt": r"""<#
  EMVIA · Onboarding bei Hybrid-Identitaet (Entra Connect)
  Auf einem Server/Admin-PC mit RSAT-AD-PowerShell ausfuehren.
  Lizenz/Cloud-Gruppen danach in Entra (gruppenbasiert) -- UsageLocation kommt bei
  gruppenbasierter Lizenzierung ohne gesetzten Wert aus dem Mandantenland.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Vorname,
    [Parameter(Mandatory)][string]$Nachname,
    [Parameter(Mandatory)][string]$Domain,      # UPN-Suffix laut Steckbrief
    [Parameter(Mandatory)][string]$ZielOU,      # z. B. 'OU=Benutzer,OU=Standort,DC=firma,DC=local'
    [string]$Abteilung = '',
    [string]$Standort  = '',
    [string]$Position  = '',
    [string[]]$ADGruppen = @(),                 # lokale (synchronisierte) Gruppen
    [string]$SyncServer = '',                   # Entra-Connect-Server fuer Delta-Sync
    [bool]$Testlauf = $true
)
Import-Module ActiveDirectory

function Normalisieren([string]$t) {
    $t = $t.Trim().ToLower() -replace 'ä','ae' -replace 'ö','oe' -replace 'ü','ue' -replace 'ß','ss'
    $t = $t.Normalize([Text.NormalizationForm]::FormD) -replace '\p{Mn}',''
    $t = $t -replace '\s+','-'
    return ($t -replace '[^a-z0-9\-]', '')
}
$Alias = '{0}.{1}' -f (Normalisieren $Vorname), (Normalisieren $Nachname)
$Sam  = $Alias.Substring(0, [Math]::Min(20, $Alias.Length))   # sAMAccountName max. 20 Zeichen
$Upn   = "$Alias@$Domain"

if (Get-ADUser -Filter "UserPrincipalName -eq '$Upn' -or SamAccountName -eq '$Sam'") {
    throw "Konto $Upn / $Sam existiert bereits."
}
$Zeichen  = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!$%&?#'
$Klartext = -join (1..16 | ForEach-Object { $Zeichen[(Get-Random -Maximum $Zeichen.Length)] })

$Param = @{
    Name                  = "$Vorname $Nachname"
    DisplayName           = "$Vorname $Nachname"
    GivenName             = $Vorname
    Surname               = $Nachname
    SamAccountName        = $Sam
    UserPrincipalName     = $Upn
    EmailAddress          = $Upn
    Path                  = $ZielOU
    AccountPassword       = (ConvertTo-SecureString $Klartext -AsPlainText -Force)
    Enabled               = $true
    ChangePasswordAtLogon = $true
}
if ($Abteilung) { $Param.Department = $Abteilung }
if ($Standort)  { $Param.Office     = $Standort }
if ($Position)  { $Param.Title      = $Position }

Write-Host "Geplant: $Upn (sAM $Sam) in $ZielOU; Gruppen: $($ADGruppen -join ', ')"
if ($Testlauf) { Write-Warning 'TESTLAUF -- nichts angelegt. Mit -Testlauf $false ausfuehren.'; return }

New-ADUser @Param
foreach ($G in $ADGruppen) { Add-ADGroupMember -Identity $G -Members $Sam; Write-Host "  + $G" }

if ($SyncServer) {
    Invoke-Command -ComputerName $SyncServer -ScriptBlock { Start-ADSyncSyncCycle -PolicyType Delta }
    Write-Host 'Delta-Sync angestossen -- Konto erscheint in Entra nach wenigen Minuten.'
}
Write-Host "Startkennwort (GETRENNT uebermitteln!): $Klartext"
# Postfach: wird bei Lizenz mit Exchange Online automatisch angelegt, wenn KEIN lokales
# Exchange-Postfach existiert. Bei vorhandenem Exchange-Hybrid stattdessen Enable-RemoteMailbox.""",
    },
    {
        "id": "emvia-skript-offboarding",
        "typ": "skript",
        "titel": "Offboarding: sperren, Sitzungen widerrufen, Postfach -> freigegeben, Vertretung, Gruppen (Testlauf zuerst)",
        "sprache": "powershell",
        "inhalt": r"""<#
  EMVIA · Offboarding (Cloud-only; bei Hybrid Konto ZUSAETZLICH im lokalen AD deaktivieren:
  Disable-ADAccount -Identity <sAMAccountName> -- sonst setzt der Sync die Sperre zurueck)
  Module: Microsoft.Graph, ExchangeOnlineManagement
  Rollen: Benutzeradministrator + Exchange-Administrator
  Nur mit schriftlicher Freigabe (Vertretungszugriff = Zugriff auf personenbezogene Daten).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Upn,
    [string]$VertretungUpn = '',
    [string]$Abwesenheitstext = 'Diese Person ist nicht mehr fuer uns taetig. Bitte wenden Sie sich an ...',
    [bool]$GruppenEntfernen = $true,
    [bool]$DirekteLizenzenEntziehen = $true,
    [bool]$Testlauf = $true
)
Connect-MgGraph -Scopes 'User.ReadWrite.All','Group.ReadWrite.All','Directory.AccessAsUser.All' -NoWelcome
Connect-ExchangeOnline -ShowBanner:$false

$U  = Get-MgUser -UserId $Upn -Property Id,DisplayName,AccountEnabled,OnPremisesSyncEnabled,AssignedLicenses,LicenseAssignmentStates
$Mb = Get-EXOMailbox -Identity $Upn -ErrorAction SilentlyContinue
$Gruppen = Get-MgUserMemberOf -UserId $U.Id -All |
    Where-Object { $_.AdditionalProperties.'@odata.type' -eq '#microsoft.graph.group' } |
    ForEach-Object { Get-MgGroup -GroupId $_.Id -Property Id,DisplayName,GroupTypes,MailEnabled,SecurityEnabled,OnPremisesSyncEnabled,Mail }
$Direkt = $U.LicenseAssignmentStates | Where-Object { -not $_.AssignedByGroup } | Select-Object -ExpandProperty SkuId -Unique

Write-Host "== $($U.DisplayName) ($Upn)"
if ($U.OnPremisesSyncEnabled) { Write-Warning 'HYBRID-Konto: zusaetzlich im lokalen AD deaktivieren und Gruppen dort pflegen!' }
Write-Host "Postfach: $(if ($Mb) { $Mb.RecipientTypeDetails } else { 'keins' })"
Write-Host "Gruppen ($($Gruppen.Count)): $(($Gruppen.DisplayName) -join ', ')"
Write-Host "Direkt zugewiesene Lizenzen: $($Direkt.Count)"
if ($Testlauf) { Write-Warning 'TESTLAUF -- keine Aenderung. Mit -Testlauf $false ausfuehren.'; return }

# 1. Anmeldung sperren + alle Sitzungen/Tokens widerrufen
Update-MgUser -UserId $U.Id -AccountEnabled:$false
Revoke-MgUserSignInSession -UserId $U.Id | Out-Null
Write-Host '1. Anmeldung gesperrt, Sitzungen widerrufen'

# 2. Postfach in freigegebenes Postfach umwandeln (VOR Lizenzentzug!)
if ($Mb -and $Mb.RecipientTypeDetails -eq 'UserMailbox') {
    Set-Mailbox -Identity $Upn -Type Shared
    Write-Host '2. Postfach -> freigegebenes Postfach (ohne Lizenz max. 50 GB!)'
}
# 3. Abwesenheitsnotiz
if ($Mb) {
    Set-MailboxAutoReplyConfiguration -Identity $Upn -AutoReplyState Enabled `
        -InternalMessage $Abwesenheitstext -ExternalMessage $Abwesenheitstext -ExternalAudience All
    Write-Host '3. Abwesenheitsnotiz gesetzt'
}
# 4. Vertretung (nur mit Freigabe)
if ($Mb -and $VertretungUpn) {
    Add-MailboxPermission -Identity $Upn -User $VertretungUpn -AccessRights FullAccess -AutoMapping $true | Out-Null
    Write-Host "4. Vollzugriff fuer $VertretungUpn (erscheint in Outlook nach bis zu 60 Min)"
}
# 5. Gruppen (synchronisierte und dynamische Gruppen werden uebersprungen)
if ($GruppenEntfernen) {
    foreach ($G in $Gruppen) {
        if ($G.OnPremisesSyncEnabled)                    { Write-Warning "  ~ $($G.DisplayName): lokal im AD pflegen"; continue }
        if ($G.GroupTypes -contains 'DynamicMembership') { Write-Host   "  ~ $($G.DisplayName): dynamisch, faellt automatisch raus"; continue }
        if ($G.MailEnabled -and -not ($G.GroupTypes -contains 'Unified')) {
            # Verteilerliste / E-Mail-aktivierte Sicherheitsgruppe -> nur ueber Exchange
            Remove-DistributionGroupMember -Identity $G.Mail -Member $Upn -BypassSecurityGroupManagerCheck -Confirm:$false
        } else {
            Remove-MgGroupMemberByRef -GroupId $G.Id -DirectoryObjectId $U.Id
        }
        Write-Host "  - $($G.DisplayName)"
    }
}
# 6. Direkt zugewiesene Lizenzen (gruppenbasierte fallen mit der Gruppe weg)
if ($DirekteLizenzenEntziehen -and $Direkt) {
    Set-MgUserLicense -UserId $U.Id -AddLicenses @() -RemoveLicenses @($Direkt) | Out-Null
    Write-Host '6. Direkte Lizenzen entzogen'
}
Write-Host 'Fertig. Offen (manuell): Geraete im MDM, OneDrive-Zugriff fuer Vorgesetzte, Ticket dokumentieren.'
Disconnect-ExchangeOnline -Confirm:$false
Disconnect-MgGraph | Out-Null""",
    },
    {
        "id": "emvia-skript-lizenzen",
        "typ": "skript",
        "titel": "Lizenzbericht: Bestand, frei, und gesperrte Konten mit Lizenz (Kosten sparen)",
        "sprache": "powershell",
        "inhalt": r"""# Nur Bericht, keine Aenderung. Rolle: Globaler Leser oder Lizenzadministrator
Connect-MgGraph -Scopes 'Organization.Read.All','User.Read.All' -NoWelcome

$Skus = Get-MgSubscribedSku -All
$SkuName = @{}; $Skus | ForEach-Object { $SkuName[$_.SkuId] = $_.SkuPartNumber }

"== Lizenzbestand"
$Skus | Select-Object SkuPartNumber,
    @{n='Gekauft'; e={ $_.PrepaidUnits.Enabled }},
    @{n='Belegt';  e={ $_.ConsumedUnits }},
    @{n='Frei';    e={ $_.PrepaidUnits.Enabled - $_.ConsumedUnits }} |
    Sort-Object SkuPartNumber | Format-Table -AutoSize

$Benutzer = Get-MgUser -All -Property DisplayName,UserPrincipalName,AccountEnabled,AssignedLicenses,Department,OfficeLocation
$Benutzer | Where-Object { $_.AssignedLicenses.Count -gt 0 } |
    Select-Object DisplayName, UserPrincipalName, AccountEnabled, Department, OfficeLocation,
        @{n='Lizenzen'; e={ ($_.AssignedLicenses.SkuId | ForEach-Object { $SkuName[$_] }) -join ', ' }} |
    Export-Csv '.\emvia-lizenzen-je-benutzer.csv' -NoTypeInformation -Encoding UTF8

"== Gesperrte Konten MIT Lizenz (Einsparpotenzial)"
$Benutzer | Where-Object { -not $_.AccountEnabled -and $_.AssignedLicenses.Count -gt 0 } |
    Select-Object DisplayName, UserPrincipalName,
        @{n='Lizenzen'; e={ ($_.AssignedLicenses.SkuId | ForEach-Object { $SkuName[$_] }) -join ', ' }} |
    Format-Table -AutoSize
# Hinweis: Gesperrte Konten mit freigegebenem Postfach > 50 GB oder Aufbewahrung brauchen die Lizenz ggf. weiter.""",
    },
    {
        "id": "emvia-skript-mfa-status",
        "typ": "skript",
        "titel": "MFA-/Anmeldemethoden-Bericht: wer hat noch keine MFA registriert",
        "sprache": "powershell",
        "inhalt": r"""# Nur Bericht. Benoetigt Entra ID P1/P2 (in Business Premium/E3/E5 enthalten).
# Rolle: Berichtsleser oder Sicherheitsleser
Connect-MgGraph -Scopes 'AuditLog.Read.All','UserAuthenticationMethod.Read.All' -NoWelcome

$Details = Get-MgReportAuthenticationMethodUserRegistrationDetail -All

$Details | Select-Object UserPrincipalName, UserDisplayName, IsAdmin, IsMfaRegistered, IsMfaCapable,
        IsSsprRegistered, @{n='Methoden'; e={ $_.MethodsRegistered -join ', ' }} |
    Export-Csv '.\emvia-mfa-status.csv' -NoTypeInformation -Encoding UTF8

"Ohne MFA-Registrierung: $(@($Details | Where-Object { -not $_.IsMfaRegistered }).Count) von $($Details.Count)"
"== Administratoren OHNE MFA (sofort klaeren!)"
$Details | Where-Object { $_.IsAdmin -and -not $_.IsMfaRegistered } |
    Select-Object UserPrincipalName, UserDisplayName | Format-Table -AutoSize""",
    },
    {
        "id": "emvia-skript-inaktive",
        "typ": "skript",
        "titel": "Inaktive Konten (letzte Anmeldung aelter als X Tage)",
        "sprache": "powershell",
        "inhalt": r"""# Nur Bericht. signInActivity braucht Entra ID P1/P2 und AuditLog.Read.All.
param([int]$Tage = 90)
Connect-MgGraph -Scopes 'User.Read.All','AuditLog.Read.All' -NoWelcome
$Grenze = (Get-Date).AddDays(-$Tage)

Get-MgUser -All -Property DisplayName,UserPrincipalName,AccountEnabled,UserType,CreatedDateTime,SignInActivity,AssignedLicenses |
    Where-Object { $_.AccountEnabled -and $_.CreatedDateTime -lt $Grenze } |
    ForEach-Object {
        $Letzte = $_.SignInActivity.LastSignInDateTime
        if (-not $Letzte -or $Letzte -lt $Grenze) {
            [pscustomobject]@{
                Name          = $_.DisplayName
                UPN           = $_.UserPrincipalName
                Typ           = $_.UserType
                LetzteAnmeldung = if ($Letzte) { $Letzte } else { 'nie' }
                Lizenziert    = $_.AssignedLicenses.Count -gt 0
            }
        }
    } | Sort-Object LetzteAnmeldung |
    Export-Csv ".\emvia-inaktiv-$Tage-tage.csv" -NoTypeInformation -Encoding UTF8
"Bericht: .\emvia-inaktiv-$Tage-tage.csv  (Funktions-/Raumkonten vor dem Sperren aussortieren!)" """,
    },
    {
        "id": "emvia-skript-postfachzugriff",
        "typ": "skript",
        "titel": "Postfachzugriff vergeben (Vollzugriff / Senden als) + Bericht wer Zugriff hat",
        "sprache": "powershell",
        "inhalt": r"""# Zugriff auf ein persoenliches Postfach nur mit dokumentierter Freigabe!
param(
    [Parameter(Mandatory)][string]$Postfach,       # z. B. pflege-haus1@... oder Person
    [string]$Benutzer = '',                        # wer bekommt Zugriff
    [ValidateSet('Bericht','Vollzugriff','SendenAls','Beides','Entfernen')][string]$Aktion = 'Bericht'
)
Connect-ExchangeOnline -ShowBanner:$false

switch ($Aktion) {
    'Vollzugriff' { Add-MailboxPermission   -Identity $Postfach -User $Benutzer -AccessRights FullAccess -AutoMapping $true | Out-Null }
    'SendenAls'   { Add-RecipientPermission -Identity $Postfach -Trustee $Benutzer -AccessRights SendAs -Confirm:$false | Out-Null }
    'Beides'      { Add-MailboxPermission   -Identity $Postfach -User $Benutzer -AccessRights FullAccess -AutoMapping $true | Out-Null
                    Add-RecipientPermission -Identity $Postfach -Trustee $Benutzer -AccessRights SendAs -Confirm:$false | Out-Null }
    'Entfernen'   { Remove-MailboxPermission   -Identity $Postfach -User $Benutzer -AccessRights FullAccess -Confirm:$false
                    Remove-RecipientPermission -Identity $Postfach -Trustee $Benutzer -AccessRights SendAs -Confirm:$false -ErrorAction SilentlyContinue }
}

"== Vollzugriff auf $Postfach"
Get-MailboxPermission -Identity $Postfach |
    Where-Object { -not $_.IsInherited -and $_.User -notlike 'NT AUTHORITY\SELF' } |
    Select-Object User, AccessRights | Format-Table -AutoSize
"== Senden als"
Get-RecipientPermission -Identity $Postfach |
    Where-Object { $_.Trustee -notlike 'NT AUTHORITY\SELF' } |
    Select-Object Trustee, AccessRights | Format-Table -AutoSize
Disconnect-ExchangeOnline -Confirm:$false""",
    },
    {
        "id": "emvia-skript-shared-mailbox",
        "typ": "skript",
        "titel": "Freigegebenes Postfach anlegen (z. B. Standort/Station) inkl. Mitglieder",
        "sprache": "powershell",
        "inhalt": r"""param(
    [Parameter(Mandatory)][string]$Anzeigename,   # z. B. 'Haus Nord - Pflegedienstleitung'
    [Parameter(Mandatory)][string]$Adresse,       # z. B. pdl-nord@<domain>
    [string[]]$Mitglieder = @(),
    [bool]$Testlauf = $true
)
Connect-ExchangeOnline -ShowBanner:$false
$Alias = $Adresse.Split('@')[0]
if (Get-EXORecipient -Identity $Adresse -ErrorAction SilentlyContinue) { throw "$Adresse ist bereits vergeben." }
"Geplant: $Anzeigename <$Adresse>, Mitglieder: $($Mitglieder -join ', ')"
if ($Testlauf) { Write-Warning 'TESTLAUF -- mit -Testlauf $false ausfuehren.'; return }

New-Mailbox -Shared -Name $Anzeigename -DisplayName $Anzeigename -Alias $Alias -PrimarySmtpAddress $Adresse | Out-Null
# Gesendete Elemente auch im freigegebenen Postfach ablegen (sonst nur beim Absender)
Set-Mailbox -Identity $Adresse -MessageCopyForSentAsEnabled $true -MessageCopyForSendOnBehalfEnabled $true
foreach ($M in $Mitglieder) {
    Add-MailboxPermission   -Identity $Adresse -User $M -AccessRights FullAccess -AutoMapping $true | Out-Null
    Add-RecipientPermission -Identity $Adresse -Trustee $M -AccessRights SendAs -Confirm:$false | Out-Null
    "  + $M"
}
"Fertig. Ohne Lizenz max. 50 GB. Erscheint in Outlook der Mitglieder nach bis zu 60 Minuten."
Disconnect-ExchangeOnline -Confirm:$false""",
    },
    {
        "id": "emvia-skript-kalender",
        "typ": "skript",
        "titel": "Kalenderberechtigung setzen (sprachunabhaengig, auch deutscher Ordner 'Kalender')",
        "sprache": "powershell",
        "inhalt": r"""param(
    [Parameter(Mandatory)][string]$Postfach,
    [Parameter(Mandatory)][string]$Benutzer,
    [ValidateSet('AvailabilityOnly','LimitedDetails','Reviewer','Author','Editor')][string]$Recht = 'Reviewer'
)
Connect-ExchangeOnline -ShowBanner:$false
# Ordnername haengt von der Postfachsprache ab ('Kalender' / 'Calendar') -- daher ermitteln
$Ordner = (Get-MailboxFolderStatistics -Identity $Postfach -FolderScope Calendar |
           Where-Object FolderType -eq 'Calendar' | Select-Object -First 1).Name
$Ziel = "${Postfach}:\$Ordner"

if (Get-MailboxFolderPermission -Identity $Ziel -User $Benutzer -ErrorAction SilentlyContinue) {
    Set-MailboxFolderPermission -Identity $Ziel -User $Benutzer -AccessRights $Recht | Out-Null
} else {
    Add-MailboxFolderPermission -Identity $Ziel -User $Benutzer -AccessRights $Recht | Out-Null
}
Get-MailboxFolderPermission -Identity $Ziel | Select-Object User, AccessRights | Format-Table -AutoSize
Disconnect-ExchangeOnline -Confirm:$false""",
    },
    {
        "id": "emvia-skript-weiterleitungen",
        "typ": "skript",
        "titel": "Sicherheit: Weiterleitungen und Posteingangsregeln nach extern finden",
        "sprache": "powershell",
        "inhalt": r"""# Nur Bericht. Externe Weiterleitungen sind ein typisches Zeichen kompromittierter Konten
# und bei Gesundheitsdaten ein Datenschutzproblem. Laeuft je nach Postfachanzahl einige Minuten.
param([string[]]$EigeneDomains = @())   # z. B. @('firma.de') -- alles andere gilt als extern
Connect-ExchangeOnline -ShowBanner:$false
function IstExtern([string]$a) {
    if (-not $a) { return $false }
    $d = ($a -replace '^smtp:','').Split('@')[-1].TrimEnd(']').ToLower()
    return -not ($EigeneDomains | Where-Object { $d -eq $_.ToLower() })
}
$Funde = foreach ($Mb in Get-EXOMailbox -ResultSize Unlimited -Properties ForwardingSmtpAddress,ForwardingAddress) {
    if ($Mb.ForwardingSmtpAddress -and (IstExtern $Mb.ForwardingSmtpAddress)) {
        [pscustomobject]@{ Postfach=$Mb.UserPrincipalName; Art='Postfach-Weiterleitung'; Ziel=$Mb.ForwardingSmtpAddress }
    }
    foreach ($R in Get-InboxRule -Mailbox $Mb.UserPrincipalName -ErrorAction SilentlyContinue) {
        foreach ($Z in @($R.ForwardTo) + @($R.RedirectTo) + @($R.ForwardAsAttachmentTo)) {
            if ($Z -and (IstExtern ([string]$Z -replace '.*\[(smtp:)?','' -replace '\].*',''))) {
                [pscustomobject]@{ Postfach=$Mb.UserPrincipalName; Art="Regel '$($R.Name)'"; Ziel=[string]$Z }
            }
        }
    }
}
$Funde | Format-Table -AutoSize
$Funde | Export-Csv '.\emvia-externe-weiterleitungen.csv' -NoTypeInformation -Encoding UTF8
Disconnect-ExchangeOnline -Confirm:$false""",
    },
    {
        "id": "emvia-skript-adminrollen",
        "typ": "skript",
        "titel": "Wer hat Admin-Rollen? (aktive Zuweisungen)",
        "sprache": "powershell",
        "inhalt": r"""# Nur Bericht. Zeigt AKTIVE Rollenmitglieder; nur berechtigte PIM-Zuweisungen (eligible)
# erscheinen hier nicht -> Entra Admin Center > Privileged Identity Management.
Connect-MgGraph -Scopes 'RoleManagement.Read.Directory','User.Read.All' -NoWelcome
Get-MgDirectoryRole -All | ForEach-Object {
    $Rolle = $_.DisplayName
    Get-MgDirectoryRoleMember -DirectoryRoleId $_.Id -All | ForEach-Object {
        [pscustomobject]@{
            Rolle = $Rolle
            Mitglied = $_.AdditionalProperties.displayName
            UPN      = $_.AdditionalProperties.userPrincipalName
            Typ      = $_.AdditionalProperties.'@odata.type' -replace '#microsoft.graph.',''
        }
    }
} | Sort-Object Rolle, Mitglied | Format-Table -AutoSize
# Ziel: hoechstens 2-4 globale Admins, davon mind. 1 Break-Glass-Konto ohne MFA-Abhaengigkeit von Einzelpersonen.""",
    },
    {
        "id": "emvia-skript-gaeste-teams",
        "typ": "skript",
        "titel": "Gastkonten und besitzerlose Teams auflisten",
        "sprache": "powershell",
        "inhalt": r"""# Nur Bericht.
Connect-MgGraph -Scopes 'User.Read.All','Group.Read.All' -NoWelcome

"== Gastkonten"
Get-MgUser -All -Filter "userType eq 'Guest'" -Property DisplayName,Mail,CreatedDateTime,ExternalUserState |
    Select-Object DisplayName, Mail, CreatedDateTime, ExternalUserState |
    Sort-Object CreatedDateTime | Format-Table -AutoSize

"== Teams ohne Besitzer"
Get-MgGroup -All -Filter "resourceProvisioningOptions/Any(x:x eq 'Team')" -Property Id,DisplayName |
    Where-Object { -not (Get-MgGroupOwner -GroupId $_.Id -All) } |
    Select-Object DisplayName, Id | Format-Table -AutoSize""",
    },
    # ------------------------------------------------------- MDM / Intune
    {
        "id": "emvia-skript-intune-bestand",
        "typ": "skript",
        "titel": "Intune: Geraetebestand, nicht konforme und veraltete Geraete",
        "sprache": "powershell",
        "inhalt": r"""# Nur Bericht. Rolle: Intune-Administrator oder Intune-Leser (RBAC)
param([int]$TageOhneSync = 30)
Connect-MgGraph -Scopes 'DeviceManagementManagedDevices.Read.All' -NoWelcome
$Grenze = (Get-Date).AddDays(-$TageOhneSync)

$Geraete = Get-MgDeviceManagementManagedDevice -All |
    Select-Object DeviceName, UserPrincipalName, OperatingSystem, OsVersion, Model, SerialNumber,
        ComplianceState, ManagedDeviceOwnerType, EnrolledDateTime, LastSyncDateTime
$Geraete | Export-Csv '.\emvia-intune-geraete.csv' -NoTypeInformation -Encoding UTF8

"== Uebersicht nach Betriebssystem / Compliance"
$Geraete | Group-Object OperatingSystem, ComplianceState | Select-Object Count, Name | Format-Table -AutoSize
"== Nicht konform"
$Geraete | Where-Object ComplianceState -eq 'noncompliant' |
    Select-Object DeviceName, UserPrincipalName, OperatingSystem, LastSyncDateTime | Format-Table -AutoSize
"== Seit mehr als $TageOhneSync Tagen ohne Synchronisation (verloren? ausgemustert?)"
$Geraete | Where-Object { $_.LastSyncDateTime -lt $Grenze } |
    Select-Object DeviceName, UserPrincipalName, OperatingSystem, LastSyncDateTime |
    Sort-Object LastSyncDateTime | Format-Table -AutoSize""",
    },
    {
        "id": "emvia-skript-intune-aktion",
        "typ": "skript",
        "titel": "Intune: Geraet synchronisieren / Daten entfernen (Retire) / Zuruecksetzen (Wipe) -- Testlauf zuerst",
        "sprache": "powershell",
        "inhalt": r"""<#
  Sync   = Richtlinien sofort anwenden (harmlos)
  Retire = nur Firmendaten/-profile entfernen, private Daten bleiben (BYOD, Austritt)
  Wipe   = Werkseinstellungen, ALLE Daten weg (Verlust/Diebstahl, Rueckgabe Firmengeraet)
  Wipe/Retire sind NICHT umkehrbar -> Freigabe dokumentieren (Loeschnachweis, DSGVO).
#>
param(
    [Parameter(Mandatory)][string]$Geraetename,
    [ValidateSet('Sync','Retire','Wipe')][string]$Aktion = 'Sync',
    [bool]$Testlauf = $true
)
Connect-MgGraph -Scopes 'DeviceManagementManagedDevices.PrivilegedOperations.All','DeviceManagementManagedDevices.Read.All' -NoWelcome
$G = Get-MgDeviceManagementManagedDevice -All -Filter "deviceName eq '$Geraetename'"
if (-not $G)        { throw "Geraet '$Geraetename' nicht gefunden." }
if ($G.Count -gt 1) { $G | Select-Object Id, DeviceName, SerialNumber, UserPrincipalName | Format-Table; throw 'Name nicht eindeutig -- per Id/Seriennummer arbeiten.' }
"Ziel: $($G.DeviceName) | $($G.OperatingSystem) | SN $($G.SerialNumber) | $($G.UserPrincipalName) -> $Aktion"
if ($Testlauf -and $Aktion -ne 'Sync') { Write-Warning 'TESTLAUF -- mit -Testlauf $false ausfuehren.'; return }

switch ($Aktion) {
    'Sync'   { Sync-MgDeviceManagementManagedDevice   -ManagedDeviceId $G.Id }
    'Retire' { Invoke-MgRetireDeviceManagementManagedDevice -ManagedDeviceId $G.Id }
    'Wipe'   { Clear-MgDeviceManagementManagedDevice  -ManagedDeviceId $G.Id }
}
"Ausgeloest. Status: Intune Admin Center > Geraete > $($G.DeviceName) > Geraeteaktionsstatus" """,
    },
    {
        "id": "emvia-skript-autopilot-hash",
        "typ": "skript",
        "titel": "Windows Autopilot: Hardware-Hash eines neuen PCs erfassen",
        "sprache": "powershell",
        "inhalt": r"""# Auf dem NEUEN Geraet als Administrator ausfuehren (z. B. in der OOBE: Shift+F10 -> powershell).
# Variante A: Hash als CSV auf USB-Stick, Import im Intune Admin Center
#   (Geraete > Windows > Registrierung > Geraete > Importieren)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
Install-Script -Name Get-WindowsAutopilotInfo -Force
Get-WindowsAutopilotInfo -OutputFile "D:\autopilot-$env:COMPUTERNAME.csv"   # D: = USB-Stick anpassen

# Variante B: direkt hochladen (Anmeldung mit Intune-Admin-Konto, optional Gruppen-Tag)
# Get-WindowsAutopilotInfo -Online -GroupTag 'EMVIA-Standard'""",
    },
    {
        "id": "emvia-doku-mdm-pflegetablet",
        "typ": "doku",
        "titel": "MDM: Checkliste Pflege-Tablet / gemeinsam genutztes Geraet",
        "sprache": "",
        "inhalt": """PFLEGE-TABLET / SHARED DEVICE -- Checkliste (MDM-System laut Steckbrief)

[ ] Geraet als Firmengeraet registrieren (Android Enterprise "Dediziertes Geraet" bzw. iOS/iPadOS mit Apple Business Manager + automatischer Geraeteregistrierung)
[ ] Kiosk-/Mehrfach-App-Modus: nur Pflegedokumentation, Telefon/Messenger laut Freigabe, keine privaten App-Stores
[ ] Bildschirmsperre + PIN, Verschluesselung (Compliance-Richtlinie), automatische Sperre nach kurzer Zeit
[ ] Kamera/Screenshots einschraenken, wenn Gesundheitsdaten angezeigt werden (Datenschutz)
[ ] WLAN-Profil per MDM verteilen (kein manuelles Kennwort auf dem Geraet)
[ ] Updates: Zeitfenster ausserhalb der Uebergabezeiten der Pflege
[ ] Verlust: sofort sperren / Wipe, Vorfall dokumentieren (ggf. Meldepflicht Datenschutz pruefen)
[ ] Inventar: Seriennummer, Standort/Station, verantwortliche Person
""",
    },
    {
        "id": "emvia-ticket-intune-nicht-konform",
        "typ": "ticket",
        "titel": "Geraet 'nicht konform' -- Zugriff auf Outlook/Teams blockiert",
        "sprache": "",
        "inhalt": """PROBLEM: Benutzer meldet "Ihr Geraet erfuellt die Anforderungen nicht" / Zugriff durch Conditional Access blockiert.
EINGRENZEN: Intune Admin Center > Geraete > <Geraet> > Gerätekonformität: welche Richtlinie/Einstellung ist "Nicht konform"?
  Haeufig: veraltetes Betriebssystem, BitLocker/Verschluesselung aus, keine Bildschirmsperre, Geraet lange nicht synchronisiert.
LOESUNG: Ursache am Geraet beheben (Update, PIN setzen), dann Unternehmensportal-App > Einstellungen pruefen bzw. Sync ausloesen (Skript "Intune: Geraet synchronisieren"). Neubewertung kann bis zu ~8 h dauern; manueller Sync beschleunigt.
NIE: Benutzer dauerhaft aus der Conditional-Access-Richtlinie ausnehmen.""",
    },
    # ------------------------------------------------------------- E-Mail
    {
        "id": "emvia-mail-mfa",
        "typ": "email",
        "titel": "Anleitung MFA einrichten (Microsoft Authenticator)",
        "sprache": "",
        "inhalt": """Betreff: Ihr Microsoft-365-Zugang: Anmeldung absichern (5 Minuten)

Guten Tag {Name},

zum Schutz Ihres Kontos und der Daten unserer Bewohnerinnen und Bewohner richten Sie bitte einmalig die Bestaetigung per Smartphone ein:

1. Installieren Sie auf Ihrem Smartphone die App "Microsoft Authenticator" (App Store / Google Play).
2. Oeffnen Sie am PC https://aka.ms/mfasetup und melden Sie sich mit Ihrer dienstlichen Kennung an.
3. Waehlen Sie "Methode hinzufuegen" > "Authenticator-App" und folgen Sie den Schritten (QR-Code mit der App scannen).
4. Bestaetigen Sie die Testbenachrichtigung in der App.

Wichtig: Bestaetigen Sie eine Anmeldeanfrage NUR, wenn Sie sich gerade selbst anmelden. Kommen unerwartete Anfragen, lehnen Sie diese ab und melden Sie sich bei der IT.

Bei Fragen: {Kontakt IT}

Viele Gruesse
{Absender}""",
    },
    {
        "id": "emvia-mail-zugang",
        "typ": "email",
        "titel": "Neuer Zugang: Benutzerkennung an Vorgesetzte (OHNE Kennwort)",
        "sprache": "",
        "inhalt": """Betreff: Zugang fuer {Vorname Nachname} ab {Eintrittsdatum} eingerichtet

Guten Tag {Vorgesetzte/r},

der Microsoft-365-Zugang fuer {Vorname Nachname} ist eingerichtet:

  Benutzerkennung: {upn}
  E-Mail-Adresse:  {upn}
  Gruppen/Postfaecher: {Liste}

Das Startkennwort uebermitteln wir aus Sicherheitsgruenden getrennt ({persoenlich / telefonisch}). Bei der ersten Anmeldung muss es geaendert und die Anmeldebestaetigung per Smartphone eingerichtet werden (Anleitung folgt).

Viele Gruesse
{Absender}""",
    },
    {
        "id": "emvia-mail-sspr",
        "typ": "email",
        "titel": "Kennwort vergessen: Selbst zuruecksetzen",
        "sprache": "",
        "inhalt": """Betreff: Kennwort vergessen? So setzen Sie es selbst zurueck

Guten Tag {Name},

Sie koennen Ihr Kennwort jederzeit selbst zuruecksetzen:

1. https://aka.ms/sspr oeffnen
2. Dienstliche Kennung eingeben und das angezeigte Zeichenraetsel loesen
3. Identitaet ueber Ihre hinterlegte Methode (Authenticator-App / Telefon) bestaetigen
4. Neues Kennwort vergeben

Funktioniert das nicht (z. B. neues Smartphone), melden Sie sich bitte bei der IT unter {Kontakt IT}.

Viele Gruesse
{Absender}""",
    },
    # ------------------------------------------------------------- Tickets
    {
        "id": "emvia-ticket-lizenz-usagelocation",
        "typ": "ticket",
        "titel": "Neuer Benutzer hat kein Postfach / Lizenzfehler",
        "sprache": "",
        "inhalt": """PROBLEM: Neuer Benutzer kann Outlook nicht nutzen, im Admin Center "Lizenz konnte nicht zugewiesen werden" bzw. kein Postfach.
URSACHE (haeufig): 1) Nutzungsstandort (UsageLocation) fehlt  2) Lizenzgruppe hat keine freien Lizenzen  3) Hybrid: lokales Exchange-Postfach-Attribut vorhanden
PRUEFEN:
  Get-MgUser -UserId <upn> -Property UsageLocation,LicenseAssignmentStates | Select-Object UsageLocation -ExpandProperty LicenseAssignmentStates
  (State 'Error' + Error 'CountViolation' = keine freien Lizenzen, 'MutuallyExclusiveViolation' = widerspruechliche Plaene)
LOESUNG: Update-MgUser -UserId <upn> -UsageLocation DE ; Lizenzen nachkaufen/freigeben (Lizenzbericht-Skript), danach Gruppenlizenz neu verarbeiten (Entra > Gruppen > Lizenzen > Erneut verarbeiten). Postfach erscheint nach bis zu 30 Min.""",
    },
    {
        "id": "emvia-ticket-automapping",
        "typ": "ticket",
        "titel": "Freigegebenes Postfach erscheint nicht in Outlook",
        "sprache": "",
        "inhalt": """PROBLEM: Benutzer hat Vollzugriff, sieht das Postfach aber nicht in Outlook.
URSACHE: AutoMapping braucht bis zu 60 Min; Zugriff ueber Gruppe statt direkt (Gruppen-Vollzugriff wird NICHT automatisch eingebunden); Outlook-Cache.
PRUEFEN: Get-MailboxPermission -Identity <postfach> | Where-Object User -like '*<benutzer>*'
LOESUNG: Outlook neu starten / 60 Min warten. Bei Zugriff ueber Gruppe: direkt berechtigen oder manuell einbinden (Datei > Kontoeinstellungen > Aendern > Weitere Einstellungen > Erweitert > Hinzufuegen). Senden-als fehlt? Add-RecipientPermission ergaenzen (Wirkung bis zu 60 Min).""",
    },
    {
        "id": "emvia-ticket-anmeldung-gesperrt",
        "typ": "ticket",
        "titel": "Anmeldung schlaegt fehl / Konto gesperrt / MFA-Geraet verloren",
        "sprache": "",
        "inhalt": """PROBLEM: Benutzer kann sich nicht anmelden.
EINGRENZEN: Entra Admin Center > Benutzer > <Benutzer> > Anmeldeprotokolle: Fehlercode lesen.
  50126 = falsches Kennwort | 50053 = Konto gesperrt (Smart Lockout, zu viele Fehlversuche) | 50057 = Konto deaktiviert
  50074/50076 = MFA erforderlich | 53003 = durch Conditional Access blockiert (Richtlinie im Protokoll ansehen)
MFA-Geraet verloren: Identitaet pruefen (Rueckruf ueber bekannte Nummer/Vorgesetzte), dann Benutzer > Authentifizierungsmethoden > "MFA erneut registrieren erforderlich" bzw. befristeten Zugriffspass (TAP) ausstellen.
NIE: MFA-Ausnahme dauerhaft setzen oder Kennwort per E-Mail/Chat an unbestaetigte Absender schicken (Social Engineering!).""",
    },
)
