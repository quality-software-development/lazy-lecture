from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from source.app.users.enums import Roles
from source.app.users.models import User
from source.app.users.schemas import UserRequest, UserUpdateRequest
from source.app.users.views import user_create, user_get, user_update


def make_user(user_id=1, username="ValidUser"):
    now = datetime.now(timezone.utc)
    user = User()
    user.id = user_id
    user.username = username
    user.password = "hash"
    user.active = True
    user.can_interact = False
    user.role = Roles.USER
    user.password_timestamp = 123.0
    user.create_date = now
    user.update_date = now
    return user


@pytest.mark.asyncio
async def test_user_create_view_success(monkeypatch):
    created = make_user()
    monkeypatch.setattr("source.app.users.views.create_user", AsyncMock(return_value=created))

    result = await user_create(UserRequest(username="ValidUser", password="StrongPass1!"), db=AsyncMock())

    assert result is created


@pytest.mark.asyncio
async def test_user_create_view_conflict(monkeypatch):
    monkeypatch.setattr("source.app.users.views.create_user", AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc_info:
        await user_create(UserRequest(username="ValidUser", password="StrongPass1!"), db=AsyncMock())

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail


@pytest.mark.asyncio
async def test_user_get_view_returns_current_user():
    user = make_user()

    assert await user_get(user) is user


@pytest.mark.asyncio
async def test_user_update_view_success(monkeypatch):
    user = make_user()
    updated = make_user()
    updated.can_interact = True
    monkeypatch.setattr("source.app.users.views.get_user_by_id", AsyncMock(return_value=user))
    monkeypatch.setattr("source.app.users.views.update_user", AsyncMock(return_value=updated))

    result = await user_update(
        user_id=1,
        request=UserUpdateRequest(can_interact=True),
        admin_secret_token="secret",
        db=AsyncMock(),
    )

    assert result is updated


@pytest.mark.asyncio
async def test_user_update_view_conflict(monkeypatch):
    user = make_user()
    monkeypatch.setattr("source.app.users.views.get_user_by_id", AsyncMock(return_value=user))
    monkeypatch.setattr("source.app.users.views.update_user", AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc_info:
        await user_update(
            user_id=1,
            request=UserUpdateRequest(can_interact=True),
            admin_secret_token="secret",
            db=AsyncMock(),
        )

    assert exc_info.value.status_code == 409
    assert "ValidUser" in exc_info.value.detail
