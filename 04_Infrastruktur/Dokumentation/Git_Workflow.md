# Git Workflow für AI-OS

## Warum Git?
- Synchronisation zwischen PC, Server und Obsidian
- Versionsgeschichte aller Änderungen
- Backup (via GitHub)
- Kostenlose Alternative zu Obsidian Sync

## Einrichtung (einmalig)

### 1. Git Repository initialisieren
```bash
cd /c/Users/vuxua/Documents/Github_Projekte/AI-OS
git init
```

### 2. GitHub Repository erstellen
1. Auf GitHub neues Repository anlegen (privat!)
2. Nicht initialisieren mit README (haben wir schon)

### 3. Mit GitHub verbinden
```bash
git remote add origin https://github.com/DEIN_USERNAME/AI-OS.git
git branch -M main
git push -u origin main
```

## Täglicher Workflow

### Vor der Arbeit (immer!)
```bash
git pull origin main
```

### Nach der Arbeit (immer!)
```bash
git add .
git commit -m "Kurze Beschreibung der Änderungen"
git push origin main
```

## Wichtige Befehle

### Status prüfen
```bash
git status
```

### Änderungen ansehen
```bash
git diff
```

### Konflikte lösen (falls vorhanden)
```bash
# Erst pullen
git pull origin main
# Konflikte in Dateien lösen (markiert mit <<<<<<<)
# Dann:
git add .
git commit -m "Konflikte gelöst"
git push
```

## Obsidian Git Plugin

Damit Obsidian automatisch synchronisiert:

1. Einstellungen → Community Plugins → Git (von Vinzent03)
2. Installieren & aktivieren
3. Einstellungen des Plugins:
   - Auto commit-and-sync interval: 5 Minuten
   - Auto commit-and-sync after stopping file edits: An
   - Auto pull interval: 5 Minuten
   - Pull on startup: An

## Auf dem Server

```bash
# Einmalig klonen
git clone https://github.com/DEIN_USERNAME/AI-OS.git
cd AI-OS

# Vor Arbeit
git pull

# Nach Arbeit
git add . && git commit -m "Update" && git push
```

---

**Faustregel:** Vor jeder Claude-Session ein `git pull`, danach ein `git push`!
