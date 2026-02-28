from pydantic import BaseModel 
from typing import List 
 
class GMBAuditRequest(BaseModel): 
    business_name: str 
 
class GMBAuditResponse(BaseModel): 
    score: int 
    missing_fields: List[str] 
