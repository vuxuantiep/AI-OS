# 🚀 Erste Schritte - Quickstart Guide

Willkommen in deinem neuen AI Operating System! Hier ist dein Plan, um loszulegen:

## Phase 1: Grundlagen (Heute)

### 1.1 CLAUDE.md anpassen (5 Minuten)
Öffne `CLAUDE.md` und fülle aus:
- [ ] Deinen Namen eintragen
- [ ] Deine Rolle/Beruf eintragen
- [ ] Deinen Arbeitsstil beschreiben
- [ ] Deine bevorzugte Sprache bestätigen

### 1.2 Git initialisieren (10 Minuten)
```bash
cd /c/Users/vuxua/Documents/Github_Projekte/AI-OS
git init
git add .
git commit -m "Initial commit: AI-OS Struktur"
```

Optional: Auf GitHub pushen (siehe `04_System/Docs/Git_Workflow.md`)

### 1.3 Obsidian einrichten (5 Minuten)
1. Obsidian starten
2. "Open folder as vault" wählen
3. Diesen Ordner (`AI-OS`) auswählen
4. Optional: Git-Plugin installieren (siehe Git Workflow)

## Phase 2: Wissen aufbauen (Diese Woche)

### 2.1 Über dich
Erstelle eine Datei in `00_Knowledge/01_About_Me/`:
- `Mein_Background.md` - Wer bist du, was machst du?
- `Meine_Ziele.md` - Was willst du erreichen?
- `Meine_Werkzeuge.md` - Welche Tools nutzt du täglich?

### 2.2 Aktuelle Projekte
Erstelle eine Datei in `00_Knowledge/03_Work_In_Progress/Active/`:
- `Project_Aktuelles_Projekt.md`

Nutze dafür das Template: `04_System/Templates/Project_Template.md` (kopieren und anpassen)

### 2.3 Erste Notiz
Erstelle deine erste Tagesnotiz:
```
00_Knowledge/03_Work_In_Progress/Active/{{date:YYYY-MM-DD}}_Tagesnotiz.md
```

## Phase 3: Verbindungen (Diese Woche)

### 3.1 GitHub CLI (Empfohlen)
Sage zu Claude:
```
"Installiere die GitHub CLI und melde mich an"
```

### 3.2 Google Workspace (Optional)
Wenn du Gmail/Calendar/Drive nutzen willst:
```
"Installiere das Google Workspace CLI Tool"
```

### 3.3 Weitere Tools
Frage Claude:
```
"Welche Verbindungen kannst du zu meinen Tools herstellen?"
```

## Phase 4: Erste Skills (Nächste Woche)

### 4.1 Meta-Skill installieren
```
"Installiere den Skill Creator Skill von Anthropic"
```

### 4.2 Ersten eigenen Skill bauen
Beispiel:
```
"Bau mir einen Skill, der meine täglichen Aufgaben zusammenfasst"
```

Oder nutze vorhandene Skills:
- `SKILL_Meeting_Summary` - Für Besprechungen
- `SKILL_Social_Media_From_Transcript` - Für Content-Erstellung

## Phase 5: Erste Routine (Optional)

Beispiel: Tägliche Zusammenfassung
```
"Richte mir eine tägliche Routine ein, die um 18:00 Uhr meine Tagesnotiz zusammenfasst und per Git sichert"
```

## 💡 Nächste Schritte

Wähle aus:
1. **"Hilf mir, CLAUDE.md auszufüllen"** - Wir passen die Systemanweisungen an
2. **"Installiere GitHub CLI"** - Wir richten die erste Verbindung ein
3. **"Bau mir einen Skill für [deine Aufgabe]"** - Wir erstellen deinen ersten Skill
4. **"Zeig mir Beispiele"** - Wir schauen uns an, wie andere das nutzen

Was möchtest du als erstes machen?
