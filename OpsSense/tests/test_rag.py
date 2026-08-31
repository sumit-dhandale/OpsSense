import json
from unittest.mock import patch

import pytest

from src.rag.generator import (
    SYSTEM_PROMPT,
    _parse_response,
    _validate_citations,
    ask,
    build_context,
    complete,
)
from src.rag.schemas import AskResponse, SimilarIncident


def test_unknown_provider():
    with pytest.raises(ValueError, match="unknown"):
        complete("hello", provider="not-a-vendor")


def test_build_context_empty():
    assert "no retrieved" in build_context([])


def test_prompt_requires_json():
    assert "JSON" in SYSTEM_PROMPT
    assert "insufficient_evidence" in SYSTEM_PROMPT


def test_parse_valid_response():
    sources = [{"incident_id": "INC-1", "text": "root cause was pool exhaustion"}]
    raw = json.dumps(
        {
            "similar_incidents": [
                {
                    "incident_id": "INC-1",
                    "title": "t",
                    "similarity": "both timeout",
                    "difference": "different service",
                    "historical_root_cause": "pool exhaustion",
                    "historical_resolution": "increased pool",
                    "source_index": 1,
                }
            ],
            "investigation_areas": ["check pool"],
            "hypotheses": ["maybe network"],
            "insufficient_evidence": False,
        }
    )
    resp = _parse_response(raw, sources)
    assert resp.similar_incidents[0].incident_id == "INC-1"


def test_citation_validation_rejects_bad_index():
    resp = AskResponse(
        similar_incidents=[
            SimilarIncident(
                incident_id="INC-1",
                title="t",
                similarity="s",
                difference="d",
                historical_root_cause="rc",
                historical_resolution="fix",
                source_index=99,
            )
        ],
        sources=[],
    )
    with pytest.raises(ValueError, match="invalid source_index"):
        _validate_citations(resp, 1)


def test_ask_guardrail_skips_llm():
    low_hits = [
        {
            "incident_id": "INC-1",
            "title": "t",
            "service": "fraud",
            "severity": "SEV1",
            "score": 0.1,
            "text": "x",
            "chunk_id": "INC-1:0",
            "chunk_index": 0,
        }
    ]
    with patch("src.rag.generator.hybrid_search", return_value=low_hits):
        result = ask("query", top_k=1)
    assert result["insufficient_evidence"] is True
    assert result["similar_incidents"] == []
