from src.retrieval.hybrid_search import minmax


def test_minmax_scales_and_flat_list():
    assert minmax([0.0, 10.0]) == [0.0, 1.0]
    assert minmax([5.0, 5.0, 5.0]) == [1.0, 1.0, 1.0]
