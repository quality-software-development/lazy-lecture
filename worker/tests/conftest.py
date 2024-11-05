import typing as tp
from pathlib import Path

import pytest
import pika
import whisper

from worker.settings import worker_config
from worker.task_queue import get_pika_connection


@pytest.fixture
def sample_mp3() -> Path:
    return Path("sample_ru_120s.mp3")


@pytest.fixture(scope="session")
def whisper_model() -> whisper.Whisper:
    return whisper.load_model(
        name=worker_config.MODEL_NAME,
        device=worker_config.DEVICE,
        download_root=worker_config.DOWNLOAD_ROOT,
        in_memory=True,
    )


@pytest.fixture()
def clean_rabbitmq_queue():
    connection, channel = get_pika_connection()
    channel.queue_delete(queue=worker_config.PIKA_QUEUE)
    channel.queue_declare(queue=worker_config.PIKA_QUEUE, durable=True)
    yield (connection, channel, worker_config.PIKA_QUEUE)
    connection.close()
