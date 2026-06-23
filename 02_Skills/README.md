# 🎓 Skills

Skills sind wiederverwendbare Arbeitsanleitungen für Claude. Einmal erstellt, können sie immer wieder abgerufen werden.

## Was ist ein Skill?

Ein Skill ist eine Markdown-Datei, die beschreibt:
- **Zweck**: Was soll erreicht werden?
- **Wann nutzen**: In welchen Situationen?
- **Input**: Was wird benötigt?
- **Output**: Was wird erzeugt?
- **Schritt-für-Schritt**: Genaue Anleitung für Claude
- **Qualitätskriterien**: Was macht eine gute Ausführung aus?

## Struktur

```
02_Skills/
├── Templates/         # Leere Skill-Templates
├── Active/            # Aktive, nutzbare Skills
├── Meta/              # Skills über Skills (z.B. Skill Creator)
└── Archive/           # Nicht mehr genutzte Skills
```

## Aktive Skills

### SKILL_Meeting_Summary
**Zweck**: Meeting-Transkript zu strukturierter Zusammenfassung
**Datei**: [[SKILL_Meeting_Summary]]
Status: [ ] Roh | [ ] Fertig | [ ] Getestet

---

### SKILL_Social_Media_From_Transcript
**Zweck**: Aus Transkript Social-Media-Posts erstellen
**Datei**: [[SKILL_Social_Media_From_Transcript]]
Status: [ ] Roh | [ ] Fertig | [ ] Getestet

---

### [Weitere Skills hier eintragen]

## Skill nutzen

Sage einfach zu Claude:
- "Nutze den Skill Meeting Summary"
- "Fass mir das Meeting zusammen" (Claude erkennt den passenden Skill)
- "Skill: Social Media aus Transkript" + dein Text

## Neuen Skill erstellen

### Variante 1: Mit Meta-Skill
```
"Nutze den Skill Creator Skill, um einen neuen Skill zu bauen"
```

### Variante 2: Manuelle Erstellung
1. Kopiere `Templates/SKILL_Template.md`
2. Benenne um zu `SKILL_[Name].md`
3. Fülle alle Abschnitte aus
4. Speichere in `Active/`
5. Teste den Skill

### Variante 3: Claude baut ihn
```
"Bau mir einen Skill, der [Beschreibung]"
```

## Empfohlener Meta-Skill: Skill Creator

Der **Skill Creator Skill** von Anthropic hilft dir, bessere Skills zu schreiben.

**Installation**:
1. Sage Claude: "Installiere den Skill Creator Skill global"
2. Claude lädt ihn von skills.sh oder GitHub
3. Danach: "Nutze den Skill Creator, um [neuen Skill] zu bauen"

## Skill-Qualität verbessern

Gute Skills haben:
- [ ] Klaren, spezifischen Zweck
- [ ] Definierten Input/Output
- [ ] Schritt-für-Schritt Anleitung
- [ ] Beispiele (Input → Output)
- [ ] Qualitätskriterien
- [ ] Getestet und iteriert

## Pflege

- Skills in `Active/` regelmäßig aktualisieren
- Nicht mehr genutzte Skills nach `Archive/` verschieben
- Neue Ideen für Skills in `Work_In_Progress/` notieren
