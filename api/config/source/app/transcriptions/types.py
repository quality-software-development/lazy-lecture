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
