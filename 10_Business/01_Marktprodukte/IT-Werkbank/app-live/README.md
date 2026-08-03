# IT-Werkbank

Arbeitsassistent für Systemadministration und Architektur. Neun Fachmodule,
Wissensspeicher mit Vektorsuche, Gesprächsgedächtnis, Skriptbibliothek und ein
Netzrechner, der ohne Modell arbeitet.

## Aufbau

```
web/index.html            Oberfläche, eine Datei, keine Abhängigkeiten
app/main.py               FastAPI, verdrahtet alles
app/module_katalog.py     Fachmodule, Fachprompts, Skriptbibliothek
app/llm.py                Modellkette: lokal -> Cloud-Fallback
app/rag.py                Qdrant, Wiki-Index und Chatgedächtnis
app/store.py              Sitzungen, Nachrichten, Wikiseiten in SQLite
wiki/                     Startseiten zum Einpflegen
```

## Start

```bash
cp .env.beispiel .env      # mindestens einen Cloud-Schlüssel eintragen
docker compose up -d --build
# Oberfläche: http://localhost:8080
```

Ohne Docker:

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Modellkette

`app/llm.py` probiert von oben nach unten: lokales Modell, dann Anthropic,
dann OpenAI. Wer scheitert, wird 120 Sekunden übersprungen — so wartet keine
Anfrage auf einen toten lokalen Endpunkt. Welcher Anbieter geantwortet hat,
steht über jeder Antwort und in der Betriebsanzeige links unten.

Die Anzeige wechselt die Akzentfarbe: blau heißt lokal, bernstein heißt
Cloud-Fallback aktiv, rot heißt nichts erreichbar.

## Wissensspeicher

Zwei Qdrant-Sammlungen:

- `werkbank_wiki` — was du selbst pflegst. Höher gewichtet.
- `werkbank_chat` — abgeschlossene Frage-Antwort-Paare, auch sitzungsübergreifend.

Wiki-Seiten schreibst du in der Oberfläche oder als Markdown-Datei unter
`wiki/`. Beim Speichern werden sie in Absatzabschnitte zerlegt und eingebettet.

Fällt Qdrant aus, antwortet der Assistent weiter — nur ohne Kontext. Das ist
Absicht: der Speicher ist Komfort, nicht Voraussetzung.

## Netzrechner

Rechnet vollständig im Browser: Maske, Bereich, Broadcast, nutzbare Hosts,
Aufteilung in Teilnetze plus Adressplan mit Kopieren-Schaltfläche. Läuft auch,
wenn das Backend steht.

## Nächste Ausbaustufen

- Wiki-Dateien aus `wiki/` beim Start automatisch indexieren
- Antwortstrom (Server-Sent Events) statt Warten auf den kompletten Text
- Zugriffsschutz vor dem Betrieb im Firmennetz — aktuell ist nichts geschützt
