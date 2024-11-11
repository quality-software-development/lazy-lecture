import typing as tp
from pathlib import Path

from mutagen.mp3 import MP3


def get_audio_len(fpath: tp.Union[str, Path]) -> float:
    p = Path(fpath)
    if not p.exists():
        raise FileNotFoundError(str(p))
    return MP3(str(p)).info.length
