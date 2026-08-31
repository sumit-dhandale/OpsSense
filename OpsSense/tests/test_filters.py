from src.retrieval.filters import normalize_filters, payload_filter


def test_normalize_filters_allowlist():
    assert normalize_filters({"service": "fraud", "bogus": "x"}) == {"service": "fraud"}
    assert normalize_filters({"service": ""}) is None


def test_payload_filter_skips_empty():
    assert payload_filter({"service": None, "severity": "SEV1"}) is not None
