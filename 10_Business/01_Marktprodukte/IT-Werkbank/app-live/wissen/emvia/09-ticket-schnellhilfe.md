# FAQ EMVIA: Ticket-Schnellhilfe (Kennwort, Konto, Berechtigung, VPN)

Grundregel für jedes Ticket: **erst ins Log schauen, dann handeln.** Das Anmeldeprotokoll in Entra zeigt in 90 % der Fälle direkt die Ursache: Fehlercode, App, Gerät, Ort und welche Conditional-Access-Regel gegriffen hat. Schneller geht es mit dem Werkbank-Skript „Benutzer-Schnelldiagnose“: eine UPN eingeben und alles auf einen Blick sehen.

## Welche Anmelde-Fehlercodes muss ich kennen?
- 50126: falsches Kennwort oder falscher Benutzername
- 50053: Konto gesperrt (Smart Lockout nach zu vielen Fehlversuchen) oder Anmeldung von einer bösartigen IP
- 50057: Konto ist deaktiviert
- 50055: Kennwort abgelaufen
- 50034: Benutzer existiert nicht (Tippfehler im UPN, falsche Domain)
- 50074 / 50076: MFA erforderlich. Das ist normal, solange der Nutzer danach erfolgreich ist.
- 500121: MFA nicht bestanden (abgelehnt, Zeitüberschreitung, kein Netz am Handy)
- 53003: durch Conditional Access blockiert. Im Protokoll auf den Reiter „Bedingter Zugriff“ klicken, dort steht die Regel.
- 53000: Gerät erfüllt die Anforderung nicht (nicht konform oder nicht verwaltet), siehe Intune > Gerät > Konformität
- 50133 / 50173: Sitzung ungültig nach Kennwortänderung. Neu anmelden, ggf. Outlook-Profil bzw. gespeicherte Anmeldeinformationen löschen.

## Kennwort vergessen: was ist der schnellste Weg?
1. Der Nutzer setzt es selbst zurück: https://aka.ms/sspr (E-Mail-Vorlage „Kennwort vergessen“). Das spart das häufigste Ticket komplett.
2. Hat der Nutzer keine Methode registriert oder ein neues Handy: Identität prüfen (Rückruf über bekannte Nummer oder Bestätigung durch die Leitung). Dann einen **befristeten Zugriffspass (TAP)** ausstellen, 60 Minuten, einmalig nutzbar. Damit meldet sich der Nutzer an und registriert Authenticator oder Passkey selbst neu.
3. Kennwort nur dann selbst setzen, wenn es nicht anders geht, immer mit „bei nächster Anmeldung ändern“. Übergabe nie per Mail oder Chat an unbestätigte Absender.
4. **Hybrid-Konto (aus dem AD synchronisiert):** Kennwort im AD zurücksetzen bzw. SSPR mit Kennwortrückschreiben. Eine Änderung in Entra greift bei Sync-Konten nicht.

## Konto gesperrt: wie entsperre ich?
- **Entra Smart Lockout** löst sich nach Ablauf der Sperrzeit von selbst (ab 1 Minute, steigt bei weiteren Fehlversuchen). Mit SSPR kann der Nutzer sofort entsperren. Ein manuelles „Entsperren“ in Entra gibt es nicht.
- **Lokales AD (Hybrid):** `Unlock-ADAccount -Identity <sam>`, Ursache mit `Get-ADUser <sam> -Properties LockedOut,BadLogonCount,LastBadPasswordAttempt` prüfen.
- Sperrt sich ein Konto immer wieder: Irgendwo ist ein altes Kennwort gespeichert. Typisch sind ein Handy-Mailprofil, ein gemeinsam genutzter PC, eine Windows-Anmeldeinformation oder ein Netzlaufwerk. Im Anmeldeprotokoll stehen Client-App und IP der Fehlversuche, damit findet man das Gerät.
- Kommen die Fehlversuche aus dem Ausland oder von fremden IPs, ist das ein Angriffsversuch: nicht entsperren, sondern Kennwort ändern, Sitzungen widerrufen und MFA-Methoden prüfen.

## Konto kompromittiert: was mache ich sofort?
1. Konto sperren (`Update-MgUser -UserId <upn> -AccountEnabled:$false`) und Sitzungen widerrufen (`Revoke-MgUserSignInSession -UserId <upn>`)
2. Kennwort zurücksetzen. Unbekannte MFA-Methoden löschen.
3. Posteingangsregeln und Weiterleitungen prüfen (Werkbank-Skript „Weiterleitungen und Posteingangsregeln nach extern“)
4. Purview > Audit: Was hat das Konto in den letzten Tagen getan?
5. Vorfall dokumentieren. Datenschutz informieren, wenn Bewohner- oder Personaldaten betroffen sein könnten (Meldefrist 72 Stunden).

## Kein Zugriff auf Ordner, Team, Postfach oder App: wie gehe ich vor?
Immer zuerst fragen: **Woher soll der Zugriff kommen?**
1. **Über eine Gruppe?** Ist der Nutzer Mitglied? (`Get-MgUserMemberOf`). Bei dynamischen Gruppen: Stimmt das Attribut, z. B. Abteilung oder Standort? Mitgliedschaften wirken mit Verzögerung: Teams und SharePoint bis zu einigen Stunden, Postfach-AutoMapping bis zu 60 Minuten.
2. **Direkt berechtigt?** Postfach: `Get-MailboxPermission`, Senden als: `Get-RecipientPermission`. SharePoint: Website > Einstellungen > Websiteberechtigungen bzw. „Zugriff prüfen“.
3. **Geerbt oder gebrochen?** In SharePoint haben Ordner mit eigener Berechtigung die Vererbung unterbrochen. Dann hilft die Mitgliedschaft in der Website-Gruppe nicht.
4. **Gesperrt durch Richtlinie?** Fehlercode 53003 oder 53000 im Anmeldeprotokoll heißt: Conditional Access oder Gerätezustand, keine fehlende Berechtigung.
Lösung möglichst über die **Gruppe** statt direkt. Wiederkehrende Kombinationen (z. B. „neue Pflegekraft Haus A“) als Zugriffspaket in My Access anlegen, dann beantragt die Leitung den Zugriff selbst.
Das Werkbank-Skript „Berechtigungs-Check“ listet für einen Benutzer alle Gruppen, Postfach-Vollzugriffe und Senden-als-Rechte.

## Berechtigung entziehen: worauf achten?
- Gruppenmitgliedschaft entfernen. Direkte Rechte entfernen nicht vergessen, die sind der häufigste Rest.
- Bei Austritt reicht das Sperren nicht. Laufende Sitzungen erst widerrufen, sonst bleibt der Zugriff bis zu einer Stunde bestehen (Token-Laufzeit).
- Freigabelinks in OneDrive/SharePoint („Jeder mit dem Link“) gelten weiter. In SharePoint Admin > Berichte zur Datenzugriffsgovernance prüfen.

## VPN bzw. Zugang ins interne Netz geht nicht: wie gehe ich vor?
Zuerst klären, welche Technik EMVIA nutzt (Steckbrief): klassisches VPN (z. B. Firewall-VPN mit Zertifikat) oder **Entra Private Access** über den Global-Secure-Access-Client (GSA).

**Bei Entra Private Access / GSA-Client:**
1. Taskleiste > GSA-Symbol: Ist der Client verbunden? Unter „Erweiterte Diagnose“ den Zustand prüfen und bei Bedarf Protokolle exportieren.
2. Entra-Anmeldeprotokoll: Ist die Anmeldung an der App „Global Secure Access“ bzw. an der Private-Access-App erfolgreich? Bei 53003 blockiert eine CA-Regel, bei 53000 ist das Gerät nicht konform.
3. Entra > Global Secure Access > Connectors: Ist der Private Network Connector im EMVIA-Netz aktiv (grün)?
4. Ist das Ziel (IP/FQDN und Port) im App-Segment bzw. in Quick Access eingetragen? Funktioniert die DNS-Auflösung für interne Namen (private DNS)?
5. Global Secure Access > Traffic-Logs: Kommt der Verkehr an, und wird er erlaubt oder blockiert?

**Bei klassischem VPN:**
1. Hat der Nutzer Internet? Funktioniert der VPN-Client lokal (Fehlermeldung als Screenshot)?
2. Ist das VPN-Profil bzw. Zertifikat per Intune verteilt? Intune > Gerät > Gerätekonfiguration: Status des VPN-Profils. Abgelaufene Zertifikate sind ein Klassiker.
3. Konto gesperrt oder Kennwort abgelaufen? Bei RADIUS/NPS mit MFA-Erweiterung: Entra-Anmeldeprotokoll und NPS-Ereignisprotokoll prüfen.
4. Logs am VPN-Gateway bzw. an der Firewall: Wird der Nutzer abgewiesen (Authentifizierung) oder klappt der Tunnel, aber nicht das Ziel (Routing, DNS)?

## Was gehört in jede Ticket-Lösung?
Ursache (mit Fehlercode), was getan wurde, wie es geprüft wurde, und ob es wiederkommen kann. Kommt ein Ticket öfter als dreimal im Monat, gehört es in Self-Service, eine Automatisierung oder einen Wiki-Artikel für den Helpdesk-Agenten.
