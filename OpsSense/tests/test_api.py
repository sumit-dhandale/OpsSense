from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_search_requires_query():
    assert client.post("/search", json={}).status_code == 422


def test_ask_requires_query():
    assert client.post("/ask", json={}).status_code == 422


def test_top_k_rejected_when_too_large():
    r = client.post(
        "/search",
        json={"query": "timeout", "top_k": 100},
    )
    assert r.status_code == 422


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert "status" in body
    assert "embedding_model" in body


def test_search_vector_happy_path():
    fake = [
        {
            "score": 0.9,
            "incident_id": "INC-1",
            "title": "t",
            "service": "fraud",
            "severity": "SEV1",
            "chunk_index": 0,
            "chunk_id": "INC-1:0",
            "text": "body",
        }
    ]
    with patch("src.api.main.vector_search", return_value=fake):
        r = client.post("/search", json={"query": "timeout", "mode": "vector"})
    assert r.status_code == 200
    assert r.json()["results"][0]["incident_id"] == "INC-1"


def test_ask_llm_unreachable_returns_503():
    with patch(
        "src.api.main.rag_ask",
        side_effect=RuntimeError("Ollama is not reachable"),
    ):
        r = client.post("/ask", json={"query": "why timeout?"})
    assert r.status_code == 503
