"""Exact-match payload filters shared by vector and keyword retrieval."""

from qdrant_client.models import FieldCondition, Filter, MatchValue

ALLOWED_FILTER_KEYS = frozenset({"service", "severity", "incident_id"})


def normalize_filters(filters: dict | None) -> dict | None:
    if not filters:
        return None
    cleaned = {
        key: value
        for key, value in filters.items()
        if key in ALLOWED_FILTER_KEYS and value not in (None, "")
    }
    return cleaned or None


def matches_filters(chunk: dict, filters: dict | None) -> bool:
    if not filters:
        return True
    return all(chunk.get(key) == value for key, value in filters.items())


def payload_filter(filters: dict | None) -> Filter | None:
    """Exact match on payload fields (metadata), not on embedding space."""
    cleaned = normalize_filters(filters)
    if not cleaned:
        return None
    must = [
        FieldCondition(key=key, match=MatchValue(value=value))
        for key, value in cleaned.items()
    ]
    return Filter(must=must)
