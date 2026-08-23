import pytest

from src.rag.generator import SYSTEM_PROMPT, build_context, complete


def test_unknown_provider():
    with pytest.raises(ValueError, match="unknown"):
        complete("hello", provider="not-a-vendor")


def test_build_context_empty():
    assert "no retrieved" in build_context([])


def test_prompt_forbids_invented_rca():
    assert "Do not invent" in SYSTEM_PROMPT
    assert "hypothes" in SYSTEM_PROMPT.lower()
