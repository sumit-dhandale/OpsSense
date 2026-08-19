"""Load incident markdown into a dict: metadata fields separate from full body."""

from pathlib import Path
import re

from src.config import DATA_DIR

_FIELD = re.compile(r"^(Title|Date|Service|Severity):\s*(.*)$", re.I)

SERVICE_ALIASES = {
    "fraud detection": "fraud",
    "fraud": "fraud",
    "payments": "payments",
    "payment authorization": "payments",
    "orders": "orders",
    "sessions": "sessions",
    "inventory": "inventory",
    "gateway": "gateway",
    "users": "users",
    "checkout": "payments",
}


def normalize_service(raw: str) -> str:
    key = raw.strip().lower()
    return SERVICE_ALIASES.get(key, key.replace(" ", "_"))


def parse_markdown(text: str, source: str = "") -> dict:
    lines = text.strip().splitlines()
    incident_id = ""
    fields: dict[str, str] = {}
    for i, line in enumerate(lines):
        if line.startswith("# ") and not incident_id:
            incident_id = line[2:].strip()
            continue
        m = _FIELD.match(line.strip())
        if m:
            fields[m.group(1).lower()] = m.group(2).strip()
    if not incident_id:
        raise ValueError(f"missing incident id heading in {source}")
    return {
        "incident_id": incident_id,
        "title": fields.get("title", ""),
        "date": fields.get("date", ""),
        "service": normalize_service(fields.get("service", "")),
        "severity": fields.get("severity", "").upper(),
        "content": text.strip(),
        "source": source,
    }


def load_documents(data_dir: Path | None = None) -> list[dict]:
    directory = data_dir or DATA_DIR
    docs = []
    for path in sorted(directory.glob("*.md")):
        docs.append(parse_markdown(path.read_text(encoding="utf-8"), source=str(path)))
    return docs
