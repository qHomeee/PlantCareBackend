from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.watering import WateringEventResponse, WateringEventUpdate
from app.services.care_service import (
    complete_watering_event,
    get_today_watering_events,
    get_user_watering_events,
    get_watering_event_by_id,
    skip_watering_event,
    get_watering_events_by_user_plant
)


router = APIRouter()


@router.get(
    "/watering-events",
    response_model=list[WateringEventResponse],
)
def get_watering_events(
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_watering_events(
        db=db,
        user_id=current_user.id,
        status=status_filter,
    )


@router.get(
    "/watering-events/today",
    response_model=list[WateringEventResponse],
)
def get_today_watering(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_today_watering_events(
        db=db,
        user_id=current_user.id,
    )


@router.patch(
    "/watering-events/{event_id}/complete",
    response_model=WateringEventResponse,
)
def complete_watering(
    event_id: int,
    data: WateringEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = get_watering_event_by_id(
        db=db,
        user_id=current_user.id,
        event_id=event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Событие полива не найдено",
        )

    if event.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Событие полива уже выполнено",
        )

    return complete_watering_event(
        db=db,
        event=event,
        note=data.note,
    )


@router.patch(
    "/watering-events/{event_id}/skip",
    response_model=WateringEventResponse,
)
def skip_watering(
    event_id: int,
    data: WateringEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = get_watering_event_by_id(
        db=db,
        user_id=current_user.id,
        event_id=event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Событие полива не найдено",
        )

    if event.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя пропустить уже выполненный полив",
        )

    return skip_watering_event(
        db=db,
        event=event,
        note=data.note,
    )

@router.get(
    "/user-plants/{user_plant_id}/watering-events",
    response_model=list[WateringEventResponse],
)
def get_plant_watering_events(
    user_plant_id: int,
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_watering_events_by_user_plant(
        db=db,
        user_id=current_user.id,
        user_plant_id=user_plant_id,
        status=status_filter,
    )