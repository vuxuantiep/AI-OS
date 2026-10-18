# EMVIA: Benutzerverwaltung AD + Exchange verstehen (Lernseite zur Abnahme M1)

Diese Seite erklärt die Befehle hinter Neuanlage, Änderung, Austritt, Kennwort-Reset und Funktionspostfächern. Sie sagt jeweils, **was** ein Befehl tut und **warum**. Das passende PowerShell-Modul liegt unter `skripte/emvia/EmviaAdmin/` (Werkbank-Vorlage „EmviaAdmin-Modul“). Bei Widerspruch gelten immer die EMVIA-Richtlinien IT.10.0x und der Pate.

## Grundbegriffe, die man sicher können muss
- **sAMAccountName** (z. B. `DE123456`): der „alte“ Anmeldename (`EMVIA\DE123456`), maximal 20 Zeichen, eindeutig in der Domäne.
- **UserPrincipalName / UPN** (z. B. `DE123456@emvia.de`): der Anmeldename im E-Mail-Format. Über ihn findet M365 das Konto nach dem Sync.
- **OU (Organisationseinheit)**: ein Ordner im AD. Er bestimmt, welche Gruppenrichtlinien greifen und wer das Konto verwalten darf (Stufe 2: nur in den Einrichtungs-OUs).
- **DN (Distinguished Name)**: der volle Pfad eines Objekts, z. B. `CN=Muster\, Anna,OU=0350,OU=Einrichtungen,DC=emvia,DC=local`. Das `\,` ist das maskierte Komma aus „Nachname, Vorname“. AD setzt es selbst.
- **OENR**: Nummer der Einrichtung. Daraus ergibt sich die Einrichtungsgruppe `G_<OENR>`, z. B. `G_0350`.
- **Rollengruppe**: Sie gibt die Rechte der Stelle (Pflege, EL, PDL …). Rechte kommen **immer über Gruppen**, nie direkt ans Konto. Bei Wechsel oder Austritt reicht dann die Gruppenpflege.
- **Hybrid**: Das Konto entsteht im lokalen AD. Entra Connect synchronisiert es nach M365, das dauert bis ca. 30 Minuten. Deshalb änderst du Kennwort, Sperre und Gruppen eines Sync-Kontos **im AD**, nicht im M365-Portal.

## Die vier Zeilen der Neuanlage, Zeile für Zeile
```powershell
# Kennwort verdeckt abfragen. -AsSecureString: es steht nie im Klartext in der Konsole oder im Verlauf.
$pw = Read-Host "Einmalkennwort" -AsSecureString

# Konto anlegen.
#  -Name               Anzeigename im AD-Baum (CN), Schema "Nachname, Vorname"
#  -GivenName/-Surname Vor- und Nachname (für Adressbuch, Suche)
#  -SamAccountName     Anmeldename EMVIA\DE123456
#  -UserPrincipalName  Anmeldung in M365
#  -Path               Ziel-OU als DN (z. B. "OU=0350,OU=Einrichtungen,DC=...")
#  -Description        Stelle + OENR -> man sieht sofort, wohin das Konto gehört
#  -ChangePasswordAtLogon $true   Einmalkennwort, der Nutzer muss es sofort ändern
#  -Enabled $true      ohne das wäre das Konto deaktiviert angelegt
New-ADUser -Name "Nachname, Vorname" -GivenName "Vorname" -Surname "Nachname" `
  -SamAccountName "DE123456" -UserPrincipalName "DE123456@emvia.de" `
  -Path "<OU der Einrichtung>" -Description "<Stelle> <OENR>" `
  -AccountPassword $pw -ChangePasswordAtLogon $true -Enabled $true

# Einrichtungsgruppe: darüber kommen Laufwerke, Drucker, Verteiler der Einrichtung.
Add-ADGroupMember -Identity "G_0350" -Members "DE123456"

# Postfach (in der Exchange Management Shell!):
#  lokal:  Enable-Mailbox
#  Hybrid: Enable-RemoteMailbox -RemoteRoutingAddress DE123456@<tenant>.mail.onmicrosoft.com
Enable-Mailbox -Identity "DE123456"
```
Was der einfachen Fassung fehlt und das Modul (`New-EmviaBenutzer`) ergänzt: Prüfung auf Doppelanlage, `-DisplayName`, die **Rollengruppe**, `-Title`/`-Department`, das Ablaufdatum bei Fremdpersonal, ein Probelauf (`-WhatIf`) und der Protokolleintrag mit Ticketnummer.

## Neuanlage, Änderung, Austritt: der Ablauf und warum
**Neuanlage:** Antrag prüfen (vollständig, berechtigt?) → `Get-ADUser` zeigt, ob es das Konto schon gibt → anlegen → G_<OENR> + Rollengruppe → Postfach → Lizenz (meist über eine Lizenzgruppe) → Einmalkennwort über den geregelten Weg übergeben → Ticket dokumentieren.

**Fremdpersonal** (Leasing, Dienstleister): immer mit **Ablaufdatum** (`AccountExpirationDate`) und Firma in der Beschreibung. Das Konto sperrt sich dann von selbst, niemand muss an den Austritt denken. Meist bekommt Fremdpersonal kein Postfach oder nur eins mit eingeschränkter Lizenz.

**Änderung:** Bei einer Namensänderung bleibt die Kennung gleich, nur Anzeigename und CN ändern sich (`Rename-ADObject`, sonst steht im AD-Baum weiter der alte Name). Beim Einrichtungswechsel verschiebst du das Konto in die neue OU, entfernst die alte G_<OENR> und fügst die neue hinzu. Die Rollengruppe tauschst du nur, wenn sich die Stelle ändert.

**Austritt:** Nicht löschen, sondern **deaktivieren**. Ein gelöschtes und neu angelegtes Konto bekommt eine neue SID, dann sind alle Datei- und Postfachrechte weg. Reihenfolge:
1. Gruppenliste sichern (ins Protokoll), dann Konto deaktivieren
2. Gruppen entfernen. Damit fallen auch die Lizenzgruppen weg und die Lizenz wird frei.
3. Beschreibung „AUSTRITT <Datum> <Ticket>“ setzen, aus dem Adressbuch ausblenden (`msExchHideFromAddressLists`)
4. In die Austritts-OU verschieben
5. Optional: Postfach in ein freigegebenes Postfach umwandeln (Vertretung braucht Zugriff) und Sitzungen widerrufen, wenn es sofort wirken muss
6. Nach der Aufbewahrungsfrist endgültig löschen. Das Modul erlaubt es nur bei deaktiviertem Konto in der Austritts-OU.

## Kennwort-Reset und Entsperren nach EMVIA-Regel
- Erst **Status lesen** (`Get-EmviaKontoStatus`): Oft ist das Konto nur gesperrt oder abgelaufen, dann ist ein Reset unnötig.
- Reset **nur** auf Anforderung aus dem **Funktionspostfach der Einrichtungsleitung** oder nach **Rückruf an die bekannte Durchwahl** aus dem Telefonverzeichnis. Nie an die Nummer, die der Anrufer nennt. Das ist der Schutz gegen Social Engineering („Hier ist die PDL, ich brauche schnell das Kennwort von …“).
- Im Modul sind `-Pruefweg` und `-Nachweis` Pflicht. Die Regel lässt sich also nicht vergessen, und der Nachweis steht im Protokoll.
- `Set-ADAccountPassword -Reset` setzt das Kennwort als Admin, das alte wird nicht gebraucht. Danach `ChangePasswordAtLogon`.
- **Ständig wieder gesperrt?** Irgendwo ist ein altes Kennwort gespeichert (Handy-Mail, gespeicherte Anmeldedaten, zweiter PC). `Get-EmviaSperrquelle` liest Ereignis **4740** auf dem PDC-Emulator. Dort steht der Rechner, der die Sperre ausgelöst hat.
- Neue Gruppenmitgliedschaften wirken erst nach **Ab- und Anmelden**, weil das Kerberos-Ticket die Gruppen beim Anmelden einmal einsammelt.

## Funktionspostfächer und ihre drei Rechte
| Recht | Was es erlaubt | Befehl (Exchange Online / lokal) |
|---|---|---|
| Vollzugriff | Postfach öffnen, lesen, löschen | `Add-MailboxPermission -AccessRights FullAccess` |
| Senden als | Mail kommt *von* it@emvia.de, der Absender ist unsichtbar | `Add-RecipientPermission -AccessRights SendAs` / `Add-ADPermission -ExtendedRights 'Send As'` |
| Senden im Auftrag | „Anna Muster im Auftrag von it@emvia.de“ | `Set-Mailbox -GrantSendOnBehalfTo @{Add=...}` |

- `@{Add=...}` / `@{Remove=...}` ergänzt die Liste bzw. entfernt einen Eintrag. Ein `-GrantSendOnBehalfTo user` ohne Hashtable **überschreibt** die ganze Liste. Das ist ein klassischer Fehler.
- **AutoMapping:** Das Postfach erscheint nach bis zu 60 Minuten automatisch in Outlook, aber nur bei direkt berechtigten Personen, nicht über Gruppen.
- Vor jedem Entzug den Ist-Stand mit `Get-EmviaPostfachRechte` ins Ticket kopieren. Das ist der Nachweis für M1 „Rechte vergeben **und entzogen**“.
- Wo setze ich das Recht? Dort, wo das Postfach liegt: Exchange Online (`Connect-ExchangeOnline`) oder lokaler Exchange (EMS).

## M365: Lizenz und MFA (Rolle Authentifizierungs- und Benutzeradministrator)
- **Lizenz:** Wird bei EMVIA über Gruppen lizenziert, nimmst du den Nutzer in die Lizenzgruppe auf. Eine direkte Zuweisung (`Set-EmviaLizenz`) ist die Ausnahme. Ohne **Nutzungsstandort** (UsageLocation = DE) schlägt jede Zuweisung fehl.
- **MFA-Reset (neues Handy):** Identität prüfen wie beim Kennwort, dann alte Methoden entfernen und einen **befristeten Zugriffspass (TAP)** ausstellen, 60 Minuten, einmalig nutzbar. Der Nutzer meldet sich damit an und richtet unter https://aka.ms/mysecurityinfo den Authenticator neu ein. Nur Methoden zu löschen wäre gefährlich: Dann könnte jeder mit dem Kennwort eine eigene MFA registrieren.

## Abnahme M1: welcher Befehl erfüllt welchen Punkt
| Checkliste M1 | Nachweis |
|---|---|
| je 3 Neuanlagen, Änderungen, Austritte | `Get-EmviaProtokoll -Seit <Datum> \| Group-Object Aktion` |
| Kennwort-Resets nur nach Regeln | Spalte „Pruefweg“ im Protokoll |
| Funktionspostfach-Rechte vergeben und entzogen | Aktionen „Postfachrecht+“ / „Postfachrecht-“ |
| Lizenz und MFA bearbeitet | Aktionen „Lizenz +/-“, „MFA-Reset“ |
| Prioritäten, Weitergabe an synaforce / Ditcon / SAP-Team | im Ticketsystem, nicht im Modul |
| Anliegen vollständig dokumentiert | Ticketnummer ist bei jeder Änderung Pflicht |

## Übungsreihenfolge bis 29.10.
1. **Mo/Di 19.–20.10. (Pate zeigt):** nur die Lese-Befehle `Get-EmviaKontoStatus`, `Get-EmviaBenutzerGruppen`, `Get-EmviaPostfachRechte`. Ergebnisse mit dem vergleichen, was der Pate im Portal zeigt.
2. **Ab Mi 21.10. (selbst, Pate prüft):** jede Änderung zuerst mit `-WhatIf` und die Ausgabe dem Paten zeigen. Erst dann echt ausführen.
3. **Ab 26.10.:** M365-Teil (Lizenz, MFA, TAP) und Anträge selbstständig.
4. **Vor dem 29.10.:** `Get-EmviaProtokoll` mit der Checkliste abgleichen: Fehlt ein Punkt (z. B. erst 2 Austritte)?
