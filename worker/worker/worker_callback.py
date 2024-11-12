import json
import traceback
from pathlib import Path
import time

import pika.channel

from .settings import object_storage_config
from .transcribe import transcribe_audio_file
from .whisper_model import whisper_model
from .audio_utils import get_audio_len


def get_user_audio_path(user_id: int, object_storage_root: Path, raise_if_not_found: bool = True) -> Path:
    if not object_storage_root.exists():
        raise FileNotFoundError(f"Object Storage Path does not exist. ({str(object_storage_root)})")
    expected_user_audiofile_path = object_storage_root / f"{user_id}.mp3"
    if not expected_user_audiofile_path.exists() and raise_if_not_found:
        raise FileNotFoundError(f"User audiofile is not present at {str(expected_user_audiofile_path)}")
    return expected_user_audiofile_path


def ack(ch: pika.channel.Channel, delivery_tag: int, negative: bool = False, requeue: bool = False):
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
        print("[x] Received message: ", str(message))
        job_dict = json.loads(message)
        print("[x] Received job: ", str(job_dict))
        user_id = job_dict["user_id"]
        transcription_id = job_dict["transcription_id"]

        # TODO: check and set job status
        #   status==queued -> status := In Progress
        #   status==completed -> ignore, skip
        #   status==in_progress -> ignore, skip
        #   status==completed_partially -> ignore, skip
        #   status==processing_error -> get last chunk id, try to continue
        #   status==processing_fail -> ignore, skip
        #   status==cancelled -> ignore, skip
        # check job is_cancelled, if true change status to cancelled

        # check if in object_storage_config
        # if not in object_storage_config -> Exception
        user_audio_path: Path = get_user_audio_path(user_id, Path(object_storage_config.PATH), raise_if_not_found=True)
        print(f"[x] Processing Begin!")

        print(f"[x] Inference Begin!")
        audio_len_s: float = get_audio_len(user_audio_path)
        print(f"[x] Audio len: {audio_len_s}")
        AUDIO_CHUNK_LEN_SEC = 15 * 60
        clip_timestamps = [
            [v, min(audio_len_s, v + AUDIO_CHUNK_LEN_SEC)] for v in range(0, int(audio_len_s) + 1, AUDIO_CHUNK_LEN_SEC)
        ]
        clip_timestamps[-1] = [
            clip_timestamps[-1][0],
        ]
        print(f"[x] Clip timestamps: {clip_timestamps}")

        for clip_timestamp in clip_timestamps:
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
            # TODO: transcription status update to postgre

        print(f"[x] Inference End!")
        # Processing start
        # split audio in chunks
        # get next chunk to process from server
        # process chunk
        # submit chunk transcription
        # check job is_cancelled, if true change status to partially completed
        # repeat till completed
        # change status to completed

        ack(ch, method.delivery_tag)
    except Exception as e:
        print(f"[x] Processing Error!\n{traceback.format_exc()}")
        processing_error_count = 3  # TODO: get actual processing_error_count
        if processing_error_count < 3:
            # TODO: set processing_error_count++
            # TODO: set status=queued
            ack(ch, method.delivery_tag, negative=True, requeue=True)
        else:
            # Don't return, set Processing Fail
            # TODO: set status=processing_fail
            ack(ch, method.delivery_tag, negative=True, requeue=False)
