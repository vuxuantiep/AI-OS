"""
Vorlagen-Paket "EMVIA · Admin-Betrieb 2026" (Ticket-Schnellhilfe, Monitoring, proaktiv).

Ergaenzt paket_emvia_m365 und folgt denselben Regeln: wird von
store._vorlagen_pakete_einspielen() genau EINMAL je Instanz eingespielt
(eigene PAKET_ID, damit es auch in Instanzen ankommt, die emvia-m365-v1
schon haben), danach gehoeren die Vorlagen dem Nutzer.

- Berichte aendern nichts, aendernde Skripte starten als Testlauf.
- Minimale Graph-Scopes, keine Zugangsdaten/Tenant-IDs im Code.
- KQL-Vorlagen laufen im Log Analytics Workspace (Entra-Diagnoseeinstellungen
  muessen SigninLogs/AuditLogs dorthin senden).
"""

MODUL = "emvia"
PAKET_ID = "emvia-betrieb-v1"

VORLAGEN: tuple[dict, ...] = (
    # --------------------------------------------------------------- Skripte
    {
        "id": "emvia-skript-benutzer-diagnose",
        "typ": "skript",
        "titel": "Benutzer-Schnelldiagnose: Konto, letzte Fehlanmeldungen, MFA, Lizenzen, Geraete (Ticket-Erstpruefung)",
        "sprache": "powershell",
        "inhalt": r"""# Nur Bericht. Erste Pruefung bei JEDEM Konto-/Anmelde-Ticket -- ersetzt das Klicken durch 4 Portale.
# Rollen: Berichtsleser + Benutzeradministrator (lesend) bzw. Intune-Leser. Anmeldeprotokolle brauchen Entra ID P1.
param([Parameter(Mandatory)][string]$Upn, [int]$Anzahl = 10)
Connect-MgGraph -Scopes 'User.Read.All','AuditLog.Read.All','UserAuthenticationMethod.Read.All',
    'DeviceManagementManagedDevices.Read.All','GroupMember.Read.All' -NoWelcome

$U = Get-MgUser -UserId $Upn -Property DisplayName,UserPrincipalName,AccountEnabled,OnPremisesSyncEnabled,
    UsageLocation,LastPasswordChangeDateTime,SignInActivity,AssignedLicenses
"== Konto"
[pscustomobject]@{
    Name             = $U.DisplayName
    Aktiv            = $U.AccountEnabled
    Hybrid_Sync      = [bool]$U.OnPremisesSyncEnabled   # True: Kennwort/Sperre im lokalen AD aendern!
    Nutzungsstandort = $U.UsageLocation
    KennwortGeaendert= $U.LastPasswordChangeDateTime
    LetzteAnmeldung  = $U.SignInActivity.LastSignInDateTime
    Lizenzen         = $U.AssignedLicenses.Count
} | Format-List

"== Letzte $Anzahl Anmeldungen (ErrorCode 0 = erfolgreich)"
Get-MgAuditLogSignIn -Filter "userPrincipalName eq '$Upn'" -Top $Anzahl |
    Select-Object CreatedDateTime, AppDisplayName, IpAddress,
        @{n='Ort';    e={ "$($_.Location.City) $($_.Location.CountryOrRegion)" }},
        @{n='Code';   e={ $_.Status.ErrorCode }},
        @{n='Grund';  e={ $_.Status.FailureReason }},
        @{n='CA';     e={ $_.ConditionalAccessStatus }},
        @{n='Client'; e={ $_.ClientAppUsed }} | Format-Table -AutoSize -Wrap

"== Registrierte Anmeldemethoden"
Get-MgUserAuthenticationMethod -UserId $Upn |
    ForEach-Object { $_.AdditionalProperties['@odata.type'] -replace '#microsoft.graph.','' }

"== Intune-Geraete"
Get-MgDeviceManagementManagedDevice -Filter "userPrincipalName eq '$Upn'" -All |
    Select-Object DeviceName, OperatingSystem, OsVersion, ComplianceState, LastSyncDateTime | Format-Table -AutoSize

"== Gruppen"
Get-MgUserMemberOf -UserId $Upn -All |
    ForEach-Object { $_.AdditionalProperties['displayName'] } | Sort-Object

# Codes: 50126 Kennwort falsch | 50053 gesperrt | 50057 deaktiviert | 500121 MFA nicht bestanden
#        53003 CA-Block | 53000 Geraet nicht konform -> Wiki "Ticket-Schnellhilfe" """,
    },
    {
        "id": "emvia-skript-tap-sitzungen",
        "typ": "skript",
        "titel": "MFA-Handy verloren / Kompromittierung: TAP ausstellen und Sitzungen widerrufen (Testlauf zuerst)",
        "sprache": "powershell",
        "inhalt": r"""# VORHER Identitaet pruefen (Rueckruf ueber bekannte Nummer / Bestaetigung durch Leitung)!
# Rolle: Authentifizierungsadministrator. TAP muss in Entra > Authentifizierungsmethoden aktiviert sein.
param(
    [Parameter(Mandatory)][string]$Upn,
    [int]$Minuten = 60,
    [switch]$Kompromittiert,          # zusaetzlich: Konto sperren + Sitzungen widerrufen
    [bool]$Testlauf = $true
)
Connect-MgGraph -Scopes 'UserAuthenticationMethod.ReadWrite.All','User.ReadWrite.All' -NoWelcome

"Aktuelle Methoden von ${Upn}:"
Get-MgUserAuthenticationMethod -UserId $Upn |
    ForEach-Object { '  ' + ($_.AdditionalProperties['@odata.type'] -replace '#microsoft.graph.','') }

if ($Testlauf) {
    "TESTLAUF: wuerde TAP ($Minuten Min, einmalig) ausstellen" +
        $(if ($Kompromittiert) { ', Konto sperren und alle Sitzungen widerrufen' } else { '' })
    'Zum Ausfuehren: -Testlauf $false'
    return
}

if ($Kompromittiert) {
    Update-MgUser -UserId $Upn -AccountEnabled:$false
    Revoke-MgUserSignInSession -UserId $Upn | Out-Null
    'Konto gesperrt, Sitzungen widerrufen. Danach: Kennwort neu, unbekannte Methoden loeschen, Posteingangsregeln pruefen.'
} else {
    $Tap = New-MgUserAuthenticationTemporaryAccessPassMethod -UserId $Upn -BodyParameter @{
        lifetimeInMinutes = $Minuten
        isUsableOnce      = $true
    }
    "TAP gueltig bis $($Tap.StartDateTime.AddMinutes($Minuten)) -- NUR muendlich/telefonisch weitergeben:"
    $Tap.TemporaryAccessPass
    'Nutzer meldet sich mit TAP an und registriert unter https://aka.ms/mysecurityinfo Authenticator/Passkey neu.'
}""",
    },
    {
        "id": "emvia-skript-berechtigungs-check",
        "typ": "skript",
        "titel": "Berechtigungs-Check: Gruppen, Postfach-Vollzugriff und Senden-als eines Benutzers",
        "sprache": "powershell",
        "inhalt": r"""# Nur Bericht. Beantwortet "warum hat X (keinen) Zugriff?" und ist Pflicht beim Abteilungswechsel/Austritt.
# Rollen: Benutzeradministrator (lesend) + Exchange-Empfaengeradministrator. Postfach-Scan dauert bei vielen Postfaechern.
param([Parameter(Mandatory)][string]$Upn)
Connect-MgGraph -Scopes 'User.Read.All','GroupMember.Read.All' -NoWelcome
Connect-ExchangeOnline -ShowBanner:$false

"== Gruppen (M365-Gruppen steuern Team + SharePoint + Gruppenpostfach)"
Get-MgUserMemberOf -UserId $Upn -All | ForEach-Object {
    [pscustomobject]@{
        Gruppe    = $_.AdditionalProperties['displayName']
        M365      = ($_.AdditionalProperties['groupTypes'] -contains 'Unified')
        Dynamisch = ($_.AdditionalProperties['groupTypes'] -contains 'DynamicMembership')
    }
} | Sort-Object Gruppe | Format-Table -AutoSize

"== Vollzugriff auf Postfaecher"
Get-EXOMailbox -ResultSize Unlimited -RecipientTypeDetails UserMailbox,SharedMailbox,RoomMailbox |
    Get-MailboxPermission -User $Upn -ErrorAction SilentlyContinue |
    Select-Object Identity, AccessRights, IsInherited | Format-Table -AutoSize

"== Senden als"
Get-RecipientPermission -Trustee $Upn -ErrorAction SilentlyContinue |
    Select-Object Identity, AccessRights | Format-Table -AutoSize

Disconnect-ExchangeOnline -Confirm:$false
# SharePoint-Ordner mit eigener Berechtigung (Vererbung unterbrochen) sieht man hier NICHT:
# Website > Einstellungen > Websiteberechtigungen bzw. "Zugriff pruefen".""",
    },
    {
        "id": "emvia-skript-morgen-check",
        "typ": "skript",
        "titel": "Morgen-Check (proaktiv, 1 Minute): Microsoft-Stoerungen, freie Lizenzen, nicht konforme Geraete",
        "sprache": "powershell",
        "inhalt": r"""# Nur Bericht. Taeglich morgens oder als Azure-Automation-Runbook mit Ausgabe in den Teams-Kanal "IT-Alarm".
# Rollen: Dienstsupportadministrator/Berichtsleser + Intune-Leser.
param([int]$MinFreieLizenzen = 5, [int]$NichtSyncTage = 7)
Connect-MgGraph -Scopes 'ServiceHealth.Read.All','Organization.Read.All','DeviceManagementManagedDevices.Read.All' -NoWelcome

"== Offene Microsoft-Stoerungen (Exchange, Teams, SharePoint, Entra, Intune)"
Get-MgServiceAnnouncementIssue -Filter "isResolved eq false" -All |
    Where-Object { $_.Classification -eq 'incident' } |
    Select-Object Id, Service, Title, StartDateTime | Format-Table -AutoSize -Wrap

"== Lizenzen mit weniger als $MinFreieLizenzen freien Einheiten"
Get-MgSubscribedSku | ForEach-Object {
    $Frei = $_.PrepaidUnits.Enabled - $_.ConsumedUnits
    if ($_.PrepaidUnits.Enabled -gt 0 -and $Frei -lt $MinFreieLizenzen) {
        [pscustomobject]@{ Lizenz = $_.SkuPartNumber; Gesamt = $_.PrepaidUnits.Enabled; Frei = $Frei }
    }
} | Format-Table -AutoSize

"== Geraete nicht konform oder > $NichtSyncTage Tage ohne Sync"
$Grenze = (Get-Date).AddDays(-$NichtSyncTage)
Get-MgDeviceManagementManagedDevice -All |
    Where-Object { $_.ComplianceState -eq 'noncompliant' -or $_.LastSyncDateTime -lt $Grenze } |
    Select-Object DeviceName, UserPrincipalName, OperatingSystem, ComplianceState, LastSyncDateTime |
    Sort-Object LastSyncDateTime | Format-Table -AutoSize""",
    },
    {
        "id": "emvia-skript-secrets-ablauf",
        "typ": "skript",
        "titel": "App-Secrets und Zertifikate, die bald ablaufen (Ausfall von Schnittstellen verhindern)",
        "sprache": "powershell",
        "inhalt": r"""# Nur Bericht. Abgelaufene Secrets sind eine haeufige Ursache fuer "Schnittstelle/Scanner/Sync geht ploetzlich nicht".
# Rolle: Anwendungsadministrator (lesend) bzw. Globaler Leser.
param([int]$Tage = 30)
Connect-MgGraph -Scopes 'Application.Read.All' -NoWelcome
$Grenze = (Get-Date).AddDays($Tage)

Get-MgApplication -All -Property DisplayName,AppId,PasswordCredentials,KeyCredentials | ForEach-Object {
    $App = $_
    foreach ($S in $App.PasswordCredentials) {
        if ($S.EndDateTime -lt $Grenze) {
            [pscustomobject]@{ App = $App.DisplayName; Art = 'Secret'; Name = $S.DisplayName; Ablauf = $S.EndDateTime; AppId = $App.AppId }
        }
    }
    foreach ($K in $App.KeyCredentials) {
        if ($K.EndDateTime -lt $Grenze) {
            [pscustomobject]@{ App = $App.DisplayName; Art = 'Zertifikat'; Name = $K.DisplayName; Ablauf = $K.EndDateTime; AppId = $App.AppId }
        }
    }
} | Sort-Object Ablauf | Format-Table -AutoSize
# Bereits abgelaufene Eintraege (Ablauf in der Vergangenheit) erscheinen auch -- pruefen, ob die App noch genutzt wird.""",
    },
    {
        "id": "emvia-remediation-druckwarteschlange",
        "typ": "skript",
        "titel": "Intune Remediation (Muster): Druckwarteschlange erkennen und neu starten",
        "sprache": "powershell",
        "inhalt": r"""# Intune > Geraete > Skripts und Korrekturen > Erstellen. Zwei Dateien hochladen, als SYSTEM, 64-Bit.
# Erst an einer Testgruppe, Zeitplan z. B. stuendlich. Ergebnis: Spalten "Erkennungsstatus"/"Korrekturstatus".

# ===== Erkennung.ps1  (Exit 1 = Problem gefunden -> Korrektur laeuft) =====
$Dienst = Get-Service -Name Spooler -ErrorAction SilentlyContinue
$Haengt = Get-ChildItem "$env:SystemRoot\System32\spool\PRINTERS" -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddMinutes(-30) }
if ($Dienst.Status -ne 'Running' -or $Haengt) {
    Write-Output "Spooler=$($Dienst.Status), alte Auftraege=$(@($Haengt).Count)"
    exit 1
}
Write-Output 'OK'
exit 0

# ===== Korrektur.ps1 =====
Stop-Service -Name Spooler -Force -ErrorAction SilentlyContinue
Get-ChildItem "$env:SystemRoot\System32\spool\PRINTERS" -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddMinutes(-30) } | Remove-Item -Force -ErrorAction SilentlyContinue
Start-Service -Name Spooler
Write-Output "Spooler neu gestartet: $((Get-Service Spooler).Status)"
exit 0""",
    },
    # ------------------------------------------------------------------- KQL
    {
        "id": "emvia-kql-anmeldeprobleme",
        "typ": "skript",
        "titel": "KQL: Anmeldeprobleme erkennen (gesperrt, CA-Block, MFA abgelehnt, Ausland, Fehler-Top-10)",
        "sprache": "kql",
        "inhalt": r"""// Log Analytics Workspace > Protokolle. Voraussetzung: Entra-Diagnoseeinstellung sendet SigninLogs.
// Jede Abfrage einzeln markieren und ausfuehren. Als Alarmregel: Azure Monitor > Warnungen > Neue Regel > Benutzerdefinierte Protokollsuche.

// 1) Fehler-Top-10 der letzten 24 h -- was brennt gerade?
SigninLogs
| where TimeGenerated > ago(24h) and ResultType != "0"
| summarize Anzahl = count(), Benutzer = dcount(UserPrincipalName) by ResultType, ResultDescription
| top 10 by Anzahl

// 2) Gesperrte Konten (50053) >= 3x in 1 h  -> ALARM
SigninLogs
| where TimeGenerated > ago(1h) and ResultType == "50053"
| summarize Versuche = count(), IPs = make_set(IPAddress), Apps = make_set(AppDisplayName) by UserPrincipalName
| where Versuche >= 3

// 3) Welche Conditional-Access-Regel blockiert wen (53003)
SigninLogs
| where TimeGenerated > ago(24h) and ResultType == "53003"
| mv-expand CA = ConditionalAccessPolicies
| where tostring(CA.result) == "failure"
| summarize Anzahl = count() by UserPrincipalName, Regel = tostring(CA.displayName), AppDisplayName
| order by Anzahl desc

// 4) MFA nicht bestanden (500121) gehaeuft -> MFA-Muedigkeit/Angriff oder Handyproblem  -> ALARM
SigninLogs
| where TimeGenerated > ago(24h) and ResultType == "500121"
| summarize Anzahl = count() by UserPrincipalName, bin(TimeGenerated, 1h)
| where Anzahl >= 3

// 5) Erfolgreiche Anmeldung ausserhalb DE  -> ALARM (Ausnahmen: Urlaub abstimmen)
SigninLogs
| where TimeGenerated > ago(24h) and ResultType == "0"
| extend Land = tostring(LocationDetails.countryOrRegion)
| where isnotempty(Land) and Land != "DE"
| project TimeGenerated, UserPrincipalName, Land, IPAddress, AppDisplayName

// 6) Neue Admin-Rollenzuweisung  -> ALARM
AuditLogs
| where TimeGenerated > ago(24h) and OperationName has "Add member to role"
| project TimeGenerated, Wer = tostring(InitiatedBy.user.userPrincipalName),
          Ziel = tostring(TargetResources[0].userPrincipalName), Details = TargetResources  // Rolle steht in modifiedProperties (Role.DisplayName)""",
    },
    {
        "id": "emvia-kql-intune",
        "typ": "skript",
        "titel": "KQL: Intune-Geraete nicht konform / lange ohne Kontakt",
        "sprache": "kql",
        "inhalt": r"""// Voraussetzung: Intune > Mandantenverwaltung > Diagnoseeinstellungen sendet "Devices" an den Workspace.
// Spaltennamen koennen je nach Schema-Version abweichen: einmal "IntuneDevices | take 5" ausfuehren und abgleichen.
IntuneDevices
| where TimeGenerated > ago(1d)
| summarize arg_max(TimeGenerated, *) by DeviceId
| extend LetzterKontakt = todatetime(LastContact)
| where CompliantState != "Compliant" or LetzterKontakt < ago(7d)
| project DeviceName, UPN, OS, CompliantState, LetzterKontakt
| order by LetzterKontakt asc""",
    },
    # --------------------------------------------------------------- Tickets
    {
        "id": "emvia-ticket-vpn-zugang",
        "typ": "ticket",
        "titel": "VPN / Zugang ins interne Netz geht nicht (Global Secure Access oder klassisches VPN)",
        "sprache": "",
        "inhalt": """PROBLEM: Benutzer erreicht Fileserver/Pflegedoku/RDP von unterwegs nicht.
ERST KLAEREN: Welche Technik nutzt EMVIA? (Steckbrief) -> Entra Private Access (GSA-Client) oder klassisches VPN.
GSA / ENTRA PRIVATE ACCESS:
  1. GSA-Symbol in der Taskleiste: verbunden? "Erweiterte Diagnose" -> Integritaetspruefung, Protokolle exportieren.
  2. Entra > Anmeldeprotokolle: 53003 = CA-Regel blockiert, 53000 = Geraet nicht konform (Intune pruefen).
  3. Entra > Global Secure Access > Connectors: Private Network Connector aktiv?
  4. Ziel (FQDN/IP + Port) im App-Segment / Quick Access? Interne DNS-Aufloesung (private DNS) eingetragen?
  5. Global Secure Access > Traffic-Logs: kommt der Verkehr an, erlaubt oder blockiert?
KLASSISCHES VPN:
  1. Internet ok? Fehlermeldung des VPN-Clients als Screenshot.
  2. Intune > Geraet > Geraetekonfiguration: VPN-Profil/Zertifikat "Erfolgreich"? Zertifikat abgelaufen?
  3. Konto gesperrt/Kennwort abgelaufen? (Benutzer-Schnelldiagnose). RADIUS/NPS: Ereignisprotokoll NPS.
  4. Gateway-/Firewall-Log: Authentifizierung abgelehnt oder Tunnel ok, aber Ziel nicht erreichbar (Routing/DNS)?
LOESUNG DOKUMENTIEREN: Ursache + Fehlercode. Bei mehreren Betroffenen gleichzeitig: Stoerung -> Info an Standorte.""",
    },
    {
        "id": "emvia-ticket-berechtigung",
        "typ": "ticket",
        "titel": "Kein Zugriff auf Ordner / Team / Postfach (Berechtigung)",
        "sprache": "",
        "inhalt": """PROBLEM: Benutzer sieht Ordner, Team, SharePoint-Website oder Postfach nicht bzw. "Zugriff verweigert".
FRAGE 1: Woher SOLL der Zugriff kommen? Gruppe / direkt / geerbt -- und wer genehmigt ihn (Leitung)?
PRUEFEN:
  - Skript "Berechtigungs-Check" (Gruppen, Postfach-Vollzugriff, Senden-als)
  - Dynamische Gruppe? Attribut (Abteilung/Standort) im Benutzerkonto korrekt?
  - SharePoint: Website > Websiteberechtigungen bzw. "Zugriff pruefen"; Ordner mit eigener Berechtigung = Vererbung unterbrochen
  - Anmeldeprotokoll 53003/53000? Dann ist es Conditional Access/Geraet, KEINE fehlende Berechtigung
LOESUNG: ueber die Gruppe berechtigen, nicht direkt. Wirkzeit: Postfach bis 60 Min, Teams/SharePoint teils mehrere Stunden.
DAUERHAFT: wiederkehrende Faelle als Zugriffspaket (My Access) oder Leitung als Gruppenbesitzer eintragen.""",
    },
    # ------------------------------------------------------------------ Doku
    {
        "id": "emvia-doku-proaktiv-routine",
        "typ": "doku",
        "titel": "Proaktiv-Routine: taeglich / woechentlich / monatlich / quartalsweise",
        "sprache": "",
        "inhalt": """TAEGLICH (ca. 10 Min, morgens)
[ ] Skript "Morgen-Check": Microsoft-Stoerungen, knappe Lizenzen, nicht konforme/nicht synchronisierte Geraete
[ ] Defender: neue Vorfaelle, Quarantaene (Freigabeanfragen)
[ ] Teams-Kanal "IT-Alarm" durchsehen, jeden Alarm als Ticket abschliessen oder Regel nachschaerfen

WOECHENTLICH
[ ] Nachrichtencenter lesen (Aenderungen mit Handlungsbedarf als Ticket anlegen)
[ ] Berichte: MFA-Luecken, inaktive Konten, Weiterleitungen nach extern
[ ] Intune: Update-Ringe/Windows-Updates, fehlgeschlagene App-Installationen
[ ] Secure Score: eine Empfehlung umsetzen
[ ] Top-3-Tickettypen der Woche: welches davon wird Self-Service/Automatisierung/Wiki-Artikel?

MONATLICH
[ ] Admin-Rollen-Zuweisungen (PIM), Notfallkonten unveraendert?
[ ] Gastkonten, besitzerlose Teams
[ ] App-Secrets/Zertifikate < 60 Tage (Skript)
[ ] Entra > Empfehlungen; Lizenzkosten (gesperrte Konten mit Lizenz)
[ ] EWS-Nutzungsbericht bis zur Abschaltung 01.04.2027

QUARTALSWEISE
[ ] Access Reviews: wer hat noch Zugriff auf sensible Bereiche (Personal, Bewohnerdaten)?
[ ] Notfallkonten-Anmeldung testen und dokumentieren
[ ] Conditional-Access-Richtlinien gegen Anmeldeprotokolle pruefen (Report-only-Ergebnisse)
[ ] Wiederherstellung testen (geloeschte Datei/Postfachelement/Gruppe)""",
    },
)
