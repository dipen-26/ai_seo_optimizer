from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class CROAuditRequest(BaseModel):
    url: HttpUrl
    goal: Optional[str] = None
    notes: Optional[str] = None


class Issue(BaseModel):
    level: str
    title: str
    detail: Optional[str] = None


class CROAuditResponse(BaseModel):
    score: int
    issues: List[Issue]
    recommendations: List[str]
