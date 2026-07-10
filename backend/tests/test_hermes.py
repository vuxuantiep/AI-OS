from fastapi.testclient import TestClient


def test_learn_is_idempotent(client: TestClient) -> None:
    first = client.post("/api/hermes/learn")
    assert first.status_code == 200
    body = first.json()
    assert sorted(body["learned"]) == ["CLAUDE.md", "ROADMAP.md"]
    assert body["missing"] == ["FEHLT.md"]

    # Zweiter Aufruf: nichts wird doppelt eingelesen
    second = client.post("/api/hermes/learn").json()
    assert second["learned"] == []
    assert sorted(second["skipped"]) == ["CLAUDE.md", "ROADMAP.md"]


def test_ask_uses_project_knowledge(client: TestClient) -> None:
    client.post("/api/hermes/learn")
    response = client.post(
        "/api/hermes/ask",
        json={"question": "Was ist Phase 4 der Roadmap?", "top_k": 1},
    )
    assert response.status_code == 200
    body = response.json()
    # Der relevanteste Chunk muss aus der Roadmap kommen
    assert body["sources"][0]["filename"] == "ROADMAP.md"
    assert "LangGraph" in body["sources"][0]["text"]


def test_work_runs_pipeline_and_learns_journal(client: TestClient) -> None:
    client.post("/api/hermes/learn")
    response = client.post(
        "/api/hermes/work",
        json={"message": "Bereite die LangGraph Migration der Roadmap vor"},
    )
    assert response.status_code == 200
    body = response.json()
    assert [step["role"] for step in body["steps"]] == ["Planner", "Developer", "Reviewer"]
    assert body["context_sources"], "Hermes muss Projektkontext geholt haben"
    assert body["journal_filename"].startswith("hermes_journal")

    # Das Journal ist jetzt Teil seines Wissens
    status = client.get("/api/hermes/status").json()
    assert status["journal_entries"] == 1
    assert body["journal_filename"] in status["known_documents"]


def test_status_before_learning(client: TestClient) -> None:
    status = client.get("/api/hermes/status").json()
    assert status["name"] == "Hermes"
    assert status["known_documents"] == []
    assert status["journal_entries"] == 0
