from fastapi import APIRouter
from ..schemas.cro_schema import CROAuditRequest, CROAuditResponse
from ..services.cro_service import CROService

router = APIRouter()
cro_service = CROService()


@router.post('/audit', response_model=CROAuditResponse)
async def cro_audit(data: CROAuditRequest):
    """
    Perform CRO audit on a URL.
    
    - **url**: Page URL to audit
    - **goal**: Optional conversion goal (e.g., "Signups", "Sales")
    - **notes**: Optional context for the audit
    """
    result = await cro_service.audit_url(
        url=str(data.url),
        goal=data.goal,
        notes=data.notes
    )
    return result
