from pathlib import Path
import tempfile

import pytest

from worker.core.settings import Settings


@pytest.fixture
def temp_object_storage():
    tempdir = tempfile.TemporaryDirectory()
    yield tempdir.name
    tempdir.cleanup()


@pytest.fixture
def temp_cache():
    tempdir = tempfile.TemporaryDirectory()
    yield tempdir.name
    tempdir.cleanup()


@pytest.fixture
def test_settings(temp_object_storage, temp_cache) -> Settings:
    return Settings(object_storage_path=temp_object_storage, download_root=temp_cache)


@pytest.fixture
def sample_mp3() -> Path:
    return Path("sample_ru_120s.mp3")
