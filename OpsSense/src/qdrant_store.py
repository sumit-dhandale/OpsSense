from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams

from src.config import COLLECTION, QDRANT_URL, VECTOR_SIZE


def get_client(url: str | None = None) -> QdrantClient:
    return QdrantClient(
        url=url or QDRANT_URL,
        timeout=5,
        prefer_grpc=False,
        check_compatibility=False,
    )


def ensure_collection(
    client: QdrantClient | None = None,
    collection: str | None = None,
    vector_size: int = VECTOR_SIZE,
    recreate: bool = False,
) -> QdrantClient:
    """Create collection with cosine distance if missing."""
    client = client or get_client()
    name = collection or COLLECTION
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
    client = client or get_client()
    name = collection or COLLECTION
    try:
        return client.get_collection(name)
    except UnexpectedResponse:
        return None
