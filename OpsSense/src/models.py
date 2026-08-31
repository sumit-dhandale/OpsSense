from dataclasses import asdict, dataclass, field


@dataclass
class Document:
    incident_id: str
    title: str
    date: str
    service: str
    severity: str
    content: str
    source: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        return cls(
            incident_id=data["incident_id"],
            title=data.get("title", ""),
            date=data.get("date", ""),
            service=data.get("service", ""),
            severity=data.get("severity", ""),
            content=data["content"],
            source=data.get("source", ""),
        )


@dataclass
class Chunk:
    chunk_id: str
    incident_id: str
    title: str
    date: str
    service: str
    severity: str
    chunk_index: int
    text: str
    section: str = ""
    parent_text: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Chunk":
        return cls(
            chunk_id=data["chunk_id"],
            incident_id=data["incident_id"],
            title=data.get("title", ""),
            date=data.get("date", ""),
            service=data.get("service", ""),
            severity=data.get("severity", ""),
            chunk_index=data["chunk_index"],
            text=data["text"],
            section=data.get("section", ""),
            parent_text=data.get("parent_text", ""),
        )


@dataclass
class Hit:
    score: float
    incident_id: str
    title: str
    service: str
    severity: str
    chunk_index: int
    chunk_id: str
    text: str
    date: str = ""
    section: str = ""
    parent_text: str = ""
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        extra = d.pop("extra", {})
        d.update(extra)
        return d

    @classmethod
    def from_payload(cls, score: float, payload: dict) -> "Hit":
        return cls(
            score=score,
            incident_id=payload.get("incident_id", ""),
            title=payload.get("title", ""),
            service=payload.get("service", ""),
            severity=payload.get("severity", ""),
            chunk_index=payload.get("chunk_index", 0),
            chunk_id=payload.get("chunk_id", ""),
            text=payload.get("text", ""),
            date=payload.get("date", ""),
            section=payload.get("section", ""),
            parent_text=payload.get("parent_text", ""),
        )
