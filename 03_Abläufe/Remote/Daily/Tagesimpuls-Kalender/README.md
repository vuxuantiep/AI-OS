# 🌱 Tagesimpuls & Kalender-Wecker (Raspberry Pi 4)

Jeden Morgen um 07:00 eine Push-Nachricht auf Deutsch und Vietnamesisch, die EQ, positive
Wortwahl und Kommunikation trainiert. Dazu ein Wecker mit Ton für die Termine aus dem Google
Kalender und am 01.06./01.12. eine Finanz- und Steuer-Erinnerung mit Links zu WISO, ELSTER und
zum Finanzplan.

Architektur und Entscheidungen: [Plannung/Architektur.md](Plannung/Architektur.md)

## Was jeden Morgen kommt

| Teil | Wozu |
|---|---|
| 📅 Termine heute | Überblick aus dem Google Kalender |
| 💬 Sprichwort DE + VI mit Sinn | Haltung, Werte |
| 🔁 Wortwahl des Tages („statt … besser …“, DE + VI) | Positive Formulierungen einüben |
| ❤️ EQ-Übung | Eine kleine, konkrete Übung für den Tag |
| ✨ Affirmation | Positive Grundhaltung |
| 😄 Witz | Gute Laune |

Inhalte stehen in `daten/inhalte.json`. Neue Einträge einfach anhängen. Innerhalb einer Runde
wiederholt sich kein Eintrag.

## Projektstruktur

```
Tagesimpuls-Kalender/
├── README.md                    diese Anleitung
├── Plannung/Architektur.md      Mermaid-Gesamtdiagramm + Entscheidungen
├── .env.example                 Vorlage für Einstellungen (.env selbst ist NICHT im Git)
├── requirements.txt             Google-API-Bibliotheken
├── install_pi.sh                Installation auf dem Pi (venv + systemd)
├── daten/inhalte.json           Sprichwörter, Wortwahl, EQ, Affirmationen, Witze (DE/VI)
├── tagesimpuls/
│   ├── __main__.py              CLI: impuls | wecker | finanz | finanztermine-anlegen | ics | vorschau | test-push
│   ├── config.py                liest .env
│   ├── inhalte.py               Auswahl + Text des Tagesimpulses
│   ├── kalender.py              Google Calendar (Service-Account): lesen, Impuls eintragen, Finanztermine
│   ├── wecker.py                fällige Erinnerungen → Push / Alarm
│   ├── finanz.py                Checklisten 01.06./01.12., Links, .ics-Export
│   └── benachrichtigung.py      ntfy-Push (JSON, UTF-8) + Alarmton am Pi (aplay)
├── systemd/                     Timer: 07:00 · jede Minute · 01.06./01.12. 08:00
├── export/                      Finanz-Erinnerungen.ics (lokal erzeugt, nicht im Git)
└── tests/test_tagesimpuls.py    7 Tests ohne Netz
```

## Einrichtung (ca. 20 Minuten)

### 1. Handy: ntfy-App
1. App **ntfy** installieren (Android: Play Store/F-Droid, iPhone: App Store).
2. Ein geheimes Topic ausdenken, z. B. Ausgabe von
   `python3 -c "import secrets;print('tiep-'+secrets.token_urlsafe(12))"`, und in der App abonnieren.
3. Android: Topic > Einstellungen > eigener **Benachrichtigungston**. In den App-Einstellungen die Option für Dauer-Alarm bei höchster Priorität
   (englisch „Keep alerting for highest priority“) einschalten, dann klingelt ein Wecker wie ein echter Wecker.
   Nicht stören: ntfy als Ausnahme erlauben.

### 2. `.env` anlegen
`.env.example` nach `.env` kopieren und `NTFY_TOPIC` eintragen. `FINANZPLAN_URL` ist in der
lokalen `.env` schon auf deine Excel in Google Drive gesetzt.

### 3. Google Kalender verbinden (Service-Account)
1. https://console.cloud.google.com öffnen > Projekt anlegen (z. B. „tagesimpuls“).
2. APIs & Dienste > **Google Calendar API** aktivieren.
3. IAM > Dienstkonten > Dienstkonto erstellen > Schlüssel > **JSON** herunterladen.
4. Datei auf den Pi nach `~/.config/tagesimpuls/service-account.json` kopieren und `chmod 600` setzen.
   Die Datei NICHT ins Git legen.
5. In **Google Calendar** > Einstellungen deines Kalenders > „Für bestimmte Personen freigeben“ >
   die `client_email` aus der JSON-Datei hinzufügen > „**Änderungen an Terminen vornehmen**“.
6. Optional: neuen Kalender „Tagesimpuls“ anlegen, genauso freigeben und dessen Kalender-ID
   als `IMPULS_KALENDER_ID` eintragen. Dann steht jeder Impuls auch im Kalender (ein-/ausblendbar).

### 4. Auf den Pi bringen und installieren
```bash
scp -r Tagesimpuls-Kalender <user>@pi-ki-tiep:~/
```
```bash
ssh <user>@pi-ki-tiep "cd ~/Tagesimpuls-Kalender && sudo ./install_pi.sh <user>"
```

### 5. Testen (auf dem Pi in /opt/tagesimpuls)
```bash
.venv/bin/python -m tagesimpuls test-push
```
```bash
.venv/bin/python -m tagesimpuls impuls
```
```bash
.venv/bin/python -m tagesimpuls finanztermine-anlegen
```
```bash
.venv/bin/python -m tagesimpuls finanz --art dezember --trocken
```

## Wecker im Google Kalender nutzen

| Du willst | So geht's in Google Calendar |
|---|---|
| normale Erinnerung mit Ton aufs Handy | Termin mit Benachrichtigung anlegen (oder Standard: 30 + 10 min vorher) |
| **lauter Wecker** (Dauer-Alarm + Ton am Pi) | ⏰ oder „Wecker“/„Alarm“ in den Titel **oder** Terminfarbe **Tomate** |
| Weckzeit morgens | Termin „⏰ Aufstehen“ um 06:00 mit Benachrichtigung „0 Minuten vorher“ |

Nur Pop-up-Benachrichtigungen zählen, E-Mail-Erinnerungen ignoriert der Pi.
Ganztägige Termine erscheinen im Morgen-Push.

## Finanz-Erinnerung 01.06. und 01.12.
- 08:00 Uhr: Push mit Priorität 5 und Buttons **WISO öffnen**, **Finanzplan bearbeiten**, **ELSTER**.
- 09:00 Uhr: jährlicher Kalendertermin mit Checkliste (`finanztermine-anlegen`, einmalig).
- Ohne Pi: `export/Finanz-Erinnerungen.ics` in Google Calendar importieren (Einstellungen >
  Importieren & Exportieren). Google übernimmt dabei keine Alarme aus der Datei; stell die
  Benachrichtigung danach im Termin selbst ein.

## Sicherheit
- `.env`, Service-Account-JSON und die .ics mit dem Drive-Link sind nicht im Git (`.gitignore`).
- Das ntfy-Topic ist wie ein Passwort. Wer es kennt, kann mitlesen, also lang und zufällig wählen.
  Für mehr Privatsphäre: ntfy selbst auf dem Pi hosten (nur über Tailscale) und `NTFY_SERVER` umstellen.
- Der Service-Account sieht nur die Kalender, die du ihm ausdrücklich freigibst.
