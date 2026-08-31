from src.retrieval.hybrid_search import reciprocal_rank_fusion


def test_rrf_merges_both_lists():
    vec = [
        {"chunk_id": "a:0", "incident_id": "INC-A", "score": 0.9},
        {"chunk_id": "b:0", "incident_id": "INC-B", "score": 0.8},
    ]
    kw = [
        {"chunk_id": "b:0", "incident_id": "INC-B", "score": 12.0},
        {"chunk_id": "c:0", "incident_id": "INC-C", "score": 8.0},
    ]
    merged = reciprocal_rank_fusion([vec, kw], k=60)
    ids = [h["chunk_id"] for h in merged]
    assert "a:0" in ids and "b:0" in ids and "c:0" in ids
    assert merged[0]["chunk_id"] == "b:0"


def test_rrf_single_list():
    hits = [{"chunk_id": "x:0", "incident_id": "INC-X", "score": 1.0}]
    merged = reciprocal_rank_fusion([hits])
    assert len(merged) == 1
