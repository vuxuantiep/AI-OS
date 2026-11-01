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

Vertrauliches liegt gitignoriert unter wissen-intern/<modul>/ und braucht --intern:
    python wissen/einspielen.py emvia --intern
Ziele ausser localhost werden dabei ohne gesetzte Basic-Auth-Zugangsdaten abgelehnt.
"""
import base64
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def main() -> int:
    intern = "--intern" in sys.argv
    argumente = [a for a in sys.argv[1:] if a != "--intern"]
    if not argumente:
        print(__doc__)
        return 1
    modul = argumente[0]
    basis = (argumente[1] if len(argumente) > 1 else "http://localhost:8090").rstrip("/")
    ordner = Path(__file__).parent / modul
    if intern:
        ordner = Path(__file__).parent.parent / "wissen-intern" / modul
        lokal = urllib.parse.urlparse(basis).hostname in ("localhost", "127.0.0.1")
        if not lokal and not os.environ.get("WERKBANK_BASIC_PASSWORT"):
            print("Abbruch: Interne Seiten gehen nicht auf ein Ziel ohne Login.")
            return 1
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
