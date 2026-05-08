from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from source.core import database
from source.core.exceptions import bad_request, conflict, forbidden, not_found
from source.core.schemas import PaginationSchema
from source.core.task_queue import get_pika_connection, get_task_queue


@pytest.mark.asyncio
async def test_get_db_yields_and_closes_session(monkeypatch):
    session = MagicMock()
    session.close = AsyncMock()
    monkeypatch.setattr(database, "SessionLocal", MagicMock(return_value=session))

    generator = database.get_db()
    yielded = await generator.__anext__()
    assert yielded is session
    with pytest.raises(StopAsyncIteration):
        await generator.__anext__()

    session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_database_health_success():
    db = MagicMock()
    db.execute = AsyncMock()

    assert await database.database_health(db) is True


@pytest.mark.asyncio
async def test_database_health_failure():
    db = MagicMock()
    db.execute = AsyncMock(side_effect=RuntimeError("db down"))

    assert await database.database_health(db) is False


@pytest.mark.parametrize(
    "exception_factory,status_code",
    [
        (bad_request, 400),
        (forbidden, 403),
        (not_found, 404),
        (conflict, 409),
    ],
)
def test_exception_helpers_raise_http_exception(exception_factory, status_code):
    with pytest.raises(HTTPException) as exc_info:
        exception_factory("detail")

    assert exc_info.value.status_code == status_code
    assert exc_info.value.detail == "detail"


def test_pagination_schema_validation_error_becomes_http_exception():
    with pytest.raises(HTTPException) as exc_info:
        PaginationSchema(page=0, size=10)

    assert exc_info.value.status_code == 422


def test_get_pika_connection_declares_queue(monkeypatch):
    channel = MagicMock()
    connection = MagicMock()
    connection.channel.return_value = channel
    blocking_connection = MagicMock(return_value=connection)
    monkeypatch.setattr("source.core.task_queue.pika.BlockingConnection", blocking_connection)

    result_connection, result_channel, queue_name = get_pika_connection()

    assert result_connection is connection
    assert result_channel is channel
    assert queue_name
    channel.queue_declare.assert_called_once_with(queue=queue_name, durable=True)


@pytest.mark.asyncio
async def test_get_task_queue_disabled_worker(monkeypatch):
    monkeypatch.setattr("source.core.task_queue.settings.DISABLE_WORKER", True)

    generator = get_task_queue()
    queue = await generator.__anext__()

    assert queue == (None, "")
    with pytest.raises(StopAsyncIteration):
        await generator.__anext__()


@pytest.mark.asyncio
async def test_get_task_queue_closes_connection(monkeypatch):
    connection = MagicMock()
    channel = MagicMock()
    monkeypatch.setattr("source.core.task_queue.settings.DISABLE_WORKER", False)
    monkeypatch.setattr("source.core.task_queue.get_pika_connection", MagicMock(return_value=(connection, channel, "q")))

    generator = get_task_queue()
    queue = await generator.__anext__()
    assert queue == (channel, "q")
    with pytest.raises(StopAsyncIteration):
        await generator.__anext__()

    connection.close.assert_called_once()
