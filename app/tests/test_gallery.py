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
