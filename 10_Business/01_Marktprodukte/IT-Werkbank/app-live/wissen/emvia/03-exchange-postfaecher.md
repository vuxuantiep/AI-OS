# FAQ EMVIA: Exchange Online und Postfächer

## Wie lege ich ein freigegebenes Postfach an (z. B. für einen Standort)?
Vorlage "Freigegebenes Postfach anlegen". Danach `MessageCopyForSentAsEnabled` setzen, damit gesendete Mails auch im freigegebenen Postfach landen und nicht nur beim Absender. Ohne Lizenz: max. 50 GB.

## Unterschied Vollzugriff, Senden als, Senden im Auftrag?
- Vollzugriff (FullAccess): Postfach öffnen und lesen.
- Senden als (SendAs): Mail erscheint, als käme sie direkt vom Postfach.
- Senden im Auftrag (SendOnBehalf): Empfänger sieht "X im Auftrag von Y".
Vollzugriff und Senden als werden getrennt vergeben (`Add-MailboxPermission` bzw. `Add-RecipientPermission`).

## Warum erscheint das freigegebene Postfach nicht in Outlook?
AutoMapping braucht bis zu 60 Minuten und funktioniert nur bei direkter Berechtigung, nicht über Gruppen. Lösung: Outlook neu starten, warten, oder manuell einbinden (Kontoeinstellungen > Ändern > Weitere Einstellungen > Erweitert > Hinzufügen).

## Wie vergebe ich Kalenderrechte?
Vorlage "Kalenderberechtigung setzen". Der Ordnername hängt von der Postfachsprache ab ("Kalender" oder "Calendar"), die Vorlage ermittelt ihn selbst. Stufen: AvailabilityOnly (nur frei/gebucht), LimitedDetails (plus Betreff/Ort), Reviewer (lesen), Editor (bearbeiten).

## Darf ich auf das Postfach eines Mitarbeiters zugreifen?
Nur mit dokumentierter Freigabe nach den internen Regeln (Vorgesetzte, Datenschutz, ggf. Betriebsrat). Vier-Augen-Prinzip. Der Zugriff ist im Audit-Protokoll nachvollziehbar. Gerade im Pflegeumfeld können Gesundheitsdaten enthalten sein.

## Eine Mail ist nicht angekommen, wie finde ich sie?
Exchange Admin Center > Nachrichtenfluss > Nachrichtenablaufverfolgung (Absender, Empfänger, Zeitraum). Steht dort "Quarantäne", dann in Defender (https://security.microsoft.com > Quarantäne) prüfen und ggf. freigeben.

## Wie finde ich gefährliche Weiterleitungen?
Vorlage "Weiterleitungen und Posteingangsregeln nach extern finden". Externe Weiterleitungen, die niemand kennt, sind ein typisches Zeichen für ein kompromittiertes Konto. Dann Kennwort zurücksetzen, Sitzungen widerrufen, Regel löschen und den Vorfall melden.

## Postfach ist voll, was tun?
Größe prüfen (Vorlage "Postfachgrößen" im Modul Microsoft 365). Optionen: Archivpostfach aktivieren (Lizenz nötig), Aufbewahrungsrichtlinie, alte Elemente aufräumen lassen. Freigegebene Postfächer über 50 GB brauchen eine Lizenz.
