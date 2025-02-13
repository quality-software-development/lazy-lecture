import typing as tp

import requests

from worker.core.settings import settings
from worker.core.enums import TranscriptionState
from worker.core.schemas import CreateTranscriptionChunk


def get_transcription_state_chunk_size_secs(transcription_id: int) -> TranscriptionState:
    url = f"{settings.api_base_url}/worker/transcription_status"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    params = {"secret_worker_token": settings.secret_worker_token}
    json_data = {"transcription_id": transcription_id}
    print("[API CALL] Transcription State Update (to get status)...")
    response = requests.post(
        url,
        params=params,
        headers=headers,
        json=json_data,
    )
    response.raise_for_status()
    print("[API CALL] Transcription State Update (to get status)... Success!")
    return response.json()["transcription"]["current_state"], int(response.json()["transcription"]["chunk_size_secs"])


def update_transcription_state(
    transcription_id: int,
    transcription_state: tp.Optional[TranscriptionState] = None,
    transcription_chunk: tp.Optional[CreateTranscriptionChunk] = None,
) -> str:
    url = f"{settings.api_base_url}/worker/transcription_status"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    params = {"secret_worker_token": settings.secret_worker_token}
    json_data = {
        "transcription_id": transcription_id,
    }
    if transcription_state:
        json_data["current_state"] = transcription_state
    if transcription_chunk:
        json_data["new_chunk"] = transcription_chunk.model_dump()

    try:
        print(
            f"[API CALL] Transcription State Update... ({transcription_id=}, {transcription_state=}, {transcription_chunk=})"
        )
        response = requests.post(
            url,
            params=params,
            headers=headers,
            json=json_data,
        )
        response.raise_for_status()
        print("[API CALL] Transcription State Update ... Success!")
    except Exception as e:
        print(f"[API CALL] Failed miserably ({e})")
        raise e
