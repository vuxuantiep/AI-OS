# FAQ EMVIA: Benutzer und Konten (On-/Offboarding)

## Wie lege ich einen neuen Mitarbeiter an?
Werkzeug "On-/Offboarding" in der IT-Werkbank nutzen (Testlauf zuerst). Vorher klären: Ist die Identität Cloud-only oder Hybrid? Bei Hybrid (Entra Connect / Cloud Sync) wird das Konto im lokalen Active Directory in der richtigen OU angelegt, nicht in Entra. Danach Delta-Sync: `Start-ADSyncSyncCycle -PolicyType Delta` auf dem Sync-Server.

## Woran erkenne ich, ob ein Konto synchronisiert ist?
Entra > Benutzer > Spalte "Lokal synchronisiert" bzw. `Get-MgUser -UserId <upn> -Property OnPremisesSyncEnabled`. Bei `True` ändere ich Name, Abteilung, Sperre und Gruppen im lokalen AD. Änderungen in Entra werden sonst beim nächsten Sync überschrieben oder sind gar nicht möglich.

## Warum hat der neue Benutzer keine Lizenz oder kein Postfach?
Häufigste Ursachen: Nutzungsstandort (UsageLocation) fehlt, die Lizenzgruppe hat keine freien Lizenzen, oder Pläne widersprechen sich. Prüfen: Benutzer > Lizenzen und Apps bzw. `LicenseAssignmentStates` (Fehler `CountViolation` = keine freien Lizenzen). Ein Postfach erscheint nach erfolgreicher Lizenzierung meist innerhalb von 30 Minuten.

## Wie gebe ich das Startkennwort sicher weiter?
Getrennt von der Benutzerkennung, zum Beispiel die Kennung per Mail an die Vorgesetzten und das Kennwort persönlich oder telefonisch. "Kennwort bei nächster Anmeldung ändern" ist gesetzt. Für die MFA-Ersteinrichtung ohne Kennwort eignet sich ein befristeter Zugriffspass (Temporary Access Pass), falls er im Tenant aktiviert ist.

## Was ist beim Austritt die richtige Reihenfolge?
1. Anmeldung sperren (bei Hybrid im lokalen AD) und Sitzungen widerrufen.
2. Postfach in ein freigegebenes Postfach umwandeln, und zwar bevor die Lizenz entzogen wird. Sonst wird das Postfach 30 Tage nach dem Lizenzentzug endgültig gelöscht. Das Postfach NICHT vorher löschen: Es wird für Vertretung, Nachweise und Aufbewahrung gebraucht.
3. Abwesenheitsnotiz setzen.
4. Vertretung berechtigen, nur mit Freigabe.
5. Gruppen und Lizenzen entfernen.
6. Geräte zurücknehmen.

Werkzeug "On-/Offboarding" > Offboarding und die Checkliste im Vorlagen-Tab nutzen.

## Was passiert mit dem Postfach, wenn ich nur die Lizenz entziehe?
Das Postfach wird nach 30 Tagen Karenzzeit endgültig gelöscht. Deshalb vorher in ein freigegebenes Postfach umwandeln. Ohne Lizenz: max. 50 GB, kein Archivpostfach, kein Litigation Hold.

## Kann ich ein gelöschtes Konto wiederherstellen?
Ja, 30 Tage lang: Entra > Benutzer > Gelöschte Benutzer > Wiederherstellen. Postfach und OneDrive kommen mit zurück. OneDrive-Inhalte bleiben nach dem Löschen standardmäßig 30 Tage erhalten. In der Zeit kann man Vorgesetzten Zugriff geben (SharePoint Admin Center > Aufbewahrung).

## Benutzer ist gesperrt, was nun?
Anmeldeprotokolle lesen:
- 50053: Smart Lockout nach zu vielen Fehlversuchen, hebt sich nach kurzer Zeit selbst auf. Kennwort zurücksetzen hilft, wenn es vergessen wurde.
- 50057: Konto deaktiviert.
- 53003: von Conditional Access blockiert.

Bei vergessenem Kennwort zuerst auf Self-Service verweisen: https://aka.ms/sspr
