"""Dokumenten-Parsing: PDF, DOCX, Markdown/Text → Klartext."""

import io
from pathlib import PurePosixPath

from pypdf import PdfReader

TEXT_SUFFIXES = {".txt", ".md", ".markdown", ".csv", ".json", ".py", ".html"}


class UnsupportedFormatError(ValueError):
    pass


def parse_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def parse_docx(data: bytes) -> str:
    from docx import Document

    document = Document(io.BytesIO(data))
    return "\n\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text)


def parse_text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def parse_bytes(filename: str, data: bytes) -> str:
    """Wählt den Parser anhand der Dateiendung."""
    suffix = PurePosixPath(filename.lower()).suffix
    if suffix == ".pdf":
        return parse_pdf(data)
    if suffix == ".docx":
        return parse_docx(data)
    if suffix in TEXT_SUFFIXES:
        return parse_text(data)
    raise UnsupportedFormatError(f"Nicht unterstütztes Format: {suffix or filename}")
