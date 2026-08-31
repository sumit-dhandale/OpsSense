from pydantic import BaseModel, Field


class SimilarIncident(BaseModel):
    incident_id: str
    title: str
    similarity: str
    difference: str
    historical_root_cause: str
    historical_resolution: str
    source_index: int = Field(ge=1)


class AskResponse(BaseModel):
    similar_incidents: list[SimilarIncident] = Field(default_factory=list)
    investigation_areas: list[str] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    insufficient_evidence: bool = False
    sources: list[dict] = Field(default_factory=list)
