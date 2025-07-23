import pytest
from unittest.mock import AsyncMock, Mock
from fastapi.testclient import TestClient
from src.app.db.main import get_session
from src.app.core.dependencies import get_current_user
from src import app

FAKE_USER_ID = 1

class FakeUser:
    def __init__(self, id):
        self.id = id

fake_user = FakeUser(id=FAKE_USER_ID)

async def get_current_user_id():
    return fake_user

mock_session = Mock()

def get_mock_session():
    yield mock_session


@pytest.fixture
def fake_session():
    return mock_session

@pytest.fixture
def testclient():
    app.dependency_overrides[get_session] = get_mock_session
    app.dependency_overrides[get_current_user] = get_current_user_id
    return TestClient(app)
