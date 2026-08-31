import json
from unittest.mock import patch

from src.rag.generator import ask


def test_faithfulness_root_cause_from_source():
    sources = [
        {
            "incident_id": "INC-2841",
            "title": "Aerospike Timeout",
            "service": "fraud",
            "severity": "SEV1",
            "score": 0.85,
            "text": "Root Cause: Connection pool exhaustion caused timeouts.",
            "chunk_id": "INC-2841:0",
            "chunk_index": 0,
            "parent_text": "Root Cause: Connection pool exhaustion caused timeouts.",
        }
    ]
    llm_json = json.dumps(
        {
            "similar_incidents": [
                {
                    "incident_id": "INC-2841",
                    "title": "Aerospike Timeout",
                    "similarity": "both involve timeouts",
                    "difference": "n/a",
                    "historical_root_cause": "Connection pool exhaustion",
                    "historical_resolution": "increased pool",
                    "source_index": 1,
                }
            ],
            "investigation_areas": ["pool size"],
            "hypotheses": ["traffic spike"],
            "insufficient_evidence": False,
        }
    )
    with patch("src.rag.generator.hybrid_search", return_value=sources):
        with patch("src.rag.generator.complete", return_value=llm_json):
            result = ask("fraud timeouts", top_k=1)
    rc = result["similar_incidents"][0]["historical_root_cause"]
    assert rc.lower() in sources[0]["text"].lower()
