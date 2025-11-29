
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class EvidenceItem(BaseModel):
    source: str
    source_type: str = Field(
        description="news / fact_check / encyclopedia / advisory / heuristic / other"
    )
    summary: str
    url: Optional[str] = None
    reliability: float = Field(ge=0.0, le=1.0, default=0.5)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    match_score: float = Field(ge=0.0, le=1.0, default=0.0)
    published_at: Optional[str] = None


class ClaimIn(BaseModel):
    text: str = Field(..., description="Claim or news text to analyze")
    language: str = Field(
        default="en",
        description="ISO language code – logic is tuned primarily for English",
    )
    severity: str = Field(
        default="normal",
        description="low / normal / high – affects conservativeness of verdict",
    )


class ClaimOut(BaseModel):
    claim: str
    category: str
    confidence: float
    truth_score: int
    verdict: str
    explanation: str
    evidence: List[EvidenceItem]
    meta: Dict[str, Any]
