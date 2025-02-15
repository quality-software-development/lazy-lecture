import time
import json
import os
import traceback
from pathlib import Path

import pika
import pika.channel
from pika.exceptions import AMQPConnectionError

from worker.core.settings import settings, Settings
from worker.worker.core.whisper_predictor import WhisperPredictor
from worker.utils.audio import get_audio_len
from worker.utils.api import (
    get_transcription_state_chunk_size_secs,
    update_transcription_state,
    TranscriptionState,
    CreateTranscriptionChunk,
)
from worker.core.task_queue import TaskQueueManager, PikaTaskQueueManager


def get_user_audio_path(user_id: int, object_storage_root: Path, raise_if_not_found: bool = True) -> Path:
    if not object_storage_root.exists():
        raise FileNotFoundError(f"Object Storage Path does not exist ({str(object_storage_root)})")
    expected_user_audiofile_path = object_storage_root / f"{user_id}.mp3"
    if not expected_user_audiofile_path.exists() and raise_if_not_found:
        raise FileNotFoundError(f"User audiofile is not present at {str(expected_user_audiofile_path)}")
    return expected_user_audiofile_path


def ack(
    ch: pika.channel.Channel,
    delivery_tag: int,
    negative: bool = False,
    requeue: bool = False,
):
    if negative:
        ch.basic_reject(delivery_tag=delivery_tag, requeue=requeue)
        if requeue:
            print("[x] Job Requeued :/")
        else:
            print("[x] Job Rejected :(")
    else:
        ch.basic_ack(delivery_tag=delivery_tag)
        print("[x] Job Done :)")


def process_transcription_job_messages(ch: pika.channel.Channel, method, body):
    try:
        message = body.decode()
        job_dict = json.loads(message)
        user_id = job_dict["user_id"]
        transcription_id = job_dict["transcription_id"]

        print("[x] Received message: ", str(message))
        print("[x] Received job: ", str(job_dict))

        transcription_state, chunk_size_secs = get_transcription_state_chunk_size_secs(transcription_id)
        if transcription_state in [
            TranscriptionState.COMPLETED,
            TranscriptionState.COMPLETED_PARTIALLY,
            TranscriptionState.PROCESSING_FAIL,
            TranscriptionState.CANCELLED,
        ]:
            print("[x] Job has already been terminated, skip")
            ack(ch, method.delivery_tag)
            return
        update_transcription_state(transcription_id, TranscriptionState.IN_PROGRESS)

        user_audio_path: Path = get_user_audio_path(user_id, Path(settings.PATH), raise_if_not_found=True)

        print("[x] Inference Begin!")
        audio_len_s: float = get_audio_len(user_audio_path)
        print(f"[x] Audio len: {audio_len_s}")
        clip_timestamps = [
            [v, min(audio_len_s, v + chunk_size_secs)] for v in range(0, int(audio_len_s) + 1, chunk_size_secs)
        ]
        clip_timestamps[-1] = [
            clip_timestamps[-1][0],
        ]
        print(f"[x] Clip timestamps: {clip_timestamps}")

        for chunk_no, clip_timestamp in enumerate(clip_timestamps):
            print(f"[x] Processing clip {clip_timestamp}")
            start = time.time()
            text, segments = transcribe_audio_file(user_audio_path, whisper_model, clip_timestamp=clip_timestamp)
            end = time.time()
            time_spent = end - start
            if len(clip_timestamp) == 2:
                speedup = (clip_timestamp[1] - clip_timestamp[0]) / time_spent
            else:
                speedup = (audio_len_s - clip_timestamp[0]) / time_spent

            print(f"[x] Inferred clip {clip_timestamp} (took {time_spent:.2f}s or x{speedup:.1f}): {text}")

            transcription_state, _ = get_transcription_state_chunk_size_secs(transcription_id)
            if transcription_state in [TranscriptionState.CANCELLED, TranscriptionState.COMPLETED_PARTIALLY]:
                update_transcription_state(
                    transcription_id,
                    transcription_state=TranscriptionState.COMPLETED_PARTIALLY,
                    transcription_chunk=CreateTranscriptionChunk(text=text, chunk_no=chunk_no),
                )
                print("[x] Job has been cancelled, exitting...")
                return
            else:
                update_transcription_state(
                    transcription_id,
                    transcription_state=TranscriptionState.IN_PROGRESS,
                    transcription_chunk=CreateTranscriptionChunk(text=text, chunk_no=chunk_no),
                )
        print("[x] Inference End!")
        update_transcription_state(
            transcription_id,
            transcription_state=TranscriptionState.COMPLETED,
        )
        if os.path.exists(user_audio_path):
            # the file has been processed and therefore
            # not to be stored on our servers
            os.remove(user_audio_path)
        ack(ch, method.delivery_tag)
    except AMQPConnectionError as e:
        print("[x] W: Disconnected from rabbitmq due to healthcheck not sending during heavy processing")
        raise e
    except:
        print(f"[x] Processing Error!\n{traceback.format_exc()}")
        update_transcription_state(
            transcription_id,
            transcription_state=TranscriptionState.PROCESSING_ERROR,
        )
        ack(ch, method.delivery_tag, negative=True, requeue=False)


class LazyLectureQueueWorker:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.whisper_predictor = WhisperPredictor(
            settings.whisper_model_name,
            settings.download_root,
            settings.device,
            preload_model=True,
        )
        self.task_queue_manager: TaskQueueManager = PikaTaskQueueManager(...)

    def start(self):
        print("[*] Connecting to RMQ...")
        connection = pika.BlockingConnection(settings.pika_connection_params)
        channel = connection.channel()
        channel.queue_declare(queue=settings.pika_queue, durable=True)
        print("[*] Connected to RMQ!")
        print("[*] Waiting for messages. To exit press CTRL+C")
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=settings.pika_queue, on_message_callback=self.callback)
        channel.start_consuming()


def callback(ch, method, properties, body):
    return process_transcription_job_messages(ch, method, body)
