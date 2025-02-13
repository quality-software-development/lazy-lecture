from pathlib import Path

import ffmpeg


def get_audio_len(file: Path) -> float:
    """Extracts duration using ffmpeg-python bindings."""
    try:
        probe = ffmpeg.probe(file, select_streams="a", show_entries="format=duration")
        duration = float(probe["format"]["duration"])
        return duration
    except Exception as e:
        raise ValueError(f"Error reading audio duration: {e}")
