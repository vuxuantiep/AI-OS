# 🔄 Routinen

Routinen sind automatisierte Abläufe, die zu festgelegten Zeiten ausgeführt werden.

## Arten von Routinen

### Lokale Routinen
Laufen auf diesem PC.
- ✅ Zugriff auf lokale Dateien
- ✅ Download-Ordner verarbeiten
- ❌ PC muss an sein

### Remote Routinen
Laufen auf dem Server.
- ✅ Laufen auch bei ausgeschaltetem PC
- ✅ Cloud-basierte Aufgaben
- ❌ Kein Zugriff auf lokale Dateien

## Struktur

```
03_Routines/
├── Local/
│   ├── Daily/
│   ├── Weekly/
│   └── Monthly/
└── Remote/
    ├── Daily/
    ├── Weekly/
    └── Monthly/
```

## Aktive Routinen

### Lokale Routinen

#### ROUTINE_Daily_Backup
**Häufigkeit**: Täglich, 18:00
**Datei**: [[ROUTINE_Daily_Backup]]
**Status**: [ ] Inaktiv | [ ] Aktiv

**Zweck**: 
- Git commit & push
- Lokale Dateien sichern

---

### Remote Routinen

#### [Routine Name]
**Häufigkeit**: 
**Datei**: 
**Status**: [ ] Inaktiv | [ ] Aktiv

**Zweck**: 
- [Beschreibung]

---

## Routine erstellen

1. Kopiere `04_System/Templates/ROUTINE_Template.md`
2. Fülle aus und speichere im richtigen Ordner
3. Sage Claude: "Richte mir die Routine [Name] ein"
4. Claude konfiguriert den Cronjob

## Cronjob-Format (für technische Kontrolle)

```
* * * * *
│ │ │ │ │
│ │ │ │ └───── Wochentag (0-7, 0=Sonntag)
│ │ │ └───────── Monat (1-12)
│ │ └──────────── Tag im Monat (1-31)
│ └────────────── Stunde (0-23)
└────────────────── Minute (0-59)
```

**Beispiele**:
- `0 9 * * 1` = Jeden Montag um 9:00
- `0 8 * * *` = Täglich um 8:00
- `0 0 * * 0` = Jeden Sonntag um Mitternacht
- `*/30 * * * *` = Alle 30 Minuten

## Verwaltung

Routinen werden in Hermes verwaltet:
```
hermes cron list      # Alle Routinen anzeigen
hermes cron create    # Neue Routine
hermes cron edit      # Bearbeiten
hermes cron remove    # Löschen
```
