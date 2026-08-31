import pytest
from qdrant_client.models import Distance

from src.deps import get_embedder
from src.qdrant_store import collection_info, ensure_collection

pytestmark = pytest.mark.integration


def test_collection_cosine_384(qdrant_up):
    client = ensure_collection()
    info = collection_info(client)
    params = info.config.params.vectors
    assert params.size == get_embedder().dim
    assert params.distance == Distance.COSINE
