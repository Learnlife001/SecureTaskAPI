import os

os.environ["SECURETASK_DATABASE_URL"] = "sqlite://"
os.environ["SECURETASK_DEBUG"] = "False"
os.environ["SECURETASK_SECRET_KEY"] = "testsecret"


import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import Base, engine

from app import models  # noqa: F401

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)
