import json
from pathlib import Path

import pika.channel

from .settings import object_storage_config


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


def process_transcription_job_messages(ch: pika.channel.Channel, method, properties, body):
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
        #   status==processing_fail -> ignore, skip
        #   status==cancelled -> ignore, skip
        # check job is_cancelled, if true change status to cancelled

        # check if in object_storage_config
        # if not in object_storage_config -> Exception
        user_audio_path: Path = get_user_audio_path(user_id, Path(object_storage_config.PATH), raise_if_not_found=True)

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
        print(f"[x] Processing Error! {e}")
        processing_error_count = 3  # TODO: get actual processing_error_count
        if processing_error_count < 3:
            # TODO: set processing_error_count++
            # TODO: set status=queued
            ack(ch, method.delivery_tag, negative=True, requeue=True)
        else:
            # Don't return, set Processing Fail
            # TODO: set status=processing_fail
            ack(ch, method.delivery_tag, negative=True, requeue=False)
