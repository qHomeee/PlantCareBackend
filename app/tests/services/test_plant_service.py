from app.schemas.plant import PlantCreate
from app.services.plant_service import (
    create_plant,
    get_plant_by_id,
    get_plant_by_scientific_name,
)


def _plant_create(scientific_name: str = "Ficus elastica") -> PlantCreate:
    return PlantCreate(
        common_name="Ficus",
        scientific_name=scientific_name,
        description="Test plant",
        watering_info="Weekly",
        watering_interval_days=7,
        light_info="Bright light",
        min_temperature_celsius=18.0,
        max_temperature_celsius=26.0,
        humidity_info="Moderate",
        soil_info="Loose soil",
        fertilizing_info="Monthly",
        fertilizing_interval_days=30,
        care_info="Basic care",
        useful_info="Houseplant",
    )


def test_create_and_get_plant_by_id(db_session):
    plant = create_plant(db_session, _plant_create())

    found = get_plant_by_id(db_session, plant.id)

    assert found is not None
    assert found.scientific_name == "Ficus elastica"


def test_get_plant_by_scientific_name(db_session):
    create_plant(db_session, _plant_create("Sansevieria trifasciata"))

    found = get_plant_by_scientific_name(db_session, "Sansevieria trifasciata")

    assert found is not None
    assert found.common_name == "Ficus"

