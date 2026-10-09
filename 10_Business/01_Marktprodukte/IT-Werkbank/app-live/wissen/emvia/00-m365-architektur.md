# M365-Architektur: wie die Dienste zusammenhängen

![Microsoft 365 – Architektur und Zusammenhänge](m365-architektur.svg)

## Wie ist Microsoft 365 aufgebaut?
Es gibt fünf Schichten:
1. Identität: Entra ID
2. Geräte: Intune
3. Dienste: Exchange, SharePoint, OneDrive, Teams
4. Sicherheit und Compliance: Defender, Purview
5. Verwaltung: Admin-Center, Microsoft Graph, PowerShell

Entra ID ist das Tor: Jeder Zugriff auf einen Dienst braucht vorher eine erfolgreiche Anmeldung und ein Token von Entra.

## Wie läuft ein Zugriff ab?
1. Der Benutzer meldet sich mit Kennwort und MFA bei Entra ID an.
2. Conditional Access prüft Benutzer, Gerät, Ort und Risiko. Den Gerätezustand (konform ja/nein) liefert Intune.
3. Passt alles, stellt Entra ein Token aus, und Outlook, Teams oder SharePoint öffnen sich.
Wenn etwas nicht geht, zuerst in Entra > Anmeldeprotokolle schauen: Fehlercode und welche Conditional-Access-Regel gegriffen hat.

## Welche Rolle spielt das lokale Active Directory?
Nur bei Hybrid-Identität: Entra Connect bzw. Cloud Sync synchronisiert Benutzer und Gruppen aus dem AD nach Entra. Dann ist das AD die führende Quelle. Änderungen an synchronisierten Konten (Name, Sperre, Gruppen) also im AD machen, nicht in Entra.

## Warum hängt Teams von Exchange und SharePoint ab?
Teams speichert nichts eigenständig:
- Kanal-Dateien liegen in der SharePoint-Website des Teams.
- Dateien aus Einzel- und Gruppenchats liegen im OneDrive des Absenders.
- Kalender und Besprechungen liegen in Exchange.
Probleme mit Dateien in Teams sind deshalb oft SharePoint-Berechtigungen, Kalenderprobleme oft Exchange.

## Was ist eine Microsoft-365-Gruppe?
Eine einzige Mitgliederliste, die gleichzeitig das Team, die SharePoint-Website und das Gruppenpostfach mit Kalender steuert. Wer in der Gruppe ist, hat überall Zugriff. Eine gelöschte Gruppe lässt sich 30 Tage wiederherstellen, inklusive Team und Website.

## Was macht die Lizenz?
Die Lizenz ist der Schalter: Ohne passende Lizenz gibt es kein Postfach, kein Teams und keine Intune-Verwaltung. Voraussetzung ist der Nutzungsstandort (UsageLocation = DE). Lizenzen am besten über Gruppen vergeben.

## Wo liegen Sicherheit und Compliance?
Quer über allen Diensten:
- Defender: Mail- und Phishing-Schutz, Quarantäne, Schutz der Geräte, Vorfälle
- Purview: Aufbewahrung und Löschfristen, DLP gegen Datenabfluss, Audit-Protokoll, eDiscovery
