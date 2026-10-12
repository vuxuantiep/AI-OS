"""Push aufs Handy über ntfy (JSON-Veröffentlichung = UTF-8-sicher für Vietnamesisch/Emoji)
und optional ein Alarmton direkt am Raspberry Pi (aplay, Lautsprecher an Klinke/USB/HDMI).

ntfy-Prioritäten: 3 = normal, 4 = hoch (Ton + Vibration), 5 = max (Pop-up, lange Vibration;
in der Android-App unter Einstellungen „Bei Max-Priorität dauerhaft alarmieren“ = Wecker-Verhalten).
"""
from __future__ import annotations

import json
import math
import shutil
import struct
import subprocess
import urllib.request
import wave
from pathlib import Path

from .config import PROJEKT, Config


def nachricht(cfg: Config, titel: str, text: str, prioritaet: int = 3,
              tags: list[str] | None = None, links: list[tuple[str, str]] | None = None,
              klick: str = "", trocken: bool = False) -> dict:
    payload = {
        "topic": cfg.ntfy_topic,
        "title": titel,
        "message": text,
        "priority": prioritaet,
        "tags": tags or [],
    }
    if links:
        payload["actions"] = [{"action": "view", "label": l, "url": u, "clear": False} for l, u in links[:3]]
    if klick:
        payload["click"] = klick
    if trocken or not cfg.ntfy_topic:
        print(f"[TROCKEN] ntfy P{prioritaet}: {titel}\n{text}\n{payload.get('actions', '')}\n")
        return payload
    req = urllib.request.Request(cfg.ntfy_server, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    if cfg.ntfy_token:
        req.add_header("Authorization", f"Bearer {cfg.ntfy_token}")
    with urllib.request.urlopen(req, timeout=15) as r:
        r.read()
    return payload


def _alarm_wav() -> Path:
    """Erzeugt einmalig einen Wecker-Ton (3 Pieptöne, 880 Hz) ohne externe Abhängigkeiten."""
    pfad = PROJEKT / "daten" / "alarm.wav"
    if pfad.exists():
        return pfad
    rate, frames = 22050, bytearray()
    for _ in range(3):
        for i in range(int(rate * 0.25)):
            frames += struct.pack("<h", int(14000 * math.sin(2 * math.pi * 880 * i / rate)))
        frames += b"\x00\x00" * int(rate * 0.15)
    with wave.open(str(pfad), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))
    return pfad


def ton(cfg: Config, wiederholungen: int | None = None, trocken: bool = False) -> None:
    if not cfg.ton_auf_pi:
        return
    if trocken or not shutil.which("aplay"):
        print("[TROCKEN] Ton am Pi (aplay fehlt oder Trockenlauf)")
        return
    wav = _alarm_wav()
    for _ in range(wiederholungen or cfg.ton_wiederholungen):
        subprocess.run(["aplay", "-q", str(wav)], check=False, timeout=10)
