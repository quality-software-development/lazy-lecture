from unittest.mock import MagicMock

import pytest

from source.app.transcriptions.types import ValidAudioFile, validate_admin_token, validate_worker_token
from source.core.settings import settings


def test_valid_audio_file_validators_contains_validate():
    validators = list(ValidAudioFile.__get_validators__())

    assert validators == [ValidAudioFile.validate]


def test_valid_audio_file_get_audio_duration_success(monkeypatch):
    upload = MagicMock()
    upload.file = "audio.mp3"
    monkeypatch.setattr(
        "source.app.transcriptions.types.ffmpeg.probe",
        lambda *args, **kwargs: {"format": {"duration": "42.5"}},
    )

    assert ValidAudioFile.get_audio_duration(upload) == 42.5


def test_valid_audio_file_get_audio_duration_error(monkeypatch):
    upload = MagicMock()
    upload.file = "broken.mp3"

    def raise_probe(*args, **kwargs):
        raise RuntimeError("ffmpeg failed")

    monkeypatch.setattr("source.app.transcriptions.types.ffmpeg.probe", raise_probe)

    with pytest.raises(ValueError, match="Error reading audio duration"):
        ValidAudioFile.get_audio_duration(upload)


def test_valid_audio_file_validate_duration_inside_range(monkeypatch):
    upload = MagicMock()
    monkeypatch.setattr(ValidAudioFile, "get_audio_duration", classmethod(lambda cls, value: 120.0))

    assert ValidAudioFile.validate(upload) is upload


def test_valid_audio_file_validate_duration_outside_range(monkeypatch):
    upload = MagicMock()
    monkeypatch.setattr(ValidAudioFile, "get_audio_duration", classmethod(lambda cls, value: 5.0))

    with pytest.raises(Exception):
        ValidAudioFile.validate(upload)


def test_validate_worker_token_success():
    assert validate_worker_token(settings.SECRET_WORKER_TOKEN) == settings.SECRET_WORKER_TOKEN


def test_validate_worker_token_failure():
    with pytest.raises(ValueError, match="Wrong worker token"):
        validate_worker_token("bad-token")


def test_validate_admin_token_success():
    assert validate_admin_token(settings.SECRET_ADMIN_TOKEN) == settings.SECRET_ADMIN_TOKEN


def test_validate_admin_token_failure():
    with pytest.raises(ValueError, match="Wrong admin token"):
        validate_admin_token("bad-token")
