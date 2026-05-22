def test_add_plant_to_gallery(client, auth_headers, sample_plant_id):
    response = client.post(
        "/api/v1/gallery",
        headers=auth_headers,
        json={
            "plant_id": sample_plant_id,
            "custom_name": "My Monstera",
        },
    )

    assert response.status_code == 201
    assert response.json()["custom_name"] == "My Monstera"


def test_add_plant_not_found(client, auth_headers):
    response = client.post(
        "/api/v1/gallery",
        headers=auth_headers,
        json={
            "plant_id": 99999,
            "custom_name": "Missing plant",
        },
    )

    assert response.status_code == 404


def test_get_gallery(client, auth_headers, sample_plant_id):
    client.post(
        "/api/v1/gallery",
        headers=auth_headers,
        json={
            "plant_id": sample_plant_id,
            "custom_name": "My Monstera",
        },
    )

    response = client.get(
        "/api/v1/gallery",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1


def test_get_gallery_item(client, auth_headers, sample_plant_id):
    add_response = client.post(
        "/api/v1/gallery",
        headers=auth_headers,
        json={
            "plant_id": sample_plant_id,
            "custom_name": "My Monstera",
        },
    )

    user_plant_id = add_response.json()["id"]

    response = client.get(
        f"/api/v1/gallery/{user_plant_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == user_plant_id


def test_get_gallery_item_not_found(client, auth_headers):
    response = client.get(
        "/api/v1/gallery/99999",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_update_gallery_item(client, auth_headers, sample_plant_id):
    add_response = client.post(
        "/api/v1/gallery",
        headers=auth_headers,
        json={
            "plant_id": sample_plant_id,
            "custom_name": "Old name",
        },
    )

    user_plant_id = add_response.json()["id"]

    response = client.patch(
        f"/api/v1/gallery/{user_plant_id}",
        headers=auth_headers,
        json={"custom_name": "New name"},
    )

    assert response.status_code == 200
    assert response.json()["custom_name"] == "New name"


def test_get_gallery_unauthorized(client):
    response = client.get("/api/v1/gallery")

    assert response.status_code == 401


def test_delete_plant_from_gallery(client, auth_headers, sample_plant_id):
    add_response = client.post(
        "/api/v1/gallery",
        headers=auth_headers,
        json={
            "plant_id": sample_plant_id,
            "custom_name": "My Monstera",
        },
    )

    user_plant_id = add_response.json()["id"]

    response = client.delete(
        f"/api/v1/gallery/{user_plant_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204
