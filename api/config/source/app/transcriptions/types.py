from fastapi import UploadFile
from pydantic import AfterValidator, PlainSerializer, WithJsonSchema
from source.core.settings import settings
from typing_extensions import Annotated
from pydantic import ValidationError
import ffmpeg


class ValidAudioFile(UploadFile):
    MIN_DURATION = 10  # Minimum audio length in seconds
    MAX_DURATION = 2 * 60 * 60  # Maximum audio length in seconds (2 hours)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def get_audio_duration(cls, file: UploadFile) -> float:
        """Extracts duration using ffmpeg-python bindings."""
        try:
            probe = ffmpeg.probe(file.file, select_streams="a", show_entries="format=duration")
            duration = float(probe["format"]["duration"])
            return duration
        except Exception as e:
            raise ValueError(f"Error reading audio duration: {e}")

    @classmethod
    def validate(cls, value: UploadFile) -> UploadFile:
        duration = cls.get_audio_duration(value)
        if not (cls.MIN_DURATION <= duration <= cls.MAX_DURATION):
            raise ValidationError(
                f"Audio duration must be between {cls.MIN_DURATION} and {cls.MAX_DURATION} seconds. "
                f"Provided file is {duration:.2f} seconds long."
            )
        return value


def validate_worker_token(secret_worker_token: str) -> str:
    print(f"Received: {secret_worker_token}, Expected: {settings.SECRET_WORKER_TOKEN}")  # Debugging
    if secret_worker_token != settings.SECRET_WORKER_TOKEN:
        raise ValueError(f"Wrong worker token")
    return secret_worker_token


def validate_admin_token(secret_admin_token: str) -> str:
    print(f"Received: {secret_admin_token}, Expected: {settings.SECRET_ADMIN_TOKEN}")  # Debugging
    if secret_admin_token != settings.SECRET_ADMIN_TOKEN:
        raise ValueError(f"Wrong admin token")
    return secret_admin_token
