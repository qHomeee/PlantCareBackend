from app.services.deepseek_service import get_fallback_plant_care


def test_get_fallback_plant_care_returns_valid_data():
    plant_data = get_fallback_plant_care(
        scientific_name="Monstera deliciosa",
        common_name="Monstera",
    )

    assert plant_data.scientific_name == "Monstera deliciosa"
    assert plant_data.common_name == "Monstera"
    assert plant_data.watering_interval_days >= 1
    assert plant_data.max_temperature_celsius > plant_data.min_temperature_celsius
