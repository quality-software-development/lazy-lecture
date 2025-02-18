from unittest.mock import patch
from worker.api.client import APIClient
from worker.core.settings import Settings
from worker.core.object_storage import SimpleObjectStorage
from worker.core.asr_predictor import WhisperASRPredictor


def test_create_api_from_settings(test_settings: Settings):
    api = APIClient.from_settings(test_settings)
    assert api is not None


def test_create_object_storage_from_settings(test_settings: Settings):
    obj_store = SimpleObjectStorage.from_settings(test_settings)
    assert obj_store.get_user_audio(42) is None


def test_create_asr_predictor_from_settings(test_settings: Settings):
    @patch("whisper.load_model")
    def get_mock_predictor_from_settings(settings, mock):
        mock.return_value.transcribe.return_value = {"text": "", "segments": []}
        return WhisperASRPredictor.from_settings(settings)

    predictor = get_mock_predictor_from_settings(test_settings)
    assert predictor is not None
