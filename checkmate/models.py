from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    url: str

class EvidenceItem(BaseModel):
    key: Optional[str] = None
    message: str
    url: Optional[str] = None
    snippet: Optional[str] = None
    value: Optional[Any] = None
    severity: Optional[Literal["HIGH", "MED", "LOW"]] = None

class PageArtifact(BaseModel):
    url: str
    final_url: Optional[str] = None
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    html: Optional[str] = None
    text: Optional[str] = None
    title: Optional[str] = None
    headings: List[str] = Field(default_factory=list)
    meta: Dict[str, str] = Field(default_factory=dict)
    links_internal: List[str] = Field(default_factory=list)
    links_external: List[str] = Field(default_factory=list)
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    errors: List[str] = Field(default_factory=list)

class ExtractionResult(BaseModel):
    primary_page: Optional[PageArtifact] = None
    key_pages: Dict[str, PageArtifact] = Field(default_factory=dict)
    all_pages: List[PageArtifact] = Field(default_factory=list)
    stats: Dict[str, Any] = Field(default_factory=dict)

class ModuleResult(BaseModel):
    score: int = Field(ge=0, le=100)
    signals: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)

class RiskItem(BaseModel):
    severity: Literal["HIGH", "MED", "LOW"]
    code: str
    title: str
    score_impact: int
    evidence: List[EvidenceItem] = Field(default_factory=list)

class DomainInfo(BaseModel):
    registered_domain: Optional[str] = None
    creation_date: Optional[str] = None
    registrar: Optional[str] = None

class SecurityInfo(BaseModel):
    uses_https: bool = False
    cert_valid: bool = False

class ThreatIntel(BaseModel):
    url_match: bool = False
    domain_match: bool = False
    provider: Optional[str] = None
    last_updated: Optional[str] = None

class AnalysisResult(BaseModel):
    status: Literal["ok", "na", "error"]
    overall_score: Optional[int] = None
    subscores: Dict[str, int] = Field(default_factory=dict)
    risks: List[RiskItem] = Field(default_factory=list)
    missing_pages: List[str] = Field(default_factory=list)
    pages_analyzed: List[Dict[str, Any]] = Field(default_factory=list)
    domain_info: Optional[DomainInfo] = None
    security_info: Optional[SecurityInfo] = None
    threat_intel: Optional[ThreatIntel] = None
    debug: Dict[str, Any] = Field(default_factory=dict)
