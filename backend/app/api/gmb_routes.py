from fastapi import APIRouter
from app.schemas.gmb_schema import GMBAuditRequest, GMBAuditResponse

router = APIRouter()


@router.post('/audit', response_model=GMBAuditResponse)
async def gmb_audit(data: GMBAuditRequest):
    return {
        'score': 78,
        'missing': ['Business Description', '10+ photos'],
        'recommendations': ['Add a business description', 'Upload recent photos']
    }
