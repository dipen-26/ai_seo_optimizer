from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any


class CROAuditRequest(BaseModel):
    url: HttpUrl
    goal: Optional[str] = None
    notes: Optional[str] = None
    industry: Optional[str] = "default"


class Issue(BaseModel):
    level: str
    title: str
    detail: Optional[str] = None
    severity: Optional[str] = None
    penalty: Optional[int] = None


class TrustSignals(BaseModel):
    is_https: bool = False
    has_schema: bool = False
    schema_types: List[str] = []
    third_party_reviews: List[str] = []
    security_badges: List[str] = []
    trust_score: int = 0


class ExtractedData(BaseModel):
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_count: int = 0
    h1_text: List[str] = []
    button_count: int = 0
    buttons: List[Dict[str, Any]] = []
    form_count: int = 0
    image_count: int = 0
    is_https: bool = False
    js_rendered: bool = False
    trust_signals: Optional[TrustSignals] = None
    schema_types: List[str] = []
    cta_positions: Dict[str, Any] = {}


class PageSpeedData(BaseModel):
    score: int = 0
    lcp: float = 0
    fid: float = 0
    cls: float = 0
    strategy: Optional[str] = None


class CROAuditResponse(BaseModel):
    success: bool = True
    score: int
    issues: List[Issue] = []
    recommendations: List[str] = []
    ai_suggestions: List[str] = []
    extracted_data: Optional[ExtractedData] = None
    industry: str = "default"
    pagespeed: Optional[PageSpeedData] = None
    viewport_analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
