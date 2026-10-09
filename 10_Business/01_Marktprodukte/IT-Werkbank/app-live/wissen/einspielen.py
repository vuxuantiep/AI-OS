"""
Spielt versionierte Wissensseiten (Markdown) ins Wiki einer IT-Werkbank-Instanz ein.

Jede Datei wissen/<modul>/<name>.md wird zu einer Wiki-Seite des Moduls <modul>:
Titel = erste "# "-Zeile, Slug = "<modul>-<name>" (stabil -> erneutes Einspielen
aktualisiert die Seite statt ein Duplikat anzulegen). Laeuft ueber die normale
API, d. h. die Seiten werden auch fuer den Chat (RAG) indexiert.

Aufruf (nur Standardbibliothek):
    python wissen/einspielen.py emvia                         # lokal: http://localhost:8090
    python wissen/einspielen.py emvia https://it-avatar.vuxuantiep.de
Basic Auth (Pi4) aus den Umgebungsvariablen WERKBANK_BASIC_USER / WERKBANK_BASIC_PASSWORT.
"""
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    modul = sys.argv[1]
    basis = (sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8090").rstrip("/")
    ordner = Path(__file__).parent / modul
    dateien = sorted(ordner.glob("*.md"))
    if not dateien:
        print(f"Keine .md-Dateien in {ordner}")
        return 1

    kopf = {"Content-Type": "application/json"}
    user, pw = os.environ.get("WERKBANK_BASIC_USER"), os.environ.get("WERKBANK_BASIC_PASSWORT")
    if user and pw:
        kopf["Authorization"] = "Basic " + base64.b64encode(f"{user}:{pw}".encode()).decode()

    fehler = 0
    for datei in dateien:
        text = datei.read_text(encoding="utf-8")
        erste = text.splitlines()[0] if text else ""
        titel = erste[2:].strip() if erste.startswith("# ") else datei.stem
        daten = {"titel": titel, "modul": modul, "inhalt": text, "slug": f"{modul}-{datei.stem}"}
        anfrage = urllib.request.Request(f"{basis}/api/wiki", data=json.dumps(daten).encode(),
                                         headers=kopf, method="POST")
        try:
            with urllib.request.urlopen(anfrage, timeout=120) as antwort:
                ergebnis = json.loads(antwort.read())
            print(f"OK  {ergebnis['slug']:<40} {ergebnis['abschnitte_indexiert']} Abschnitte indexiert")
        except Exception as e:  # weiter mit der naechsten Seite, am Ende Fehlerzahl melden
            fehler += 1
            print(f"ERR {datei.name}: {e}")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
