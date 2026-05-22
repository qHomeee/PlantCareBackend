from unittest.mock import AsyncMock, patch

from app.schemas.plant import PlantCreate
from app.tests.conftest import TEST_IMAGE_PATH


def test_mock_recognize_plant(client, auth_headers):
    response = client.post(
        "/api/v1/plants/mock-recognize",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["scientific_name"] == "Monstera deliciosa"
    assert "plant_id" in data


def test_mock_recognize_unauthorized(client):
    response = client.post("/api/v1/plants/mock-recognize")

    assert response.status_code == 401


@patch(
    "app.api.v1.endpoints.plants.get_plant_care_from_deepseek",
    new_callable=AsyncMock,
)
@patch(
    "app.api.v1.endpoints.plants.recognize_plant_with_plantnet",
    new_callable=AsyncMock,
)
def test_recognize_plant(
    mock_plantnet,
    mock_ai,
    client,
    auth_headers,
):
    mock_plantnet.return_value = {
        "results": [
            {
                "score": 0.95,
                "species": {
                    "scientificNameWithoutAuthor": "Monstera deliciosa",
                    "commonNames": ["Monstera"],
                },
            }
        ]
    }

    mock_ai.return_value = PlantCreate(
        common_name="Monstera",
        scientific_name="Monstera deliciosa",
        description="Beautiful tropical plant",
        watering_info="Water once a week",
        watering_interval_days=7,
        light_info="Bright indirect light",
        min_temperature_celsius=18.0,
        max_temperature_celsius=26.0,
        humidity_info="Moderate humidity",
        soil_info="Well-draining soil",
        fertilizing_info="Monthly in summer",
        fertilizing_interval_days=30,
        care_info="Avoid overwatering",
        useful_info="Popular houseplant",
    )

    with TEST_IMAGE_PATH.open("rb") as image:
        response = client.post(
            "/api/v1/plants/recognize",
            headers=auth_headers,
            files={"file": ("plant.jpg", image, "image/jpeg")},
        )

    assert response.status_code == 200

    data = response.json()

    assert data["scientific_name"] == "Monstera deliciosa"


@patch(
    "app.api.v1.endpoints.plants.recognize_plant_with_plantnet",
    new_callable=AsyncMock,
)
def test_recognize_plant_no_results(mock_plantnet, client, auth_headers):
    mock_plantnet.return_value = {"results": []}

    with TEST_IMAGE_PATH.open("rb") as image:
        response = client.post(
            "/api/v1/plants/recognize",
            headers=auth_headers,
            files={"file": ("plant.jpg", image, "image/jpeg")},
        )

    assert response.status_code == 404


@patch(
    "app.api.v1.endpoints.plants.recognize_plant_with_plantnet",
    new_callable=AsyncMock,
)
def test_recognize_plant_plantnet_error(mock_plantnet, client, auth_headers):
    mock_plantnet.side_effect = RuntimeError("PlantNet unavailable")

    with TEST_IMAGE_PATH.open("rb") as image:
        response = client.post(
            "/api/v1/plants/recognize",
            headers=auth_headers,
            files={"file": ("plant.jpg", image, "image/jpeg")},
        )

    assert response.status_code == 502


def test_recognize_unauthorized(client):
    with TEST_IMAGE_PATH.open("rb") as image:
        response = client.post(
            "/api/v1/plants/recognize",
            files={"file": ("plant.jpg", image, "image/jpeg")},
        )

    assert response.status_code == 401


def test_upload_non_image_file(client, auth_headers):
    response = client.post(
        "/api/v1/plants/recognize",
        headers=auth_headers,
        files={
            "file": (
                "test.txt",
                b"not image",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
