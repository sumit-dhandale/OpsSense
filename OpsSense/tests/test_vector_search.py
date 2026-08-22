import socket

import pytest

from src.qdrant_store import get_client
from src.retrieval.vector_search import search


def indexed() -> bool:
    try:
        socket.create_connection(("127.0.0.1", 6333), timeout=0.4).close()
        info = get_client().get_collection("incident_memory")
        return (info.points_count or 0) > 0
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not indexed(), reason="collection not indexed")


def test_vector_search_aerospike():
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
