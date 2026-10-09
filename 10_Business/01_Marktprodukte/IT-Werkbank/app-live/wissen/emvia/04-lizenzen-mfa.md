# FAQ EMVIA: Lizenzen, MFA und Conditional Access

## Wie sehe ich, wie viele Lizenzen frei sind?
M365 Admin Center > Abrechnung > Ihre Produkte bzw. Vorlage "Lizenzbericht". Der Bericht zeigt auch gesperrte Konten, die noch eine Lizenz belegen. Das ist das häufigste Einsparpotenzial.

## Gruppenbasierte oder direkte Lizenzvergabe?
Gruppenbasiert ist übersichtlicher: Wer in der Gruppe ist, bekommt die Lizenz, und beim Entfernen fällt sie weg. Das setzt Entra ID P1 voraus (z. B. in Microsoft 365 Business Premium, E3 oder E5 enthalten). Fehler sieht man unter Entra > Gruppen > <Gruppe> > Lizenzen. Direkt zugewiesene Lizenzen muss man beim Austritt einzeln entziehen.

## Wer hat noch keine MFA eingerichtet?
Vorlage "MFA-/Anmeldemethoden-Bericht" oder Entra > Schutz > Authentifizierungsmethoden > Benutzerregistrierungsdetails. Administratoren ohne MFA sofort klären.

## Sicherheitsstandards oder Conditional Access?
Sicherheitsstandards (Security Defaults) sind der einfache Grundschutz. Conditional Access (braucht Entra ID P1) ist feiner steuerbar. Beides gleichzeitig geht nicht: Für Conditional Access müssen die Sicherheitsstandards aus sein.

## Wie ändere ich Conditional Access gefahrlos?
Neue Richtlinien immer zuerst im Modus "Nur Bericht" (Report-only) laufen lassen und die Anmeldeprotokolle auswerten. Break-Glass-Konten von allen Richtlinien ausnehmen. Niemals eine Richtlinie aktivieren, die alle Admins aussperren könnte. Bestehende Richtlinien zuerst dokumentieren (Vorlage im Modul Entra ID).

## Mitarbeiter hat ein neues Smartphone oder die Authenticator-App verloren?
Identität prüfen (Rückruf über bekannte Nummer oder Vorgesetzte, nie nur per Mail). Dann Entra > Benutzer > Authentifizierungsmethoden: alte Methode löschen bzw. "Erneute MFA-Registrierung anfordern". Alternativ einen befristeten Zugriffspass ausstellen. Keine dauerhaften Ausnahmen.

## Was tun bei unerwarteten MFA-Anfragen ("MFA-Bombing")?
Der Benutzer soll ablehnen und melden. Das Kennwort ist dann wahrscheinlich bekannt: Kennwort zurücksetzen, Sitzungen widerrufen, Anmeldeprotokolle prüfen (Ort/IP) und den Vorfall dokumentieren. Number Matching im Authenticator ist bei Microsoft inzwischen Standard.
