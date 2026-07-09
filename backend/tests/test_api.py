from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_endpoint(client: TestClient) -> None:
    response = client.post("/api/chat", json={"message": "Hallo AI-OS"})
    assert response.status_code == 200
    body = response.json()
    assert "Hallo AI-OS" in body["answer"]
    assert body["model"] == "fake-model"


def test_chat_validation_rejects_empty_message(client: TestClient) -> None:
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422


def test_upload_and_rag_query(client: TestClient) -> None:
    content = (
        "Das AI-OS ist eine AI Engineering Platform.\n\n"
        "Der Vector Store speichert Embeddings als JSON.\n\n"
        "LangGraph orchestriert die Agenten der KI-Fabrik."
    )
    upload = client.post(
        "/api/documents/upload",
        files={"file": ("wissen.txt", content.encode("utf-8"), "text/plain")},
    )
    assert upload.status_code == 200
    assert upload.json()["num_chunks"] >= 1

    documents = client.get("/api/documents")
    assert len(documents.json()) == 1

    query = client.post(
        "/api/rag/query",
        json={"question": "Was speichert der Vector Store?", "top_k": 2},
    )
    assert query.status_code == 200
    body = query.json()
    assert body["answer"].startswith("ANTWORT")
    assert len(body["sources"]) >= 1
    # Der relevanteste Chunk muss der Vector-Store-Absatz sein
    assert "Vector Store" in body["sources"][0]["text"]


def test_upload_unsupported_format(client: TestClient) -> None:
    response = client.post(
        "/api/documents/upload",
        files={"file": ("bild.png", b"\x89PNG", "image/png")},
    )
    assert response.status_code == 422


def test_agent_pipeline(client: TestClient) -> None:
    response = client.post("/api/agents/run", json={"message": "Baue eine Login-Seite"})
    assert response.status_code == 200
    body = response.json()
    assert [step["role"] for step in body["steps"]] == ["Planner", "Developer", "Reviewer"]
    assert body["final"]
