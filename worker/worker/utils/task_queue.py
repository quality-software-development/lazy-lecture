import json
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


def send_transcription_job_to_queue(
    channel: pika.channel.Channel,
    queue_name: str,
    transcription_id: int,
    user_id: int,
) -> tp.Mapping[str, tp.Any]:
    job_dict = {
        "transcription_id": transcription_id,
        "user_id": user_id,
    }
    channel.basic_publish(exchange="", routing_key=queue_name, body=json.dumps(job_dict))
    return job_dict
