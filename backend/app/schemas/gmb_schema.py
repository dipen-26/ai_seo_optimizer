from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class GMBAuditRequest(BaseModel):
    business_name: str
    address: Optional[str] = None
    category: Optional[str] = None


class Issue(BaseModel):
    level: str
    title: str
    detail: Optional[str] = None


class Metrics(BaseModel):
    profile_completeness: float = 0
    reviews: float = 0
    photos: float = 0
    posts: float = 0
    engagement: float = 0
    rating: float = 0
    review_count: int = 0
    photo_count: int = 0
    post_count: int = 0


class ExtractedData(BaseModel):
    business_name: Optional[str] = None
    location: Optional[str] = None
    categories: List[str] = []
    phone: Optional[str] = None
    website: Optional[str] = None


class GMBAuditResponse(BaseModel):
    success: bool = True
    score: int
    issues: List[Issue]
    recommendations: List[str]
    ai_suggestions: List[str] = []
    metrics: Metrics = {}
    extracted_data: Optional[ExtractedData] = None
    error: Optional[str] = None
