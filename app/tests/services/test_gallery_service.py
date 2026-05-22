from datetime import date

from app.models.plant import Plant
from app.schemas.gallery import UserPlantCreate
from app.services.gallery_service import add_plant_to_gallery, get_user_gallery
from app.core.security import hash_password
from app.models.user import User


def _create_user(db_session, email: str = "gallery@test.com"):
    user = User(
        email=email,
        username="gallery_user",
        hashed_password=hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _create_plant(db_session):
    plant = Plant(
        common_name="Monstera",
        scientific_name="Monstera deliciosa",
        description="Test plant",
        watering_info="Weekly",
        watering_interval_days=7,
        light_info="Indirect",
        min_temperature_celsius=18.0,
        max_temperature_celsius=26.0,
        humidity_info="Moderate",
        soil_info="Loose soil",
        fertilizing_info="Monthly",
        fertilizing_interval_days=30,
        care_info="Avoid overwatering",
        useful_info="Houseplant",
    )
    db_session.add(plant)
    db_session.commit()
    db_session.refresh(plant)
    return plant


def test_add_plant_to_gallery_creates_watering_events(db_session):
    user = _create_user(db_session)
    plant = _create_plant(db_session)

    user_plant = add_plant_to_gallery(
        db_session,
        user.id,
        plant,
        UserPlantCreate(plant_id=plant.id, custom_name="My plant"),
    )

    assert user_plant.custom_name == "My plant"
    assert user_plant.next_watering_date is not None
    assert user_plant.next_watering_date >= date.today()


def test_get_user_gallery_returns_user_plants(db_session):
    user = _create_user(db_session, email="gallery2@test.com")
    plant = _create_plant(db_session)

    add_plant_to_gallery(
        db_session,
        user.id,
        plant,
        UserPlantCreate(plant_id=plant.id, custom_name="Gallery item"),
    )

    gallery = get_user_gallery(db_session, user.id)

    assert len(gallery) == 1
    assert gallery[0].plant.scientific_name == "Monstera deliciosa"
