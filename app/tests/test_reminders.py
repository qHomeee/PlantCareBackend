def test_get_reminders(client, auth_headers):
    response = client.get(
        "/api/v1/care/watering-events",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_today_reminders(client, auth_headers):
    response = client.get(
        "/api/v1/care/watering-events/today",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def _add_gallery_item(client, auth_headers, sample_plant_id):
    return client.post(
        "/api/v1/gallery",
        headers=auth_headers,
        json={
            "plant_id": sample_plant_id,
            "custom_name": "Watering test plant",
        },
    )


def test_complete_watering(client, auth_headers, sample_plant_id):
    _add_gallery_item(client, auth_headers, sample_plant_id)

    events_response = client.get(
        "/api/v1/care/watering-events",
        headers=auth_headers,
    )

    events = events_response.json()
    assert events

    event_id = events[0]["id"]

    response = client.patch(
        f"/api/v1/care/watering-events/{event_id}/complete",
        headers=auth_headers,
        json={"note": "Watered in the morning"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_skip_watering(client, auth_headers, sample_plant_id):
    _add_gallery_item(client, auth_headers, sample_plant_id)

    events_response = client.get(
        "/api/v1/care/watering-events",
        headers=auth_headers,
    )

    events = events_response.json()
    assert events

    event_id = events[0]["id"]

    response = client.patch(
        f"/api/v1/care/watering-events/{event_id}/skip",
        headers=auth_headers,
        json={"note": "Skipped today"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "skipped"
