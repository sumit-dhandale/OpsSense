"""Retrieval preprocessing for RAG."""

from src.settings import get_settings


def dedupe_by_incident(
    hits: list[dict], max_chunks_per_incident: int = 1
) -> list[dict]:
    by_incident: dict[str, list[dict]] = {}
    for hit in hits:
        iid = hit.get("incident_id")
        if not iid:
            continue
        by_incident.setdefault(iid, []).append(hit)
    deduped: list[dict] = []
    for group in by_incident.values():
        group.sort(key=lambda h: float(h.get("score") or 0), reverse=True)
        deduped.extend(group[:max_chunks_per_incident])
    deduped.sort(key=lambda h: float(h.get("score") or 0), reverse=True)
    return deduped


def expand_parent_text(hits: list[dict]) -> list[dict]:
    expanded = []
    for hit in hits:
        parent = hit.get("parent_text") or hit.get("text", "")
        expanded.append({**hit, "text": parent or hit.get("text", "")})
    return expanded


def apply_retrieval_guardrail(
    hits: list[dict], min_score: float | None = None
) -> tuple[list[dict], bool]:
    settings = get_settings()
    threshold = min_score if min_score is not None else settings.retrieval_min_score
    if not hits:
        return hits, True
    best = max(float(h.get("score") or 0) for h in hits)
    if best < threshold:
        return hits, True
    return hits, False
