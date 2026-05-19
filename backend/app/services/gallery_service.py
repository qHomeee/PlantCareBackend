from datetime import date, timedelta

from sqlalchemy.orm import Session, joinedload

from app.models.plant import Plant
from app.models.user_plant import UserPlant
from app.models.watering_event import WateringEvent
from app.schemas.gallery import UserPlantCreate


def generate_watering_events(
    db: Session,
    user_plant: UserPlant,
    plant: Plant,
    days_ahead: int = 30,
) -> None:
    today = date.today()
    interval = plant.watering_interval_days

    current_date = today + timedelta(days=interval)

    while current_date <= today + timedelta(days=days_ahead):
        event = WateringEvent(
            user_plant_id=user_plant.id,
            scheduled_date=current_date,
            status="planned",
        )
        db.add(event)
        current_date += timedelta(days=interval)


def add_plant_to_gallery(
    db: Session,
    user_id: int,
    plant: Plant,
    data: UserPlantCreate,
) -> UserPlant:
    today = date.today()

    user_plant = UserPlant(
        user_id=user_id,
        plant_id=plant.id,
        custom_name=data.custom_name,
        image_url=data.image_url,
        last_watered_at=None,
        next_watering_date=today + timedelta(days=plant.watering_interval_days),
    )

    db.add(user_plant)
    db.commit()
    db.refresh(user_plant)

    generate_watering_events(db, user_plant, plant)
    db.commit()
    db.refresh(user_plant)

    return user_plant


def get_user_gallery(db: Session, user_id: int) -> list[UserPlant]:
    return (
        db.query(UserPlant)
        .options(joinedload(UserPlant.plant))
        .filter(UserPlant.user_id == user_id)
        .order_by(UserPlant.added_at.desc())
        .all()
    )


def get_user_plant_by_id(
    db: Session,
    user_id: int,
    user_plant_id: int,
) -> UserPlant | None:
    return (
        db.query(UserPlant)
        .options(joinedload(UserPlant.plant))
        .filter(UserPlant.id == user_plant_id, UserPlant.user_id == user_id)
        .first()
    )