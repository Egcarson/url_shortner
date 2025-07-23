import pytest
from unittest.mock import AsyncMock, Mock
from fastapi import status
from src.app.api import shortner as url_module
from datetime import datetime, timedelta, timezone

BASE_URL = "api/v1/urls"

url_short_code = "ABC123"

url_data = {
    "original_url": "https://google.com/",
    "short_code": url_short_code,
    "is_active": True,
    "expires_at": "2025-07-21T19:16:29.290Z",
    "id": 1,
    "user_id": 1,
    "created_at": "2025-07-21T19:16:29.290Z",
    "click_count": 0
    }

url_payload = {
    "original_url": "https://google.com/",
    "short_code": url_short_code,
    "is_active": True,
    "expires_at": "2025-07-21T19:21:10.759Z"
    }

urls = [
    {
    "original_url": "https://google.com/",
    "short_code": url_short_code,
    "is_active": True,
    "expires_at": "2025-07-21T19:16:29.290Z",
    "id": 1,
    "user_id": 1,
    "created_at": "2025-07-21T19:16:29.290Z",
    "click_count": 0
    }
]


@pytest.mark.asyncio
async def test_create_short_url_success(fake_session, testclient, monkeypatch):

    mock_service = Mock()
    mock_service.existing_short_code = AsyncMock(return_value=None)
    mock_service.create_short_url = AsyncMock(return_value=url_data)

    monkeypatch.setattr(url_module, "url_services", mock_service)

    
    response = testclient.post(f"{BASE_URL}", json=url_payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["original_url"] == "https://google.com/"
    assert data["short_code"] == url_short_code

    mock_service.existing_short_code.assert_awaited()
    mock_service.create_short_url.assert_awaited()


@pytest.mark.asyncio
async def test_create_short_url_already_exists(fake_session, testclient, monkeypatch):

    mock_service = Mock()
    mock_service.existing_short_code = AsyncMock(return_value=url_data)
    mock_service.create_short_url = AsyncMock(return_value=url_data)

    monkeypatch.setattr(url_module, "url_services", mock_service)

    
    response = testclient.post(f"{BASE_URL}", json=url_payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["detail"] == "Shortcode already exists. Please choose another or autogenerate."

    mock_service.existing_short_code.assert_awaited()


@pytest.mark.asyncio
async def test_get_urls(fake_session, testclient, monkeypatch):

    fake_user = 1

    mock_service = Mock()
    mock_service.get_urls = AsyncMock(return_value=urls)

    monkeypatch.setattr(url_module, "url_services", mock_service)

    response = testclient.get(f"{BASE_URL}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]["original_url"] == "https://google.com/"
    assert data[0]["short_code"] == url_short_code

    mock_service.get_urls.assert_awaited_once_with(fake_user, fake_session)


@pytest.mark.asyncio
async def test_redirect_to_original_url_success(fake_session, testclient, monkeypatch):

    mock_url = Mock()
    mock_url.original_url = "https://google.com"
    mock_url.is_active = True
    mock_url.expires_at = datetime.now() + timedelta(days=1)
    mock_url.click_count = 0

    mock_service = Mock()
    mock_service.existing_short_code = AsyncMock(return_value=mock_url)
    mock_service.redirect_url = AsyncMock(return_value=None)

    monkeypatch.setattr(url_module, "url_services", mock_service)

    response = testclient.get(f"{BASE_URL}/{url_short_code}", follow_redirects=False)

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

    mock_service.existing_short_code.assert_awaited()
    mock_service.redirect_url.assert_awaited()