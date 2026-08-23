from src.config import HYBRID_ALPHA
from src.retrieval.keyword_search import KeywordIndex
from src.retrieval.vector_search import search as vector_search


def minmax(scores: list[float]) -> list[float]:
    if not scores:
        return []
    lo, hi = min(scores), max(scores)
    if hi - lo < 1e-12:
        return [1.0 for _ in scores]
    return [(s - lo) / (hi - lo) for s in scores]


def hybrid_search(
    query: str,
    top_k: int = 5,
    alpha: float | None = None,
    filters: dict | None = None,
    candidate_k: int | None = None,
    keyword_index: KeywordIndex | None = None,
) -> list[dict]:
    """final = alpha * vector + (1-alpha) * keyword after per-list min-max."""
    a = HYBRID_ALPHA if alpha is None else alpha
    pool = candidate_k or max(top_k * 4, 20)
    vec_hits = vector_search(query, top_k=pool, filters=filters)
    kw_index = keyword_index or KeywordIndex()
    kw_hits = kw_index.search(query, top_k=pool, filters=filters)

    vec_norm = minmax([h["score"] for h in vec_hits])
    kw_norm = minmax([h["score"] for h in kw_hits])
    merged: dict[str, dict] = {}
    for hit, n in zip(vec_hits, vec_norm):
        key = hit.get("chunk_id") or f"{hit['incident_id']}:{hit.get('chunk_index')}"
        merged[key] = {**hit, "vector_score": n, "keyword_score": 0.0}
    for hit, n in zip(kw_hits, kw_norm):
        key = hit.get("chunk_id") or f"{hit['incident_id']}:{hit.get('chunk_index')}"
        if key in merged:
            merged[key]["keyword_score"] = n
        else:
            merged[key] = {**hit, "vector_score": 0.0, "keyword_score": n}
    ranked = []
    for row in merged.values():
        row["score"] = a * row["vector_score"] + (1 - a) * row["keyword_score"]
        ranked.append(row)
    ranked.sort(key=lambda r: r["score"], reverse=True)
    return ranked[:top_k]
