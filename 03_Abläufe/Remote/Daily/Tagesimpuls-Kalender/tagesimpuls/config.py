"""Einstellungen aus .env (neben dem Projektordner) bzw. Umgebungsvariablen.

Keine Secrets im Code: Service-Account-Datei und ntfy-Topic stehen nur in .env (nicht versioniert).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from zoneinfo import ZoneInfo

PROJEKT = Path(__file__).resolve().parent.parent


def _lade_env(pfad: Path) -> None:
    if not pfad.exists():
        return
    for zeile in pfad.read_text(encoding="utf-8").splitlines():
        zeile = zeile.strip()
        if not zeile or zeile.startswith("#") or "=" not in zeile:
            continue
        k, v = zeile.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _liste(wert: str) -> list[str]:
    return [x.strip() for x in wert.split(",") if x.strip()]


@dataclass
class Config:
    zeitzone: ZoneInfo
    ntfy_server: str
    ntfy_topic: str
    ntfy_token: str
    kalender_ids: list[str]
    impuls_kalender_id: str
    google_sa_datei: str
    wecker_standard_min: list[int]
    alarm_woerter: list[str]
    ton_auf_pi: bool
    ton_wiederholungen: int
    wiso_url: str
    elster_url: str
    finanzplan_url: str
    zustand_datei: Path
    inhalte_datei: Path = field(default=PROJEKT / "daten" / "inhalte.json")

    @property
    def google_aktiv(self) -> bool:
        return bool(self.google_sa_datei) and Path(self.google_sa_datei).exists() and bool(self.kalender_ids)


def lade() -> Config:
    _lade_env(PROJEKT / ".env")
    e = os.environ.get
    return Config(
        zeitzone=ZoneInfo(e("ZEITZONE", "Europe/Berlin")),
        ntfy_server=e("NTFY_SERVER", "https://ntfy.sh").rstrip("/"),
        ntfy_topic=e("NTFY_TOPIC", ""),
        ntfy_token=e("NTFY_TOKEN", ""),
        kalender_ids=_liste(e("KALENDER_IDS", "")),
        impuls_kalender_id=e("IMPULS_KALENDER_ID", ""),
        google_sa_datei=e("GOOGLE_SA_DATEI", ""),
        wecker_standard_min=[int(x) for x in _liste(e("WECKER_STANDARD_MIN", "30,10"))],
        alarm_woerter=[w.lower() for w in _liste(e("ALARM_WOERTER", "⏰,wecker,alarm,!!"))],
        ton_auf_pi=e("TON_AUF_PI", "0") == "1",
        ton_wiederholungen=int(e("TON_WIEDERHOLUNGEN", "3")),
        wiso_url=e("WISO_URL", "https://www.wiso.de"),
        elster_url=e("ELSTER_URL", "https://www.elster.de"),
        finanzplan_url=e("FINANZPLAN_URL", "https://drive.google.com/drive/search?q=Finanzplan"),
        zustand_datei=Path(e("ZUSTAND_DATEI", str(Path.home() / ".local/state/tagesimpuls/zustand.json"))),
    )
