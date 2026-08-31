"""Cached singletons for expensive resources."""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from qdrant_client import QdrantClient

from src.settings import get_settings

if TYPE_CHECKING:
    from src.embeddings.embedder import Embedder
    from src.retrieval.keyword_search import KeywordIndex
    from src.retrieval.reranker import Reranker

_keyword_index: KeywordIndex | None = None
_keyword_index_collection: str | None = None


@functools.lru_cache
def get_client(url: str | None = None) -> QdrantClient:
    settings = get_settings()
    return QdrantClient(
        url=url or settings.qdrant_url,
        timeout=5,
        prefer_grpc=False,
        check_compatibility=False,
    )


def reset_client() -> None:
    get_client.cache_clear()


@functools.lru_cache
def get_embedder(model_name: str | None = None) -> Embedder:
    from src.embeddings.embedder import Embedder

    settings = get_settings()
    return Embedder(model_name=model_name or settings.embedding_model)


def reset_embedder() -> None:
    get_embedder.cache_clear()


@functools.lru_cache
def get_reranker(model_name: str | None = None) -> Reranker:
    from src.retrieval.reranker import Reranker

    settings = get_settings()
    return Reranker(model_name=model_name or settings.rerank_model)


def reset_reranker() -> None:
    get_reranker.cache_clear()


def get_keyword_index(collection: str | None = None) -> KeywordIndex:
    from src.retrieval.keyword_search import KeywordIndex

    global _keyword_index, _keyword_index_collection
    settings = get_settings()
    name = collection or settings.qdrant_collection
    if _keyword_index is None or _keyword_index_collection != name:
        _keyword_index = KeywordIndex(collection=name)
        _keyword_index_collection = name
    return _keyword_index


def invalidate_keyword_index() -> None:
    global _keyword_index, _keyword_index_collection
    _keyword_index = None
    _keyword_index_collection = None


def warm_dependencies() -> None:
    """Pre-load embedder and keyword index (API startup)."""
    get_embedder()
    get_keyword_index()
    settings = get_settings()
    if settings.rerank_enabled:
        get_reranker()


def reset_all() -> None:
    reset_client()
    reset_embedder()
    reset_reranker()
    invalidate_keyword_index()
