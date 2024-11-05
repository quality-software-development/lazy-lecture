import json
import typing as tp

import pika
import pika.channel

from .settings import worker_config


def get_pika_connection(host: tp.Optional[str] = None, port: tp.Optional[int] = None):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host or worker_config.PIKA_HOST,
            port=port or worker_config.PIKA_PORT,
            credentials=pika.PlainCredentials(username=worker_config.PIKA_USER, password=worker_config.PIKA_PASS),
            connection_attempts=3,
            retry_delay=5,
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=worker_config.PIKA_QUEUE, durable=True)
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
