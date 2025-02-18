import json
import typing as tp

import pika
import pika.channel


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
