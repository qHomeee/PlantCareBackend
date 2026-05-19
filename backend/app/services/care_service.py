from datetime import datetime,date,timedelta

from sqlalchemy.orm import Session
from app.models.plant import Plant
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

    user_plant = (
        db.query(UserPlant)
        .filter(UserPlant.id == event.user_plant_id)
        .first()
    )

    if status == "completed":
        now = datetime.utcnow()
        today = date.today()

        event.completed_at = now

        if user_plant is not None:
            plant = (
                db.query(Plant)
                .filter(Plant.id == user_plant.plant_id)
                .first()
            )

            user_plant.last_watered_at = today

            if plant is not None:
                next_date = today + timedelta(days=plant.watering_interval_days)
                user_plant.next_watering_date = next_date

                existing_next_event = (
                    db.query(WateringEvent)
                    .filter(
                        WateringEvent.user_plant_id == user_plant.id,
                        WateringEvent.scheduled_date == next_date,
                    )
                    .first()
                )

                if existing_next_event is None:
                    next_event = WateringEvent(
                        user_plant_id=user_plant.id,
                        scheduled_date=next_date,
                        status="planned",
                    )
                    db.add(next_event)

    elif status == "planned":
        event.completed_at = None

    elif status == "missed":
        event.completed_at = None

    db.commit()
    db.refresh(event)

    return event