import socket

import pytest

from src.config import COLLECTION
from src.ingestion.indexer import index_documents
from src.qdrant_store import collection_info, get_client


def qdrant_up() -> bool:
    try:
        socket.create_connection(("127.0.0.1", 6333), timeout=0.4).close()
        get_client().get_collections()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not qdrant_up(), reason="Qdrant not running")


def test_index_writes_points_with_payload():
    n = index_documents()
    assert n >= 15
    info = collection_info()
    assert info.points_count == n
    recs, _ = get_client().scroll(COLLECTION, limit=1, with_payload=True)
    payload = recs[0].payload or {}
    for key in ("incident_id", "title", "service", "severity", "chunk_index", "text"):
        assert key in payload
