from src.retrieval.keyword_search import KeywordIndex


CHUNKS = [
    {
        "chunk_id": "INC-2841:0",
        "incident_id": "INC-2841",
        "title": "Aerospike Timeout",
        "service": "fraud",
        "severity": "SEV1",
        "chunk_index": 0,
        "text": "Aerospike timeout during peak traffic connection pool exhaustion",
    },
    {
        "chunk_id": "INC-1510:0",
        "incident_id": "INC-1510",
        "title": "Feature Store Became Slow",
        "service": "fraud",
        "severity": "SEV2",
        "chunk_index": 0,
        "text": "the feature store became slow compaction backlog default features",
    },
    {
        "chunk_id": "INC-3102:0",
        "incident_id": "INC-3102",
        "title": "Redis Latency",
        "service": "sessions",
        "severity": "SEV2",
        "chunk_index": 0,
        "text": "Redis session cache latency after login spinner",
    },
]


def test_keyword_prefers_exact_token():
    hits = KeywordIndex(chunks=CHUNKS).search("Aerospike timeout", top_k=3)
    assert hits[0]["incident_id"] == "INC-2841"


def test_keyword_feature_store_phrase():
    hits = KeywordIndex(chunks=CHUNKS).search("feature store became slow", top_k=3)
    assert hits[0]["incident_id"] == "INC-1510"
