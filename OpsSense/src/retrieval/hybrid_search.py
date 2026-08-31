import logging

from src.deps import get_keyword_index
from src.retrieval.keyword_search import KeywordIndex
from src.retrieval.reranker import rerank
from src.retrieval.vector_search import search as vector_search
from src.settings import get_settings

logger = logging.getLogger(__name__)


def reciprocal_rank_fusion(
    rank_lists: list[list[dict]], k: int | None = None
) -> list[dict]:
    settings = get_settings()
    k = k if k is not None else settings.rrf_k
    scores: dict[str, float] = {}
    rows: dict[str, dict] = {}
    for hits in rank_lists:
        for rank, hit in enumerate(hits, start=1):
            key = hit.get("chunk_id") or f"{hit['incident_id']}:{hit.get('chunk_index')}"
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            rows.setdefault(key, hit)
    merged = []
    for key, score in scores.items():
        row = {**rows[key], "score": score}
        merged.append(row)
    merged.sort(key=lambda r: r["score"], reverse=True)
    return merged


def hybrid_search(
    query: str,
    top_k: int = 5,
    alpha: float | None = None,
    filters: dict | None = None,
    candidate_k: int | None = None,
    keyword_index: KeywordIndex | None = None,
) -> list[dict]:
    """RRF merge of vector + keyword lists, optional cross-encoder rerank."""
    if alpha is not None:
        logger.warning(
            "hybrid_search alpha=%s is deprecated and ignored; using RRF", alpha
        )
    settings = get_settings()
    pool = candidate_k or max(top_k * 4, 20)
    vec_hits = vector_search(query, top_k=pool, filters=filters)
    kw_index = keyword_index or get_keyword_index()
    kw_hits = kw_index.search(query, top_k=pool, filters=filters)
    merged = reciprocal_rank_fusion([vec_hits, kw_hits])
    if settings.rerank_enabled and merged:
        return rerank(query, merged, top_k=top_k)
    return merged[:top_k]
