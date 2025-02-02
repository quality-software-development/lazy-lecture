from fastapi import UploadFile
from mutagen import File as MutagenFile
from pydantic import AfterValidator, PlainSerializer, WithJsonSchema
from source.core.settings import settings
from typing_extensions import Annotated


class ValidAudioFile(UploadFile):
    MIN_DURATION = 10  # Minimum audio length in seconds
    MAX_DURATION = 2 * 60 * 60  # Maximum audio length in seconds (2 hours)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: UploadFile) -> UploadFile:
        try:
            audio = MutagenFile(value.file)
            if not audio or not hasattr(audio, "info"):
                raise ValueError("Invalid audio file format or metadata.")
        except Exception as e:
            raise ValueError(f"Could not read the audio file: {e}")
        duration = getattr(audio.info, "length", None)
        if duration is None:
            raise ValueError("Audio duration could not be determined.")
        if not (cls.MIN_DURATION <= duration <= cls.MAX_DURATION):
            raise ValueError(
                f"Audio duration must be between {cls.MIN_DURATION} seconds and {cls.MAX_DURATION} seconds. "
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
