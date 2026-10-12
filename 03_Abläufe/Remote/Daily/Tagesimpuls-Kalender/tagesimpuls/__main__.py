"""CLI: python -m tagesimpuls <befehl> [--trocken]

  impuls                 Morgen-Impuls (DE/VI) + heutige Termine als Push, optional in Impuls-Kalender
  wecker                 fällige Kalender-Erinnerungen senden (systemd: jede Minute)
  finanz [--art X]       Finanz-/Steuer-Erinnerung (läuft nur am 01.06./01.12., mit --art erzwingen)
  finanztermine-anlegen  jährliche Termine 01.06./01.12. im Google-Kalender anlegen (idempotent)
  ics                    export/Finanz-Erinnerungen.ics schreiben (Sofort-Import ohne Pi)
  vorschau [--tage N]    Impulse der nächsten N Tage anzeigen
  test-push              Testnachricht (Priorität 5) + Ton
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta

from . import benachrichtigung, config, finanz, inhalte, kalender, wecker


def _impuls(cfg, trocken: bool, tag: date | None = None) -> None:
    tag = tag or datetime.now(cfg.zeitzone).date()
    imp = inhalte.impuls(inhalte.lade_inhalte(cfg.inhalte_datei), tag)
    text = inhalte.als_text(imp)
    if cfg.google_aktiv:
        try:
            von = datetime.combine(tag, datetime.min.time(), cfg.zeitzone)
            text = kalender.tages_uebersicht(kalender.termine(cfg, von, von + timedelta(days=1)), cfg) + "\n\n" + text
            if not trocken:
                kalender.impuls_eintragen(cfg, tag, f"🌱 {imp['affirmation']['de']}", text)
        except Exception as fehler:  # Impuls soll auch ohne Kalender ankommen
            text = f"(Kalender gerade nicht erreichbar: {type(fehler).__name__})\n\n{text}"
    benachrichtigung.nachricht(cfg, f"🌞 Guten Morgen – Chào buổi sáng ({tag:%d.%m.})", text,
                               prioritaet=3, tags=["sunny"], trocken=trocken)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="tagesimpuls")
    p.add_argument("befehl", choices=["impuls", "wecker", "finanz", "finanztermine-anlegen", "ics", "vorschau", "test-push"])
    p.add_argument("--trocken", action="store_true", help="nichts senden/schreiben, nur anzeigen")
    p.add_argument("--art", choices=["juni", "dezember"])
    p.add_argument("--tage", type=int, default=3)
    a = p.parse_args(argv)
    cfg = config.lade()
    heute = datetime.now(cfg.zeitzone).date()

    if a.befehl == "impuls":
        _impuls(cfg, a.trocken)
    elif a.befehl == "wecker":
        if not cfg.google_aktiv:
            print("Google-Kalender nicht eingerichtet (GOOGLE_SA_DATEI/KALENDER_IDS).", file=sys.stderr)
            return 2
        print(f"{wecker.lauf(cfg, trocken=a.trocken)} Erinnerung(en) gesendet")
    elif a.befehl == "finanz":
        art = a.art or finanz.art_fuer_tag(heute)
        if not art:
            print("Heute kein Finanz-Termin (nur 01.06./01.12.).")
            return 0
        c = finanz.CHECKLISTE[art]
        benachrichtigung.nachricht(cfg, c["titel"], "\n".join(c["text"]), prioritaet=5, tags=["moneybag"],
                                   links=finanz.links(cfg), klick=cfg.finanzplan_url, trocken=a.trocken)
        benachrichtigung.ton(cfg, trocken=a.trocken)
    elif a.befehl == "finanztermine-anlegen":
        for zeile in finanz_anlegen(cfg, heute, a.trocken):
            print(zeile)
    elif a.befehl == "ics":
        ziel = config.PROJEKT / "export" / "Finanz-Erinnerungen.ics"
        ziel.write_text(finanz.ics(cfg, heute), encoding="utf-8", newline="")
        print(f"geschrieben: {ziel}")
    elif a.befehl == "vorschau":
        for i in range(a.tage):
            _impuls(cfg, trocken=True, tag=heute + timedelta(days=i))
    elif a.befehl == "test-push":
        benachrichtigung.nachricht(cfg, "⏰ Test-Wecker", "Wenn du das hörst, funktioniert der Alarm. 🎉\nNếu bạn nghe thấy, báo thức đã hoạt động.",
                                   prioritaet=5, tags=["alarm_clock"], trocken=a.trocken)
        benachrichtigung.ton(cfg, trocken=a.trocken)
    return 0


def finanz_anlegen(cfg, heute: date, trocken: bool) -> list[str]:
    defs = finanz.termin_definitionen(cfg, heute)
    if trocken or not cfg.google_aktiv:
        return [f"[TROCKEN] würde anlegen: {d['titel']} ab {d['erster_termin']:%d.%m.%Y}, jährlich 09:00" for d in defs]
    return kalender.finanztermine_anlegen(cfg, defs)


if __name__ == "__main__":
    sys.exit(main())
