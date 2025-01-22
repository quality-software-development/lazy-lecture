import json
import os
import traceback
from pathlib import Path
import time

import pika.channel

from .settings import object_storage_config
from .transcribe import transcribe_audio_file
from .whisper_model import whisper_model
from .audio_utils import get_audio_len
from .api_client import (
    get_transcription_state_chunk_size_secs,
    update_transcription_state,
    TranscriptionState,
    CreateTranscriptionChunk,
)


def get_user_audio_path(user_id: int, object_storage_root: Path, raise_if_not_found: bool = True) -> Path:
    if not object_storage_root.exists():
        raise FileNotFoundError(f"Object Storage Path does not exist. ({str(object_storage_root)})")
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
        print("[x] Received message: ", str(message))
        job_dict = json.loads(message)
        print("[x] Received job: ", str(job_dict))
        user_id = job_dict["user_id"]
        transcription_id = job_dict["transcription_id"]

        transcription_state, chunk_size_secs = get_transcription_state_chunk_size_secs(transcription_id)
        # if transcription_state == TranscriptionState.IN_PROGRESS:
        #     #   status==in_progress -> ignore, skip
        #     print("[x] Job has already in progress, skip")
        #     # ack should be done by the one who does the job
        #     ack(ch, method.delivery_tag)
        #     return
        if transcription_state in [
            TranscriptionState.COMPLETED,
            TranscriptionState.COMPLETED_PARTIALLY,
        ]:
            #   status==completed -> ignore, skip
            #   status==completed_partially -> ignore, skip
            print("[x] Job has already been completed, skip")
            ack(ch, method.delivery_tag)
            return
        if transcription_state in [
            TranscriptionState.PROCESSING_FAIL,
            TranscriptionState.CANCELLED,
        ]:
            #   status==processing_fail -> ignore, skip
            #   status==cancelled -> ignore, skip
            print("[x] Job is not to be processed anymore due to cancellation or processing fail, skip")
            ack(ch, method.delivery_tag)
            return
        update_transcription_state(transcription_id, TranscriptionState.IN_PROGRESS)

        # TODO: add restoration logic from the last place
        #   status==processing_error -> get last chunk id, try to continue

        # check if in object_storage_config
        # if not in object_storage_config -> Exception
        user_audio_path: Path = get_user_audio_path(user_id, Path(object_storage_config.PATH), raise_if_not_found=True)
        print(f"[x] Inference Begin!")
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
            update_transcription_state(
                transcription_id,
                transcription_state=TranscriptionState.IN_PROGRESS,
                transcription_chunk=CreateTranscriptionChunk(text=text, chunk_no=chunk_no),
            )
            transcription_state, _ = get_transcription_state_chunk_size_secs(transcription_id)
            if transcription_state == TranscriptionState.CANCELLED:
                update_transcription_state(
                    transcription_id,
                    transcription_state=TranscriptionState.COMPLETED_PARTIALLY,
                )
                print("[x] Job has been cancelled, exitting...")
                return
        print(f"[x] Inference End!")
        update_transcription_state(
            transcription_id,
            transcription_state=TranscriptionState.COMPLETED,
        )
        if os.path.exists(user_audio_path):
            # the file has been processed and therefore
            # not to be stored on our servers
            os.remove(user_audio_path)

        ack(ch, method.delivery_tag)
    except:
        print(f"[x] Processing Error!\n{traceback.format_exc()}")
        update_transcription_state(
            transcription_id,
            transcription_state=TranscriptionState.PROCESSING_FAIL,
        )
        ack(ch, method.delivery_tag, negative=True, requeue=False)

        # processing_error_count = 3  # TODO: get actual processing_error_count
        # if processing_error_count < 3:
        #     # TODO: set processing_error_count++
        #     # TODO: set status=queued
        #     ack(ch, method.delivery_tag, negative=True, requeue=True)
        # else:
        #     # Don't return, set Processing Fail
        #     # TODO: set status=processing_fail
        #     ack(ch, method.delivery_tag, negative=True, requeue=False)
