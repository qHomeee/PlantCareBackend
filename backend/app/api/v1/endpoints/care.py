from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.watering import WateringEventResponse, WateringEventUpdate
from app.services.care_service import get_user_watering_calendar,get_watering_event_by_id,update_watering_event
    
    
    



router = APIRouter()


@router.get(
    "/calendar",
    response_model=list[WateringEventResponse],
)
def get_calendar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_watering_calendar(db, current_user.id)


@router.patch(
    "/watering/{event_id}",
    response_model=WateringEventResponse,
)
def update_watering(
    event_id: int,
    data: WateringEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = get_watering_event_by_id(db, current_user.id, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Событие полива не найдено",
        )

    return update_watering_event(db, event, data.status, data.note)