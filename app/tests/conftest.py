import os
from pathlib import Path

from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

_TESTS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _TESTS_DIR.parent.parent

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")
os.environ.setdefault("PLANTNET_API_KEY", "test-plantnet-key")
os.environ.setdefault("PLANTNET_API_URL", "https://example.com/plantnet")
os.environ.setdefault("OPENROUTER_API_KEY", "test-openrouter-key")

(_PROJECT_ROOT / "static").mkdir(exist_ok=True)

from app.main import app  # noqa: E402
from app.core.database import Base, get_db  # noqa: E402

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

fake = Faker()

FIXTURES_DIR = _TESTS_DIR / "fixtures"
TEST_IMAGE_PATH = FIXTURES_DIR / "test_img.jpg"


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    test_db = _PROJECT_ROOT / "test.db"
    if test_db.exists():
        try:
            test_db.unlink()
        except OSError:
            pass


@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def _clean_database(db_session):
    yield
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def auth_token(client):
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
    return response.json()["access_token"]


@pytest.fixture()
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture()
def sample_plant_id(client, auth_headers):
    response = client.post(
        "/api/v1/plants/mock-recognize",
        headers=auth_headers,
    )
    assert response.status_code == 200
    return response.json()["plant_id"]
