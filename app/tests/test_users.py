from app.tests.conftest import TEST_IMAGE_PATH


def test_get_current_user(client, auth_headers):
    response = client.get(
        "/api/v1/users/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert "email" in response.json()


def test_get_current_user_unauthorized(client):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_get_current_user_invalid_token(client):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_update_user(client, auth_headers):
    response = client.patch(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"username": "updated_username"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "updated_username"


def test_upload_avatar_success(client, auth_headers):
    with TEST_IMAGE_PATH.open("rb") as image:
        response = client.post(
            "/api/v1/users/me/avatar",
            headers=auth_headers,
            files={"file": ("avatar.jpg", image, "image/jpeg")},
        )

    assert response.status_code == 200
    assert response.json()["avatar_url"].startswith("/static/uploads/avatars/")


def test_upload_avatar_invalid_type(client, auth_headers):
    response = client.post(
        "/api/v1/users/me/avatar",
        headers=auth_headers,
        files={"file": ("avatar.txt", b"text", "text/plain")},
    )

    assert response.status_code == 400


def test_upload_avatar_unauthorized(client):
    with TEST_IMAGE_PATH.open("rb") as image:
        response = client.post(
            "/api/v1/users/me/avatar",
            files={"file": ("avatar.jpg", image, "image/jpeg")},
        )

    assert response.status_code == 401
