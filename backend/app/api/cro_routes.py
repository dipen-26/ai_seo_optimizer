from fastapi import APIRouter
from app.schemas.cro_schema import CROAuditRequest, CROAuditResponse, Issue

router = APIRouter()


@router.post('/audit', response_model=CROAuditResponse)
async def cro_audit(data: CROAuditRequest):
    issues = [
        Issue(level='critical', title='Missing meta description', detail='No meta description found.'),
        Issue(level='improve', title='Weak CTA', detail='CTA is generic; consider stronger action verbs.'),
    ]
    return {
        'score': 85,
        'issues': [i.dict() for i in issues],
        'recommendations': ['Add a clear meta description', 'Use action-oriented CTA copy']
    }
