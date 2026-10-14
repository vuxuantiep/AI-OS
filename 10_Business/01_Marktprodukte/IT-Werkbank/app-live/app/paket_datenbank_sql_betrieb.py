"""
Vorlagen-Paket "Datenbank · SQL-Server-Betrieb".

Wartung nach Ola Hallengren (ola.hallengren.com, MIT-Lizenz): Sicherung,
Integritaetspruefung, Index- und Statistikpflege. Das Wartungsskript selbst
wird NICHT mitgeliefert, sondern immer aktuell von der Originalseite geladen;
hier stehen nur Installationsparameter, Zeitplaene, Aufrufe und Kontrollen.
Dazu das Rollback-Konzept fuer fehlerhafte Updates (Snapshot, markierte
Transaktion, Schlussprotokoll, Point-in-Time) als Skripte + Runbooks.
Einspielen wie die EMVIA-Pakete: eigene PAKET_ID, genau einmal je Instanz.
"""

MODUL = "datenbank"
PAKET_ID = "datenbank-sql-betrieb-v1"

VORLAGEN: tuple[dict, ...] = (
    # ------------------------------------------------------------ Wartung
    {
        "id": "db-ola-installation",
        "typ": "skript",
        "titel": "Ola Hallengren Maintenance Solution installieren (Sicherung, CHECKDB, Indexpflege)",
        "sprache": "sql",
        "inhalt": r"""-- 1) MaintenanceSolution.sql IMMER aktuell von https://ola.hallengren.com/downloads.html
--    laden (MIT-Lizenz) -- nicht aus alten Kopien/Foren. Erst in der Testumgebung.
-- 2) Im Kopf des Skripts NUR diese Variablen anpassen, dann komplett in SSMS ausfuehren
--    (als sysadmin, Datenbank master):
--
--    SET @CreateJobs      = 'Y'                          -- legt SQL-Agent-Jobs an (ohne Zeitplan!)
--    SET @BackupDirectory = N'\\backupserver\sql'        -- NICHT auf dem DB-Server selbst
--    SET @CleanupTime     = 336                          -- Stunden: Sicherungen 14 Tage behalten
--    SET @OutputFileDirectory = NULL                     -- Standard-Logordner der Instanz
--    SET @LogToTable      = 'Y'                          -- jedes Kommando in master.dbo.CommandLog
--
-- 3) Ergebnis pruefen: Objekte + Jobs vorhanden?
SELECT name, type_desc FROM master.sys.objects
WHERE name IN ('CommandLog','CommandExecute','DatabaseBackup','DatabaseIntegrityCheck','IndexOptimize');

SELECT name, enabled FROM msdb.dbo.sysjobs
WHERE name LIKE 'DatabaseBackup%' OR name LIKE 'DatabaseIntegrityCheck%'
   OR name LIKE 'IndexOptimize%'  OR name IN ('CommandLog Cleanup','Output File Cleanup',
                                              'sp_delete_backuphistory','sp_purge_jobhistory');

-- 4) Danach Vorlage "Zeitplaene fuer die Ola-Jobs anlegen" ausfuehren.
-- Hinweise:
--  * SQL Server EXPRESS hat keinen SQL-Agent: Prozeduren per Windows-Aufgabenplanung + sqlcmd
--    aufrufen, z. B. sqlcmd -E -S .\SQLEXPRESS -d master -Q "EXECUTE dbo.DatabaseBackup ..." -b
--  * Dienstkonto des SQL Servers braucht Schreibrecht auf @BackupDirectory.
--  * Sichert schon Veeam mit "Protokolle kuerzen"? Dann EINEN Verantwortlichen fuer die
--    Protokollsicherung festlegen, sonst entsteht eine lueckenhafte Protokollkette.""",
    },
    {
        "id": "db-ola-zeitplaene",
        "typ": "skript",
        "titel": "Zeitplaene fuer die Ola-Hallengren-Jobs anlegen (Voll, Diff, Log 15 Min, CHECKDB, Index)",
        "sprache": "sql",
        "inhalt": r"""-- Die Installation legt die Jobs OHNE Zeitplan an -- ohne diesen Schritt laeuft nichts.
-- Zeiten an das Wartungsfenster anpassen; Index/CHECKDB nicht parallel zur Vollsicherung.
USE msdb;
GO
-- Vollsicherung Benutzer-DBs: taeglich 01:00
EXEC sp_add_jobschedule @job_name = N'DatabaseBackup - USER_DATABASES - FULL', @name = N'taeglich 01:00',
     @freq_type = 4, @freq_interval = 1, @active_start_time = 010000;
-- Differenziell: alle 6 Stunden ab 07:00
EXEC sp_add_jobschedule @job_name = N'DatabaseBackup - USER_DATABASES - DIFF', @name = N'alle 6 Std',
     @freq_type = 4, @freq_interval = 1, @freq_subday_type = 8, @freq_subday_interval = 6,
     @active_start_time = 070000;
-- Transaktionsprotokoll: alle 15 Minuten, rund um die Uhr (bestimmt den max. Datenverlust)
EXEC sp_add_jobschedule @job_name = N'DatabaseBackup - USER_DATABASES - LOG', @name = N'alle 15 Min',
     @freq_type = 4, @freq_interval = 1, @freq_subday_type = 4, @freq_subday_interval = 15,
     @active_start_time = 000000;
-- Systemdatenbanken (master, model, msdb): taeglich 00:30
EXEC sp_add_jobschedule @job_name = N'DatabaseBackup - SYSTEM_DATABASES - FULL', @name = N'taeglich 00:30',
     @freq_type = 4, @freq_interval = 1, @active_start_time = 003000;
-- Integritaetspruefung: sonntags 02:00 (Benutzer) / 01:30 (System)   freq_interval 1 = Sonntag
EXEC sp_add_jobschedule @job_name = N'DatabaseIntegrityCheck - USER_DATABASES', @name = N'So 02:00',
     @freq_type = 8, @freq_interval = 1, @freq_recurrence_factor = 1, @active_start_time = 020000;
EXEC sp_add_jobschedule @job_name = N'DatabaseIntegrityCheck - SYSTEM_DATABASES', @name = N'So 01:30',
     @freq_type = 8, @freq_interval = 1, @freq_recurrence_factor = 1, @active_start_time = 013000;
-- Index- und Statistikpflege: samstags 03:00   freq_interval 64 = Samstag
EXEC sp_add_jobschedule @job_name = N'IndexOptimize - USER_DATABASES', @name = N'Sa 03:00',
     @freq_type = 8, @freq_interval = 64, @freq_recurrence_factor = 1, @active_start_time = 030000;
-- Aufraeumen (Historie, CommandLog, Ausgabedateien): sonntags 05:00
EXEC sp_add_jobschedule @job_name = N'sp_delete_backuphistory', @name = N'So 05:00',
     @freq_type = 8, @freq_interval = 1, @freq_recurrence_factor = 1, @active_start_time = 050000;
EXEC sp_add_jobschedule @job_name = N'sp_purge_jobhistory', @name = N'So 05:05',
     @freq_type = 8, @freq_interval = 1, @freq_recurrence_factor = 1, @active_start_time = 050500;
EXEC sp_add_jobschedule @job_name = N'CommandLog Cleanup', @name = N'So 05:10',
     @freq_type = 8, @freq_interval = 1, @freq_recurrence_factor = 1, @active_start_time = 051000;
EXEC sp_add_jobschedule @job_name = N'Output File Cleanup', @name = N'So 05:15',
     @freq_type = 8, @freq_interval = 1, @freq_recurrence_factor = 1, @active_start_time = 051500;
GO
-- Alarm bei Fehlschlag: Datenbank-E-Mail + Operator einrichten, dann je Job:
-- EXEC msdb.dbo.sp_update_job @job_name = N'DatabaseBackup - USER_DATABASES - LOG',
--      @notify_level_email = 2, @notify_email_operator_name = N'IT-Alarm';""",
    },
    {
        "id": "db-ola-aufrufe",
        "typ": "skript",
        "titel": "Ola-Aufrufe mit empfohlenen Parametern (Backup, DatabaseIntegrityCheck, IndexOptimize)",
        "sprache": "sql",
        "inhalt": r"""-- So sollten die Job-Schritte aussehen (Job > Schritte > Befehl). Die Installation erzeugt
-- aehnliche Aufrufe; diese Werte sind ein bewaehrter Standard fuer kleine/mittlere Instanzen.

-- SICHERUNG ------------------------------------------------------------------------------
EXECUTE dbo.DatabaseBackup
    @Databases = 'USER_DATABASES',
    @Directory = N'\\backupserver\sql',
    @BackupType = 'FULL',            -- 'DIFF' bzw. 'LOG' fuer die anderen Jobs
    @Verify = 'Y',                   -- RESTORE VERIFYONLY nach jeder Sicherung
    @CheckSum = 'Y',                 -- Seitenpruefsummen mitsichern/pruefen
    @Compress = 'Y',
    @CleanupTime = 336,              -- Stunden; alte Dateien erst NACH erfolgreicher Sicherung loeschen
    @ChangeBackupType = 'Y',         -- DIFF/LOG ohne vorherige Vollsicherung -> automatisch FULL
    @LogToTable = 'Y';

-- INTEGRITAETSPRUEFUNG (findet beschaedigte Seiten, BEVOR die Sicherungen sie weitertragen)
EXECUTE dbo.DatabaseIntegrityCheck
    @Databases = 'USER_DATABASES',
    @CheckCommands = 'CHECKDB',
    @LogToTable = 'Y';
-- Sehr grosse DB, zu kleines Fenster: unter der Woche @PhysicalOnly = 'Y', am Wochenende komplett.

-- INDEX- UND STATISTIKPFLEGE --------------------------------------------------------------
EXECUTE dbo.IndexOptimize
    @Databases = 'USER_DATABASES',
    @FragmentationLow = NULL,                                            -- < 5 %: nichts tun
    @FragmentationMedium = 'INDEX_REORGANIZE,INDEX_REBUILD_ONLINE,INDEX_REBUILD_OFFLINE', -- 5-30 %
    @FragmentationHigh = 'INDEX_REBUILD_ONLINE,INDEX_REBUILD_OFFLINE',  -- > 30 %
    @FragmentationLevel1 = 5,
    @FragmentationLevel2 = 30,
    @MinNumberOfPages = 1000,         -- kleine Indizes ignorieren (Nutzen ~0)
    @UpdateStatistics = 'ALL',
    @OnlyModifiedStatistics = 'Y',    -- nur geaenderte Statistiken -> deutlich schneller
    @LogToTable = 'Y';
-- REBUILD_ONLINE gibt es nur in Enterprise/Developer; in Standard faellt Ola automatisch auf
-- OFFLINE zurueck -> Tabelle ist waehrenddessen gesperrt => nur im Wartungsfenster laufen lassen.

-- SONDERSICHERUNG vor einem Update (stoert die Sicherungskette nicht):
-- EXECUTE dbo.DatabaseBackup @Databases = 'PflegeDB', @Directory = N'\\backupserver\sql',
--     @BackupType = 'FULL', @CopyOnly = 'Y', @Verify = 'Y', @CheckSum = 'Y', @Compress = 'Y',
--     @Description = 'vor Update 12.3', @LogToTable = 'Y';""",
    },
    {
        "id": "db-wartung-kontrolle",
        "typ": "skript",
        "titel": "Morgen-Kontrolle: letzte Sicherungen, Wiederherstellungsmodell, CHECKDB, Fehler im CommandLog",
        "sprache": "sql",
        "inhalt": r"""-- Nur lesend. Taeglich morgens oder als Monitoring-Abfrage (Checkmk/Zabbix: SQL-Pruefung).
-- 1) Je Datenbank: Modell, letzte Voll-/Diff-/Log-Sicherung, letzter erfolgreicher CHECKDB
SELECT d.name AS DB,
       d.recovery_model_desc AS Modell,
       MAX(CASE WHEN b.type = 'D' THEN b.backup_finish_date END) AS LetzteVoll,
       MAX(CASE WHEN b.type = 'I' THEN b.backup_finish_date END) AS LetzteDiff,
       MAX(CASE WHEN b.type = 'L' THEN b.backup_finish_date END) AS LetztesLog,
       DATABASEPROPERTYEX(d.name, 'LastGoodCheckDbTime') AS LetzterCheckDB,   -- ab SQL 2016 SP2
       CASE
         WHEN d.recovery_model_desc = 'SIMPLE' AND d.database_id > 4 THEN 'WARNUNG: SIMPLE -> kein Point-in-Time'
         WHEN MAX(CASE WHEN b.type = 'D' THEN b.backup_finish_date END) < DATEADD(HOUR, -26, GETDATE())
           OR MAX(CASE WHEN b.type = 'D' THEN b.backup_finish_date END) IS NULL THEN 'FEHLER: keine Vollsicherung < 26 h'
         WHEN d.recovery_model_desc = 'FULL'
          AND (MAX(CASE WHEN b.type = 'L' THEN b.backup_finish_date END) < DATEADD(MINUTE, -30, GETDATE())
            OR MAX(CASE WHEN b.type = 'L' THEN b.backup_finish_date END) IS NULL) THEN 'FEHLER: Log-Sicherung > 30 Min alt'
         ELSE 'ok'
       END AS Bewertung
FROM sys.databases d
LEFT JOIN msdb.dbo.backupset b ON b.database_name = d.name AND b.is_copy_only = 0
WHERE d.name <> 'tempdb' AND d.source_database_id IS NULL      -- keine Snapshots
GROUP BY d.name, d.recovery_model_desc, d.database_id
ORDER BY Bewertung DESC, d.name;

-- 2) Fehler der Wartungsjobs der letzten 7 Tage (Ola-Protokoll)
SELECT StartTime, DatabaseName, CommandType, ErrorNumber, ErrorMessage
FROM master.dbo.CommandLog
WHERE ErrorNumber <> 0 AND StartTime > DATEADD(DAY, -7, GETDATE())
ORDER BY StartTime DESC;

-- 3) Fehlgeschlagene Agent-Jobs der letzten 24 h
SELECT j.name, h.run_date, h.run_time, h.message
FROM msdb.dbo.sysjobhistory h JOIN msdb.dbo.sysjobs j ON j.job_id = h.job_id
WHERE h.step_id = 0 AND h.run_status = 0
  AND msdb.dbo.agent_datetime(h.run_date, h.run_time) > DATEADD(HOUR, -24, GETDATE());

-- 4) Beschaedigte Seiten, die SQL Server bereits bemerkt hat (sollte leer sein)
SELECT * FROM msdb.dbo.suspect_pages;""",
    },
    {
        "id": "db-restore-test",
        "typ": "skript",
        "titel": "Monatlicher Wiederherstellungstest mit Zeitmessung (dbatools Test-DbaLastBackup)",
        "sprache": "powershell",
        "inhalt": r"""# Spielt die letzte Sicherung jeder DB auf einer TEST-Instanz zurueck, fuehrt CHECKDB aus und
# loescht die Testkopie wieder. Die gemessene Dauer = euer echtes RTO (Wiederherstellungszeit).
# dbatools (MIT-Lizenz): Install-Module dbatools -Scope CurrentUser
param(
    [string]$Quelle = 'SQLPROD01',            # Produktiv-Instanz (nur lesend: Sicherungshistorie)
    [string]$Ziel   = 'SQLTEST01',            # Test-Instanz mit Zugriff auf die Sicherungsfreigabe
    [string[]]$Datenbanken,                   # leer = alle Benutzer-DBs
    [string]$Bericht = ".\restore-test_$(Get-Date -Format 'yyyy-MM').csv"
)
Import-Module dbatools
$Param = @{ SqlInstance = $Quelle; Destination = $Ziel; Prefix = 'rtest_' }
if ($Datenbanken) { $Param.Database = $Datenbanken }

$Ergebnis = Test-DbaLastBackup @Param
$Ergebnis | Select-Object Database, RestoreResult, DbccResult, RestoreElapsed, DbccElapsed, FileExists, BackupDate |
    Tee-Object -Variable Tabelle | Format-Table -AutoSize
$Tabelle | Export-Csv $Bericht -NoTypeInformation -Encoding UTF8 -Delimiter ';'

$Fehler = $Ergebnis | Where-Object { $_.RestoreResult -ne 'Success' -or $_.DbccResult -ne 'Success' }
if ($Fehler) { Write-Warning "Wiederherstellung FEHLGESCHLAGEN: $($Fehler.Database -join ', ') -> sofort Ticket!" }
else         { "Alle Wiederherstellungen ok. Bericht: $Bericht (als Nachweis im Monatsbericht ablegen)" }
# Die Testkopien enthalten echte Personendaten: Test-Instanz gleich schuetzen wie Produktion.""",
    },
    # ----------------------------------------------------------- Rollback
    {
        "id": "db-rollback-vorbereiten",
        "typ": "skript",
        "titel": "Rollback vorbereiten VOR einem Update: Sondersicherung, Snapshot, markierte Transaktion",
        "sprache": "sql",
        "inhalt": r"""-- Im Wartungsfenster, NACHDEM die Anwendung gestoppt ist (niemand schreibt mehr).
-- Platzhalter: PflegeDB, Update_12_3, Pfade. Wiederherstellungsmodell muss FULL sein.
USE master;
DECLARE @DB sysname = N'PflegeDB', @Name sysname = N'Update_12_3',
        @SnapOrdner nvarchar(260) = N'D:\Snapshots\';   -- gleiche Instanz, genug Platz

-- 1) Letzte Protokollsicherung + Sondersicherung (COPY_ONLY stoert die Kette nicht)
EXECUTE dbo.DatabaseBackup @Databases = @DB, @Directory = N'\\backupserver\sql', @BackupType = 'LOG',
        @CheckSum = 'Y', @LogToTable = 'Y';
EXECUTE dbo.DatabaseBackup @Databases = @DB, @Directory = N'\\backupserver\sql', @BackupType = 'FULL',
        @CopyOnly = 'Y', @Verify = 'Y', @CheckSum = 'Y', @Compress = 'Y',
        @Description = 'vor Update 12.3', @LogToTable = 'Y';

-- 2) Datenbank-Snapshot (alle Datendateien, erzeugt sich selbst aus sys.master_files)
DECLARE @sql nvarchar(max) = N'CREATE DATABASE ' + QUOTENAME(@DB + N'_Snap_' + @Name) + N' ON ';
SELECT @sql += STRING_AGG(CONVERT(nvarchar(max),
         N'(NAME = ' + QUOTENAME(name) + N', FILENAME = N''' + @SnapOrdner + @DB + N'_' + name + N'.ss'')'), N', ')
FROM sys.master_files WHERE database_id = DB_ID(@DB) AND type_desc = 'ROWS';
SET @sql += N' AS SNAPSHOT OF ' + QUOTENAME(@DB) + N';';
PRINT @sql;  EXEC (@sql);

-- 3) Markierte Transaktion = benannter Punkt im Protokoll fuer STOPBEFOREMARK
SET @sql = N'USE ' + QUOTENAME(@DB) + N';
IF OBJECT_ID(N''dbo.it_wartungsmarke'') IS NULL CREATE TABLE dbo.it_wartungsmarke (zeit datetime2, text nvarchar(200));
BEGIN TRAN ' + @Name + N' WITH MARK N''Beginn ' + @Name + N''';
  INSERT dbo.it_wartungsmarke VALUES (SYSDATETIME(), N''' + @Name + N''');
COMMIT;';
EXEC (@sql);
-- Hinweis: Tabelle it_wartungsmarke mit dem Hersteller abstimmen; alternativ jede eigene
-- Hilfstabelle. Ohne Schreibzugriff wird keine Marke ins Protokoll geschrieben.

-- 4) Kontrolle
SELECT name, create_date FROM sys.databases WHERE source_database_id = DB_ID(@DB);
SELECT TOP (1) mark_name, mark_time FROM msdb.dbo.logmarkhistory WHERE database_name = @DB ORDER BY mark_time DESC;
-- logmarkhistory fuellt sich erst mit der naechsten Log-Sicherung.
-- Danach: App-Server-Pruefpunkt, Update einspielen, Funktionstest.
-- Nach der Beobachtungsphase ohne Rollback: DROP DATABASE [PflegeDB_Snap_Update_12_3];""",
    },
    {
        "id": "db-rollback-snapshot",
        "typ": "skript",
        "titel": "Rollback Fall A: Datenbank auf den Snapshot zurueckdrehen (Minuten, kein Datenverlust vor Freigabe)",
        "sprache": "sql",
        "inhalt": r"""-- NUR solange seit dem Update noch keine echten Benutzereingaben passiert sind!
-- Sonst Vorlage "Rollback Fall B/C/D" verwenden (sonst gehen diese Eingaben verloren).
USE master;
-- Voraussetzung: es existiert GENAU EIN Snapshot dieser DB (andere vorher loeschen)
SELECT name FROM sys.databases WHERE source_database_id = DB_ID(N'PflegeDB');

-- Optional, aber empfohlen: aktuellen (fehlerhaften) Stand als Nachweis fuer den Hersteller sichern
-- EXECUTE dbo.DatabaseBackup @Databases = 'PflegeDB', @Directory = N'\\backupserver\sql',
--     @BackupType = 'FULL', @CopyOnly = 'Y', @Description = 'fehlerhaft nach Update 12.3';

ALTER DATABASE PflegeDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;   -- trennt alle Verbindungen
RESTORE DATABASE PflegeDB FROM DATABASE_SNAPSHOT = N'PflegeDB_Snap_Update_12_3';
ALTER DATABASE PflegeDB SET MULTI_USER;

-- PFLICHT danach: das Zurueckdrehen baut das Protokoll neu auf -> Protokollkette unterbrochen.
EXECUTE dbo.DatabaseBackup @Databases = 'PflegeDB', @Directory = N'\\backupserver\sql',
        @BackupType = 'FULL', @Verify = 'Y', @CheckSum = 'Y', @Compress = 'Y', @LogToTable = 'Y';
-- Dann: App-Server-Pruefpunkt zuruecksetzen, Funktionstest, Snapshot loeschen, Ticket dokumentieren.
-- Grenzen: nicht moeglich bei mehreren Snapshots, offline/schreibgeschuetzten Dateigruppen.""",
    },
    {
        "id": "db-rollback-pointintime",
        "typ": "skript",
        "titel": "Rollback Fall B/C/D: Schlussprotokoll + Wiederherstellung bis zur Marke oder Uhrzeit",
        "sprache": "sql",
        "inhalt": r"""-- Kein Datenverlust nur mit: (1) Schlussprotokoll sichern, (2) fehlerhaften Stand aufheben.
USE master;

-- 1) Schlussprotokoll (Tail-Log): sichert die letzten Aenderungen und versetzt die DB in RESTORING.
--    Ab hier ist die Anwendung offline -> Pflege auf Papier-Notfalldokumentation.
BACKUP LOG PflegeDB TO DISK = N'\\backupserver\sql\PflegeDB_tail.trn'
    WITH NORECOVERY, CHECKSUM, INIT;
-- Server/Platte defekt? Dann WITH NO_TRUNCATE, CONTINUE_AFTER_ERROR statt NORECOVERY.

-- 2) Fehlerhaften Stand als zweite DB erhalten (Datenquelle fuer Nacherfassung + Nachweis):
--    vorher bzw. parallel eine COPY_ONLY-Sicherung ziehen oder Abschnitt 4 als PflegeDB_defekt nutzen.

-- 3) Benoetigte Sicherungen ermitteln (letzte Voll, letzte Diff, alle Logs danach)
SELECT b.type, b.backup_start_date, b.backup_finish_date, m.physical_device_name
FROM msdb.dbo.backupset b JOIN msdb.dbo.backupmediafamily m ON m.media_set_id = b.media_set_id
WHERE b.database_name = N'PflegeDB' AND b.backup_finish_date > DATEADD(DAY, -2, GETDATE())
ORDER BY b.backup_start_date;

-- 4) Wiederherstellen in genau dieser Reihenfolge, alles WITH NORECOVERY bis auf den letzten Schritt
RESTORE DATABASE PflegeDB FROM DISK = N'\\backupserver\sql\...\PflegeDB_FULL_....bak' WITH NORECOVERY, REPLACE;
RESTORE DATABASE PflegeDB FROM DISK = N'\\backupserver\sql\...\PflegeDB_DIFF_....bak' WITH NORECOVERY;
RESTORE LOG      PflegeDB FROM DISK = N'\\backupserver\sql\...\PflegeDB_LOG_1.trn'    WITH NORECOVERY;
-- ... weitere Logs ...
RESTORE LOG      PflegeDB FROM DISK = N'\\backupserver\sql\PflegeDB_tail.trn'
    WITH STOPBEFOREMARK = N'Update_12_3', RECOVERY;          -- Fall B: exakt vor dem Update
--  oder: WITH STOPAT = '2026-10-14T06:55:00', RECOVERY;      -- Fall C: auf eine Uhrzeit
--  oder: WITH RECOVERY;                                      -- Fall D: alles, Totalausfall

-- FALL C (Daten verfaelscht, Anwendung soll weiterlaufen): NICHT ueber PflegeDB, sondern parallel:
-- RESTORE DATABASE PflegeDB_Restore FROM DISK = N'...FULL.bak'
--   WITH MOVE N'PflegeDB' TO N'D:\Data\PflegeDB_Restore.mdf',
--        MOVE N'PflegeDB_log' TO N'L:\Log\PflegeDB_Restore.ldf', NORECOVERY;
-- RESTORE LOG PflegeDB_Restore FROM DISK = N'...' WITH STOPAT = '...', RECOVERY;
-- -> Tabellen vergleichen (EXCEPT) und nur betroffene Zeilen zurueckkopieren, in einer Transaktion.
-- Logische Dateinamen: RESTORE FILELISTONLY FROM DISK = N'...FULL.bak';

-- 5) Danach: neue Vollsicherung, Funktionstest, Nacherfassung aus PflegeDB_defekt, Ticket.""",
    },
    # ------------------------------------------------------- Ticket / Doku
    {
        "id": "db-ticket-change-update",
        "typ": "ticket",
        "titel": "Change: Update der Fachanwendung mit Datenbank-Rueckwegplan",
        "sprache": "",
        "inhalt": """CHANGE: Update <Anwendung> von Version <alt> auf <neu>, Termin <Datum, Uhrzeit>, Dauer <x> Std.
VERANTWORTLICH: <IT>   ENTSCHEIDER ROLLBACK: <Name, erreichbar unter ...>   FACHBEREICH: <Name>
HERSTELLER GEFRAGT: Downgrade-Skript vorhanden? Schema-Aenderung? Alte Version mit neuer DB lauffaehig?
ABBRUCHKRITERIEN (vorher festlegen):
  - Anmeldung > <10> Sek. oder Kernfunktion <X> geht nicht -> Rollback
  - Update-Skript bricht mit Fehler ab -> Rollback
  - Entscheidungsfrist: bis <Uhrzeit, Ende Beobachtungsphase>, danach nur noch vorwaerts korrigieren
VORHER:
  [ ] Messbasis erfasst (Robot-Test, Antwortzeiten, Query Store)
  [ ] Fachbereich + Pflege informiert, Papier-Notfalldokumentation liegt bereit
  [ ] Anwendung gestoppt, keine Sitzungen mehr
  [ ] Skript "Rollback vorbereiten": Log + COPY_ONLY-Vollsicherung, Snapshot, Marke <Name>
  [ ] Pruefpunkt App-Server <Name>
DURCHFUEHRUNG: [ ] Update  [ ] Funktionstest  [ ] Messwerte vs. Messbasis  [ ] Pilot-Freigabe
ROLLBACK (falls noetig): Fall A Snapshot / Fall B Marke / Fall C parallel -> Runbook "Ablauf im Ernstfall"
ABSCHLUSS:
  [ ] Beobachtungsphase ohne Befund -> Snapshot geloescht
  [ ] Tatsaechliche Ausfallzeit: <Min>   Datenverlust: <keiner/...>
  [ ] Bei Fehler: Fehlerbericht an Hersteller (Zeitpunkt, Ebene, Messwerte, Logauszug)""",
    },
    {
        "id": "db-doku-rollback-ernstfall",
        "typ": "doku",
        "titel": "Runbook: Datenbank-Rollback im Ernstfall (9 Schritte, ohne Datenverlust)",
        "sprache": "",
        "inhalt": """WIE SCHNELL? (haengt fast nur davon ab, WANN der Fehler bemerkt wird)
  Waehrend Update/Abnahmetest .......... 5-15 Min, kein Verlust (Snapshot)
  Beobachtungsphase (1-2 Std.) ......... 30-60 Min, kein Verlust, wenige Eingaben nacherfassen
  Stunden/Tage spaeter ................. vorwaerts korrigieren oder Reparatur aus Parallel-DB (1-3 Std.)
  Totalausfall Server .................. 30 Min - 2 Std., max. 15 Min Verlust (0 mit Schlussprotokoll)

1. Fehler gegen Abbruchkriterien pruefen, Entscheider laut Change-Ticket entscheidet: Rollback ja/nein.
2. Anwendung sperren (keine neuen Eingaben). Pflege informieren: Papier-Notfalldokumentation.
3. SCHLUSSPROTOKOLL sichern (Tail-Log) -- niemals ueberspringen, sonst gehen Aenderungen verloren.
4. Fehlerhafte DB als Kopie aufheben (PflegeDB_defekt): Quelle fuer Nacherfassung + Nachweis.
5. Rollback: Fall A Snapshot | Fall B bis Marke | Fall C parallel wiederherstellen | Fall D komplett.
6. App-Server zuruecksetzen (Pruefpunkt oder alte Programmversion).
7. Funktion pruefen: Robot-Test, Messwerte vs. Messbasis, Stichprobe durch Fachbereich.
8. Freigabe, Benutzer informieren, Nacherfassung organisieren, NEUE VOLLSICHERUNG starten.
9. Dokumentieren: Change-Ticket, Fehlerbericht an Hersteller, gemessene Ausfallzeit.

VORAUSSETZUNGEN (sonst gelten die Zeiten oben nicht):
  - Wiederherstellungsmodell FULL, Log-Sicherung alle 15 Min (Ola-Jobs mit Zeitplan)
  - EIN Verantwortlicher fuer Log-Sicherungen (Ola ODER Veeam, nicht beides)
  - Monatlicher Wiederherstellungstest bestanden (Skript "Wiederherstellungstest")
  - Hochverfuegbarkeit (Always On/Replikation) ist KEIN Rollback: Fehler wird sofort mitkopiert.""",
    },
    {
        "id": "db-doku-wartungsplan",
        "typ": "doku",
        "titel": "Wartungsplan SQL Server: was laeuft wann und warum (Ola Hallengren)",
        "sprache": "",
        "inhalt": """JOB                                   WANN               WARUM
DatabaseBackup USER FULL              taegl. 01:00       Startpunkt jeder Wiederherstellung
DatabaseBackup USER DIFF              alle 6 Std.        weniger Logs beim Zurueckspielen
DatabaseBackup USER LOG               alle 15 Min        max. Datenverlust = 15 Min (RPO)
DatabaseBackup SYSTEM FULL            taegl. 00:30       master/msdb: Logins, Jobs, Sicherungshistorie
DatabaseIntegrityCheck USER/SYSTEM    So 02:00 / 01:30   Beschaedigung finden, bevor Sicherungen sie weitertragen
IndexOptimize USER                    Sa 03:00           Fragmentierung + Statistiken -> Abfragen bleiben schnell
Cleanup-Jobs                          So 05:00-05:15     Historie/CommandLog/Ausgabedateien klein halten

TAEGLICH:   Skript "Morgen-Kontrolle" (Sicherungen, CHECKDB, CommandLog-Fehler, suspect_pages)
MONATLICH:  Skript "Wiederherstellungstest" -> Bericht = Nachweis + echtes RTO
JAEHRLICH:  Ola-Skript aktualisieren (Downloads-Seite), Testumgebung zuerst; Aufbewahrung pruefen

WARUM OLA HALLENGREN statt Wartungsplan-Assistent?
  - Seit vielen Jahren Standard, MIT-Lizenz, kostenlos, auf allen Editionen ab SQL 2008
  - Index nur bei Bedarf (Fragmentierung), Statistiken nur wenn geaendert -> kuerzere Fenster
  - Jeder Schritt in master.dbo.CommandLog -> nachvollziehbar und ueberwachbar
  - Saubere Ordnerstruktur Server\\DB\\Typ, automatische Bereinigung erst nach erfolgreicher Sicherung""",
    },
)
