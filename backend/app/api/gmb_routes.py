from fastapi import APIRouter
from ..schemas.gmb_schema import GMBAuditRequest, GMBAuditResponse
from ..services.gmb_service import GMBService

router = APIRouter()
gmb_service = GMBService()


@router.post('/audit', response_model=GMBAuditResponse)
async def gmb_audit(data: GMBAuditRequest):
    """
    Perform GMB audit on a business.
    
    - **business_name**: Name of the business (required)
    - **address**: Optional business address/location
    - **category**: Optional business category
    """
    result = await gmb_service.audit_business(
        business_name=data.business_name,
        address=data.address,
        category=data.category
    )
    return result
