import shutil
import tempfile

import pytest

from worker.core.object_storage import SimpleObjectStorage
from worker.core.settings import Settings


# Техника тест-дизайна: эквивалентные классы
# Автор: Илья Тампио
# Классы:
# - пользователь с загруженной аудиозаписью
# - пользователь без загруженной аудиозаписи
def test_get_user_audio_good_when_exists(test_settings: Settings, sample_mp3):
    obj_store = SimpleObjectStorage(test_settings.object_storage_path)
    user_id = 42
    expected_user_audio_path = test_settings.object_storage_path / f"{user_id}.mp3"
    shutil.copy2(sample_mp3, expected_user_audio_path)
    user_audio_path = obj_store.get_user_audio(user_id)
    assert user_audio_path == expected_user_audio_path


def test_get_user_audio_bad_when_does_not_exist(test_settings: Settings):
    obj_store = SimpleObjectStorage(test_settings.object_storage_path)
    user_id = 42
    user_audio_path = obj_store.get_user_audio(user_id)
    assert user_audio_path is None


def test_remove_user_audio_good_when_exists(test_settings: Settings, sample_mp3):
    obj_store = SimpleObjectStorage(test_settings.object_storage_path)
    user_id = 42
    expected_user_audio_path = test_settings.object_storage_path / f"{user_id}.mp3"
    shutil.copy2(sample_mp3, expected_user_audio_path)
    obj_store.remove_user_audio(user_id)
    assert not expected_user_audio_path.exists()


def test_remove_user_audio_good_when_not_exist(test_settings: Settings):
    obj_store = SimpleObjectStorage(test_settings.object_storage_path)
    user_id = 42
    expected_user_audio_path = test_settings.object_storage_path / f"{user_id}.mp3"
    obj_store.remove_user_audio(user_id)
    assert not expected_user_audio_path.exists()


# Техники тест-дизайна: эквивалентные классы и прогнозирование ошибок
# Автор: Илья Тампио
# Классы:
# - существующая папка
# - несуществующая папка
def test_init_when_folder_exists_good():
    with tempfile.TemporaryDirectory() as tempdir:
        obj_store = SimpleObjectStorage(tempdir)
        assert obj_store.get_user_audio(42) is None


def test_init_when_folder_not_exists_bad():
    with tempfile.TemporaryDirectory() as tempdir:
        shutil.rmtree(tempdir)
        with pytest.raises(ValueError):
            SimpleObjectStorage(tempdir)
