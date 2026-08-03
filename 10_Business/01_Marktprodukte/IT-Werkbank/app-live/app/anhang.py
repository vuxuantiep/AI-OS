"""
Anhang-Verarbeitung fuer den Chat.

Extrahiert Text aus hochgeladenen Dateien (Dokumente, ZIP), damit der
Assistent sie im Chatkontext nutzen kann -- die Chat-API selbst bleibt
reines JSON, der Anhangtext wird vom Frontend vor die eigentliche Frage
gesetzt (siehe web/index.html: anhaengeVerarbeiten()).

Bilder werden aktuell nur benannt, nicht inhaltlich analysiert -- es ist
keine Bildanalyse (Vision-Modell) angebunden. Ehrlicher Hinweis statt
stillschweigendem Weglassen.
"""

from __future__ import annotations

import io
import zipfile

import pypdf
from docx import Document

MAX_ZEICHEN_PRO_DATEI = 20_000
MAX_DATEIEN_IM_ZIP = 20

TEXT_ENDUNGEN = (".txt", ".md", ".csv", ".json", ".yaml", ".yml")
BILD_ENDUNGEN = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")


def _pdf_text(daten: bytes) -> str:
    leser = pypdf.PdfReader(io.BytesIO(daten))
    return "\n\n".join(seite.extract_text() or "" for seite in leser.pages)


def _docx_text(daten: bytes) -> str:
    dokument = Document(io.BytesIO(daten))
    return "\n".join(absatz.text for absatz in dokument.paragraphs)


def _zip_text(daten: bytes) -> str:
    teile: list[str] = []
    with zipfile.ZipFile(io.BytesIO(daten)) as archiv:
        for info in archiv.infolist()[:MAX_DATEIEN_IM_ZIP]:
            if info.is_dir():
                continue
            inhalt = archiv.read(info)
            text = datei_text(info.filename, inhalt)
            if text:
                teile.append(f"[{info.filename}]\n{text[:MAX_ZEICHEN_PRO_DATEI]}")
    return "\n\n".join(teile)


def datei_text(name: str, daten: bytes) -> str:
    """Extrahiert Text aus einer Datei anhand ihrer Endung."""
    tief = name.lower()
    try:
        if tief.endswith(".pdf"):
            return _pdf_text(daten)[:MAX_ZEICHEN_PRO_DATEI]
        if tief.endswith(".docx"):
            return _docx_text(daten)[:MAX_ZEICHEN_PRO_DATEI]
        if tief.endswith(".zip"):
            return _zip_text(daten)[:MAX_ZEICHEN_PRO_DATEI]
        if tief.endswith(TEXT_ENDUNGEN):
            return daten.decode("utf-8", errors="replace")[:MAX_ZEICHEN_PRO_DATEI]
        if tief.endswith(BILD_ENDUNGEN):
            return "(Bild angehängt -- Inhalt wird aktuell nicht automatisch analysiert, keine Bildanalyse angebunden.)"
    except Exception as fehler:
        return f"(Datei konnte nicht gelesen werden: {type(fehler).__name__})"
    return "(Dateiformat wird nicht unterstützt.)"
