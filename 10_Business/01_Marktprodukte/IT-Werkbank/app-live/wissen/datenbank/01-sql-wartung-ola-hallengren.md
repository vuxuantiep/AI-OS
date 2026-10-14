# FAQ Datenbank: SQL-Server-Wartung mit Ola Hallengren

Quelle: https://ola.hallengren.com/ (SQL Server Maintenance Solution, MIT-Lizenz, kostenlos). Die Werkbank liefert das Skript nicht mit. Lade es immer aktuell von der Downloads-Seite. Passende Vorlagen im Modul Datenbank: „Ola Hallengren Maintenance Solution installieren“, „Zeitpläne für die Ola-Jobs anlegen“, „Ola-Aufrufe mit empfohlenen Parametern“, „Morgen-Kontrolle“, „Monatlicher Wiederherstellungstest“, „Wartungsplan SQL Server“.

## Was ist die Ola Hallengren Maintenance Solution?
Eine Sammlung gespeicherter Prozeduren für die drei Pflichtaufgaben jeder SQL-Server-Instanz:
- **DatabaseBackup**: Voll-, Differenz- und Protokollsicherung mit Prüfsumme, Überprüfung, Komprimierung und automatischer Bereinigung alter Dateien.
- **DatabaseIntegrityCheck**: führt DBCC CHECKDB aus und findet beschädigte Datenseiten.
- **IndexOptimize**: baut Indizes nur bei Bedarf neu auf bzw. reorganisiert sie und aktualisiert Statistiken.
Jeder Befehl landet in der Tabelle `master.dbo.CommandLog`, so ist jederzeit nachvollziehbar, was wann gelaufen ist und was fehlschlug.

## Warum nicht einfach den Wartungsplan-Assistenten von SQL Server?
- Der Assistent baut **jeden** Index jede Woche neu, auch wenn er nicht fragmentiert ist. Das kostet Zeit, Protokollplatz und Sicherungsgröße.
- Ola arbeitet nach Schwellwerten: unter 5 % Fragmentierung passiert nichts, zwischen 5 und 30 % wird reorganisiert, über 30 % neu aufgebaut. Statistiken aktualisiert er nur, wenn sie sich geändert haben.
- Bereinigung erst **nach** erfolgreicher Sicherung, saubere Ordnerstruktur `Server\Datenbank\Typ`, Protokoll in einer Tabelle, die sich überwachen lässt.

## Wie installiere ich es?
1. `MaintenanceSolution.sql` von ola.hallengren.com laden.
2. Im Kopf des Skripts anpassen: `@CreateJobs = 'Y'`, `@BackupDirectory` (Freigabe **außerhalb** des DB-Servers), `@CleanupTime` (Stunden, z. B. 336 = 14 Tage), `@LogToTable = 'Y'`.
3. In SSMS als sysadmin in `master` ausführen. Zuerst in der Testumgebung.
4. **Wichtig:** Die SQL-Agent-Jobs werden **ohne Zeitplan** angelegt. Ohne Zeitplan läuft gar nichts. Die Werkbank-Vorlage „Zeitpläne für die Ola-Jobs anlegen“ ausführen.
5. Datenbank-E-Mail und einen Operator einrichten, damit ein fehlgeschlagener Job alarmiert.

## Welcher Zeitplan ist sinnvoll?
- Vollsicherung täglich nachts, Differenzsicherung alle 6 Stunden, **Protokollsicherung alle 15 Minuten** rund um die Uhr. Das Protokollintervall bestimmt, wie viele Minuten Daten bei einem Totalausfall höchstens verloren gehen.
- Integritätsprüfung wöchentlich (Sonntag), Index- und Statistikpflege wöchentlich (Samstag), nicht gleichzeitig mit der Vollsicherung.
- Bei großen Datenbanken mit kurzem Fenster: werktags `@PhysicalOnly = 'Y'`, am Wochenende den vollständigen CHECKDB.

## Was muss ich bei SQL Server Express beachten?
Express hat keinen SQL-Agent. Die Prozeduren funktionieren trotzdem. Sie werden über die Windows-Aufgabenplanung mit `sqlcmd -E -S .\SQLEXPRESS -d master -Q "EXECUTE dbo.DatabaseBackup ..." -b` gestartet.

## Was hat es mit ONLINE- und OFFLINE-Neuaufbau auf sich?
Ein Online-Neuaufbau lässt die Tabelle während der Arbeit nutzbar, gibt es aber nur in Enterprise bzw. Developer. In der Standard Edition fällt Ola automatisch auf OFFLINE zurück. Die Tabelle ist dann für die Dauer gesperrt, deshalb IndexOptimize nur im Wartungsfenster laufen lassen.

## Woran sehe ich jeden Morgen, ob alles läuft?
Vorlage „Morgen-Kontrolle“: zeigt je Datenbank das Wiederherstellungsmodell, die letzte Voll-, Diff- und Protokollsicherung, den letzten erfolgreichen CHECKDB, Fehler im CommandLog, fehlgeschlagene Jobs und `msdb.dbo.suspect_pages`. Rot sind: Modell SIMPLE bei einer Fachanwendungs-DB, Vollsicherung älter als 26 Stunden, Protokollsicherung älter als 30 Minuten.

## Veeam sichert doch schon die VM. Brauche ich das trotzdem?
Veeam sichert die VM. Für Point-in-Time-Wiederherstellung braucht es aber eine lückenlose Protokollkette. Entscheidend: **Nur ein System darf die Protokolle sichern.** Wenn Veeam mit „Protokolle kürzen“ arbeitet und gleichzeitig Ola Protokolle sichert, entstehen zwei halbe Ketten, und die Wiederherstellung schlägt im Ernstfall fehl. Festlegen, dokumentieren und in der Morgen-Kontrolle prüfen.

## Wie weiß ich, dass die Sicherung wirklich funktioniert?
Nur durch Zurückspielen. Monatlich die Vorlage „Monatlicher Wiederherstellungstest“ (dbatools `Test-DbaLastBackup`) gegen eine Testinstanz laufen lassen: Wiederherstellung, CHECKDB, Zeitmessung. Die gemessene Dauer ist die echte Wiederherstellungszeit (RTO). Der CSV-Bericht ist der Nachweis für Leitung und Datenschutz.
