from pathlib import Path

import pytest


@pytest.fixture
def sample_mp3() -> Path:
    return Path("sample_ru_120s.mp3")
