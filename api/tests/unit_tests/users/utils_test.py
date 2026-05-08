from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from source.app.users.utils import create_admin


@pytest.mark.asyncio
async def test_create_admin_creates_user_when_absent():
    db = MagicMock()
    db.scalar = AsyncMock(return_value=False)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.close = AsyncMock()

    await create_admin(db)

    db.add.assert_called_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once()
    db.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_admin_skips_when_admin_exists():
    db = MagicMock()
    db.scalar = AsyncMock(return_value=True)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.close = AsyncMock()

    await create_admin(db)

    db.add.assert_not_called()
    db.commit.assert_not_awaited()
    db.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_admin_suppresses_integrity_error():
    db = MagicMock()
    db.scalar = AsyncMock(side_effect=IntegrityError("statement", "params", Exception("duplicate")))
    db.close = AsyncMock()

    await create_admin(db)

    db.close.assert_awaited_once()
