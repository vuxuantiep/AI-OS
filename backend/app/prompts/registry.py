"""Prompt Registry — verwaltet das Prompt-Repository als Kanban-Board.

Jeder Prompt ist eine Markdown-Datei im Prompt-Verzeichnis. Board-Status,
Version und Tags leben als YAML-Frontmatter IN der Datei selbst — das Board
ist nur eine Sicht darauf. Dateien ohne Frontmatter (Alt-Bestand) werden als
"backlog" einsortiert und beim ersten Update automatisch migriert.

Das ist Modul 4 ("Prompt Registry") des AI-Engineering-Lernkonzepts:
Prompts nicht im Code verstreuen, sondern versioniert und mit Freigabe-Status
zentral pflegen.
"""

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

PromptStatus = Literal["backlog", "entwurf", "test", "freigegeben"]
STATUSES: tuple[PromptStatus, ...] = ("backlog", "entwurf", "test", "freigegeben")

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_SLUG_RE = re.compile(r"[^a-z0-9äöüß]+")


class PromptCard(BaseModel):
    name: str
    title: str
    status: PromptStatus = "backlog"
    version: int = 1
    tags: list[str] = Field(default_factory=list)
    updated: datetime | None = None


class PromptDetail(PromptCard):
    content: str


class PromptCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = ""
    status: PromptStatus = "backlog"
    tags: list[str] = Field(default_factory=list)


class PromptUpdate(BaseModel):
    content: str | None = None
    status: PromptStatus | None = None
    tags: list[str] | None = None


def _slugify(title: str) -> str:
    slug = _SLUG_RE.sub("-", title.lower()).strip("-")
    return slug or "prompt"


def _split_frontmatter(text: str) -> tuple[dict[str, object], str]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}, text
    if not isinstance(data, dict):
        return {}, text
    return data, text[match.end() :]


def _first_heading(body: str, fallback: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    return fallback


class PromptRegistry:
    def __init__(self, directory: Path) -> None:
        self._dir = directory
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        # Kein Pfad-Escape: Name muss eine flache .md-Datei im Verzeichnis sein
        candidate = (self._dir / f"{name}.md").resolve()
        if candidate.parent != self._dir.resolve():
            raise ValueError(f"Ungültiger Prompt-Name: {name}")
        return candidate

    def _read(self, path: Path) -> PromptDetail:
        raw = path.read_text(encoding="utf-8")
        meta, body = _split_frontmatter(raw)
        status = str(meta.get("status", "backlog"))
        raw_tags = meta.get("tags", [])
        tags = [str(tag) for tag in raw_tags] if isinstance(raw_tags, list) else []
        updated_raw = meta.get("updated")
        updated: datetime | None = None
        if isinstance(updated_raw, datetime):
            updated = updated_raw
        elif isinstance(updated_raw, str):
            try:
                updated = datetime.fromisoformat(updated_raw)
            except ValueError:
                updated = None
        if updated is None:
            updated = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
        try:
            version = int(str(meta.get("version", 1)))
        except ValueError:
            version = 1
        return PromptDetail(
            name=path.stem,
            title=str(meta.get("title", "")) or _first_heading(body, path.stem),
            status=status if status in STATUSES else "backlog",
            version=version,
            tags=tags,
            updated=updated,
            content=body.strip(),
        )

    def _write(self, name: str, detail: PromptDetail) -> None:
        meta = {
            "title": detail.title,
            "status": detail.status,
            "version": detail.version,
            "tags": detail.tags,
            "updated": datetime.now(UTC).isoformat(timespec="seconds"),
        }
        frontmatter = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).strip()
        self._path(name).write_text(
            f"---\n{frontmatter}\n---\n\n{detail.content.strip()}\n", encoding="utf-8"
        )

    def list(self) -> list[PromptCard]:
        cards = [
            PromptCard(**self._read(path).model_dump(exclude={"content"}))
            for path in sorted(self._dir.glob("*.md"))
        ]
        cards.sort(key=lambda card: card.updated or datetime.min.replace(tzinfo=UTC), reverse=True)
        return cards

    def get(self, name: str) -> PromptDetail | None:
        path = self._path(name)
        if not path.is_file():
            return None
        return self._read(path)

    def create(self, data: PromptCreate) -> PromptDetail:
        name = _slugify(data.title)
        if self._path(name).exists():
            name = f"{name}-{datetime.now(UTC).strftime('%H%M%S')}"
        detail = PromptDetail(
            name=name,
            title=data.title,
            status=data.status,
            version=1,
            tags=data.tags,
            updated=datetime.now(UTC),
            content=data.content or f"# {data.title}\n",
        )
        self._write(name, detail)
        return self._read(self._path(name))

    def update(self, name: str, data: PromptUpdate) -> PromptDetail | None:
        existing = self.get(name)
        if existing is None:
            return None
        content_changed = data.content is not None and data.content.strip() != existing.content
        detail = PromptDetail(
            name=name,
            title=existing.title,
            status=data.status or existing.status,
            version=existing.version + 1 if content_changed else existing.version,
            tags=data.tags if data.tags is not None else existing.tags,
            updated=datetime.now(UTC),
            content=data.content if data.content is not None else existing.content,
        )
        self._write(name, detail)
        return self._read(self._path(name))
