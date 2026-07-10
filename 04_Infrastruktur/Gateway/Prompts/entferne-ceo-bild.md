# Prompt: CEO-Bild aus Dashboard entfernen

## Ziel
Entferne die **gesamte CEO-Darstellung** über und im Bereich des 3D-Logos / 3D-Canvas, inklusive aller assoziierten Themes, Dateien und Logik, ohne die übrigen Dashboard-Funktionen zu zerstören.

## Scope
- Datei `04_Infrastruktur/Gateway/templates/dashboard.html` prüfen und anpassen.
- Prüfe, ob `04_Infrastruktur/Gateway/Design-Farbe.png` referenziert wird und entferne diese Referenz; entferne bzw. lösche die Datei nur, wenn sie durch das Dashboard geladen wird.
- Behalte alle übrigen 3D-/Factory-/Architektur-Elemente bei.

## Kontext
Die Sektion ist vermutlich unter den 3D-/Branding-Elementen versteckt und nicht als normales `<img>` eingebunden.

## Prüfpfad
- Suche nach: `Design-Farbe.png`, `ceo`, `CEO`, `logo`, `LOGO`, `3D`.
- Prüfe die Factory-3D Initialisierung und dazugehörige Zeichenroutinen auf CEO-spezifische Elemente.

## Anforderung
- Die Entfernung muss **restlos** sein: kein Bild, keine Figur, keine Referenz.
- Nach der Änderung muss das Dashboard weiterstartbar sein und das 3D-/Factory-Canvas ohne CEO-Anteil rendern.

## Output
- Nenne exakt die geänderten Dateien und Zeilen.