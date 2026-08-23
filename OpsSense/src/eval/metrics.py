"""Recall@k over unique incident IDs (chunk hits collapsed)."""


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
