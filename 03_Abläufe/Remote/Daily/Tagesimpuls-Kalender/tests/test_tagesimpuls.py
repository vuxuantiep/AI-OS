"""Tests ohne Netz und ohne Google: python -m pytest tests -q"""
from datetime import date, datetime, timedelta

from tagesimpuls import config, finanz, inhalte, wecker

CFG = config.lade()
CFG.ntfy_topic = ""  # niemals echt senden


def test_alle_eintraege_zweisprachig():
    daten = inhalte.lade_inhalte(CFG.inhalte_datei)
    for kat, liste in daten.items():
        assert len(liste) >= 10, kat
        for e in liste:
            texte = [v for k, v in e.items() if k.endswith("de") or k.endswith("vi") or k in ("de", "vi")]
            assert all(t.strip() for t in texte), (kat, e)
            assert any(k.endswith("vi") or k == "vi" for k in e), (kat, e)


def test_keine_wiederholung_innerhalb_einer_runde():
    daten = inhalte.lade_inhalte(CFG.inhalte_datei)
    liste = daten["wortwahl"]
    tage = [date(2027, 1, 1) + timedelta(days=i) for i in range(len(liste))]
    gewaehlt = [inhalte.eintrag_fuer_tag(liste, t, "wortwahl")["besser_de"] for t in tage]
    assert len(set(gewaehlt)) == len(liste)


def test_impulstext_enthaelt_alle_teile():
    text = inhalte.als_text(inhalte.impuls(inhalte.lade_inhalte(CFG.inhalte_datei), date(2026, 10, 13)))
    for marke in ("Sprichwort", "Wortwahl", "EQ-Übung", "Witz", "🇻🇳"):
        assert marke in text


def _ev(start: datetime, titel="Zahnarzt", overrides=None, farbe=None):
    ev = {"id": "e1", "summary": titel, "start": {"dateTime": start.isoformat()},
          "reminders": {"useDefault": overrides is None, "overrides": overrides or []}}
    if farbe:
        ev["colorId"] = farbe
    return ev


def test_wecker_standard_vorlauf_und_einmalig():
    jetzt = datetime(2026, 10, 13, 9, 50, tzinfo=CFG.zeitzone)
    ev = _ev(jetzt + timedelta(minutes=10))
    treffer = wecker.faellige([ev], CFG, jetzt, set())
    assert [m for _, m, _ in treffer] == [10]
    assert wecker.faellige([ev], CFG, jetzt, {treffer[0][2]}) == []


def test_wecker_nachholfenster_und_email_ignoriert():
    start = datetime(2026, 12, 1, 9, 0, tzinfo=CFG.zeitzone)
    ev = _ev(start, overrides=[{"method": "popup", "minutes": 0}, {"method": "email", "minutes": 10080}])
    assert wecker.faellige([ev], CFG, start + timedelta(minutes=3), set())
    assert not wecker.faellige([ev], CFG, start + timedelta(minutes=6), set())
    assert not wecker.faellige([ev], CFG, start - timedelta(minutes=10080), set())


def test_alarm_erkennung():
    from tagesimpuls import kalender
    jetzt = datetime(2026, 10, 13, 6, 0, tzinfo=CFG.zeitzone)
    assert kalender.ist_alarm(_ev(jetzt, "⏰ Aufstehen"), CFG)
    assert kalender.ist_alarm(_ev(jetzt, "Steuer", farbe="11"), CFG)
    assert not kalender.ist_alarm(_ev(jetzt, "Kaffee mit Anna"), CFG)


def test_finanz_tage_und_ics():
    assert finanz.art_fuer_tag(date(2027, 6, 1)) == "juni"
    assert finanz.art_fuer_tag(date(2026, 12, 1)) == "dezember"
    assert finanz.art_fuer_tag(date(2026, 12, 2)) is None
    defs = finanz.termin_definitionen(CFG, date(2026, 10, 12))
    assert [d["erster_termin"] for d in defs] == [date(2027, 6, 1), date(2026, 12, 1)]
    ics = finanz.ics(CFG, date(2026, 10, 12))
    assert ics.count("BEGIN:VEVENT") == 2 and "RRULE:FREQ=YEARLY" in ics and "wiso.de" in ics
