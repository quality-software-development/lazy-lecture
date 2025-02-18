from pathlib import Path
import shutil
import tempfile
import pytest
from unittest.mock import patch

from worker.core.asr_predictor import WhisperASRPredictor


@patch("whisper.load_model")
def get_asr_predictor_with_mocked_model(whisper_load_mock, **kwargs):
    whisper_load_mock.return_value.transcribe.return_value = {"text": "", "segments": []}
    return WhisperASRPredictor(**kwargs)


@pytest.fixture
def predictor(temp_cache) -> WhisperASRPredictor:
    return get_asr_predictor_with_mocked_model(
        **dict(whisper_model_name="tiny", download_root=temp_cache, device="cpu", preload_model=True)
    )


# Техника тест-дизайна: эквивалентные классы
# Автор: Илья Тампио
# Классы:
# - существующий аудиофайл
# - несуществующий аудиофайл
def test_transcribe_audio_file_not_exists_raises_exception(predictor):
    with tempfile.TemporaryDirectory() as tempdir:
        audio_file = Path(tempdir) / "sample_file.mp3"
        with pytest.raises(ValueError):
            predictor.transcribe_audio_file(audio_file)


def test_transcribe_audio_file_exists_returns_transcription(predictor, sample_mp3: Path):
    with tempfile.TemporaryDirectory() as tempdir:
        audio_file = Path(tempdir) / "sample_file.mp3"
        shutil.copy2(sample_mp3, audio_file)
        text = predictor.transcribe_audio_file(audio_file)
        assert isinstance(text, str)
