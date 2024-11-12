import typing as tp
from pathlib import Path
import random
import shutil

import pytest
import pika
import whisper

from worker.settings import worker_config, object_storage_config
from worker.task_queue import get_pika_connection, send_transcription_job_to_queue
from worker.whisper_model import whisper_model as w_model


@pytest.fixture
def sample_mp3() -> Path:
    return Path("sample_ru_120s.mp3")


@pytest.fixture(scope="session")
def whisper_model() -> whisper.Whisper:
    return w_model


@pytest.fixture()
def clean_queue():
    connection, channel = get_pika_connection()
    channel.queue_delete(queue=worker_config.PIKA_QUEUE)
    channel.queue_declare(queue=worker_config.PIKA_QUEUE, durable=True)
    yield (connection, channel, worker_config.PIKA_QUEUE)
    connection.close()


@pytest.fixture()
def sample_transcription_file_path():
    fpath = "sample_ru_120s.mp3"
    assert Path(fpath).exists(), fpath
    return fpath


@pytest.fixture()
def long_sample_transcription_file_path():
    fpath = "sample_ru_long.mp3"
    assert Path(fpath).exists(), fpath
    return fpath


@pytest.fixture()
def object_storage_dir():
    assert Path(object_storage_config.PATH).exists(), object_storage_config.PATH
    return object_storage_config.PATH


@pytest.fixture()
def queue_with_single_task(clean_queue, sample_transcription_file_path, object_storage_dir):
    connection, channel, q_name = clean_queue
    user_id = random.randint(10**4, 10**5)
    shutil.copyfile(sample_transcription_file_path, Path(object_storage_dir) / f"{user_id}.mp3")
    transcription_id = random.randint(10**4, 10**5)
    job_sent = send_transcription_job_to_queue(channel, q_name, transcription_id, user_id=user_id)
    return (connection, channel, q_name, job_sent)


@pytest.fixture()
def queue_with_single_long_task(clean_queue, long_sample_transcription_file_path, object_storage_dir):
    connection, channel, q_name = clean_queue
    user_id = random.randint(10**4, 10**5)
    shutil.copyfile(long_sample_transcription_file_path, Path(object_storage_dir) / f"{user_id}.mp3")
    transcription_id = random.randint(10**4, 10**5)
    job_sent = send_transcription_job_to_queue(channel, q_name, transcription_id, user_id=user_id)
    return (connection, channel, q_name, job_sent)
