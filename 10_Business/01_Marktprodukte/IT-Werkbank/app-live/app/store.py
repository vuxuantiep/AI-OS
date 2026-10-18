"""
Dauerspeicher der IT-Werkbank (SQLite).

Warum SQLite und nicht der RAG-Speicher allein: der Verlauf muss exakt und in
Reihenfolge wiederherstellbar sein, ein Vektorspeicher liefert nur Aehnlichkeit.
Qdrant ist das Gedaechtnis, SQLite das Protokoll.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

import aiosqlite

PFAD = os.getenv("WERKBANK_DB", "/daten/werkbank.sqlite")

SCHEMA = """
CREATE TABLE IF NOT EXISTS sitzungen (
    id        TEXT PRIMARY KEY,
    titel     TEXT NOT NULL,
    modul     TEXT NOT NULL,
    erstellt  TEXT NOT NULL,
    geaendert TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS nachrichten (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    sitzung_id TEXT NOT NULL REFERENCES sitzungen(id) ON DELETE CASCADE,
    rolle      TEXT NOT NULL,
    inhalt     TEXT NOT NULL,
    anbieter   TEXT,
    zeit       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_nachrichten_sitzung ON nachrichten(sitzung_id, id);
CREATE TABLE IF NOT EXISTS wiki (
    slug      TEXT PRIMARY KEY,
    titel     TEXT NOT NULL,
    modul     TEXT NOT NULL,
    inhalt    TEXT NOT NULL,
    geaendert TEXT NOT NULL,
    erstellt  TEXT NOT NULL DEFAULT '',
    neu       INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS scraper_lauf (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    thema  TEXT NOT NULL,
    modul  TEXT NOT NULL,
    slug   TEXT NOT NULL,
    status TEXT NOT NULL,
    zeit   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_scraper_lauf_zeit ON scraper_lauf(zeit DESC);
CREATE TABLE IF NOT EXISTS quellen (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    url       TEXT NOT NULL UNIQUE,
    titel     TEXT NOT NULL,
    modul     TEXT NOT NULL,
    hinzugefuegt TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS rss_eintrag (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    thema        TEXT NOT NULL,
    quelle_titel TEXT NOT NULL,
    titel        TEXT NOT NULL,
    url          TEXT NOT NULL UNIQUE,
    veroeffentlicht TEXT,
    gefunden_am  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_rss_eintrag_gefunden ON rss_eintrag(gefunden_am DESC);
CREATE TABLE IF NOT EXISTS vorlage (
    id        TEXT PRIMARY KEY,
    modul     TEXT NOT NULL,
    typ       TEXT NOT NULL,
    titel     TEXT NOT NULL,
    sprache   TEXT NOT NULL DEFAULT '',
    inhalt    TEXT NOT NULL,
    erstellt  TEXT NOT NULL,
    geaendert TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_vorlage_modul_typ ON vorlage(modul, typ);
CREATE TABLE IF NOT EXISTS vorlage_paket (
    id          TEXT PRIMARY KEY,
    eingespielt TEXT NOT NULL
);
"""


def _jetzt() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


async def vorbereiten() -> None:
    os.makedirs(os.path.dirname(PFAD), exist_ok=True)
    async with aiosqlite.connect(PFAD) as db:
        await db.executescript(SCHEMA)
        await db.commit()
        # Migration fuer bereits bestehende wiki-Tabellen (CREATE TABLE IF NOT
        # EXISTS ergaenzt keine Spalten nachtraeglich) -- SQLite kennt kein
        # ADD COLUMN IF NOT EXISTS, daher Fehler bei bereits vorhandener
        # Spalte einfach ignorieren.
        for anweisung in (
            "ALTER TABLE wiki ADD COLUMN erstellt TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE wiki ADD COLUMN neu INTEGER NOT NULL DEFAULT 0",
        ):
            try:
                await db.execute(anweisung)
                await db.commit()
            except aiosqlite.OperationalError:
                pass
        await _vorlagen_erstbefuellen(db)
        await _vorlagen_pakete_einspielen(db)


async def _vorlagen_pakete_einspielen(db: aiosqlite.Connection) -> None:
    """Spielt fachliche Vorlagen-Pakete (z. B. EMVIA M365) genau EINMAL je
    Instanz ein -- gemerkt in vorlage_paket. Anders als die Erstbefuellung
    auch in bereits genutzte Datenbanken (Pi4), aber spaeter geaenderte oder
    geloeschte Vorlagen kommen bei einem Neustart nicht zurueck. Bereits
    vorhandene IDs werden nie ueberschrieben (INSERT OR IGNORE)."""
    from . import (  # lokal, wie bei der Erstbefuellung
        paket_datenbank_sql_betrieb, paket_emvia_benutzerverwaltung, paket_emvia_betrieb, paket_emvia_endpoint,
        paket_emvia_m365, paket_generatoren,
    )

    for paket in (paket_emvia_m365, paket_emvia_betrieb, paket_emvia_endpoint, paket_generatoren,
                  paket_datenbank_sql_betrieb, paket_emvia_benutzerverwaltung):
        cursor = await db.execute("SELECT 1 FROM vorlage_paket WHERE id = ?", (paket.PAKET_ID,))
        if await cursor.fetchone():
            continue
        jetzt = _jetzt()
        for v in paket.VORLAGEN:
            await db.execute(
                "INSERT OR IGNORE INTO vorlage (id, modul, typ, titel, sprache, inhalt, erstellt, geaendert)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (v["id"], v.get("modul", paket.MODUL), v["typ"], v["titel"], v["sprache"], v["inhalt"], jetzt, jetzt),
            )
        await db.execute("INSERT INTO vorlage_paket (id, eingespielt) VALUES (?,?)", (paket.PAKET_ID, jetzt))
        await db.commit()


# Die urspruengliche Skriptbibliothek war eine statische, nicht editierbare
# Python-Liste (module_katalog.SKRIPTE). Zwei ihrer Support-Eintraege sind
# inhaltlich kein Skript, sondern eine Ticket- bzw. E-Mail-Vorlage -- werden
# bei der Migration entsprechend umetikettiert statt als "skript" zu landen.
_ERSTBEFUELLUNG_TYP_AUSNAHME = {
    "support-ticket-dokumentation": "ticket",
    "support-email-anwendungsupdate": "email",
}


async def _vorlagen_erstbefuellen(db: aiosqlite.Connection) -> None:
    """Migriert die frueher statische Skriptbibliothek einmalig in die
    editierbare vorlage-Tabelle -- nur wenn die Tabelle noch leer ist, damit
    das bei jedem Neustart nicht erneut passiert und spaeter selbst
    angelegte/geloeschte Vorlagen unangetastet bleiben."""
    cursor = await db.execute("SELECT COUNT(*) FROM vorlage")
    (anzahl,) = await cursor.fetchone()
    if anzahl:
        return
    from . import module_katalog  # lokal, um store.py von Fachmodulen unabhaengig zu halten

    jetzt = _jetzt()
    for skript in module_katalog.SKRIPTE:
        typ = _ERSTBEFUELLUNG_TYP_AUSNAHME.get(skript["id"], "skript")
        await db.execute(
            "INSERT INTO vorlage (id, modul, typ, titel, sprache, inhalt, erstellt, geaendert)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (skript["id"], skript["modul"], typ, skript["titel"], skript["sprache"],
             skript["code"], jetzt, jetzt),
        )
    await db.commit()


# --- Sitzungen und Nachrichten ---------------------------------------------

async def sitzung_anlegen(titel: str, modul: str) -> str:
    kennung = str(uuid.uuid4())
    async with aiosqlite.connect(PFAD) as db:
        await db.execute(
            "INSERT INTO sitzungen (id, titel, modul, erstellt, geaendert) VALUES (?,?,?,?,?)",
            (kennung, titel[:120] or "Neue Sitzung", modul, _jetzt(), _jetzt()),
        )
        await db.commit()
    return kennung


async def sitzung_sichern(kennung: str, modul: str, titel: str) -> str:
    """Gibt eine gueltige Sitzungskennung zurueck, legt bei Bedarf an."""
    if kennung:
        async with aiosqlite.connect(PFAD) as db:
            cursor = await db.execute("SELECT 1 FROM sitzungen WHERE id = ?", (kennung,))
            if await cursor.fetchone():
                return kennung
    return await sitzung_anlegen(titel, modul)


async def nachricht_anfuegen(
    sitzung_id: str, rolle: str, inhalt: str, anbieter: str | None = None
) -> None:
    async with aiosqlite.connect(PFAD) as db:
        await db.execute(
            "INSERT INTO nachrichten (sitzung_id, rolle, inhalt, anbieter, zeit)"
            " VALUES (?,?,?,?,?)",
            (sitzung_id, rolle, inhalt, anbieter, _jetzt()),
        )
        await db.execute(
            "UPDATE sitzungen SET geaendert = ? WHERE id = ?", (_jetzt(), sitzung_id)
        )
        await db.commit()


async def verlauf(sitzung_id: str, grenze: int = 20) -> list[dict]:
    """Letzte Nachrichten in richtiger Reihenfolge, fuer den Modellkontext."""
    async with aiosqlite.connect(PFAD) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT rolle, inhalt, anbieter, zeit FROM nachrichten"
            " WHERE sitzung_id = ? ORDER BY id DESC LIMIT ?",
            (sitzung_id, grenze),
        )
        zeilen = await cursor.fetchall()
    return [dict(z) for z in reversed(zeilen)]


async def sitzungen(grenze: int = 50) -> list[dict]:
    async with aiosqlite.connect(PFAD) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, titel, modul, geaendert FROM sitzungen"
            " ORDER BY geaendert DESC LIMIT ?",
            (grenze,),
        )
        return [dict(z) for z in await cursor.fetchall()]


async def sitzung_loeschen(sitzung_id: str) -> None:
    """Loescht eine einzelne Sitzung samt ihrer Nachrichten -- z.B. wenn eine
    fehlgeschlagene/veraltete Unterhaltung nicht mehr im Verlauf auftauchen
    soll. Gleiches Zwei-Schritt-Muster wie alte_sitzungen_loeschen() (siehe
    Begruendung dort zu ON DELETE CASCADE)."""
    async with aiosqlite.connect(PFAD) as db:
        await db.execute("DELETE FROM nachrichten WHERE sitzung_id = ?", (sitzung_id,))
        await db.execute("DELETE FROM sitzungen WHERE id = ?", (sitzung_id,))
        await db.commit()


async def alte_sitzungen_loeschen(tage: int = 7) -> int:
    """Loescht Sitzungen und ihre Nachrichten, die laenger als `tage` nicht
    mehr geaendert wurden (Aufbewahrungsfrist). Nachrichten werden explizit
    mitgeloescht -- SQLites ON DELETE CASCADE greift nur mit
    PRAGMA foreign_keys=ON pro Verbindung, was hier bewusst nicht gesetzt
    wird (gefunden 30.07.2026), daher expliziter Zwei-Schritt-Loeschvorgang."""
    grenze = (datetime.now(timezone.utc) - timedelta(days=tage)).isoformat(timespec="seconds")
    async with aiosqlite.connect(PFAD) as db:
        cursor = await db.execute("SELECT id FROM sitzungen WHERE geaendert < ?", (grenze,))
        alte_ids = [zeile[0] for zeile in await cursor.fetchall()]
        if alte_ids:
            platzhalter = ",".join("?" * len(alte_ids))
            await db.execute(f"DELETE FROM nachrichten WHERE sitzung_id IN ({platzhalter})", alte_ids)
            await db.execute(f"DELETE FROM sitzungen WHERE id IN ({platzhalter})", alte_ids)
            await db.commit()
    return len(alte_ids)


# --- Wiki -------------------------------------------------------------------

async def wiki_schreiben(slug: str, titel: str, modul: str, inhalt: str, wichtig: bool = False) -> None:
    """wichtig=True markiert die Seite als 'neu' -- aber nur bei echter
    Erstanlage. Ein taeglicher Refresh eines schon bekannten Themas soll
    nicht jeden Tag erneut aufblinken."""
    async with aiosqlite.connect(PFAD) as db:
        cursor = await db.execute("SELECT 1 FROM wiki WHERE slug = ?", (slug,))
        vorhanden = await cursor.fetchone()
        if vorhanden:
            await db.execute(
                "UPDATE wiki SET titel=?, modul=?, inhalt=?, geaendert=? WHERE slug=?",
                (titel, modul, inhalt, _jetzt(), slug),
            )
        else:
            await db.execute(
                "INSERT INTO wiki (slug, titel, modul, inhalt, geaendert, erstellt, neu)"
                " VALUES (?,?,?,?,?,?,?)",
                (slug, titel, modul, inhalt, _jetzt(), _jetzt(), 1 if wichtig else 0),
            )
        await db.commit()


async def wiki_liste(modul: str | None = None) -> list[dict]:
    frage = "SELECT slug, titel, modul, geaendert, neu FROM wiki"
    werte: tuple = ()
    if modul and modul != "assistent":
        frage += " WHERE modul = ?"
        werte = (modul,)
    frage += " ORDER BY titel"
    async with aiosqlite.connect(PFAD) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(frage, werte)
        return [dict(z) for z in await cursor.fetchall()]


async def module_mit_neuem_wissen() -> list[str]:
    async with aiosqlite.connect(PFAD) as db:
        cursor = await db.execute("SELECT DISTINCT modul FROM wiki WHERE neu = 1")
        return [zeile[0] for zeile in await cursor.fetchall()]


async def wiki_als_gelesen_markieren(slug: str) -> None:
    async with aiosqlite.connect(PFAD) as db:
        await db.execute("UPDATE wiki SET neu = 0 WHERE slug = ?", (slug,))
        await db.commit()


async def wiki_loeschen(slug: str) -> None:
    async with aiosqlite.connect(PFAD) as db:
        await db.execute("DELETE FROM wiki WHERE slug = ?", (slug,))
        await db.commit()


async def wiki_lesen(slug: str) -> dict | None:
    async with aiosqlite.connect(PFAD) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM wiki WHERE slug = ?", (slug,))
        zeile = await cursor.fetchone()
    return dict(zeile) if zeile else None


# --- Scraper-Verlauf --------------------------------------------------------

async def scraper_lauf_eintragen(thema: str, modul: str, slug: str, status: str) -> None:
    async with aiosqlite.connect(PFAD) as db:
        await db.execute(
            "INSERT INTO scraper_lauf (thema, modul, slug, status, zeit) VALUES (?,?,?,?,?)",
            (thema, modul, slug, status, _jetzt()),
        )
        await db.commit()


async def scraper_lauf_liste(grenze: int = 30) -> list[dict]:
    async with aiosqlite.connect(PFAD) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT thema, modul, slug, status, zeit FROM scraper_lauf"
            " ORDER BY id DESC LIMIT ?",
            (grenze,),
        )
        return [dict(z) for z in await cursor.fetchall()]


# --- Eigene Quellen (CEO traegt selbst entdeckte gute Links ein) ------------

async def quelle_hinzufuegen(url: str, titel: str, modul: str) -> int:
    async with aiosqlite.connect(PFAD) as db:
        cursor = await db.execute(
            "INSERT INTO quellen (url, titel, modul, hinzugefuegt) VALUES (?,?,?,?)"
            " ON CONFLICT(url) DO UPDATE SET titel=excluded.titel, modul=excluded.modul",
            (url, titel, modul, _jetzt()),
        )
        await db.commit()
        return cursor.lastrowid


async def quellen_liste() -> list[dict]:
    async with aiosqlite.connect(PFAD) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM quellen ORDER BY hinzugefuegt DESC")
        return [dict(z) for z in await cursor.fetchall()]


async def quelle_loeschen(quelle_id: int) -> None:
    async with aiosqlite.connect(PFAD) as db:
        await db.execute("DELETE FROM quellen WHERE id = ?", (quelle_id,))
        await db.commit()


# --- Tech-News: RSS-Funde ----------------------------------------------------

async def rss_eintrag_speichern(
    thema: str, quelle_titel: str, titel: str, url: str, veroeffentlicht: str
) -> bool:
    """True, wenn der Eintrag neu war (url noch nicht bekannt), sonst False --
    so zaehlt der Aufrufer nur echte Neufunde, nicht jeden Feed-Eintrag."""
    async with aiosqlite.connect(PFAD) as db:
        cursor = await db.execute(
            "INSERT OR IGNORE INTO rss_eintrag"
            " (thema, quelle_titel, titel, url, veroeffentlicht, gefunden_am)"
            " VALUES (?,?,?,?,?,?)",
            (thema, quelle_titel, titel, url, veroeffentlicht, _jetzt()),
        )
        await db.commit()
        return cursor.rowcount > 0


async def rss_eintraege_liste(grenze: int = 40) -> list[dict]:
    async with aiosqlite.connect(PFAD) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT thema, quelle_titel, titel, url, veroeffentlicht, gefunden_am"
            " FROM rss_eintrag ORDER BY gefunden_am DESC LIMIT ?",
            (grenze,),
        )
        return [dict(z) for z in await cursor.fetchall()]


# --- Vorlagen (Skript-/E-Mail-/Ticket-/Doku-Bausteine je Modul) -------------

async def vorlage_schreiben(
    id_: str, modul: str, typ: str, titel: str, sprache: str, inhalt: str
) -> None:
    """Upsert nach id -- gleiches Muster wie wiki_schreiben()."""
    async with aiosqlite.connect(PFAD) as db:
        cursor = await db.execute("SELECT 1 FROM vorlage WHERE id = ?", (id_,))
        vorhanden = await cursor.fetchone()
        if vorhanden:
            await db.execute(
                "UPDATE vorlage SET modul=?, typ=?, titel=?, sprache=?, inhalt=?, geaendert=?"
                " WHERE id=?",
                (modul, typ, titel, sprache, inhalt, _jetzt(), id_),
            )
        else:
            await db.execute(
                "INSERT INTO vorlage (id, modul, typ, titel, sprache, inhalt, erstellt, geaendert)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (id_, modul, typ, titel, sprache, inhalt, _jetzt(), _jetzt()),
            )
        await db.commit()


async def vorlage_liste(modul: str | None = None, typ: str | None = None) -> list[dict]:
    frage = "SELECT id, modul, typ, titel, sprache, inhalt, geaendert FROM vorlage"
    bedingungen: list[str] = []
    werte: list[str] = []
    if modul and modul != "assistent":
        bedingungen.append("modul = ?")
        werte.append(modul)
    if typ:
        bedingungen.append("typ = ?")
        werte.append(typ)
    if bedingungen:
        frage += " WHERE " + " AND ".join(bedingungen)
    frage += " ORDER BY titel"
    async with aiosqlite.connect(PFAD) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(frage, werte)
        return [dict(z) for z in await cursor.fetchall()]


async def vorlage_lesen(id_: str) -> dict | None:
    async with aiosqlite.connect(PFAD) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM vorlage WHERE id = ?", (id_,))
        zeile = await cursor.fetchone()
    return dict(zeile) if zeile else None


async def vorlage_loeschen(id_: str) -> None:
    async with aiosqlite.connect(PFAD) as db:
        await db.execute("DELETE FROM vorlage WHERE id = ?", (id_,))
        await db.commit()


async def vorlagen_uebersicht() -> list[dict]:
    """Anzahl Vorlagen je (modul, typ), nur Kombinationen mit mindestens einem
    Eintrag -- treibt die Unterkategorien in der Menueleiste."""
    async with aiosqlite.connect(PFAD) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT modul, typ, COUNT(*) AS anzahl FROM vorlage GROUP BY modul, typ"
        )
        return [dict(z) for z in await cursor.fetchall()]
