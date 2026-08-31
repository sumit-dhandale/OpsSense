"""Recall@k, MRR@k, nDCG@k over unique incident IDs (chunk hits collapsed)."""

import math


def unique_incident_ids(hits: list[dict], k: int | None = None) -> list[str]:
    seen: list[str] = []
    for hit in hits:
        iid = hit.get("incident_id")
        if iid and iid not in seen:
            seen.append(iid)
        if k is not None and len(seen) >= k:
            break
    return seen


def recall_at_k(retrieved_ids: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    return len(set(retrieved_ids[:k]) & relevant) / len(relevant)


def mean_recall(rows: list[tuple[list[str], set[str]]], k: int) -> float:
    if not rows:
        return 0.0
    return sum(recall_at_k(ids, gold, k) for ids, gold in rows) / len(rows)


def mrr_at_k(retrieved_ids: list[str], relevant: set[str], k: int) -> float:
    for rank, iid in enumerate(retrieved_ids[:k], start=1):
        if iid in relevant:
            return 1.0 / rank
    return 0.0


def mean_mrr(rows: list[tuple[list[str], set[str]]], k: int) -> float:
    if not rows:
        return 0.0
    return sum(mrr_at_k(ids, gold, k) for ids, gold in rows) / len(rows)


def ndcg_at_k(retrieved_ids: list[str], relevant: set[str], k: int) -> float:
    dcg = 0.0
    for rank, iid in enumerate(retrieved_ids[:k], start=1):
        rel = 1.0 if iid in relevant else 0.0
        dcg += rel / math.log2(rank + 1)
    ideal_hits = min(len(relevant), k)
    if ideal_hits == 0:
        return 0.0
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal_hits + 1))
    return dcg / idcg if idcg else 0.0


def mean_ndcg(rows: list[tuple[list[str], set[str]]], k: int) -> float:
    if not rows:
        return 0.0
    return sum(ndcg_at_k(ids, gold, k) for ids, gold in rows) / len(rows)
