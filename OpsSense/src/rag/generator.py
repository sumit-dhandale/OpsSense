"""LLM over retrieved incidents. Facts only from context; hypotheses labeled."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import httpx
from pydantic import ValidationError

from src.rag.retrieval import (
    apply_retrieval_guardrail,
    dedupe_by_incident,
    expand_parent_text,
)
from src.rag.schemas import AskResponse
from src.retrieval.hybrid_search import hybrid_search
from src.retrieval.vector_search import search as vector_search
from src.settings import get_settings

logger = logging.getLogger(__name__)

_http_client: httpx.Client | None = None

SYSTEM_PROMPT = """You are an incident investigation assistant.

You are given:
1. A current incident.
2. Retrieved historical incidents.

Use ONLY the provided historical incidents as factual evidence.

Respond with valid JSON only (no markdown fences) matching this schema:
{
  "similar_incidents": [
    {
      "incident_id": "INC-XXXX",
      "title": "...",
      "similarity": "...",
      "difference": "...",
      "historical_root_cause": "...",
      "historical_resolution": "...",
      "source_index": 1
    }
  ],
  "investigation_areas": ["..."],
  "hypotheses": ["..."],
  "insufficient_evidence": false
}

Rules:
- source_index must reference the [n] index in the retrieved context.
- historical_root_cause and historical_resolution must come from retrieved text only.
- hypotheses must be clearly speculative; do not claim they are the actual root cause.
- Set insufficient_evidence to true if retrieved incidents are not relevant enough.
- Do not invent an RCA that is not in the retrieved text.
"""


def _client() -> httpx.Client:
    global _http_client
    if _http_client is None:
        _http_client = httpx.Client(timeout=120)
    return _http_client


def build_context(hits: list[dict]) -> str:
    if not hits:
        return "(no retrieved incidents)"
    parts = []
    for i, hit in enumerate(hits, 1):
        parts.append(
            f"[{i}] {hit.get('incident_id')} — {hit.get('title')} "
            f"(service={hit.get('service')}, severity={hit.get('severity')}, "
            f"score={float(hit.get('score') or 0):.3f})\n{hit.get('text', '')}"
        )
    return "\n\n".join(parts)


def _post_with_retry(
    url: str,
    *,
    headers: dict | None = None,
    json_body: dict | None = None,
    params: dict | None = None,
    retries: int = 2,
) -> httpx.Response:
    client = _client()
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            r = client.post(url, headers=headers, json=json_body, params=params)
            if r.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(0.5 * (2**attempt))
                continue
            return r
        except httpx.HTTPError as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(0.5 * (2**attempt))
                continue
            raise RuntimeError(f"HTTP request failed: {exc}") from exc
    raise RuntimeError(f"HTTP request failed after retries: {last_exc}")


def _complete_ollama(user: str) -> str:
    settings = get_settings()
    url = f"{settings.ollama_url.rstrip('/')}/api/chat"
    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"temperature": 0},
    }
    try:
        r = _post_with_retry(url, json_body=payload)
    except httpx.ConnectError as exc:
        raise RuntimeError(
            f"Ollama is not reachable at {settings.ollama_url}. "
            "Start it with `ollama serve`, then `ollama pull llama3.2` "
            "(or set LLM_PROVIDER=openai|gemini with an API key)."
        ) from exc
    r.raise_for_status()
    data = r.json()
    message = data.get("message") or {}
    content = message.get("content")
    if not content:
        raise RuntimeError("Ollama returned empty response")
    return content


def _complete_openai(user: str) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    r = _post_with_retry(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.openai_api_key}"},
        json_body={
            "model": settings.openai_model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user},
            ],
        },
    )
    r.raise_for_status()
    data = r.json()
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("OpenAI returned empty choices")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if not content:
        raise RuntimeError("OpenAI returned empty content")
    return content


def _complete_gemini(user: str) -> str:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
    )
    body = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": user}]}],
        "generationConfig": {"temperature": 0},
    }
    r = _post_with_retry(
        url,
        headers={"x-goog-api-key": settings.gemini_api_key},
        json_body=body,
    )
    r.raise_for_status()
    data = r.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned empty candidates")
    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    if not parts or "text" not in parts[0]:
        raise RuntimeError("Gemini returned empty content")
    return parts[0]["text"]


def complete(user: str, provider: str | None = None) -> str:
    settings = get_settings()
    p = (provider or settings.llm_provider).lower()
    if p == "ollama":
        return _complete_ollama(user)
    if p == "openai":
        return _complete_openai(user)
    if p == "gemini":
        return _complete_gemini(user)
    raise ValueError(f"unknown LLM_PROVIDER: {p}")


def _parse_response(raw: str, sources: list[dict]) -> AskResponse:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    data: dict[str, Any] = json.loads(text)
    response = AskResponse.model_validate({**data, "sources": sources})
    _validate_citations(response, len(sources))
    return response


def _validate_citations(response: AskResponse, source_count: int) -> None:
    for item in response.similar_incidents:
        if item.source_index < 1 or item.source_index > source_count:
            raise ValueError(
                f"invalid source_index {item.source_index} for {source_count} sources"
            )


def _insufficient_response(sources: list[dict]) -> AskResponse:
    return AskResponse(
        similar_incidents=[],
        investigation_areas=[],
        hypotheses=[],
        insufficient_evidence=True,
        sources=sources,
    )


def ask(
    query: str,
    top_k: int = 5,
    use_hybrid: bool = True,
    alpha: float | None = None,
    filters: dict | None = None,
    provider: str | None = None,
) -> dict:
    settings = get_settings()
    t0 = time.perf_counter()
    logger.info(
        "ask query=%r top_k=%d hybrid=%s provider=%s",
        query[:80],
        top_k,
        use_hybrid,
        provider or settings.llm_provider,
    )
    hits = (
        hybrid_search(query, top_k=top_k, alpha=alpha, filters=filters)
        if use_hybrid
        else vector_search(query, top_k=top_k, filters=filters)
    )
    hits = dedupe_by_incident(hits)
    hits = expand_parent_text(hits)
    hits, insufficient = apply_retrieval_guardrail(hits)
    if insufficient:
        logger.warning("retrieval guardrail triggered for query=%r", query[:80])
        return _insufficient_response(hits).model_dump()

    user = (
        f"Current incident / question:\n{query}\n\n"
        f"Retrieved historical incidents:\n{build_context(hits)}"
    )
    raw = complete(user, provider=provider)
    try:
        response = _parse_response(raw, hits)
    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
        logger.warning("parse failed, retrying once: %s", exc)
        repair = (
            f"{user}\n\nYour previous response was invalid ({exc}). "
            "Return valid JSON only matching the schema."
        )
        try:
            response = _parse_response(complete(repair, provider=provider), hits)
        except (json.JSONDecodeError, ValidationError, ValueError):
            logger.warning("parse failed after retry")
            return _insufficient_response(hits).model_dump()

    response.sources = hits
    logger.info(
        "ask done latency=%.2fs incidents=%s",
        time.perf_counter() - t0,
        [h.get("incident_id") for h in hits[:top_k]],
    )
    return response.model_dump()
