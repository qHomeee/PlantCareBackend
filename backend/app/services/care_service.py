from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user_plant import UserPlant
from app.models.watering_event import WateringEvent


def get_user_watering_calendar(
    db: Session,
    user_id: int,
) -> list[WateringEvent]:
    return (
        db.query(WateringEvent)
        .join(UserPlant, WateringEvent.user_plant_id == UserPlant.id)
        .filter(UserPlant.user_id == user_id)
        .order_by(WateringEvent.scheduled_date.asc())
        .all()
    )


def get_watering_event_by_id(
    db: Session,
    user_id: int,
    event_id: int,
) -> WateringEvent | None:
    return (
        db.query(WateringEvent)
        .join(UserPlant, WateringEvent.user_plant_id == UserPlant.id)
        .filter(
            WateringEvent.id == event_id,
            UserPlant.user_id == user_id,
        )
        .first()
    )


def update_watering_event(
    db: Session,
    event: WateringEvent,
    status: str,
    note: str | None,
) -> WateringEvent:
    event.status = status
    event.note = note

    if status == "completed":
        event.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(event)

    return event