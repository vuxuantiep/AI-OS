"""
IT-Werkbank — Backend.

@copyright Tiep Vu Xuan - 2026

Start:
    uvicorn app.main:app --host 0.0.0.0 --port 8080
"""

from __future__ import annotations

import base64
import contextlib
import hmac
import ipaddress
import os
import re
from pathlib import Path

from fastapi import APIRouter, FastAPI, File, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import anhang, cron, llm, module_katalog, rag, rss, scraper, store

api = APIRouter(prefix="/api")


@contextlib.asynccontextmanager
async def lebenszyklus(app: FastAPI):
    await store.vorbereiten()
    with contextlib.suppress(Exception):
        await rag.vorbereiten()  # ohne Qdrant laeuft der Chat weiter, nur ohne RAG
    cron.starten()
    yield
    cron.stoppen()


app = FastAPI(title="IT-Werkbank", version="1.0", lifespan=lebenszyklus)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Zugriffsschutz (HTTP Basic Auth) — die Werkbank ist unter einer eigenen
# oeffentlichen Domain erreichbar (Cloudflare Tunnel, wechselnder Origin:
# Windows-PC oder Pi4), war bislang aber vollstaendig ungeschuetzt (dokumentiert
# als offener Punkt in 00_Wissen/09_Wiki/Entitäten/IT-Werkbank-Avatar.md).
# Bewusst App-seitig statt am Cloudflare Worker (wie beim AI-OS-Dashboard):
# funktioniert dadurch unveraendert, egal auf welchem Rechner der Container
# gerade laeuft, und ruehrt nicht an der bestehenden, funktionierenden
# Worker-Absicherung des Dashboards.
# Ohne gesetztes Passwort bleibt der Zugriff bewusst offen (lokale Entwicklung
# ohne Basic-Auth-Popup) -- vor jedem oeffentlichen Betrieb muss das Passwort
# in der .env gesetzt sein.
WERKBANK_BASIC_USER = os.getenv("WERKBANK_BASIC_USER", "")
WERKBANK_BASIC_PASSWORT = os.getenv("WERKBANK_BASIC_PASSWORT", "")


@app.middleware("http")
async def basic_auth_pruefen(request, call_next):
    if not WERKBANK_BASIC_PASSWORT or request.url.path == "/api/health":
        return await call_next(request)

    kopf = request.headers.get("authorization", "")
    gueltig = False
    if kopf.startswith("Basic "):
        with contextlib.suppress(Exception):
            nutzer, _, passwort = base64.b64decode(kopf[6:]).decode("utf-8").partition(":")
            gueltig = hmac.compare_digest(nutzer, WERKBANK_BASIC_USER) and hmac.compare_digest(
                passwort, WERKBANK_BASIC_PASSWORT
            )
    if not gueltig:
        return Response(
            "Authentifizierung erforderlich",
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="IT-Werkbank"'},
        )
    return await call_next(request)


# ---------------------------------------------------------------------------
# Katalog und Betriebszustand
# ---------------------------------------------------------------------------

@api.get("/module")
async def module() -> list[dict]:
    return [
        {"id": m.id, "name": m.name, "kurz": m.kurz, "stichworte": list(m.stichworte)}
        for m in module_katalog.MODULE
    ]


@api.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@api.get("/module/neu")
async def module_neu() -> list[str]:
    """Module, in denen der Scraper neu entdeckte, wichtige Themen (Sicherheit,
    Härtung, ...) abgelegt hat -- fürs blinkende Abzeichen in der Modulschiene."""
    return await store.module_mit_neuem_wissen()


@api.get("/zustand")
async def zustand() -> dict:
    kette = await llm.zustand()
    aktiv = next((a for a in kette if a["zustand"] == "bereit"), None)
    return {
        "kette": kette,
        "aktiv": aktiv["name"] if aktiv else None,
        "art": aktiv["art"] if aktiv else "keiner",
    }


# ---------------------------------------------------------------------------
# Chat mit RAG und Gedaechtnis
# ---------------------------------------------------------------------------

class ChatAnfrage(BaseModel):
    frage: str = Field(min_length=2, max_length=8000)
    modul: str = "assistent"
    sitzung_id: str = ""
    rag: bool = True


# Unterhalb dieser gewichteten Aehnlichkeit (rag.suchen() liefert 0..1) gilt der
# beste RAG-Treffer als nicht belastbar -- das Modell soll dann nicht aus eigenem
# (moeglicherweise erfundenem) Wissen antworten, sondern es wird automatisch
# einmal live im Web nachgesehen, bevor der Systemprompt gebaut wird. Ueber
# RAG_MINDESTGUETE in der .env feinjustierbar, falls sich in der Praxis zeigt,
# dass zu oft/zu selten gesucht wird.
RAG_MINDESTGUETE = float(os.getenv("RAG_MINDESTGUETE", "0.30"))


# Fragen mit diesen Stichwoertern verlangen zwingend einen aktuellen Stand --
# ein generischer, thematisch passender Wiki-Treffer (z.B. eine vom Scraper
# vor Wochen abgelegte "aktuelle Best Practices"-Seite) beantwortet die Frage
# NICHT, auch wenn er die RAG_MINDESTGUETE-Schwelle ueberschreitet. Deshalb
# unabhaengig von der Trefferguete pruefen -- siehe Vorfall: "gibt es Neues
# bei Windows Server/Hyper-V/M365" wurde aus veraltetem Trainingswissen
# beantwortet (Windows Server 2022, Stand 2021, als aktuelle Neuigkeit
# dargestellt), weil ein thematisch passender, aber inhaltlich nicht
# einschlaegiger RAG-Treffer die Websuche unterdrueckt hat.
AKTUALITAETS_SCHLUESSELWOERTER = (
    "neu", "neues", "neuigkeit", "neuigkeiten", "aktuell", "update", "news",
    "kuerzlich", "letzte", "letzten", "changelog", "release notes",
    "was gibt es", "stand heute", "roadmap",
)


def _fragt_nach_aktualitaet(frage: str) -> bool:
    tief = frage.lower()
    return any(wort in tief for wort in AKTUALITAETS_SCHLUESSELWOERTER)


async def _web_fallback(frage: str) -> list[dict]:
    """Schnelle SearXNG-Suche (nur Titel/Kurzbeschreibung, keine Seiten laden --
    das waere fuer eine einzelne Chat-Antwort zu langsam) als Grundlage, wenn
    Wiki und Gedaechtnis nichts Passendes hatten. Liefert dieselbe Form wie
    rag.suchen(), damit rag.kontext_bauen() und die quellen-Liste unveraendert
    weiterverwendet werden koennen."""
    rohe = await scraper.suchen(frage, max_treffer=4)
    return [
        {
            "quelle": "web",
            "titel": r["titel"] or r["url"],
            "slug": r["url"],
            "text": f"{r['titel']}\n{r['kurz']}\nQuelle: {r['url']}",
            "guete": None,
        }
        for r in rohe
        if r.get("titel") or r.get("kurz")
    ]


@api.post("/chat")
async def chat(anfrage: ChatAnfrage) -> dict:
    sitzung_id = await store.sitzung_sichern(
        anfrage.sitzung_id, anfrage.modul, anfrage.frage
    )

    treffer: list[dict] = []
    if anfrage.rag:
        with contextlib.suppress(Exception):
            treffer = await rag.suchen(anfrage.frage, anfrage.modul)

    # Reicht das Wissen aus Wiki/Gedaechtnis nicht (nichts gefunden oder der
    # beste Treffer zu schwach), muss vor der Antwort im Web nachgesehen werden
    # -- sonst faengt das Modell an, Luecken selbst zu erfinden (siehe Vorfall
    # "Eureka-Fach"/"eIP": erfundene Beschreibungen statt Recherche).
    deckt_ab = bool(treffer) and (treffer[0]["guete"] or 0) >= RAG_MINDESTGUETE
    zeitkritisch = _fragt_nach_aktualitaet(anfrage.frage)
    web_treffer: list[dict] = []
    if not deckt_ab or zeitkritisch:
        with contextlib.suppress(Exception):
            web_treffer = await _web_fallback(anfrage.frage)

    kontext = rag.kontext_bauen(treffer)
    if web_treffer:
        grund = (
            "die Frage ausdruecklich nach Aktualitaet fragt (Trainingswissen allein reicht dafuer nie)"
            if zeitkritisch and deckt_ab
            else "Wiki/Gedaechtnis keinen ausreichenden Treffer hatten"
        )
        block = f"Live-Websuche (automatisch, da {grund}):\n\n"
        block += rag.kontext_bauen(web_treffer)
        kontext = f"{kontext}\n\n{block}" if kontext else block

    alle_treffer = treffer + web_treffer
    systemprompt = module_katalog.systemprompt(anfrage.modul, kontext)

    vorher = await store.verlauf(sitzung_id, grenze=10)
    verlauf = [
        {"role": n["rolle"], "content": n["inhalt"]}
        for n in vorher
        if n["rolle"] in ("user", "assistant")
    ]
    verlauf.append({"role": "user", "content": anfrage.frage})

    try:
        ergebnis = await llm.frage(systemprompt, verlauf)
    except llm.KeinAnbieter as fehler:
        raise HTTPException(503, str(fehler)) from fehler

    await store.nachricht_anfuegen(sitzung_id, "user", anfrage.frage)
    await store.nachricht_anfuegen(sitzung_id, "assistant", ergebnis.text, ergebnis.anbieter)
    with contextlib.suppress(Exception):
        await rag.chat_merken(sitzung_id, anfrage.modul, anfrage.frage, ergebnis.text)

    return {
        "antwort": ergebnis.text,
        "sitzung_id": sitzung_id,
        "anbieter": ergebnis.anbieter,
        "art": ergebnis.art,
        "modell": ergebnis.modell,
        "versuche": ergebnis.versuche,
        "quellen": [
            {"titel": t["titel"], "quelle": t["quelle"], "slug": t["slug"], "guete": t["guete"]}
            for t in alle_treffer
        ],
    }


MAX_ANHANG_BYTES = 15 * 1024 * 1024  # 15 MB pro Datei


@api.post("/anhang")
async def anhang_lesen(dateien: list[UploadFile] = File(...)) -> dict:
    """Liest hochgeladene Dateien (Dokumente, ZIP, Fotos) und liefert je
    Datei den extrahierten Text zurueck. Das Frontend setzt diesen Text vor
    die eigentliche Chat-Frage -- die /api/chat-Schnittstelle bleibt reines
    JSON, kein separater Upload-Zustand im Backend noetig."""
    texte = []
    for datei in dateien:
        inhalt = await datei.read()
        if len(inhalt) > MAX_ANHANG_BYTES:
            texte.append({"name": datei.filename, "inhalt": "(Datei zu groß, übersprungen.)"})
            continue
        texte.append({"name": datei.filename, "inhalt": anhang.datei_text(datei.filename, inhalt)})
    return {"texte": texte}


@api.get("/sitzungen")
async def sitzungen() -> list[dict]:
    return await store.sitzungen()


@api.get("/sitzung/{sitzung_id}")
async def sitzung(sitzung_id: str) -> list[dict]:
    return await store.verlauf(sitzung_id, grenze=200)


@api.delete("/sitzung/{sitzung_id}")
async def sitzung_loeschen(sitzung_id: str) -> dict:
    await store.sitzung_loeschen(sitzung_id)
    with contextlib.suppress(Exception):
        await rag.chat_sitzung_vergessen(sitzung_id)
    return {"geloescht": True}


# ---------------------------------------------------------------------------
# Wiki
# ---------------------------------------------------------------------------

class WikiSeite(BaseModel):
    titel: str = Field(min_length=2, max_length=200)
    modul: str = "assistent"
    inhalt: str = Field(min_length=1)
    slug: str = ""


def _slug(text: str) -> str:
    ersatz = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    for alt, neu in ersatz.items():
        text = text.lower().replace(alt, neu)
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80] or "seite"


@api.get("/wiki")
async def wiki_liste(modul: str | None = None) -> list[dict]:
    return await store.wiki_liste(modul)


@api.get("/wiki/{slug}")
async def wiki_lesen(slug: str) -> dict:
    seite = await store.wiki_lesen(slug)
    if not seite:
        raise HTTPException(404, "Seite nicht gefunden.")
    if seite.get("neu"):
        # Oeffnen der Seite gilt als "gelesen" -- Abzeichen verschwindet.
        await store.wiki_als_gelesen_markieren(slug)
    return seite


@api.post("/wiki")
async def wiki_schreiben(seite: WikiSeite) -> dict:
    slug = seite.slug or _slug(seite.titel)
    await store.wiki_schreiben(slug, seite.titel, seite.modul, seite.inhalt)
    abschnitte = 0
    with contextlib.suppress(Exception):
        abschnitte = await rag.wiki_speichern(slug, seite.titel, seite.modul, seite.inhalt)
    return {"slug": slug, "abschnitte_indexiert": abschnitte}


@api.delete("/wiki/{slug}")
async def wiki_loeschen(slug: str) -> dict:
    await store.wiki_loeschen(slug)
    with contextlib.suppress(Exception):
        await rag.wiki_loeschen(slug)
    return {"geloescht": slug}


# ---------------------------------------------------------------------------
# Vorlagen (Skript-/E-Mail-/Ticket-/Doku-Bausteine je Modul) — ersetzt die
# frueher statische, nur lesbare Skriptbibliothek. Editierbar ueber die UI,
# vier Typen (siehe module_katalog.VORLAGE_TYPEN), Erstbefuellung aus der
# alten module_katalog.SKRIPTE-Liste passiert einmalig in store.vorbereiten().
# ---------------------------------------------------------------------------

class VorlageEintrag(BaseModel):
    id: str = ""
    titel: str = Field(min_length=2, max_length=200)
    modul: str = "assistent"
    typ: str = Field(pattern="^(skript|email|ticket|doku)$")
    sprache: str = ""
    inhalt: str = Field(min_length=1)


@api.get("/vorlagen/typen")
async def vorlagen_typen() -> list[dict]:
    return list(module_katalog.VORLAGE_TYPEN)


@api.get("/vorlagen/uebersicht")
async def vorlagen_uebersicht() -> list[dict]:
    return await store.vorlagen_uebersicht()


@api.get("/vorlagen")
async def vorlagen_liste(modul: str | None = None, typ: str | None = None) -> list[dict]:
    return await store.vorlage_liste(modul, typ)


@api.get("/vorlagen/{id_}")
async def vorlage_lesen(id_: str) -> dict:
    vorlage = await store.vorlage_lesen(id_)
    if not vorlage:
        raise HTTPException(404, "Vorlage nicht gefunden.")
    return vorlage


@api.post("/vorlagen")
async def vorlage_schreiben(eintrag: VorlageEintrag) -> dict:
    id_ = eintrag.id or _slug(eintrag.titel)
    await store.vorlage_schreiben(
        id_, eintrag.modul, eintrag.typ, eintrag.titel, eintrag.sprache, eintrag.inhalt
    )
    return {"id": id_}


@api.delete("/vorlagen/{id_}")
async def vorlage_loeschen(id_: str) -> dict:
    await store.vorlage_loeschen(id_)
    return {"geloescht": id_}


# ---------------------------------------------------------------------------
# Web-Scraper-Agent
# ---------------------------------------------------------------------------

class ScraperAnfrage(BaseModel):
    thema: str = Field(min_length=2, max_length=300)
    modul: str = "assistent"
    mit_microsoft: bool = True


@api.post("/scraper/lauf")
async def scraper_lauf_start(anfrage: ScraperAnfrage) -> dict:
    return await scraper.thema_aktualisieren(anfrage.thema, anfrage.modul, anfrage.mit_microsoft)


@api.get("/scraper/verlauf")
async def scraper_verlauf() -> list[dict]:
    return await store.scraper_lauf_liste()


# --- Eigene Quellen: CEO traegt selbst entdeckte gute Links ein ------------

class QuelleAnfrage(BaseModel):
    url: str = Field(min_length=8, max_length=500)
    titel: str = ""
    modul: str = "assistent"


@api.get("/quellen")
async def quellen_liste() -> list[dict]:
    return await store.quellen_liste()


@api.post("/quellen")
async def quelle_anlegen(anfrage: QuelleAnfrage) -> dict:
    if not anfrage.url.startswith(("http://", "https://")):
        raise HTTPException(400, "URL muss mit http:// oder https:// beginnen.")
    quelle_id = await store.quelle_hinzufuegen(anfrage.url, anfrage.titel, anfrage.modul)
    # Sofort einmal laden, damit die Wiki-Seite gleich verfuegbar ist -- danach
    # haelt der taegliche Cronjob sie automatisch aktuell.
    ergebnis = await scraper.quelle_aktualisieren(anfrage.url, anfrage.titel, anfrage.modul)
    if not anfrage.titel and ergebnis.get("thema"):
        # Automatisch erkannten Titel auch in der Quellen-Liste festhalten,
        # statt bei jedem Cron-Lauf wieder mit leerem Titel zu starten.
        await store.quelle_hinzufuegen(anfrage.url, ergebnis["thema"], anfrage.modul)
    return {"id": quelle_id, **ergebnis}


@api.delete("/quellen/{quelle_id}")
async def quelle_entfernen(quelle_id: int) -> dict:
    await store.quelle_loeschen(quelle_id)
    return {"geloescht": quelle_id}


# ---------------------------------------------------------------------------
# Tech-News: RSS-Check
# ---------------------------------------------------------------------------

@api.get("/technews/aktuelles")
async def technews_aktuelles() -> list[dict]:
    return await store.rss_eintraege_liste()


@api.post("/technews/pruefen")
async def technews_pruefen() -> dict:
    return await rss.rss_pruefen()


# ---------------------------------------------------------------------------
# Architektur-Diagramm
# ---------------------------------------------------------------------------

@api.get("/architektur")
async def architektur() -> dict:
    pfad = Path(__file__).resolve().parent / "architektur.mmd"
    return {"mermaid": pfad.read_text(encoding="utf-8") if pfad.exists() else ""}


# ---------------------------------------------------------------------------
# Netzrechner — deterministisch, ohne Modell
# ---------------------------------------------------------------------------

@api.get("/netz/rechnen")
async def netz_rechnen(netz: str, teilen_in: int | None = None) -> dict:
    """Beispiel: /api/netz/rechnen?netz=10.20.30.0/24&teilen_in=4"""
    try:
        objekt = ipaddress.ip_network(netz, strict=False)
    except ValueError as fehler:
        raise HTTPException(400, f"Ungueltige Angabe: {fehler}") from fehler

    hosts = list(objekt.hosts())
    ergebnis = {
        "netz": str(objekt),
        "maske": str(objekt.netmask),
        "platzhalter": str(objekt.hostmask),
        "erste_adresse": str(hosts[0]) if hosts else None,
        "letzte_adresse": str(hosts[-1]) if hosts else None,
        "broadcast": str(objekt.broadcast_address) if objekt.version == 4 else None,
        "nutzbare_hosts": len(hosts),
        "privat": objekt.is_private,
    }

    if teilen_in and teilen_in > 1:
        zusatz = (teilen_in - 1).bit_length()
        neu = objekt.prefixlen + zusatz
        if neu > objekt.max_prefixlen:
            raise HTTPException(400, "Netz zu klein fuer diese Aufteilung.")
        ergebnis["teilnetze"] = [
            {"netz": str(t), "erste": str(next(iter(t.hosts()), t.network_address))}
            for t in list(objekt.subnets(new_prefix=neu))[:64]
        ]
    return ergebnis


app.include_router(api)

# Screenshots/Bilder zu Wiki-Seiten (z.B. aus Schulungsunterlagen extrahiert) --
# je Slug ein Unterordner, ueber diesen Pfad statisch ausgeliefert. Muss vor
# dem Frontend-Catch-all-Mount ("/") registriert werden, sonst fangen dessen
# Routen jede Anfrage vorher ab.
_BILD_ORDNER = Path(os.getenv("WERKBANK_DATEN", "/daten")) / "wiki-bilder"
_BILD_ORDNER.mkdir(parents=True, exist_ok=True)
app.mount("/wiki-bilder", StaticFiles(directory=_BILD_ORDNER), name="wiki-bilder")

# Frontend ausliefern, falls vorhanden
web = Path(__file__).resolve().parent.parent / "web"
if web.is_dir():
    app.mount("/", StaticFiles(directory=web, html=True), name="web")
