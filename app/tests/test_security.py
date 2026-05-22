from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    password = "mypassword"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)


def test_verify_wrong_password():
    hashed = hash_password("correct")

    assert verify_password("wrong", hashed) is False


def test_create_access_token():
    token = create_access_token(subject="1")

    assert token is not None


def test_decode_access_token():
    token = create_access_token(subject="1")

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "1"


def test_decode_invalid_token():
    payload = decode_access_token("not-a-valid-jwt")

    assert payload is None
