
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models import ReconciliationException


router = APIRouter(
    prefix="/exceptions",
    tags=["Exceptions"]
)


@router.get("/")
def get_exceptions(
    reason_code: str | None = Query(default=None),
    location_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(ReconciliationException).filter(
        ReconciliationException.organization_id
        == current_user["organization_id"]
    )

    if reason_code:
        query = query.filter(
            ReconciliationException.reason_code == reason_code
        )

    if location_id is not None:
        query = query.filter(
            ReconciliationException.location_id == location_id
        )

    exceptions = query.order_by(
        ReconciliationException.id
    ).all()

    return [
        {
            "id": item.id,
            "organization_id": item.organization_id,
            "location_id": item.location_id,
            "normalized_reference": item.normalized_reference,
            "reason_code": item.reason_code,
            "description": item.description,
            "system_a_source_id": item.system_a_source_id,
            "system_b_entry_ids": item.system_b_entry_ids,
            "evidence": item.evidence,
            "status": item.status,
            "created_at": item.created_at
        }
        for item in exceptions
    ]
