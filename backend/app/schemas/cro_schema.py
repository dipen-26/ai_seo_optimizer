from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any


class CROAuditRequest(BaseModel):
    url: HttpUrl
    goal: Optional[str] = None
    notes: Optional[str] = None


class Issue(BaseModel):
    level: str
    title: str
    detail: Optional[str] = None


class ExtractedData(BaseModel):
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_count: int = 0
    button_count: int = 0
    form_count: int = 0
    image_count: int = 0


class CROAuditResponse(BaseModel):
    success: bool = True
    score: int
    issues: List[Issue]
    recommendations: List[str]
    ai_suggestions: List[str] = []
    extracted_data: Optional[ExtractedData] = None
    error: Optional[str] = None
