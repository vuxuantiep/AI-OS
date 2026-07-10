from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.prompts.registry import PromptCreate, PromptRegistry, PromptUpdate


@pytest.fixture
def registry(tmp_path: Path) -> PromptRegistry:
    return PromptRegistry(tmp_path / "prompts")


def test_create_and_read(registry: PromptRegistry) -> None:
    detail = registry.create(PromptCreate(title="Login-Seite bauen", tags=["web"]))
    assert detail.name == "login-seite-bauen"
    assert detail.status == "backlog"
    assert detail.version == 1
    assert registry.get(detail.name) is not None


def test_status_change_keeps_version(registry: PromptRegistry) -> None:
    created = registry.create(PromptCreate(title="Test-Prompt", content="# Test\n\nInhalt"))
    updated = registry.update(created.name, PromptUpdate(status="freigegeben"))
    assert updated is not None
    assert updated.status == "freigegeben"
    assert updated.version == 1  # Nur Status verschoben: keine neue Version


def test_content_change_bumps_version(registry: PromptRegistry) -> None:
    created = registry.create(PromptCreate(title="Versionierung"))
    updated = registry.update(created.name, PromptUpdate(content="# Neu\n\nGeänderter Text"))
    assert updated is not None
    assert updated.version == 2


def test_legacy_file_without_frontmatter(registry: PromptRegistry, tmp_path: Path) -> None:
    legacy = tmp_path / "prompts" / "alt-prompt.md"
    legacy.write_text("# Alter Prompt\n\nOhne Frontmatter.", encoding="utf-8")

    cards = registry.list()
    assert [card.name for card in cards].count("alt-prompt") == 1
    card = next(c for c in cards if c.name == "alt-prompt")
    assert card.status == "backlog"
    assert card.title == "Alter Prompt"

    # Nach einem Update ist die Datei migriert (Frontmatter vorhanden)
    registry.update("alt-prompt", PromptUpdate(status="entwurf"))
    assert legacy.read_text(encoding="utf-8").startswith("---")


def test_path_escape_is_rejected(registry: PromptRegistry) -> None:
    with pytest.raises(ValueError):
        registry.get("../../etc/passwd")


def test_board_api(client: TestClient) -> None:
    created = client.post(
        "/api/prompts",
        json={"title": "API Prompt", "content": "# API Prompt", "tags": ["api"]},
    )
    assert created.status_code == 201
    name = created.json()["name"]

    moved = client.patch(f"/api/prompts/{name}", json={"status": "test"})
    assert moved.status_code == 200
    assert moved.json()["status"] == "test"

    cards = client.get("/api/prompts").json()
    assert any(card["name"] == name and card["status"] == "test" for card in cards)

    assert client.get("/api/prompts/gibt-es-nicht").status_code == 404
    assert client.get("/prompts").status_code == 200
    assert "Prompt-Board" in client.get("/prompts").text
