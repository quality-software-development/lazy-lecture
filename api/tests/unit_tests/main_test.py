from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI

from source.main import health_check, lifespan, validation_exception_handler


@pytest.mark.asyncio
async def test_lifespan_creates_admin(monkeypatch):
    create_admin_mock = AsyncMock()
    monkeypatch.setattr("source.main.create_admin", create_admin_mock)

    async with lifespan(FastAPI()):
        create_admin_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_validation_exception_handler_returns_teapot_response():
    response = await validation_exception_handler(request=None, exc=RuntimeError("boom"))

    assert response.status_code == 418
    assert b"boom" in response.body


@pytest.mark.asyncio
async def test_health_check_uses_database_health(monkeypatch):
    monkeypatch.setattr("source.main.database_health", AsyncMock(return_value=True))

    result = await health_check(db=AsyncMock())

    assert result.api is True
    assert result.database is True
