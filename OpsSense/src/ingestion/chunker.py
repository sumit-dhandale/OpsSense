"""Split document text into section-aware overlapping windows."""

import re

from src.settings import get_settings

_SECTION_LABELS = (
    "Symptoms",
    "Impact",
    "Logs",
    "Root Cause",
    "Resolution",
    "Preventive Actions",
)
_SECTION_PATTERN = re.compile(
    r"^(?:" + "|".join(re.escape(s) for s in _SECTION_LABELS) + r"|##\s+.+?):\s*$",
    re.I | re.M,
)


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    settings = get_settings()
    chunk_size = chunk_size if chunk_size is not None else settings.chunk_size
    overlap = overlap if overlap is not None else settings.chunk_overlap
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")
    tokens = text.split()
    if not tokens:
        return []
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunks.append(" ".join(tokens[start:end]))
        if end == len(tokens):
            break
        start += chunk_size - overlap
    return chunks


def split_sections(content: str) -> list[tuple[str, str]]:
    """Return (section_name, section_body) pairs."""
    lines = content.splitlines()
    if not lines:
        return [("body", "")]
    # Skip title + metadata header until first section or blank after metadata
    start = 0
    if lines[0].startswith("# "):
        start = 1
    while start < len(lines) and lines[start].strip():
        if _SECTION_PATTERN.match(lines[start].strip()):
            break
        start += 1
    body_lines = lines[start:]
    if not body_lines:
        return [("body", content)]

    sections: list[tuple[str, str]] = []
    current_name = "body"
    current_lines: list[str] = []

    for line in body_lines:
        stripped = line.strip()
        if _SECTION_PATTERN.match(stripped):
            if current_lines:
                sections.append((current_name, "\n".join(current_lines).strip()))
            label = stripped.rstrip(":").strip()
            if label.startswith("##"):
                current_name = label.lstrip("#").strip()
            else:
                current_name = label
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((current_name, "\n".join(current_lines).strip()))
    return sections or [("body", content)]


def chunk_document(
    doc: dict,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[dict]:
    settings = get_settings()
    chunk_size = chunk_size if chunk_size is not None else settings.chunk_size
    overlap = overlap if overlap is not None else settings.chunk_overlap
    parent_text = doc["content"]
    chunks: list[dict] = []
    chunk_index = 0
    for section_name, section_text in split_sections(parent_text):
        if not section_text.strip():
            continue
        parts = chunk_text(section_text, chunk_size=chunk_size, overlap=overlap)
        for part in parts:
            chunks.append(
                {
                    "chunk_id": f"{doc['incident_id']}:{chunk_index}",
                    "incident_id": doc["incident_id"],
                    "title": doc.get("title", ""),
                    "date": doc.get("date", ""),
                    "service": doc.get("service", ""),
                    "severity": doc.get("severity", ""),
                    "section": section_name,
                    "chunk_index": chunk_index,
                    "text": part,
                    "parent_text": parent_text,
                }
            )
            chunk_index += 1
    return chunks


def chunk_documents(
    docs: list[dict],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[dict]:
    chunks: list[dict] = []
    for doc in docs:
        chunks.extend(chunk_document(doc, chunk_size=chunk_size, overlap=overlap))
    return chunks
