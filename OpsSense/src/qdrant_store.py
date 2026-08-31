from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams

from src.deps import get_client as _get_cached_client
from src.settings import get_settings


def get_client(url: str | None = None) -> QdrantClient:
    if url is not None:
        from qdrant_client import QdrantClient as QC

        return QC(
            url=url,
            timeout=5,
            prefer_grpc=False,
            check_compatibility=False,
        )
    return _get_cached_client()


def ensure_collection(
    client: QdrantClient | None = None,
    collection: str | None = None,
    vector_size: int | None = None,
    recreate: bool = False,
) -> QdrantClient:
    """Create collection with cosine distance if missing."""
    settings = get_settings()
    client = client or get_client()
    name = collection or settings.qdrant_collection
    if vector_size is None:
        from src.deps import get_embedder

        vector_size = get_embedder().dim
    exists = client.collection_exists(name)
    if exists and recreate:
        client.delete_collection(name)
        exists = False
    if not exists:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
    return client


def collection_info(client: QdrantClient | None = None, collection: str | None = None):
    settings = get_settings()
    client = client or get_client()
    name = collection or settings.qdrant_collection
    try:
        return client.get_collection(name)
    except UnexpectedResponse:
        return None
