"""
RAG-Speicher der IT-Werkbank.

Zwei Sammlungen in Qdrant:
  werkbank_wiki — Nachschlagewissen, das du selbst pflegst (Wiki-Seiten,
                  Betriebshandbuecher, eigene Notizen). Beim Speichern einer
                  Wiki-Seite wird sie in Abschnitte zerlegt und eingebettet.
  werkbank_chat — Gedaechtnis. Abgeschlossene Frage-Antwort-Paare wandern hier
                  hinein, damit der Assistent frueher geloeste Faelle
                  wiederfindet, auch aus einer anderen Sitzung.

Bei der Suche werden beide Sammlungen abgefragt, Wiki hoeher gewichtet als
Chatverlauf: gepflegtes Wissen schlaegt Erinnerung.
"""

from __future__ import annotations

import os
import re
import uuid

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from . import llm

WIKI = "werkbank_wiki"
CHAT = "werkbank_chat"
VEKTORGROESSE = int(os.getenv("VEKTORGROESSE", "768"))
GEWICHT_WIKI = 1.0
GEWICHT_CHAT = 0.75

client = AsyncQdrantClient(url=os.getenv("QDRANT_URL", "http://qdrant:6333"))


async def vorbereiten() -> None:
    """Sammlungen anlegen, falls sie fehlen. Beim Start aufrufen."""
    vorhanden = {s.name for s in (await client.get_collections()).collections}
    for name in (WIKI, CHAT):
        if name not in vorhanden:
            await client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=VEKTORGROESSE, distance=Distance.COSINE),
            )


def abschnitte(text: str, groesse: int = 900, ueberlappung: int = 120) -> list[str]:
    """Zerlegt Text an Absatzgrenzen, damit Abschnitte lesbar bleiben."""
    absaetze = [a.strip() for a in re.split(r"\n\s*\n", text) if a.strip()]
    stuecke: list[str] = []
    puffer = ""
    for absatz in absaetze:
        if len(puffer) + len(absatz) + 2 <= groesse:
            puffer = f"{puffer}\n\n{absatz}".strip()
        else:
            if puffer:
                stuecke.append(puffer)
            puffer = (puffer[-ueberlappung:] + "\n\n" + absatz).strip() if puffer else absatz
            while len(puffer) > groesse:
                stuecke.append(puffer[:groesse])
                puffer = puffer[groesse - ueberlappung :]
    if puffer:
        stuecke.append(puffer)
    return stuecke


async def wiki_speichern(slug: str, titel: str, modul: str, inhalt: str) -> int:
    """Ersetzt eine Wiki-Seite im Index. Rueckgabe: Zahl der Abschnitte."""
    await client.delete(
        collection_name=WIKI,
        points_selector=Filter(must=[FieldCondition(key="slug", match=MatchValue(value=slug))]),
    )
    stuecke = abschnitte(inhalt)
    if not stuecke:
        return 0
    vektoren = await llm.einbetten([f"{titel}\n\n{s}" for s in stuecke])
    await client.upsert(
        collection_name=WIKI,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vektor,
                payload={
                    "slug": slug,
                    "titel": titel,
                    "modul": modul,
                    "text": stueck,
                    "abschnitt": nummer,
                },
            )
            for nummer, (stueck, vektor) in enumerate(zip(stuecke, vektoren), start=1)
        ],
    )
    return len(stuecke)


async def wiki_loeschen(slug: str) -> None:
    """Entfernt alle Chunks einer Wiki-Seite aus dem Vektorindex (z.B. bei
    Duplikat-Bereinigung -- siehe Vorfall doppelt indizierter Quellen durch
    einen frueheren Slug-Bug in scraper.quelle_aktualisieren)."""
    await client.delete(
        collection_name=WIKI,
        points_selector=Filter(must=[FieldCondition(key="slug", match=MatchValue(value=slug))]),
    )


async def chat_merken(sitzung_id: str, modul: str, frage: str, antwort: str) -> None:
    """Legt ein Frage-Antwort-Paar ins Langzeitgedaechtnis."""
    text = f"Frage: {frage}\n\nAntwort: {antwort}"
    try:
        vektor = (await llm.einbetten([text]))[0]
    except llm.KeinAnbieter:
        return  # Gedaechtnis ist Komfort, kein Grund die Antwort zu verlieren
    await client.upsert(
        collection_name=CHAT,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vektor,
                payload={
                    "sitzung_id": sitzung_id,
                    "modul": modul,
                    "titel": frage[:80],
                    "text": text,
                },
            )
        ],
    )


async def suchen(frage: str, modul: str | None = None, anzahl: int = 5) -> list[dict]:
    """Sucht in Wiki und Chatgedaechtnis und mischt nach gewichteter Guete."""
    try:
        vektor = (await llm.einbetten([frage]))[0]
    except llm.KeinAnbieter:
        return []

    filter_ = (
        Filter(must=[FieldCondition(key="modul", match=MatchValue(value=modul))])
        if modul and modul != "assistent"
        else None
    )

    treffer: list[dict] = []
    for sammlung, gewicht, quelle in ((WIKI, GEWICHT_WIKI, "wiki"), (CHAT, GEWICHT_CHAT, "chat")):
        try:
            rohe = await client.search(
                collection_name=sammlung,
                query_vector=vektor,
                query_filter=filter_ if sammlung == WIKI else None,
                limit=anzahl,
                with_payload=True,
            )
        except Exception:
            continue
        for punkt in rohe:
            treffer.append(
                {
                    "quelle": quelle,
                    "titel": punkt.payload.get("titel", "ohne Titel"),
                    "slug": punkt.payload.get("slug"),
                    "modul": punkt.payload.get("modul"),
                    "text": punkt.payload.get("text", ""),
                    "guete": round(punkt.score * gewicht, 4),
                }
            )

    treffer.sort(key=lambda t: t["guete"], reverse=True)
    return treffer[:anzahl]


def kontext_bauen(treffer: list[dict], zeichen: int = 4000) -> str:
    """Formt Treffer zu einem Kontextblock fuer den Systemprompt."""
    zeilen: list[str] = []
    laenge = 0
    for nummer, t in enumerate(treffer, start=1):
        kopf = f"[{nummer}] {t['titel']} ({t['quelle']})"
        block = f"{kopf}\n{t['text']}"
        if laenge + len(block) > zeichen:
            break
        zeilen.append(block)
        laenge += len(block)
    return "\n\n".join(zeilen)
