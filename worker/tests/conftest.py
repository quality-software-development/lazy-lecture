import typing as tp
from pathlib import Path

import pytest
import whisper

from worker.settings import settings


@pytest.fixture
def sample_mp3() -> Path:
    return Path("sample_ru_120s.mp3")


@pytest.fixture(scope="session")
def whisper_model() -> whisper.Whisper:
    return whisper.load_model(
        name=settings.MODEL_NAME,
        device=settings.DEVICE,
        download_root=settings.DOWNLOAD_ROOT,
        in_memory=True,
    )
