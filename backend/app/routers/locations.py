
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies import get_current_user
from app.models.location import Location
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.location import Location

router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)


@router.get("/")
def get_locations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    locations = (
        db.query(Location)
        .filter(
            Location.organization_id == current_user["organization_id"]
        )
        .order_by(Location.id)
        .all()
    )

    return [
        {
            "id": location.id,
            "location_code": location.location_code,
            "name": location.name
        }
        for location in locations
    ]
