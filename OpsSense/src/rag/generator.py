"""LLM over retrieved incidents. Facts only from context; hypotheses labeled."""

import httpx

from src import config
from src.retrieval.hybrid_search import hybrid_search
from src.retrieval.vector_search import search as vector_search

SYSTEM_PROMPT = """You are an incident investigation assistant.

You are given:
1. A current incident.
2. Retrieved historical incidents.

Use ONLY the provided historical incidents as factual evidence.

For each relevant historical incident:
- explain the similarity
- explain the difference
- provide the historical root cause
- provide the historical resolution

Then provide:
- likely investigation areas
- possible hypotheses

Clearly label hypotheses as hypotheses.

Do not claim that a hypothesis is the actual root cause.

If the retrieved incidents are not sufficiently relevant,
say that there is insufficient historical evidence.

Distinguish:
- Known from historical incidents
- Inference / hypothesis

Do not invent an RCA that is not in the retrieved text.
"""


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


def _complete_ollama(user: str) -> str:
    url = f"{config.OLLAMA_URL.rstrip('/')}/api/chat"
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ],
        "stream": False,
    }
    with httpx.Client(timeout=120) as client:
        try:
            r = client.post(url, json=payload)
        except httpx.ConnectError as exc:
            raise RuntimeError(
                f"Ollama is not reachable at {config.OLLAMA_URL}. "
                "Start it with `ollama serve`, then `ollama pull llama3.2` "
                "(or set LLM_PROVIDER=openai|gemini with an API key)."
            ) from exc
        r.raise_for_status()
        return r.json()["message"]["content"]


def _complete_openai(user: str) -> str:
    if not config.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")
    with httpx.Client(timeout=120) as client:
        r = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {config.OPENAI_API_KEY}"},
            json={
                "model": config.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user},
                ],
            },
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


def _complete_gemini(user: str) -> str:
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{config.GEMINI_MODEL}:generateContent"
    )
    body = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": user}]}],
    }
    with httpx.Client(timeout=120) as client:
        r = client.post(url, params={"key": config.GEMINI_API_KEY}, json=body)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def complete(user: str, provider: str | None = None) -> str:
    p = (provider or config.LLM_PROVIDER).lower()
    if p == "ollama":
        return _complete_ollama(user)
    if p == "openai":
        return _complete_openai(user)
    if p == "gemini":
        return _complete_gemini(user)
    raise ValueError(f"unknown LLM_PROVIDER: {p}")


def ask(
    query: str,
    top_k: int = 5,
    use_hybrid: bool = True,
    alpha: float | None = None,
    filters: dict | None = None,
    provider: str | None = None,
) -> dict:
    hits = (
        hybrid_search(query, top_k=top_k, alpha=alpha, filters=filters)
        if use_hybrid
        else vector_search(query, top_k=top_k, filters=filters)
    )
    user = (
        f"Current incident / question:\n{query}\n\n"
        f"Retrieved historical incidents:\n{build_context(hits)}"
    )
    return {"answer": complete(user, provider=provider), "sources": hits}
