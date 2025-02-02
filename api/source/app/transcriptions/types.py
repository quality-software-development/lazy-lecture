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


def validate_worker_token(value: str) -> str:
    if not value == settings.SECRET_WORKER_TOKEN:
        raise ValueError(f"Wrong worker token")
    return value


SecretWorkerToken = Annotated[
    str,
    AfterValidator(validate_worker_token),
    PlainSerializer(lambda x: str(x), return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]
