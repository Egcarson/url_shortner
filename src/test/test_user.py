import pytest
from fastapi import status
from unittest.mock import Mock, AsyncMock
from src.app.api import user as user_module


BASE_URL = "/api/v1"

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

user_data = {
    "first_name": "test1",
    "last_name": "test1",
    "username": "test1",
    "email_address": "test1@gmail.com",
    "id": 1,
    "created_at": "2025-07-17T21:47:42.633973"
}

@pytest.mark.asyncio
async def test_get_users(fake_session, testclient, monkeypatch, skip: int=0, limit:int=10,):

    mock_service = Mock()

    mock_service.get_users = AsyncMock(return_value=users)

    monkeypatch.setattr(user_module, "user_services", mock_service)

    response = testclient.get(f"{BASE_URL}/users")
   
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]['first_name'] == "test1"

    mock_service.get_users.assert_awaited()
    mock_service.get_users.assert_awaited_once_with(skip, limit, fake_session)

@pytest.mark.asyncio
async def test_get_single_user_success(fake_session, testclient, monkeypatch):
    
    user_id = 1
    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=user_data)

    monkeypatch.setattr(user_module, "user_services", mock_service)

    response = testclient.get(f"{BASE_URL}/users/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "test1"

    mock_service.get_user.assert_awaited_once_with(user_id, fake_session)

@pytest.mark.asyncio
async def test_get_single_user_not_found(fake_session, testclient, monkeypatch):
    
    user_id = 10
    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=None)

    monkeypatch.setattr(user_module, "user_services", mock_service)

    response = testclient.get(f"{BASE_URL}/users/{user_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "User not found"

@pytest.mark.asyncio
async def test_update_user_success(fake_session, testclient, monkeypatch):

    user_id = 1
    existing_user = Mock()
    existing_user.first_name = "test1"
    existing_user.last_name = "test1"
    existing_user.username = "test1"
    existing_user.email_address = "test1@gmail.com"
    existing_user.id = user_id
    existing_user.created_at = "2025-07-17T21:47:42.633973"

    update_data = {
        "first_name": "test4",
        "last_name": "test4",
        "username": "test4"
        }

    payload = {
        **update_data,
        "email_address": "test1@gmail.com",
        "id": 1,
        "created_at": "2025-07-17T21:47:42.633973"
        }

    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=existing_user)
    mock_service.update_user = AsyncMock(return_value=payload)

    monkeypatch.setattr(user_module, "user_services", mock_service)

    response = testclient.put(f"{BASE_URL}/users/{user_id}", json=update_data)

    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert data["username"] == "test4"
    
    mock_service.get_user.assert_awaited()
    mock_service.update_user.assert_awaited()

@pytest.mark.asyncio
async def test_update_user_not_found(fake_session, testclient, monkeypatch):

    user_id = 1

    update_data = {
        "first_name": "test4",
        "last_name": "test4",
        "username": "test4"
        }

    payload = {
        **update_data,
        "email_address": "test1@gmail.com",
        "id": 1,
        "created_at": "2025-07-17T21:47:42.633973"
        }

    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=None)
    mock_service.update_user = AsyncMock(return_value=payload)

    monkeypatch.setattr(user_module, "user_services", mock_service)

    response = testclient.put(f"{BASE_URL}/users/{user_id}", json=update_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "User not found"


@pytest.mark.asyncio
async def test_delete_user_success(fake_session, testclient, monkeypatch):

    user_id = 1
    fake_user = Mock()
    fake_user.id = user_id

    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=fake_user)
    mock_service.delete_user = AsyncMock()

    monkeypatch.setattr(user_module, "user_services", mock_service)

    response = testclient.delete(f"{BASE_URL}/users/{user_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    mock_service.get_user.assert_awaited_once_with(user_id, fake_session)
    mock_service.delete_user.assert_awaited_once_with(user_id, fake_session)


@pytest.mark.asyncio
async def test_delete_user_user_not_found(fake_session, testclient, monkeypatch):

    user_id = 1

    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=None)
    mock_service.delete_user = AsyncMock()

    monkeypatch.setattr(user_module, "user_services", mock_service)

    response = testclient.delete(f"{BASE_URL}/users/{user_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    mock_service.get_user.assert_awaited_once_with(user_id, fake_session)