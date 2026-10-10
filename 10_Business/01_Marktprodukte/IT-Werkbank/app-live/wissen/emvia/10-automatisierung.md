# FAQ EMVIA: Tickets automatisieren und smarter arbeiten

Ziel: Jedes Ticket, das öfter kommt, wird beim dritten Mal abgeschafft. Die Reihenfolge ist immer Self-Service, dann Automatisierung, dann Handarbeit mit Vorlage.

## Welche Tickets lassen sich am leichtesten abschaffen?
1. **Kennwort vergessen / Konto gesperrt:** Self-Service-Kennwortzurücksetzung (SSPR) für alle einschalten. Bei Hybrid zusätzlich Kennwortrückschreiben in Entra Connect bzw. Cloud Sync. Registrierung zusammen mit MFA erzwingen (kombinierte Registrierung).
2. **Neues Handy / MFA weg:** Befristeter Zugriffspass (TAP) als Methode erlauben. Die Leitung bekommt beim Eintritt einen TAP statt eines Kennworts.
3. **„Bitte XY ins Team / in die Gruppe aufnehmen“:** Stations- bzw. Teamleitung als Besitzer der M365-Gruppe eintragen, dann pflegt die Leitung selbst. Oder dynamische Gruppen nach Abteilung/Standort einrichten.
4. **„Ich brauche Zugriff auf …“:** Zugriffspakete in My Access (Entra ID Governance bzw. P2). Ein Paket bündelt Gruppe, Team, SharePoint-Website und App, mit Genehmigung durch die Leitung und automatischem Ablauf.
5. **App installieren:** Apps im Unternehmensportal als „verfügbar“ veröffentlichen statt auf Zuruf installieren.

## Wie automatisiere ich Ein-, Um- und Austritt?
- **Ohne Zusatzlizenz:** Werkbank-Generator „On-/Offboarding“ plus dynamische Gruppen und Lizenz über Gruppe. Die Abteilungs- und Standort-Attribute entscheiden dann automatisch über Gruppen, Lizenz, Teams und Intune-Apps.
- **Mit Entra ID Governance:** Lifecycle Workflows. Sie starten anhand des Eintritts- bzw. Austrittsdatums (Attribut `employeeHireDate` / `employeeLeaveDateTime`): TAP an die Leitung schicken, Gruppen setzen, Willkommensmail. Beim Austritt: Konto sperren, aus Gruppen entfernen, nach X Tagen löschen. Workflows lassen sich jetzt klonen, z. B. eine Vorlage je Standort.
- Wichtig: Das Eintrittsdatum muss zuverlässig gepflegt sein, entweder aus der Personalabteilung (HR-Import) oder vom AD. Ohne saubere Stammdaten keine Automatisierung.

## Wie wird aus einem Ticket ein automatischer Ablauf?
Bewährtes Muster:
1. **Formular** (Microsoft Forms, Teams-App oder Ticketsystem) mit festen Feldern statt Freitext
2. **Power Automate** nimmt das Formular an, holt die Genehmigung der Leitung (Genehmigungsaktion in Teams)
3. **Azure Automation Runbook** (PowerShell mit Microsoft.Graph) führt aus, angemeldet über **Managed Identity**. Kein Kennwort und kein Secret im Skript.
4. Ergebnis als Kommentar zurück ins Ticket und als Nachricht an die anfragende Person
Die Werkbank-Skripte sind bereits so gebaut (Testlauf zuerst, minimale Scopes) und lassen sich als Runbook übernehmen.

## Wie gebe ich einer Managed Identity Graph-Rechte?
In der Automation-Konto-Identität einschalten, dann per PowerShell die App-Rollen vergeben (einmalig, als Global/Privileged Role Admin):
```powershell
Connect-MgGraph -Scopes 'AppRoleAssignment.ReadWrite.All','Application.Read.All' -NoWelcome
$Mi    = Get-MgServicePrincipal -Filter "displayName eq '<Name des Automation-Kontos>'"
$Graph = Get-MgServicePrincipal -Filter "appId eq '00000003-0000-0000-c000-000000000000'"
$Rolle = $Graph.AppRoles | Where-Object { $_.Value -eq 'User.Read.All' -and $_.AllowedMemberTypes -contains 'Application' }
New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $Mi.Id -PrincipalId $Mi.Id -ResourceId $Graph.Id -AppRoleId $Rolle.Id
```
Im Runbook dann: `Connect-MgGraph -Identity -NoWelcome`. Nur die Rollen vergeben, die das Runbook wirklich braucht.

## Was sind Intune Remediations und wofür lohnen sie sich?
Ein Skriptpaar läuft regelmäßig auf den Windows-Geräten: Das **Erkennungsskript** prüft einen Zustand (Exit 1 = Problem), das **Korrekturskript** behebt ihn. So werden Probleme gelöst, bevor jemand anruft. Gute Kandidaten:
- Druckwarteschlange hängt bzw. Dienst gestoppt
- Festplatte fast voll: Temp-Ordner und Teams-Cache leeren
- Uhrzeit falsch, deshalb scheitern Anmeldungen
- Altes VPN- oder WLAN-Profil entfernen
Lizenz: Windows Enterprise E3/E5 (in M365 E3/E5 enthalten) bzw. Business Premium mit Windows-Business-Berechtigung prüfen. Werkbank-Vorlage „Intune Remediation: Druckwarteschlange“ als Muster.

## Welche Berichte sollten automatisch kommen statt manuell gezogen?
- Wöchentlich: Benutzer ohne MFA, inaktive Konten (90 Tage), freie und verschwendete Lizenzen, nicht konforme Geräte
- Monatlich: Admin-Rollen-Zuweisungen, Gastkonten, besitzerlose Teams, ablaufende App-Secrets und Zertifikate
Alle Skripte liegen in der Werkbank im Modul EMVIA. Als Runbook mit Zeitplan laufen lassen und das Ergebnis per Power Automate in einen Teams-Kanal „IT-Berichte“ posten.

## Wobei hilft KI im Admin-Alltag wirklich?
- **Skripte schreiben und erklären:** Werkbank-Generator „PowerShell“. Immer im Testlauf prüfen. Erfundene Cmdlets fallen dort auf, wenn man `Get-Command <Name>` ausführt.
- **Logs lesen:** Fehlermeldung oder KQL-Ergebnis in den Werkbank-Chat geben (ohne Namen und Tenant-Daten!) und nach Ursache und nächstem Schritt fragen.
- **Security Copilot (falls E5):** CA-Optimierungsagent und Intune-Agenten machen Vorschläge, umgesetzt wird nur nach Admin-Freigabe.
- **Helpdesk-Agent:** beantwortet Standardfragen der Pflegekräfte aus den Wiki-Artikeln (Wiki-Seite 07).

## Welche Grundsätze gelten für jede Automatisierung?
- Testlauf zuerst ($Testlauf = $true), dann mit kleiner Pilotgruppe, dann für alle
- Least Privilege: minimale Graph-Rechte, Managed Identity statt Secret
- Jede Automatisierung schreibt ein Protokoll (wer, was, wann) und meldet Fehler an den IT-Kanal
- Dokumentieren: Was macht sie, wer ist verantwortlich, wie schaltet man sie ab?
