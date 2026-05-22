from app.core.security import hash_password
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user,
)


def test_create_user_and_get_by_email(db_session):
    user = create_user(
        db_session,
        UserCreate(
            email="service@test.com",
            username="service_user",
            password="password123",
        ),
    )

    found = get_user_by_email(db_session, "service@test.com")

    assert found is not None
    assert found.id == user.id


def test_authenticate_user_success(db_session):
    create_user(
        db_session,
        UserCreate(
            email="auth@test.com",
            username="auth_user",
            password="password123",
        ),
    )

    user = authenticate_user(db_session, "auth@test.com", "password123")

    assert user is not None
    assert user.email == "auth@test.com"


def test_authenticate_user_wrong_password(db_session):
    create_user(
        db_session,
        UserCreate(
            email="wrongpass@test.com",
            username="wrongpass_user",
            password="password123",
        ),
    )

    user = authenticate_user(db_session, "wrongpass@test.com", "wrong")

    assert user is None


def test_update_user_username(db_session):
    user = create_user(
        db_session,
        UserCreate(
            email="update@test.com",
            username="old_name",
            password="password123",
        ),
    )

    updated = update_user(
        db_session,
        user,
        UserUpdate(username="new_name"),
    )

    assert updated.username == "new_name"
    assert get_user_by_id(db_session, user.id).username == "new_name"

