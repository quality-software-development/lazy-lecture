from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from source.app.auth.schemas import Credentials, Refresh
from source.app.auth.views import refresh, token


@pytest.mark.asyncio
async def test_token_view_success(monkeypatch):
    user = type("User", (), {"id": 1, "password_timestamp": 123.0})()
    generated_token = {"access_token": "access", "refresh_token": "refresh", "token_type": "bearer"}

    monkeypatch.setattr("source.app.auth.views.authenticate_user", AsyncMock(return_value=user))
    generate_mock = AsyncMock(return_value=generated_token)
    monkeypatch.setattr("source.app.auth.views.generate_token", generate_mock)

    result = await token(Credentials(username="ValidUser", password="StrongPass1!"), db=AsyncMock())

    assert result == generated_token
    generate_mock.assert_awaited_once_with(user_id=1, password_timestamp=123.0)


@pytest.mark.asyncio
async def test_token_view_wrong_credentials(monkeypatch):
    monkeypatch.setattr("source.app.auth.views.authenticate_user", AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc_info:
        await token(Credentials(username="ValidUser", password="StrongPass1!"), db=AsyncMock())

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect username or password"


@pytest.mark.asyncio
async def test_refresh_view_success(monkeypatch):
    refreshed = {"access_token": "new_access", "refresh_token": "new_refresh", "token_type": "bearer"}
    monkeypatch.setattr("source.app.auth.views.authenticate_refresh_token", AsyncMock(return_value=refreshed))

    result = await refresh(Refresh(refresh_token="refresh"), db=AsyncMock())

    assert result == refreshed


@pytest.mark.asyncio
async def test_refresh_view_invalid_token(monkeypatch):
    monkeypatch.setattr("source.app.auth.views.authenticate_refresh_token", AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc_info:
        await refresh(Refresh(refresh_token="bad"), db=AsyncMock())

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid or expired token"
