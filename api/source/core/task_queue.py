from typing import Any, AsyncGenerator, Tuple, Optional
import contextlib
import pika
import pika.channel

from source.core.settings import settings


def get_pika_connection():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.PIKA_HOST,
            port=settings.PIKA_PORT,
            credentials=pika.PlainCredentials(username=settings.PIKA_USER, password=settings.PIKA_PASS),
            connection_attempts=3,
            retry_delay=5,
        )
    )
    channel = connection.channel()
    queue_name = settings.PIKA_QUEUE
    channel.queue_declare(queue=queue_name, durable=True)
    return connection, channel, queue_name


@contextlib.asynccontextmanager
async def get_task_queue() -> AsyncGenerator[Tuple[Optional[pika.channel.Channel], str], Any]:
    """
    Если DISABLE_WORKER=true – возвращаем (None, '')
    иначе – настоящую очередь
    """
    if settings.DISABLE_WORKER:
        yield None, ""  # «пустая» очередь
        return

    connection, channel, queue_name = get_pika_connection()
    try:
        yield channel, queue_name
    finally:
        connection.close()
