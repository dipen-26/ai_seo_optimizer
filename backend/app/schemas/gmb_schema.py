from pydantic import BaseModel
from typing import List, Optional

class GMBAuditRequest(BaseModel):
    business_name: str
    address: Optional[str] = None
    category: Optional[str] = None

class GMBAuditResponse(BaseModel):
    score: int
    missing: List[str]
    recommendations: Optional[List[str]] = []
