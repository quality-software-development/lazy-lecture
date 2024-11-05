from pathlib import Path

import pytest
import whisper

from worker.transcribe import transcribe_audio_file


@pytest.mark.ml
def test_transcribe_audio_file(sample_mp3: Path, whisper_model: whisper.Whisper):
    text = transcribe_audio_file(sample_mp3, whisper_model)
    assert isinstance(text, str) and text.strip() != ""
