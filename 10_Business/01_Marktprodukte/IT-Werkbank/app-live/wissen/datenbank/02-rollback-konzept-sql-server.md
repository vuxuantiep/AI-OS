# FAQ Datenbank: Rollback-Konzept bei fehlerhaftem Update (SQL Server)

Passende Vorlagen im Modul Datenbank: „Rollback vorbereiten VOR einem Update“, „Rollback Fall A: Snapshot“, „Rollback Fall B/C/D: Schlussprotokoll + Wiederherstellung“, Ticket „Change: Update mit Datenbank-Rückwegplan“, Runbook „Datenbank-Rollback im Ernstfall“.

## Was ist beim Rollback das eigentliche Problem?
Technisch lässt sich fast jedes Update zurückdrehen. Das Problem sind die **Daten, die nach dem Update eingetragen wurden**, z. B. Pflegedokumentation oder Medikation. Ein blindes Zurückspielen der Sicherung löscht genau diese Eingaben. Zwei Kennzahlen:
- **RPO** (Recovery Point Objective): Wie viele Daten dürfen höchstens verloren gehen? Ziel: 0 beim geplanten Rollback, höchstens 15 Minuten bei einem Totalausfall.
- **RTO** (Recovery Time Objective): Wie lange darf die Anwendung stehen? Ziel: unter 15 Minuten direkt nach dem Update, unter 2 Stunden im schlimmsten Fall.

## Wie schnell können wir handeln, ohne Daten zu verlieren?
Das hängt fast nur davon ab, **wann der Fehler bemerkt wird**:
- Während Update oder Abnahmetest: 5–15 Minuten über den Datenbank-Snapshot, kein Verlust.
- In der Beobachtungsphase (1–2 Stunden): 30–60 Minuten, kein Verlust, wenige Eingaben werden nacherfasst.
- Stunden oder Tage später: vorwärts korrigieren (Hotfix) oder Parallel-Wiederherstellung und gezielte Reparatur, 1–3 Stunden, Anwendung läuft weiter.
- Totalausfall des Servers: 30 Minuten bis 2 Stunden, höchstens 15 Minuten Verlust, mit Schlussprotokoll 0.
Faustregel Dauer: Wiederherstellung schafft grob 100–300 MB/s, eine 50-GB-Datenbank ist in etwa 5–10 Minuten zurückgespielt, plus Protokolle. Die echte Zahl liefert nur der monatliche Wiederherstellungstest.

## Was bereite ich vor jedem Update vor?
1. Abbruchkriterien und Entscheider festlegen (im Change-Ticket).
2. Messbasis erfassen (Robot-Test, Antwortzeiten, Query Store).
3. Anwendung stoppen, damit niemand mehr schreibt.
4. Letzte Protokollsicherung und eine **COPY_ONLY**-Vollsicherung („vor Update 12.3“). COPY_ONLY stört die normale Sicherungskette nicht.
5. **Datenbank-Snapshot** anlegen: ein eingefrorener Stand auf demselben Server, Zurückdrehen in Sekunden bis Minuten. Seit SQL Server 2016 SP1 in allen Editionen, auch Standard und Express.
6. **Markierte Transaktion** setzen (`BEGIN TRAN Name WITH MARK`): ein benannter Punkt im Protokoll, auf den `STOPBEFOREMARK` exakt zurückspringt.
7. Prüfpunkt des **App-Servers**. Für den DB-Server **keinen** VM-Prüfpunkt als Rollback nutzen, er setzt auch korrekte Daten zurück.
8. Beim Hersteller fragen: Gibt es ein Downgrade-Skript? Ändert das Update das Schema?

## Welche Rollback-Fälle gibt es?
- **Fall A – noch keine Benutzerdaten:** Snapshot zurückdrehen (`RESTORE DATABASE ... FROM DATABASE_SNAPSHOT`), danach sofort eine neue Vollsicherung, denn das Zurückdrehen unterbricht die Protokollkette.
- **Fall B – Benutzer haben schon gearbeitet:** bevorzugt vorwärts korrigieren. Sonst Schlussprotokoll sichern, fehlerhafte DB als Kopie behalten, bis zur Marke wiederherstellen, neue Eingaben aus der Kopie übertragen oder nacherfassen.
- **Fall C – Daten verfälscht, spät bemerkt:** auf den Zeitpunkt vor dem Update als **zweite Datenbank** wiederherstellen, vergleichen und nur betroffene Zeilen zurückkopieren. Die Anwendung läuft weiter.
- **Fall D – Totalausfall:** Schlussprotokoll falls möglich, dann Voll + Diff + Protokolle auf einen Ersatzserver oder Veeam Instant Recovery.

## Welcher Schritt verhindert Datenverlust?
Das **Schlussprotokoll (Tail-Log-Backup)**: `BACKUP LOG ... WITH NORECOVERY` sichert die letzten Änderungen, bevor zurückgespielt wird. Und: die fehlerhafte Datenbank **nie überschreiben, ohne eine Kopie aufzuheben**. Sie ist Datenquelle für die Nacherfassung und Nachweis für den Hersteller.

## Was muss ich über den Snapshot wissen?
Er ersetzt **keine** Sicherung, denn er liegt auf demselben Server und ist bei einem Plattendefekt mit weg. Er wächst mit jeder Änderung und bremst Schreibzugriffe leicht, deshalb nach der Beobachtungsphase löschen. Zurückdrehen geht nur, wenn genau ein Snapshot der Datenbank existiert.

## Ist Always On oder Replikation nicht schon ein Rollback?
Nein. Hochverfügbarkeit überträgt ein fehlerhaftes Update in Sekunden auf alle Kopien. Sie schützt vor Serverausfall, nicht vor fehlerhaften Änderungen.

## Was mache ich mit der Pflege während des Rollbacks?
Vorher ankündigen, dass für die Dauer die **Papier-Notfalldokumentation** gilt, und die Nacherfassung danach organisieren. Das gehört ins Change-Ticket, nicht erst in den Ernstfall.
