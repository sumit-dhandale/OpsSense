from src.eval.metrics import mean_recall, recall_at_k, unique_incident_ids


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
