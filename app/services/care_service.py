from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session, joinedload

from app.models.user_plant import UserPlant
from app.models.watering_event import WateringEvent


def get_user_watering_events(
    db: Session,
    user_id: int,
    status: str | None = None,
) -> list[WateringEvent]:
    query = (
        db.query(WateringEvent)
        .join(UserPlant, WateringEvent.user_plant_id == UserPlant.id)
        .options(joinedload(WateringEvent.user_plant))
        .filter(UserPlant.user_id == user_id)
        .order_by(WateringEvent.scheduled_date.asc())
    )

    if status:
        query = query.filter(WateringEvent.status == status)

    return query.all()


def get_today_watering_events(
    db: Session,
    user_id: int,
) -> list[WateringEvent]:
    today = date.today()

    return (
        db.query(WateringEvent)
        .join(UserPlant, WateringEvent.user_plant_id == UserPlant.id)
        .filter(
            UserPlant.user_id == user_id,
            WateringEvent.scheduled_date == today,
            WateringEvent.status == "planned",
        )
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


def complete_watering_event(
    db: Session,
    event: WateringEvent,
    note: str | None = None,
) -> WateringEvent:
    today = date.today()
    now = datetime.utcnow()

    event.status = "completed"
    event.completed_at = now

    if note is not None:
        event.note = note

    user_plant = (
        db.query(UserPlant)
        .filter(UserPlant.id == event.user_plant_id)
        .first()
    )

    if user_plant:
        interval = user_plant.plant.watering_interval_days

        user_plant.last_watered_at = today
        user_plant.next_watering_date = today + timedelta(days=interval)

        existing_next_event = (
            db.query(WateringEvent)
            .filter(
                WateringEvent.user_plant_id == user_plant.id,
                WateringEvent.scheduled_date == user_plant.next_watering_date,
            )
            .first()
        )

        if existing_next_event is None:
            next_event = WateringEvent(
                user_plant_id=user_plant.id,
                scheduled_date=user_plant.next_watering_date,
                status="planned",
            )
            db.add(next_event)

    db.commit()
    db.refresh(event)

    return event


def skip_watering_event(
    db: Session,
    event: WateringEvent,
    note: str | None = None,
) -> WateringEvent:
    event.status = "skipped"

    if note is not None:
        event.note = note

    db.commit()
    db.refresh(event)

    return event

def get_watering_events_by_user_plant(
    db: Session,
    user_id: int,
    user_plant_id: int,
    status: str | None = None,
) -> list[WateringEvent]:
    query = (
        db.query(WateringEvent)
        .join(UserPlant, WateringEvent.user_plant_id == UserPlant.id)
        .filter(
            UserPlant.id == user_plant_id,
            UserPlant.user_id == user_id,
        )
        .order_by(WateringEvent.scheduled_date.asc(), WateringEvent.id.asc())
    )

    if status is not None:
        query = query.filter(WateringEvent.status == status)

    return query.all()

def user_plant_exists_for_user(
    db: Session,
    user_id: int,
    user_plant_id: int,
) -> bool:
    return (
        db.query(UserPlant.id)
        .filter(
            UserPlant.id == user_plant_id,
            UserPlant.user_id == user_id,
        )
        .first()
        is not None
    )