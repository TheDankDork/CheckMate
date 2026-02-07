from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    url: str

class EvidenceItem(BaseModel):
    message: str
    url: Optional[str] = None
    snippet: Optional[str] = None
    key: Optional[str] = None
    value: Optional[Any] = None

class RiskItem(BaseModel):
    severity: Literal["HIGH", "MED", "LOW", "UNCERTAIN"]
    code: str
    title: str
    evidence: List[EvidenceItem] = Field(default_factory=list)

class PageSummary(BaseModel):
    url: str
    status_code: Optional[int] = None
    title: Optional[str] = None
    extracted_date: Optional[str] = None

class Subscores(BaseModel):
    formatting: int
    relevance: int
    sources: int
    risk: int

class AnalysisResult(BaseModel):
    status: Literal["ok", "na", "error"]
    overall_score: Optional[int] = None
    subscores: Optional[Subscores] = None
    risks: List[RiskItem] = Field(default_factory=list)
    missing_pages: List[str] = Field(default_factory=list)
    pages_analyzed: List[PageSummary] = Field(default_factory=list)
    domain_info: Dict[str, Any] = Field(default_factory=dict)
    security_info: Dict[str, Any] = Field(default_factory=dict)
    threat_intel: Dict[str, Any] = Field(default_factory=dict)
    limitations: List[str] = Field(default_factory=list)
    debug: Dict[str, Any] = Field(default_factory=dict)
