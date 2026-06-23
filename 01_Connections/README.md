# 🔗 Verbindungen (Connections)

Dieser Ordner enthält alle Verbindungen zu externen Tools und Diensten.

## Struktur

```
01_Connections/
├── MCP/                  # Model Context Protocol
│   ├── Installed/        # Installierte MCPs
│   └── Configurations/   # MCP-Konfigurationen
├── CLI/                  # Command Line Interface Tools
│   ├── Google_Workspace/ # gws CLI
│   ├── GitHub/            # gh CLI
│   └── Other/             # Weitere CLI Tools
└── APIs/                 # API Verbindungen
    ├── Configs/           # API-Konfigurationen
    └── Secrets/           # API-Keys (NICHT im Git!)
```

## Aktive Verbindungen

### Google Workspace
Status: [ ] Nicht konfiguriert | [ ] Konfiguriert | [ ] Aktiv

Tool: gws CLI
Dokumentation: Siehe `CLI/Google_Workspace/`

#### Funktionen:
- [ ] Gmail lesen/schreiben
- [ ] Calendar Events erstellen
- [ ] Drive Dateien verwalten

---

### GitHub
Status: [ ] Nicht konfiguriert | [ ] Konfiguriert | [ ] Aktiv

Tool: gh CLI
Dokumentation: Siehe `CLI/GitHub/`

#### Funktionen:
- [ ] Repositories verwalten
- [ ] Issues & PRs bearbeiten
- [ ] Actions steuern

---

### [Weitere Tools]
Status: [ ] Nicht konfiguriert | [ ] Konfiguriert | [ ] Aktiv

Tool: [Tool-Name]
Dokumentation: [Link oder Datei]

#### Funktionen:
- [ ] [Funktion 1]
- [ ] [Funktion 2]

---

## Neue Verbindung hinzufügen

Um ein neues Tool anzubinden:

1. Prüfe in `CLAUDE.md`, ob es bereits erwähnt ist
2. Sage Claude: "Installiere mir [Tool-Name] und richte die Verbindung ein"
3. Claude wird:
   - Das passende Installationsverfahren finden (MCP/CLI/API)
   - Die Installation durchführen
   - Die Konfiguration dokumentieren
   - Eine Test-Verbindung aufbauen

## Sicherheit

- **Secrets** (API-Keys, Tokens) werden in `APIs/Secrets/` gespeichert
- Dieser Ordner ist in `.gitignore` ausgeschlossen
- Secrets gehören NIE ins Git-Repository!

## Hilfreiche Fragen für Claude

- "Welche Tools habe ich bereits verbunden?"
- "Richte mir Google Workspace ein"
- "Welche MCPs sind verfügbar für [Tool]?"
- "Teste die Verbindung zu [Tool]"
