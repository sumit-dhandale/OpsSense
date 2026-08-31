import pytest

from src.ingestion.indexer import index_documents
from src.qdrant_store import collection_info, get_client
from src.settings import get_settings

pytestmark = pytest.mark.integration


def test_index_writes_points_with_payload(qdrant_up):
    n = index_documents(recreate=True)
    assert n >= 15
    info = collection_info()
    assert info.points_count == n
    settings = get_settings()
    recs, _ = get_client().scroll(
        settings.qdrant_collection, limit=1, with_payload=True
    )
    payload = recs[0].payload or {}
    for key in (
        "incident_id",
        "title",
        "date",
        "service",
        "severity",
        "section",
        "chunk_index",
        "text",
        "parent_text",
    ):
        assert key in payload
