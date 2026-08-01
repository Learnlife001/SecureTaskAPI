import os

os.environ.setdefault("SECURETASK_DATABASE_URL", "sqlite://")
os.environ.setdefault("SECURETASK_DEBUG", "False")
os.environ.setdefault("SECURETASK_SECRET_KEY", "test-secret-key-at-least-16-characters")
os.environ.setdefault("SECURETASK_METRICS_TOKEN", "test-metrics-token")
os.environ.setdefault("SECURETASK_AUTH_RATE_LIMIT_REQUESTS", "100")


import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import Base, SessionLocal, engine
from app.models.user import User, UserRole

from app import models  # noqa: F401


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers(client):
    client.post(
        "/register",
        json={"email": "user@example.com", "password": "correct-horse"},
    )
    response = client.post(
        "/login",
        data={"username": "user@example.com", "password": "correct-horse"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def admin_headers(client):
    client.post(
        "/register",
        json={"email": "admin@example.com", "password": "correct-horse"},
    )
    with SessionLocal() as db:
        admin = db.query(User).filter(User.email == "admin@example.com").one()
        admin.role = UserRole.admin
        db.commit()
    response = client.post(
        "/login",
        data={"username": "admin@example.com", "password": "correct-horse"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
