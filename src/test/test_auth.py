import pytest
from fastapi import status
from unittest.mock import Mock, AsyncMock
from src.app.api import auth as auth_module
from src.app.schemas import UserCreate

BASE_URL = "/api/v1/auth"

users = [
  {
    "first_name": "test1",
    "last_name": "test1",
    "username": "test1",
    "email_address": "test1@gmail.com",
    "id": 1,
    "created_at": "2025-07-17T21:47:42.633973"
  },

  {
    "first_name": "test2",
    "last_name": "test2",
    "username": "test2",
    "email_address": "test2@gmail.com",
    "id": 2,
    "created_at": "2025-07-17T21:47:42.633973"
  }
]

user_payload = {
    "first_name": "test1",
    "last_name": "test1",
    "username": "test1",
    "email_address": "test1@gmail.com",
    "hashed_password": "Dyoung@20"
}

user_data = {
    "first_name": "test1",
    "last_name": "test1",
    "username": "test1",
    "email_address": "test1@gmail.com",
    "id": 1,
    "created_at": "2025-07-17T21:47:42.633973"
}

@pytest.mark.asyncio
async def test_signup_success(fake_session, testclient, monkeypatch):

    mock_user_service = Mock()
    mock_user_service.get_user_by_email = AsyncMock(return_value=None)
    mock_user_service.create_user = AsyncMock(return_value=user_data)

    monkeypatch.setattr(auth_module, "user_services", mock_user_service)

    # signup_data = UserCreate(**user_payload)

    response = testclient.post(f"{BASE_URL}/signup", json=user_payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['username'] == "test1"
    assert data["email_address"] == "test1@gmail.com"

    mock_user_service.get_user_by_email.assert_awaited()
    mock_user_service.create_user.assert_awaited()

@pytest.mark.asyncio
async def test_signup_user_already_exists(fake_session, testclient, monkeypatch):

    mock_user_service = Mock()
    mock_user_service.get_user_by_email = AsyncMock(return_value=user_data)
    mock_user_service.create_user = AsyncMock(return_value=user_data)

    monkeypatch.setattr(auth_module, "user_services", mock_user_service)

    # signup_data = UserCreate(**user_payload)

    response = testclient.post(f"{BASE_URL}/signup", json=user_payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    data = response.json()
    assert data['detail'] == "User already exists!"

    mock_user_service.get_user_by_email.assert_awaited()
    

@pytest.mark.asyncio
async def test_login_success(fake_session, testclient, monkeypatch):

    fake_user = Mock()
    fake_user.id = 1
    fake_user.email_address = "test1@gmail.com"
    fake_user.hashed_password = "Dyoung@20"

    mock_service = Mock()
    mock_service.get_username = AsyncMock(return_value=fake_user)

    monkeypatch.setattr(auth_module, "user_services", mock_service)
    monkeypatch.setattr(auth_module, "verify_password", lambda p, h: True)
    monkeypatch.setattr(auth_module, "create_access_token", lambda user_data, refresh=False, expiry=None: "fake_token_" + ("refresh" if refresh else "access"))

    payload = {
        "username": "test1@gmail.com",
        "password": "Dyoung@20"
    }

    response = testclient.post(f"{BASE_URL}/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "User logged in successfully"

@pytest.mark.asyncio
async def test_login_invalid_info(fake_session, testclient, monkeypatch):

    fake_user = Mock()
    fake_user.id = 1
    fake_user.email_address = "test1@gmail.com"

    mock_service = Mock()
    mock_service.get_username = AsyncMock(return_value=None)

    monkeypatch.setattr(auth_module, "user_services", mock_service)
    monkeypatch.setattr(auth_module, "verify_password", lambda p, h: True)
    monkeypatch.setattr(auth_module, "create_access_token", lambda user_data, refresh=False, expiry=None: "fake_token_" + ("refresh" if refresh else "access"))

    payload = {
        "username": "test1@gmail.com",
        "password": "Dyoung@20"
    }

    response = testclient.post(f"{BASE_URL}/login", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()

    assert data['detail'] == "Invalid username or password"


@pytest.mark.asyncio
async def test_logout_success(monkeypatch, testclient):
    mock_blacklist_token = AsyncMock()
    mock_delete_expired_tokens = Mock()

    monkeypatch.setattr(auth_module, "blacklist_token", mock_blacklist_token)
    monkeypatch.setattr(auth_module, "delete_expired_tokens", mock_delete_expired_tokens)

    token = "valid.jwt.token"

    response = testclient.post("/api/v1/auth/logout", params={"token": token})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Logged out successfully!"
    mock_blacklist_token.assert_called_once()

@pytest.mark.asyncio
async def test_logout_invalid_token(monkeypatch, testclient):
    async def raise_value_error(token, session):
        raise ValueError("Invalid token")

    monkeypatch.setattr(auth_module, "blacklist_token", raise_value_error)
    monkeypatch.setattr(auth_module, "delete_expired_tokens", Mock())

    token = "invalid.jwt.token"

    response = testclient.post("/api/v1/auth/logout", params={"token": token})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["detail"] == "Invalid Token"