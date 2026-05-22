def test_get_current_user(client, auth_headers):
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert "email" in response.json()


def test_update_user(client, auth_headers):
    response = client.patch(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"username": "updated_username"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "updated_username"
