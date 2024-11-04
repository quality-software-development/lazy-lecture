import typing as tp
from pathlib import Path

import pika.adapters.blocking_connection
import pika.channel
import pytest
import pika
import whisper

from worker.settings import worker_config


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
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=worker_config.PIKA_HOST,
            port=worker_config.PIKA_PORT,
            credentials=pika.PlainCredentials(username=worker_config.PIKA_USER, password=worker_config.PIKA_PASS),
            connection_attempts=3,
            retry_delay=5,
        )
    )
    channel = connection.channel()
    channel.queue_delete(queue=worker_config.PIKA_QUEUE)
    channel.queue_declare(queue=worker_config.PIKA_QUEUE, durable=True)
    yield (connection, channel, worker_config.PIKA_QUEUE)
    connection.close()
