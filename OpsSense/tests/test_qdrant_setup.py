import socket

import pytest
from qdrant_client.models import Distance

from src.qdrant_store import collection_info, ensure_collection, get_client


def qdrant_up() -> bool:
    try:
        socket.create_connection(("127.0.0.1", 6333), timeout=0.4).close()
    except OSError:
        return False
    try:
        get_client().get_collections()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not qdrant_up(), reason="Qdrant not running")


def test_collection_cosine_384():
    client = ensure_collection()
    info = collection_info(client)
    params = info.config.params.vectors
    assert params.size == 384
    assert params.distance == Distance.COSINE
