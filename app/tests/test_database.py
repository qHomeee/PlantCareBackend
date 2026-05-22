from app.core.security import hash_password
from app.models.user import User


def test_create_user(db_session):
    user = User(
        email="test@test.com",
        username="test",
        hashed_password=hash_password("password123"),
    )

    db_session.add(user)
    db_session.commit()

    saved_user = db_session.query(User).filter(User.email == "test@test.com").first()

    assert saved_user is not None
    assert saved_user.email == "test@test.com"
