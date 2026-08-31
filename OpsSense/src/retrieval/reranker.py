from sentence_transformers import CrossEncoder

from src.settings import get_settings


class Reranker:
    def __init__(self, model_name: str | None = None):
        settings = get_settings()
        self.model_name = model_name or settings.rerank_model
        self.model = CrossEncoder(self.model_name)

    def score_pairs(self, pairs: list[tuple[str, str]]) -> list[float]:
        if not pairs:
            return []
        scores = self.model.predict(pairs)
        return [float(s) for s in scores]


def rerank(
    query: str,
    hits: list[dict],
    top_k: int = 5,
    reranker: Reranker | None = None,
) -> list[dict]:
    if not hits:
        return []
    from src.deps import get_reranker

    reranker = reranker or get_reranker()
    pairs = [(query, h.get("text", "")) for h in hits]
    scores = reranker.score_pairs(pairs)
    ranked = []
    for hit, score in zip(hits, scores):
        ranked.append({**hit, "score": score, "rerank_score": score})
    ranked.sort(key=lambda r: r["score"], reverse=True)
    return ranked[:top_k]
