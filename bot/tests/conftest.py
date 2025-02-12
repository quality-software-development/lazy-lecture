import pytest
from unittest.mock import AsyncMock
from handlers.echo import echo_handler

@pytest.mark.asyncio
async def test_echo_handler():
    text_mock = "test123"
    message_mock = AsyncMock(text=text_mock)

    await echo_handler(message=message_mock)

    message_mock.answer.assert_called_with(text_mock)

