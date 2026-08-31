from src.ingestion.loader import load_documents, parse_markdown

SAMPLE = """# INC-2841

Title: Aerospike Timeout During Peak Traffic
Date: 2024-11-12
Service: Fraud Detection
Severity: SEV1

Symptoms:
Fraud feature lookups started timing out.
"""


def test_parse_markdown_metadata():
    doc = parse_markdown(SAMPLE)
    assert doc["incident_id"] == "INC-2841"
    assert doc["title"].startswith("Aerospike")
    assert doc["service"] == "fraud"
    assert doc["severity"] == "SEV1"
    assert doc["date"] == "2024-11-12"
    assert "Fraud feature" in doc["content"]


def test_load_documents_from_data_dir():
    docs = load_documents()
    assert len(docs) >= 15
    ids = {d["incident_id"] for d in docs}
    assert "INC-2841" in ids
    assert "INC-1510" in ids
    for doc in docs:
        assert doc["incident_id"].startswith("INC-")
        assert doc["title"]
        assert doc["service"]
        assert doc["severity"] in {"SEV1", "SEV2", "SEV3"}
        assert doc["content"]
