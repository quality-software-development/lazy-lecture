import typing as tp

import pika
import pika.channel

from worker.core.settings import settings


def get_pika_connection(host: tp.Optional[str] = None, port: tp.Optional[int] = None):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host or settings.pika_host,
            port=port or settings.pika_port,
            credentials=pika.PlainCredentials(username=settings.pika_user, password=settings.pika_pass),
            connection_attempts=3,
            retry_delay=5,
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=settings.pika_queue, durable=True)
    return connection, channel
