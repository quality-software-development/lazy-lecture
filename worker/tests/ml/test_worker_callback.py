import typing as tp
import json

import pytest
import pika
import pika.channel

from worker.main import process_transcription_job_messages


@pytest.mark.ml
@pytest.mark.integration
def test_worker_callback(
    queue_with_single_task: tp.Tuple[pika.adapters.BlockingConnection, pika.channel.Channel, str, dict]
):
    connection, channel, q_name, job_sent = queue_with_single_task

    # Consume a single message
    method_frame, header_frame, body = channel.basic_get(queue=q_name, auto_ack=False)

    # validate the job id
    job_received = json.loads(body.decode("utf-8"))
    assert method_frame is not None
    assert job_received == job_sent, f"{job_received=} != {job_sent=}"

    # perform the job
    process_transcription_job_messages(channel, method_frame, body)

    # TODO: add status validation in postgre here


@pytest.mark.ml
@pytest.mark.integration
def test_worker_callback_on_long(
    queue_with_single_long_task: tp.Tuple[pika.adapters.BlockingConnection, pika.channel.Channel, str, dict]
):
    connection, channel, q_name, job_sent = queue_with_single_long_task

    # Consume a single message
    method_frame, header_frame, body = channel.basic_get(queue=q_name, auto_ack=False)

    # validate the job id
    job_received = json.loads(body.decode("utf-8"))
    assert method_frame is not None
    assert job_received == job_sent, f"{job_received=} != {job_sent=}"

    # perform the job
    process_transcription_job_messages(channel, method_frame, body)

    # TODO: add status validation in postgre here
