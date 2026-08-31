"""Load incident markdown into a dict: metadata fields separate from full body."""

import logging
import re
from pathlib import Path

from src.settings import get_settings

logger = logging.getLogger(__name__)

_FIELD = re.compile(r"^(Title|Date|Service|Severity):\s*(.*)$", re.I)
_SECTION_START = re.compile(
    r"^(Symptoms|Impact|Logs|Root Cause|Resolution|Preventive Actions|##\s+).*$",
    re.I,
)

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
    in_header = False
    for line in lines:
        if line.startswith("# ") and not incident_id:
            incident_id = line[2:].strip()
            in_header = True
            continue
        if not in_header:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        if _SECTION_START.match(stripped):
            break
        m = _FIELD.match(stripped)
        if m:
            fields[m.group(1).lower()] = m.group(2).strip()
        elif fields:
            break
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
    settings = get_settings()
    directory = data_dir or settings.data_dir
    docs = []
    errors: list[str] = []
    for path in sorted(directory.glob("*.md")):
        try:
            docs.append(
                parse_markdown(path.read_text(encoding="utf-8"), source=str(path))
            )
        except ValueError as exc:
            errors.append(f"{path.name}: {exc}")
            logger.warning("Skipping %s: %s", path.name, exc)
    if errors:
        logger.warning("Failed to load %d file(s): %s", len(errors), "; ".join(errors))
    return docs
