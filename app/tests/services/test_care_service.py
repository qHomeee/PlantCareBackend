from datetime import date

from app.core.security import hash_password
from app.models.plant import Plant
from app.models.user import User
from app.models.user_plant import UserPlant
from app.models.watering_event import WateringEvent
from app.schemas.gallery import UserPlantCreate
from app.services.care_service import (
    get_user_watering_events,
    user_plant_exists_for_user,
)
from app.services.gallery_service import add_plant_to_gallery


def _seed_user_plant(db_session):
    user = User(
        email="care@test.com",
        username="care_user",
        hashed_password=hash_password("password123"),
    )
    plant = Plant(
        common_name="Monstera",
        scientific_name="Monstera deliciosa",
        description="Test",
        watering_info="Weekly",
        watering_interval_days=7,
        light_info="Indirect",
        min_temperature_celsius=18.0,
        max_temperature_celsius=26.0,
        humidity_info="Moderate",
        soil_info="Soil",
        fertilizing_info="Monthly",
        fertilizing_interval_days=30,
        care_info="Care",
        useful_info="Info",
    )
    db_session.add_all([user, plant])
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(plant)

    user_plant = add_plant_to_gallery(
        db_session,
        user.id,
        plant,
        UserPlantCreate(plant_id=plant.id, custom_name="Care plant"),
    )

    return user, user_plant


def test_user_plant_exists_for_user(db_session):
    user, user_plant = _seed_user_plant(db_session)

    assert user_plant_exists_for_user(db_session, user.id, user_plant.id) is True
    assert user_plant_exists_for_user(db_session, user.id, 99999) is False


def test_get_user_watering_events_returns_planned(db_session):
    user, user_plant = _seed_user_plant(db_session)

    events = get_user_watering_events(db_session, user.id, status="planned")

    assert events
    assert all(event.status == "planned" for event in events)
    assert all(event.user_plant_id == user_plant.id for event in events)

