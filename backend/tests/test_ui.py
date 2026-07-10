from fastapi.testclient import TestClient


def test_root_redirects_to_ui(client: TestClient) -> None:
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/ui"


def test_ui_serves_hermes_page(client: TestClient) -> None:
    response = client.get("/ui")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Hermes" in response.text
    assert "/api/hermes/ask" in response.text
