# FAQ EMVIA: Teams, SharePoint, OneDrive und Gäste

## Ein Team hat keinen Besitzer mehr, was tun?
Vorlage "Gastkonten und besitzerlose Teams" findet sie. Im Teams Admin Center > Teams > <Team> > Mitglieder einen neuen Besitzer festlegen. Jedes Team sollte mindestens zwei Besitzer haben.

## Team oder Gruppe versehentlich gelöscht?
Microsoft-365-Gruppen (und damit Teams) sind 30 Tage wiederherstellbar: Entra > Gruppen > Gelöschte Gruppen > Wiederherstellen bzw. M365 Admin Center > Teams und Gruppen > Gelöschte Gruppen.

## Wie gehe ich mit Gästen um?
Gäste (B2B) regelmäßig prüfen (Vorlage "Gastkonten"). Nicht mehr benötigte Gäste entfernen. Mit Entra ID P2 lassen sich Zugriffsüberprüfungen (Access Reviews) automatisieren. Sensible Bereiche (Personal, Bewohnerdaten) nicht für Gäste freigeben.

## Mitarbeiter tritt aus: Was wird aus seinem OneDrive?
Vor dem Löschen des Kontos Vorgesetzten Zugriff geben (M365 Admin Center > Benutzer > <Benutzer> > OneDrive > Zugriff auf Dateien erstellen) oder die Daten verschieben. Nach dem Löschen bleibt das OneDrive standardmäßig 30 Tage erhalten (einstellbar im SharePoint Admin Center > Einstellungen > OneDrive-Aufbewahrung).

## Datei versehentlich gelöscht oder überschrieben?
- Gelöscht: Papierkorb der Website bzw. des OneDrive (zwei Stufen, insgesamt 93 Tage).
- Überschrieben: Versionsverlauf der Datei.
- Ganze Bibliothek kaputt (z. B. Ransomware): "OneDrive wiederherstellen" bzw. "Diese Bibliothek wiederherstellen" auf einen Zeitpunkt der letzten 30 Tage.

## Externe Freigabe: Was ist erlaubt?
Das regeln die Freigabeeinstellungen im SharePoint Admin Center (Organisation) und je Website. Standardlinks auf "Personen in Ihrer Organisation" stellen, "Jeder"-Links nur, wenn es ausdrücklich erlaubt ist. Die internen Vorgaben stehen im EMVIA-Steckbrief.
