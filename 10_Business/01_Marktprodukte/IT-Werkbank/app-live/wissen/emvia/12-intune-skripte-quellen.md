# FAQ EMVIA: Intune-Skripte aus fremden Quellen richtig nutzen

Quelle geprüft am 10.10.2026: github.com/tomwechsler/Microsoft_Endpoint_Manager (Ordner Scripts, 14 Skripte). Gute Ideen, aber zum großen Teil veraltete Technik. Das Repo hat keine Lizenz, deshalb sind die Skripte in der Werkbank nicht kopiert, sondern **neu geschrieben** (Modul EMVIA, Vorlagen „Intune-Konfiguration sichern“, „Intune-Sicherungen vergleichen“, „Was bekommt diese Gruppe?“, „LAPS/BitLocker abrufen“, „Intune-Änderungsprotokoll“, „Alte Anmeldeprotokolle finden“).

## Woran erkenne ich ein veraltetes Intune-Skript?
- `Microsoft.Graph.Intune`, `Connect-MSGraph`, `Get-IntuneDeviceConfigurationPolicy`, `Get-AADGroup`: altes Intune-PowerShell-Modul, nicht mehr gepflegt. Die zugehörige App-Registrierung „Microsoft Intune PowerShell“ funktioniert nicht mehr.
- `AzureAD`, `MSOnline`: abgeschaltet
- `IntuneBackupAndRestore` baut auf dem alten Modul auf. Ersatz ist die Werkbank-Vorlage „Intune-Konfiguration sichern“ oder das Community-Tool IntuneManagement bzw. Microsoft365DSC.
- `MSAL.PS` mit App-Registrierung: unnötig, `Connect-MgGraph` erledigt die Anmeldung
Ersatz für alles: das Modul **Microsoft.Graph** mit `Connect-MgGraph` und `Invoke-MgGraphRequest` für Intune-Endpunkte (meist `/beta/deviceManagement/...`).

## Was ist an solchen Beispielskripten gefährlich?
- **Client-Secret, Tenant-ID oder Benutzername im Skript**: Wer das Skript hat, hat den Zugang. Stattdessen interaktiv anmelden (`Connect-MgGraph`) oder im Runbook mit Managed Identity.
- **Kennwort per `ConvertFrom-SecureString` in einer Datei**: Das ist nur an diesen PC und diesen Benutzer gebunden und funktioniert ohnehin nicht mehr mit MFA. Nicht verwenden.
- **`Set-ExecutionPolicy Unrestricted`**: nicht systemweit setzen. Wenn nötig, `-Scope Process -ExecutionPolicy Bypass` nur für die Sitzung.
- **Automatischer Import bzw. Wiederherstellung**: legt doppelte Richtlinien an und kann Zuweisungen überschreiben. Immer erst eine Testgruppe, nie blind den ganzen Tenant zurückspielen.
- **Massenänderungen ohne Testlauf** (z. B. UPN aller AD-Benutzer ändern): erst Ausgabe prüfen, dann mit kleiner Gruppe. UPN-Änderungen betreffen Anmeldung, OneDrive-Pfade und gespeicherte Profile.

## Welche Skripte sparen mir im Intune-Alltag die meiste Zeit?
- **Was bekommt diese Gruppe?** Die häufigste Intune-Frage im Ticket: „Warum hat das Gerät die App bzw. Einstellung (nicht)?“ Das Skript zeigt alle Zuweisungen einer Gruppe, inklusive Ausschlüssen.
- **Intune-Änderungsprotokoll:** „Seit gestern geht X nicht.“ Das Skript zeigt, wer in den letzten Tagen etwas geändert hat.
- **Sicherung und Vergleich:** vor jeder größeren Änderung sichern. Bei Problemen die alte mit der neuen Sicherung vergleichen, das zeigt, welche Richtlinie sich geändert hat.
- **LAPS/BitLocker:** Lokales Admin-Kennwort und BitLocker-Schlüssel in einer Minute, mit Protokoll. Danach das LAPS-Kennwort in Intune rotieren lassen.
- **Alte Anmeldeprotokolle:** findet Scanner und Programme mit POP/IMAP/SMTP-Auth oder EWS, bevor sie nach einer Abschaltung als Störung gemeldet werden.

## Wie gehe ich mit BitLocker-Wiederherstellung im Ticket um?
1. Identität prüfen (Rückruf über bekannte Nummer oder Leitung). Den Schlüssel nie per Mail oder Chat herausgeben.
2. Am Gerät die angezeigte Schlüssel-ID (erste 8 Zeichen) mit der Liste vergleichen.
3. Abruf im Ticket begründen, denn er steht im Entra-Überwachungsprotokoll.
4. Nach der Nutzung einen neuen Schlüssel erzeugen lassen (Intune > Gerät > „BitLocker-Schlüssel rotieren“).
5. Ob Benutzer ihren eigenen Schlüssel selbst sehen dürfen (Self-Service unter myaccount.microsoft.com), regelt Entra > Geräte > Geräteeinstellungen > „Benutzer daran hindern, den BitLocker-Schlüssel für ihre eigenen Geräte wiederherzustellen“. Für EMVIA mit IT-Leitung und Datenschutz entscheiden.

## Darf ich fremde Skripte einfach übernehmen?
Ohne Lizenzangabe im Repo nicht 1:1 in eigene Produkte oder Wikis kopieren. Lesen, verstehen und selbst neu schreiben ist in Ordnung, die Quelle als Inspiration nennen. Fremde Skripte nie ungeprüft im Kunden-Tenant ausführen: erst lesen, dann in einer Testumgebung bzw. mit einem Konto mit nur Leserechten testen.
