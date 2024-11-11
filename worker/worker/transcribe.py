from pathlib import Path
import typing as tp

import whisper


def transcribe_audio_file(
    audio_path: tp.Union[str, Path], model: whisper.Whisper, clip_timestamp: tp.Optional[tp.Tuple[float, float]] = "0"
) -> str:
    audio_path = Path(audio_path)
    if not audio_path.exists() or not audio_path.is_file():
        raise FileNotFoundError(f"Audiofile {audio_path} is not found")

    # TODO: experiment with settings
    # https://github.com/openai/whisper/blob/cdb81479623391f0651f4f9175ad986e85777f31/whisper/transcribe.py#L38
    result = model.transcribe(
        str(audio_path),
        clip_timestamps=clip_timestamp,
    )

    return result["text"], result["segments"]
