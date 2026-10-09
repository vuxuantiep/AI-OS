# Themen (Topics) für den Agenten

Grundsatz: Normale Fragen beantwortet der Agent **generativ aus den Hilfeartikeln**. Feste
Themen braucht es nur dort, wo die Antwort exakt und verlässlich sein muss (Kontaktdaten,
Notfall, Ticketaufnahme).

---

## 1. Begrüßung (System-Thema „Unterhaltung starten“ anpassen)
Nachricht:
> Hallo! Ich bin die IT-Hilfe von EMVIA. Ich helfe bei Anmeldung, Kennwort, Authenticator-App,
> Outlook, Teams und Dienstgeräten. Wobei kann ich helfen?

Schnellantworten (Buttons): „Kennwort vergessen“ · „Neues Handy“ · „Authenticator einrichten“ ·
„IT kontaktieren“

---

## 2. Notfall: Gerät verloren / Hackerverdacht
**Auslösesätze:** Handy verloren · Tablet gestohlen · Diensthandy weg · gehackt · komische
Mail mit Link geklickt · Kennwort an Fremde gegeben · unbekannte Anmeldeanfrage · Konto
missbraucht

**Ablauf:**
1. Nachricht: „Das ist dringend. Bitte melden Sie es sofort der IT. Je schneller wir handeln,
   desto besser können wir Ihr Konto und die Daten schützen.“
2. Kontakt anzeigen (feste Werte, kein generierter Text):
   - Während der Dienstzeit: {Telefon IT}, {Zeiten}
   - Außerhalb: {Notfallnummer / Bereitschaft} bzw. Pflegedienstleitung informieren
3. Bei Link geklickt / Kennwort weitergegeben: „Ändern Sie Ihr Kennwort jetzt sofort:
   https://aka.ms/sspr“
4. Ticket-Thema (5) anbieten.

---

## 3. Kennwort vergessen
**Auslösesätze:** Kennwort vergessen · Passwort vergessen · kann mich nicht anmelden ·
Konto gesperrt · Passwort abgelaufen

**Ablauf:** Generative Antwort aus Artikel „Kennwort vergessen“ ist ausreichend. Nur wenn
SSPR bei EMVIA NICHT aktiv ist, als festes Thema: „Bitte rufen Sie die IT an: {Telefon IT}.
Wir setzen das Kennwort nach einer kurzen Identitätsprüfung zurück.“

---

## 4. Mit einem Menschen sprechen
**Auslösesätze:** Mitarbeiter sprechen · echte Person · Anruf · Rückruf · Hilfe von der IT

**Ablauf:** Kontaktdaten (wie in 2.) + Ticket-Thema anbieten.

---

## 5. IT kontaktieren / Ticket (auch Ziel des System-Themas „Eskalieren“)
**Fragen (Variablen):**
1. „Wie heißen Sie?“ → Name (Text). Alternativ automatisch aus `System.User.DisplayName`.
2. „In welcher Einrichtung/Station arbeiten Sie?“ → Einrichtung (Auswahl: {Liste der Häuser})
3. „Um welches Gerät geht es?“ → Gerät (Auswahl: PC · Diensthandy · Tablet · Privathandy · weiß nicht)
4. „Beschreiben Sie kurz das Problem.“ → Beschreibung (Text)
5. „Wie erreichen wir Sie am besten?“ → Rückruf (Text)

**Aktion v1:** Zusammenfassung anzeigen + Text „Bitte senden Sie diese Angaben an
{Ticket-Mailadresse} oder rufen Sie an: {Telefon IT}.“
**Aktion v2 (Ausbau):** Power-Automate-Flow „Ticket anlegen“ (Mail an Ticketsystem mit den
Variablen) → Bestätigung „Ticket ist angelegt“.

---

## 6. Außerhalb des Themas (System-Thema „Fallback“ anpassen)
> Dabei kann ich leider nicht helfen, ich bin nur für IT-Fragen zuständig. Für Dienstplan,
> Urlaub oder Personalfragen wenden Sie sich bitte an Ihre Leitung bzw. die Personalabteilung.
