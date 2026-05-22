def _add_gallery_item(client, auth_headers, sample_plant_id):
    return client.post(
        "/api/v1/gallery",
        headers=auth_headers,
        json={
            "plant_id": sample_plant_id,
            "custom_name": "Watering test plant",
        },
    )


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


def test_watering_events_filter_planned(client, auth_headers, sample_plant_id):
    _add_gallery_item(client, auth_headers, sample_plant_id)

    response = client.get(
        "/api/v1/care/watering-events?status=planned",
        headers=auth_headers,
    )

    assert response.status_code == 200
    events = response.json()
    assert events
    assert all(event["status"] == "planned" for event in events)


def test_get_plant_watering_events(client, auth_headers, sample_plant_id):
    add_response = _add_gallery_item(client, auth_headers, sample_plant_id)
    user_plant_id = add_response.json()["id"]

    response = client.get(
        f"/api/v1/care/user-plants/{user_plant_id}/watering-events",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_get_plant_watering_events_not_found(client, auth_headers):
    response = client.get(
        "/api/v1/care/user-plants/99999/watering-events",
        headers=auth_headers,
    )

    assert response.status_code == 404


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


def test_complete_watering_not_found(client, auth_headers):
    response = client.patch(
        "/api/v1/care/watering-events/99999/complete",
        headers=auth_headers,
        json={"note": "test"},
    )

    assert response.status_code == 404


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


def test_care_unauthorized(client):
    response = client.get("/api/v1/care/watering-events")

    assert response.status_code == 401
