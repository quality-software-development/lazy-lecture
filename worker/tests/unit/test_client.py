import pytest
from unittest.mock import patch

import requests

from worker.api.schemas import TranscriptionChunk, TranscriptionInfo, TranscriptionState
from worker.api.client import APIClient


# Техника тест-дизайна: эквивалентные классы
# Автор: Илья Тампио
# Классы:
# - существующая транскрипция
# - несуществующая транскрипция
@patch("requests.request")
def test_get_transcription_info_exists_returns_info(mock_request):
    api = APIClient("http://wedontcare.com:9999/", "wedontcare")
    transcription_id = 42
    awaited_info = TranscriptionInfo(
        creator_id=transcription_id,
        audio_len_secs=12738.0,
        chunk_size_secs=900,
        current_state=TranscriptionState.IN_PROGRESS,
        error_count=0,
    )
    mock_request.return_value.json.return_value = {"transcription": awaited_info.model_dump(mode="json")}
    got_info = api.get_transcription_info(transcription_id)
    assert awaited_info == got_info


@patch("requests.request")
def test_get_transcription_info_not_exists_raises_exception(mock_request):
    api = APIClient("http://wedontcare.com:9999/", "wedontcare")
    transcription_id = 42
    response_not_found = requests.Response()
    response_not_found.status_code = 418  # teapot
    mock_request.return_value = response_not_found
    with pytest.raises(requests.exceptions.HTTPError):
        api.get_transcription_info(transcription_id)


@patch("requests.request")
def test_update_transcription_state_exists_returns_info(mock_request):
    api = APIClient("http://wedontcare.com:9999/", "wedontcare")
    transcription_id = 42
    new_state = TranscriptionState.IN_PROGRESS
    new_chunk = TranscriptionChunk(text="some_text", chunk_no=0)
    awaited_info = TranscriptionInfo(
        creator_id=transcription_id, audio_len_secs=12738.0, chunk_size_secs=900, current_state=new_state, error_count=0
    )
    mock_request.return_value.json.return_value = {"transcription": awaited_info.model_dump(mode="json")}
    got_info = api.update_transcription_state(transcription_id, new_state, new_chunk)
    assert got_info == awaited_info


@patch("requests.request")
def test_update_transcription_state_not_exists_raise_exception(mock_request):
    api = APIClient("http://wedontcare.com:9999/", "wedontcare")
    transcription_id = 42
    new_state = TranscriptionState.IN_PROGRESS
    new_chunk = TranscriptionChunk(text="some_text", chunk_no=0)
    response_not_found = requests.Response()
    response_not_found.status_code = 418  # teapot
    mock_request.return_value = response_not_found
    with pytest.raises(requests.exceptions.HTTPError):
        api.update_transcription_state(transcription_id, new_state, new_chunk)
