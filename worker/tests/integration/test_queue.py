import json
import random

from worker.task_queue import send_transcription_job_to_queue


def test_send_receive_hello_world(clean_queue):
    connection, channel, queue = clean_queue
    body_sent = "Hello World!"

    channel.basic_publish(exchange="", routing_key=queue, body=body_sent)

    # Consume a single message
    method_frame, header_frame, body_received = channel.basic_get(queue=queue, auto_ack=True)
    body_received = body_received.decode("utf-8")
    assert method_frame is not None
    assert body_received == body_sent, f"{body_received=} != {body_sent=}"


def test_send_receive_single_job(clean_queue):
    connection, channel, queue = clean_queue
    job_sent = send_transcription_job_to_queue(
        channel, queue, random.randint(10**4, 10**6), random.randint(10**4, 10**6)
    )

    # Consume a single message
    method_frame, header_frame, job_received = channel.basic_get(queue=queue, auto_ack=True)
    job_received = json.loads(job_received.decode("utf-8"))
    assert method_frame is not None
    assert job_received == job_sent, f"{job_received=} != {job_sent=}"
