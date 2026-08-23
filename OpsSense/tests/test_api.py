from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_search_requires_query():
    assert client.post("/search", json={}).status_code == 422


def test_ask_requires_query():
    assert client.post("/ask", json={}).status_code == 422
