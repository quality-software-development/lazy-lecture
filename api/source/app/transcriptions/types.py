from fastapi import UploadFile
from mutagen import File as MutagenFile


class ValidAudioFile(UploadFile):
    MIN_DURATION = 10  # Minimum audio length in seconds
    MAX_DURATION = 2 * 60 * 60  # Maximum audio length in seconds (2 hours)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: UploadFile) -> UploadFile:
        # Ensure the file can be processed by mutagen
        try:
            audio = MutagenFile(value.file)
            if not audio or not hasattr(audio, "info"):
                raise ValueError("Invalid audio file format or metadata.")
        except Exception as e:
            raise ValueError(f"Could not read the audio file: {e}")

        # Get the duration of the audio file
        duration = getattr(audio.info, "length", None)
        if duration is None:
            raise ValueError("Audio duration could not be determined.")

        # Check if the duration is within the allowed range
        if not (cls.MIN_DURATION <= duration <= cls.MAX_DURATION):
            raise ValueError(
                f"Audio duration must be between {cls.MIN_DURATION} seconds and {cls.MAX_DURATION} seconds. "
                f"Provided file is {duration:.2f} seconds long."
            )

        # If all checks pass, return the valid file
        return value
