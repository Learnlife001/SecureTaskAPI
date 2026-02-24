import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["DEBUG"] = "False"
os.environ["SECRET_KEY"] = "testsecret"


import pytest
from fastapi.testclient import TestClient

from main import app
from db.database import Base, engine

import models

Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)