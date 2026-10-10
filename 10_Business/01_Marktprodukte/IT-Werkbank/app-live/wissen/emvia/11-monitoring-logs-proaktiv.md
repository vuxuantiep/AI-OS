# FAQ EMVIA: Monitoring, Logs lesen und proaktiv arbeiten

Proaktiv heißt: Die IT weiß von einem Problem, bevor der erste Anruf kommt. Dafür braucht es drei Dinge: Logs an einem Ort, feste Abfragen und Alarme, die in einem Kanal landen, den jemand liest.

## Welche Logs gibt es in M365 und wo finde ich sie?
- **Entra-Anmeldeprotokolle:** jede Anmeldung mit Fehlercode, App, IP, Gerät und CA-Ergebnis (Entra > Überwachung > Anmeldeprotokolle)
- **Entra-Überwachungsprotokolle (Audit):** Änderungen an Benutzern, Gruppen, Rollen, Apps
- **Intune:** Gerätekonformität, Konfigurationsstatus, App-Installationen, Endpoint Analytics (Startzeit, App-Abstürze)
- **Exchange:** Nachrichtenablaufverfolgung (`Get-MessageTraceV2`), Quarantäne
- **Defender XDR:** Vorfälle und Warnungen (Phishing, Schadsoftware, riskante Anmeldungen)
- **Purview Audit:** „Wer hat was wann getan“ über alle Dienste (Datei gelöscht, Postfachzugriff, Freigabe)
- **Global Secure Access:** Traffic-Logs für den Zugang ins interne Netz
- **Windows-Ereignisprotokolle:** über den Azure Monitor Agent (AMA) und eine Datensammlungsregel
- **M365-Dienstintegrität:** Störungen bei Microsoft selbst

## Warum reichen die Admin-Center nicht?
Entra hält Anmeldeprotokolle nur **30 Tage** (mit P1/P2, ohne Lizenz 7 Tage). Jedes Portal zeigt nur seinen eigenen Teil, und Alarme auf beliebige Muster gibt es dort kaum. Lösung: In Entra unter **Überwachung > Diagnoseeinstellungen** die Tabellen `SigninLogs`, `AuditLogs` (und bei Bedarf `NonInteractiveUserSignInLogs`) an einen **Log Analytics Workspace** senden. Intune hat dieselbe Option (Mandantenverwaltung > Diagnoseeinstellungen). Kosten entstehen je GB, also nur senden, was gebraucht wird. Nicht-interaktive Anmeldungen sind das größte Volumen.

## Wie lese ich ein Log effizient?
1. **Zeitraum eingrenzen:** Wann genau trat es auf? Ohne Zeitpunkt ist jedes Log ein Heuhaufen.
2. **Nach dem Benutzer bzw. Gerät filtern**, dann nach **Status = Fehler**
3. **Fehlercode lesen und nachschlagen** (Wiki „Ticket-Schnellhilfe“ oder https://login.microsoftonline.com/error?code=<Code>)
4. **Muster suchen:** Gleicher Fehler bei vielen Nutzern? Dann ist es eine Störung oder Richtlinie, kein Einzelfall. Gleiche IP? Dann ein Gerät mit altem Kennwort oder ein Angriff.
5. **Korrelation:** Was hat sich kurz vorher geändert (Audit-Log, neue CA-Regel, Intune-Richtlinie, Microsoft-Störung)?

## Welche KQL-Abfragen brauche ich am häufigsten?
Gesperrte Konten in der letzten Stunde (Alarmkandidat):
```kql
SigninLogs
| where TimeGenerated > ago(1h)
| where ResultType == "50053"
| summarize Versuche = count(), IPs = make_set(IPAddress), Apps = make_set(AppDisplayName) by UserPrincipalName
| where Versuche >= 3
```
Welche Conditional-Access-Regel blockiert wen:
```kql
SigninLogs
| where TimeGenerated > ago(24h)
| where ResultType == "53003"
| mv-expand CA = ConditionalAccessPolicies
| where tostring(CA.result) == "failure"
| summarize Anzahl = count() by UserPrincipalName, Regel = tostring(CA.displayName), AppDisplayName
| order by Anzahl desc
```
MFA abgelehnt bzw. nicht bestanden (Hinweis auf MFA-Müdigkeit oder Handyproblem):
```kql
SigninLogs
| where TimeGenerated > ago(24h)
| where ResultType == "500121"
| summarize Anzahl = count() by UserPrincipalName, bin(TimeGenerated, 1h)
| where Anzahl >= 3
```
Erfolgreiche Anmeldungen außerhalb Deutschlands:
```kql
SigninLogs
| where TimeGenerated > ago(24h)
| where ResultType == "0"
| extend Land = tostring(LocationDetails.countryOrRegion)
| where Land != "DE" and isnotempty(Land)
| project TimeGenerated, UserPrincipalName, Land, IPAddress, AppDisplayName
```
Weitere Abfragen (Intune, Fehler-Top-10) stehen als Vorlagen in der Werkbank.

## Welche Alarme lohnen sich für EMVIA?
- Konto gesperrt ≥ 3× in 1 Stunde
- Mehrere MFA-Ablehnungen bei einem Nutzer (Angreifer kennt das Kennwort!)
- Erfolgreiche Anmeldung aus dem Ausland
- Neue Admin-Rollenzuweisung (AuditLogs, „Add member to role“)
- Gerät länger als 7 Tage nicht konform oder nicht synchronisiert
- App-Secret oder Zertifikat läuft in 30 Tagen ab (Werkbank-Skript, wöchentlich)
- Weniger als 5 freie Lizenzen einer Sorte (vor dem nächsten Eintritt!)
- Neue Weiterleitung nach extern (Defender-Warnungsrichtlinie, Werkbank-Skript)
- Microsoft-Störung bei Exchange/Teams: Dienstintegrität, Benachrichtigung per Mail im Admin Center einschalten
Alarm = **Azure Monitor Alarmregel** auf die KQL-Abfrage, Aktionsgruppe = Mail bzw. Teams-Kanal „IT-Alarm“ (über Power Automate oder Webhook). Wenige gute Alarme sind besser als viele, die niemand mehr liest.

## Wie sieht eine proaktive Routine aus?
- **Täglich (10 Minuten, morgens):** Werkbank-Skript „Morgen-Check“: Microsoft-Störungen, nicht konforme Geräte, gesperrte Konten, freie Lizenzen. Dazu Defender-Vorfälle und die Quarantäne kurz ansehen.
- **Wöchentlich:** Nachrichtencenter lesen, Bericht MFA-Lücken und inaktive Konten, Intune-Updatestatus, Secure Score ansehen (security.microsoft.com > Secure Score, eine Empfehlung pro Woche umsetzen)
- **Monatlich:** Admin-Rollen, Gastkonten, ablaufende Secrets und Zertifikate, Entra-Empfehlungen (Entra > Übersicht > Empfehlungen), Lizenzkosten, Backup- bzw. Aufbewahrungsrichtlinien
- **Quartalsweise:** Access Reviews (wer hat noch Zugriff auf was), Notfallkonten testen, CA-Richtlinien im Bericht „Nur-Bericht“ gegenprüfen

## Welche Dashboards gibt es fertig?
- Entra > Überwachung > Arbeitsmappen: „Anmeldungen“, „Erkenntnisse zum bedingten Zugriff“, „Authentifizierungsmethoden“ (brauchen Log Analytics)
- Intune > Berichte: Gerätekonformität, Windows-Updates, Endpoint Analytics bzw. Advanced Analytics (seit 07/2026 in E3/E5)
- Defender: Secure Score und Vorfallübersicht
- M365 Admin Center > Berichte > Nutzung: auch der EWS-Nutzungsbericht und die Copilot-Nutzung

## Was ist datenschutzrechtlich zu beachten?
Logs enthalten personenbezogene Daten (Anmeldezeiten, IP, Ort). Bei EMVIA (Pflegeeinrichtung) daher: Zweck festlegen (IT-Sicherheit und Betrieb, keine Leistungs- oder Verhaltenskontrolle), Aufbewahrung begrenzen (z. B. 90 Tage), Zugriff nur für die IT. Vor dem Einrichten mit Datenschutz und ggf. Betriebsrat abstimmen. Keine Log-Exporte mit Namen in private Tools oder Cloud-KI kopieren.
