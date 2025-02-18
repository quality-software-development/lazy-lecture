from typing import AsyncGenerator, Iterable
from unittest.mock import AsyncMock, MagicMock, Mock, patch
import pytest

from worker.core.task_consumer import AioPikaTaskConsumer
from worker.core.settings import Settings


@pytest.fixture
def queue_consumer(test_settings: Settings) -> AioPikaTaskConsumer:
    return AioPikaTaskConsumer.from_settings(test_settings)


# Техника тест-дизайна: диаграмма состояний
# Автор: Илья Тампио
# AioPikaTaskConsumer
# Состояния:
# - Не подключен
# - Подключён
# Переходы:
# - Начало: Не подключён
# - Переход в подключен при: _connect(), process_message()
# - Не подключается ещё один раз, если уже подключён
@pytest.mark.asyncio
@patch("aio_pika.connect_robust", new_callable=AsyncMock)
async def test_task_consumer_connection_state_using_connect(
    mock_connect: Mock, queue_consumer: AioPikaTaskConsumer, test_settings: Settings
):
    mock_connection = AsyncMock()
    mock_connect.return_value = mock_connection

    # Начало: Не подключён
    assert queue_consumer.connection is None

    # Переход: _connect()
    await queue_consumer._connect()
    mock_connect.assert_called_once_with(test_settings.aio_pika_connection_string)
    assert queue_consumer.connection is mock_connection

    # Переход: _connect() - не подключается лишний раз
    await queue_consumer._connect()
    mock_connect.assert_called_once()  # checks that it is not twice


async def iterate_async(iterable: Iterable) -> AsyncGenerator:
    for item in iterable:
        yield item


@pytest.mark.asyncio
@patch("aio_pika.connect_robust", new_callable=AsyncMock)
@patch("worker.core.task_consumer.AioPikaTaskConsumer._read_messages", new_callable=Mock)
async def test_task_consumer_connection_state_using_process_messages(
    mock_iterable, mock_connect, test_settings: Settings
):
    mock_connection = AsyncMock()
    mock_connect.return_value = mock_connection
    mock_message = Mock()
    mock_iterable.return_value = iterate_async([mock_message])

    queue_consumer = AioPikaTaskConsumer.from_settings(test_settings)

    # Начало: Не подключён
    assert queue_consumer.connection is None
    # Переход: process_messages()
    async for message in queue_consumer.process_messages():
        break  # Сразу выходим

    mock_connect.assert_called_once_with(test_settings.aio_pika_connection_string)
    assert queue_consumer.connection is mock_connection
    # Переход: _connect() - не подключается лишний раз
    await queue_consumer._connect()
    mock_connect.assert_called_once()  # checks that it is not twice
