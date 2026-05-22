from app.tests.conftest import fake


def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": fake.email(),
            "username": fake.user_name(),
            "password": "testpassword123",
        },
    )

    assert response.status_code == 201
    assert "id" in response.json()
    assert "email" in response.json()


def test_register_invalid_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "username": fake.user_name(),
            "password": "testpassword123",
        },
    )

    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": fake.email(),
            "username": fake.user_name(),
            "password": "123",
        },
    )

    assert response.status_code == 422


def test_register_duplicate_email(client):
    email = fake.email()
    payload = {
        "email": email,
        "username": fake.user_name(),
        "password": "testpassword123",
    }

    client.post("/api/v1/auth/register", json=payload)

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 400


def test_login_success(client):
    email = fake.email()
    password = "testpassword123"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": fake.user_name(),
            "password": password,
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_unknown_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == 401


def test_login_invalid_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong@test.com",
            "password": "wrong",
        },
    )

    assert response.status_code == 401
