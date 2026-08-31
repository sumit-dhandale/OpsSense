from src.eval.metrics import (
    mean_mrr,
    mean_ndcg,
    mean_recall,
    mrr_at_k,
    ndcg_at_k,
    recall_at_k,
    unique_incident_ids,
)


def test_unique_incident_ids_dedupes_chunks():
    hits = [
        {"incident_id": "INC-1"},
        {"incident_id": "INC-1"},
        {"incident_id": "INC-2"},
    ]
    assert unique_incident_ids(hits, k=2) == ["INC-1", "INC-2"]


def test_recall_at_k():
    assert recall_at_k(["INC-1", "INC-2"], {"INC-1", "INC-9"}, k=1) == 0.5
    assert mean_recall([(["A", "B"], {"A"}), (["X"], {"A"})], k=1) == 0.5


def test_mrr_at_k():
    assert mrr_at_k(["INC-2", "INC-1"], {"INC-1"}, k=2) == 0.5
    assert mrr_at_k(["INC-9"], {"INC-1"}, k=5) == 0.0
    assert mean_mrr([(["INC-1"], {"INC-1"}), (["X"], {"INC-1"})], k=3) == 0.5


def test_ndcg_at_k():
    assert ndcg_at_k(["INC-1", "INC-9"], {"INC-1"}, k=2) > 0.0
    assert ndcg_at_k(["INC-9"], {"INC-1"}, k=2) == 0.0
    assert mean_ndcg([(["INC-1"], {"INC-1"})], k=5) == 1.0
