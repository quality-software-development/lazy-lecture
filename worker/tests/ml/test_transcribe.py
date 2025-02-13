from pathlib import Path

import pytest
import whisper

from worker.transcribe.transcribe import transcribe_audio_file


@pytest.mark.ml
@pytest.mark.unit
def test_transcribe_audio_file(sample_mp3: Path, whisper_model: whisper.Whisper):
    text, segments = transcribe_audio_file(sample_mp3, whisper_model)
    assert isinstance(text, str) and text.strip() != ""


@pytest.mark.ml
@pytest.mark.unit
def test_transcribe_audio_file_with_clip(sample_mp3: Path, whisper_model: whisper.Whisper):
    text, segments = transcribe_audio_file(sample_mp3, whisper_model, clip_timestamp=[0, 10.0])
    assert isinstance(text, str) and text.strip() != ""
