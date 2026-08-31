import pytest

from src.retrieval.vector_search import search

pytestmark = pytest.mark.integration


def test_vector_search_aerospike(indexed_collection):
    hits = search(
        "Fraud feature lookups are timing out because Aerospike is responding slowly.",
        top_k=5,
    )
    assert hits
    ids = {h["incident_id"] for h in hits}
    assert ids & {"INC-2841", "INC-1923", "INC-1407", "INC-1744"}
    assert "score" in hits[0]
    assert hits[0]["title"] and hits[0]["text"]
    scores = [h["score"] for h in hits]
    assert scores == sorted(scores, reverse=True)


def test_metadata_filter_narrows_service_and_severity(indexed_collection):
    query = "Aerospike timeout"
    filtered = search(
        query, top_k=8, filters={"service": "fraud", "severity": "SEV1"}
    )
    assert filtered
    assert all(h["service"] == "fraud" and h["severity"] == "SEV1" for h in filtered)
    assert all(h["incident_id"] != "INC-1923" for h in filtered)
