import os
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime


# Импортируем тестируемые функции и модели
from source.app.auth.services import authenticate_user
from source.app.users.services import create_user
from source.app.users.schemas import UserCreate
from source.app.transcriptions.views import create_upload_file
from source.app.transcriptions.services import list_user_transcriptions, info_transcript
from source.app.transcriptions.models import Transcription
from source.app.users.models import User
from source.app.transcriptions.enums import TranscriptionState


# 1. Авторизация пользователя
@pytest.mark.asyncio
async def test_authorization_user(monkeypatch):
    """
    Проверяем, что при корректных учетных данных функция authenticate_user возвращает объект пользователя.
    При этом объект БД и внешняя функция проверки пароля замоканы.
    """
    # Создаем фейкового пользователя с необходимыми полями
    fake_user = User()
    fake_user.id = 1
    fake_user.username = "testuser"
    fake_user.password = "hashedpassword"
    fake_user.active = True
    fake_user.password_timestamp = 1234567890.0

    # Мокаем сессию БД: метод scalar возвращает fake_user
    fake_db = AsyncMock()
    fake_db.scalar = AsyncMock(return_value=fake_user)

    # Патчим verify_password, чтобы он всегда возвращал True
    monkeypatch.setattr("source.app.auth.services.verify_password", lambda plain_password, hashed_password: True)

    # Вызываем функцию аутентификации
    result = await authenticate_user("testuser", "TestP@ss123", fake_db)
    assert result is fake_user


# 2. Регистрация пользователя
@pytest.mark.asyncio
async def test_registration_user(monkeypatch):
    """
    Проверяем, что при вызове create_user возвращается объект нового пользователя,
    пароль преобразовывается (хешируется) и все необходимые поля заполняются.
    """

    user_data = UserCreate(username="newuser", password="ValidP@ss123")
    fake_db = AsyncMock()
    # Мокаем методы работы с сессией: add, commit, refresh (refresh присваивает id)
    fake_db.add = MagicMock()
    fake_db.commit = AsyncMock()
    fake_db.refresh = AsyncMock(side_effect=lambda user: setattr(user, "id", 1) or None)

    result = await create_user(user_data, fake_db)
    assert result is not None
    assert result.username == "newuser"
    # Пароль не должен совпадать с исходным (он хешируется)
    assert result.password != "ValidP@ss123"
    assert hasattr(result, "id") and result.id == 1


# 3. Загрузка аудио для обработки
@pytest.mark.asyncio
async def test_upload_audio(monkeypatch):
    """
    Тестируем функцию create_upload_file для загрузки аудиофайла.
    Все внешние зависимости (aiofiles, доступ к объектному хранилищу, очередь,
    получение длительности аудио, проверка наличия незавершенных транскрипций)
    мокаются.
    """
    from source.app.transcriptions.views import create_upload_file

    # Фейковый пользователь с правом can_interact
    dummy_user = User()
    dummy_user.id = 1
    dummy_user.can_interact = True

    # Фейковый объект аудиофайла с content_type "audio/mpeg"
    class FakeUploadFile:
        content_type = "audio/mpeg"

        def __init__(self):
            self.file = None  # не используется в тесте
            self._chunks = [b"audio_chunk", b""]
            self._index = 0

        async def read(self, size):
            if self._index < len(self._chunks):
                chunk = self._chunks[self._index]
                self._index += 1
                return chunk
            return b""

    fake_audio = FakeUploadFile()

    # Фейковая очередь: кортеж (канал, имя очереди)
    fake_channel = MagicMock()
    fake_channel.basic_publish = MagicMock()
    fake_task_q = (fake_channel, "dummy_queue")

    # Мокаем работу с БД: get_current_transcriptions возвращает пустой список,
    # а create_transcription возвращает фейковую транскрипцию с id=42.
    fake_db = AsyncMock()
    monkeypatch.setattr("source.app.transcriptions.views.get_current_transcriptions", AsyncMock(return_value=[]))
    dummy_transcription = Transcription()
    dummy_transcription.id = 42
    dummy_transcription.creator_id = dummy_user.id
    monkeypatch.setattr(
        "source.app.transcriptions.views.create_transcription", AsyncMock(return_value=dummy_transcription)
    )
    # Патчим get_audio_duration, чтобы возвращалась фиксированная длительность (например, 120 секунд)
    monkeypatch.setattr("source.app.transcriptions.views.get_audio_duration", lambda filepath: 120.0)

    # Патчим aiofiles.open, чтобы не производилось реальное обращение к файловой системе
    class DummyAiofilesContextManager:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def write(self, data):
            pass

    monkeypatch.setattr(
        "source.app.transcriptions.views.aiofiles.open", lambda filepath, mode: DummyAiofilesContextManager()
    )
    # Патчим os.path.join для предсказуемого пути файла
    monkeypatch.setattr(os.path, "join", lambda *parts: f"/dummy_path/{parts[-1]}")

    # Вызываем функцию загрузки аудио
    result = await create_upload_file(dummy_user, fake_audio, fake_task_q, fake_db)
    assert result["message"] == "File uploaded successfully"
    assert result["task_id"] == 42
    assert "/dummy_path/" in result["file"]
    # Проверяем, что функция отправки задания в очередь была вызвана
    fake_channel.basic_publish.assert_called_once()


# 4. Взятие списка транскрипций пользователя
@pytest.mark.asyncio
async def test_list_user_transcriptions(monkeypatch):
    """
    Тестируем функцию list_user_transcriptions, которая должна возвращать
    страницу транскрипций для заданного пользователя. Все запросы к БД мокаются.
    """
    from source.app.transcriptions.services import list_user_transcriptions

    # Создаем фейковый объект транскрипции
    dummy_transcription = Transcription()
    dummy_transcription.id = 101
    dummy_transcription.creator_id = 1
    dummy_transcription.audio_len_secs = 300.0
    dummy_transcription.chunk_size_secs = 30.0
    dummy_transcription.current_state = TranscriptionState.QUEUED
    dummy_transcription.error_count = 0
    dummy_transcription.create_date = datetime(2024, 1, 1)
    dummy_transcription.update_date = datetime(2024, 1, 1)

    # Мокаем сессию БД: scalar и scalars должны вернуть соответствующие значения.
    fake_db = AsyncMock()
    fake_scalars = MagicMock()
    fake_scalars.all.return_value = [dummy_transcription]
    fake_db.scalars = AsyncMock(return_value=fake_scalars)
    fake_db.scalar = AsyncMock(return_value=1)

    # Патчим функцию получения описания транскрипции
    monkeypatch.setattr(
        "source.app.transcriptions.services.get_transcritption_descrtiption",
        AsyncMock(return_value="dummy description"),
    )

    result = await list_user_transcriptions(page=1, size=10, user_id=1, db=fake_db)
    assert result.total == 1
    assert len(result.transcriptions) == 1
    # Проверяем, что описание транскрипции заполнено
    assert result.transcriptions[0].description == "dummy description"


# 5. Взятие статуса транскрипции
@pytest.mark.asyncio
async def test_get_transcription_status(monkeypatch):
    """
    Тестируем функцию info_transcript, которая возвращает данные транскрипции
    для текущего пользователя. Здесь проверяется, что если транскрипция принадлежит пользователю,
    статус возвращается корректно.
    """
    from source.app.transcriptions.services import info_transcript

    # Создаем фейковую транскрипцию с нужными данными
    dummy_transcription = Transcription()
    dummy_transcription.id = 55
    dummy_transcription.creator_id = 1
    dummy_transcription.current_state = TranscriptionState.IN_PROGRESS

    # Мокаем метод получения транскрипции из БД (get_one)
    fake_db = AsyncMock()
    fake_db.get_one = AsyncMock(return_value=dummy_transcription)

    result = await info_transcript(user_id=1, transcript_id=55, db=fake_db)
    assert result.current_state == TranscriptionState.IN_PROGRESS
    assert result.id == 55
