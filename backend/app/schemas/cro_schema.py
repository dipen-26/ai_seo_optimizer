from pydantic import BaseModel, HttpUrl 
from typing import List 
 
class CROAuditRequest(BaseModel): 
    url: HttpUrl 
 
class CROAuditResponse(BaseModel): 
    score: int 
    issues: List[str] 
    recommendations: List[str] 
