import asyncio
import pytest
from math import ceil, floor
from unittest.mock import patch, MagicMock
import subprocess

from source.app.transcriptions import services
from source.app.transcriptions.enums import TranscriptionState
from source.app.transcriptions.models import Transcription, TranscriptionChunk
from source.app.transcriptions.schemas import (
    TranscriptionStatusUpdateRequest,
    CreateTranscriptionChunk,
    TranscriptionRequest,
    TranscriptionResponse,
)

# ---------------------------------------------------------
# Вспомогательные «фиктивные» классы и объекты базы данных
# ---------------------------------------------------------


class DummyTranscription:
    def __init__(
        self,
        id=1,
        creator_id=10,
        audio_len_secs=100.0,
        chunk_size_secs=10.0,
        current_state=TranscriptionState.QUEUED,
        error_count=0,
    ):
        self.id = id
        self.creator_id = creator_id
        self.audio_len_secs = audio_len_secs
        self.chunk_size_secs = chunk_size_secs
        self.current_state = current_state
        self.error_count = error_count
        self.create_date = None
        self.update_date = None


class DummyTranscriptionChunk:
    def __init__(self, id=1, transcript_id=1, chunk_no=0, text="dummy"):
        self.id = id
        self.transcript_id = transcript_id
        self.chunk_no = chunk_no
        self.text = text


class DummyDB:
    def __init__(self):
        self.data = {
            "transcription": DummyTranscription(),
            "chunk": None,
        }

    async def get_one(self, model, id):
        # Эмулируем работу ORM
        if model == Transcription and self.data.get("transcription"):
            return self.data["transcription"]
        if model == TranscriptionChunk and self.data.get("chunk"):
            return self.data["chunk"]
        return None

    async def add(self, obj):
        if isinstance(obj, Transcription):
            self.data["transcription"] = obj

    async def commit(self):
        pass

    async def refresh(self, obj):
        pass

    async def delete(self, obj):
        self.data.pop("transcription", None)

    async def scalar(self, query):
        """Подставляем логику для .scalar() в зависимости от содержимого запроса."""
        query_str = str(query).lower()
        if "count" in query_str:
            # Для упрощения пусть всегда 1
            return 1
        return None

    async def scalars(self, query):
        """Имитация fetch-механизма (return all)."""

        # Возвращаем результат в зависимости от того, что ищем
        class FakeResult:
            def __init__(self, lst):
                self._lst = lst

            def all(self):
                return self._lst

        if "transcriptionchunk" in str(query).lower():
            # Один фиктивный чанк
            chunk = DummyTranscriptionChunk(id=99, transcript_id=1, chunk_no=0, text="chunk_text")
            return FakeResult([chunk])
        elif "transcription" in str(query).lower():
            # Несколько транскрипций
            t1 = DummyTranscription(id=1, creator_id=10, audio_len_secs=50.0, chunk_size_secs=5.0)
            t2 = DummyTranscription(id=2, creator_id=10, audio_len_secs=80.0, chunk_size_secs=10.0)
            return FakeResult([t1, t2])
        return FakeResult([])


# ---------------------------------------------------------
# Тесты
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_create_transcription_equivalence():
    """
    КЛАССЫ ЭКВИВАЛЕНТНОСТИ:
    Проверяем создание транскрипции с «обычными» входными данными.
    """
    db = DummyDB()
    req = TranscriptionRequest(
        creator_id=10, audio_len_secs=90.0, chunk_size_secs=10.0, current_state=TranscriptionState.QUEUED
    )
    result = await services.create_transcription(req, db)
    assert result is not None
    assert result.creator_id == 10
    assert result.audio_len_secs == 90.0
    assert result.current_state == TranscriptionState.QUEUED


@pytest.mark.asyncio
async def test_create_transcription_over_100_limit():
    """
    ПРОГНОЗИРОВАНИЕ ОШИБОК + ГРАНИЧНЫЕ ЗНАЧЕНИЯ:
    Допустим, если у пользователя есть более 100 транскрипций,
    то самая старая удаляется.
    Проверим, что метод delete() будет вызван.
    """
    db = DummyDB()

    # Эмулируем наличие 101 транскрипции (чтобы вызвать удаление старой).
    class FakeScalars:
        def __init__(self, n):
            self.n = n

        def all(self):
            # возвращаем список "старых" транскрипций
            return [DummyTranscription(id=i) for i in range(self.n)]

    async def fake_scalars(query):
        return FakeScalars(101)  # больше 100

    db.scalars = fake_scalars

    with patch.object(db, "delete", wraps=db.delete) as mock_del:
        req = TranscriptionRequest(
            creator_id=10, audio_len_secs=90.0, chunk_size_secs=10.0, current_state=TranscriptionState.QUEUED
        )
        await services.create_transcription(req, db)
        mock_del.assert_called_once()  # проверяем, что удаление действительно вызывалось.


@pytest.mark.asyncio
async def test_update_transcription_state_ok():
    """
    ДИАГРАММА СОСТОЯНИЙ:
    Проверяем обычное обновление состояния (QUEUED -> IN_PROGRESS)
    без ошибок и без чанка.
    """
    db = DummyDB()
    update_data = TranscriptionStatusUpdateRequest(
        transcription_id=1, current_state=TranscriptionState.IN_PROGRESS, new_chunk=None
    )
    result = await services.update_transcription_state(update_data, db)
    assert result.current_state == TranscriptionState.IN_PROGRESS


@pytest.mark.asyncio
async def test_update_transcription_state_processing_error_boundary():
    """
    ТАБЛИЦА ПРИНЯТИЯ РЕШЕНИЙ / ГРАНИЧНЫЕ ЗНАЧЕНИЯ:
    Если error_count уже 2, а новое состояние PROCESSING_ERROR,
    то в итоге переходим на PROCESSING_FAIL.
    """
    db = DummyDB()
    db.data["transcription"].error_count = 2
    update_data = TranscriptionStatusUpdateRequest(
        transcription_id=1, current_state=TranscriptionState.PROCESSING_ERROR, new_chunk=None
    )
    result = await services.update_transcription_state(update_data, db)
    assert result.current_state == TranscriptionState.PROCESSING_FAIL


@pytest.mark.asyncio
async def test_update_transcription_state_new_chunk_causes_error():
    """
    ПРОГНОЗИРОВАНИЕ ОШИБОК:
    Если передать chunk_no, который больше максимально допустимого,
    должна быть поднята ошибка (ValueError).
    """
    db = DummyDB()
    # Транскрипция: audio_len_secs=100, chunk_size_secs=10 -> max_chunk_no = floor(100/10)=10
    req = TranscriptionStatusUpdateRequest(
        transcription_id=1,
        current_state=None,
        new_chunk=CreateTranscriptionChunk(text="some text", chunk_no=999),  # выходим за диапазон
    )
    with pytest.raises(ValueError) as e:
        await services.update_transcription_state(req, db)
    assert "Chunk no is bigger than max chunk no" in str(e.value)


@pytest.mark.asyncio
async def test_update_transcription_state_cancelled():
    """
    ДИАГРАММА СОСТОЯНИЙ:
    Перевод в состояние CANCELLED должен смениться на COMPLETED_PARTIALLY,
    если в транскрипции уже есть чанки.
    """
    db = DummyDB()
    # считаем, что у нас есть 1 чанк, тогда CANCELLED -> COMPLETED_PARTIALLY
    update_data = TranscriptionStatusUpdateRequest(
        transcription_id=1, current_state=TranscriptionState.CANCELLED, new_chunk=None
    )
    result = await services.update_transcription_state(update_data, db)
    assert result.current_state == TranscriptionState.COMPLETED_PARTIALLY


def test_row2dict_equivalence():
    """
    КЛАССЫ ЭКВИВАЛЕНТНОСТИ:
    Проверяем row2dict на простом объекте.
    """

    class DummyRow:
        class Table:
            columns = [
                type("Column", (), {"name": "col1"}),
                type("Column", (), {"name": "col2"}),
            ]

        __table__ = Table()
        col1 = "value1"
        col2 = 2

    res = services.row2dict(DummyRow())
    assert res == {"col1": "value1", "col2": "2"}


def test_get_audio_duration_error_prediction(monkeypatch, tmp_path):
    """
    ПРОГНОЗИРОВАНИЕ ОШИБОК:
    Проверяем, что при ошибке чтения файла бросается ValueError.
    """
    dummy_file = tmp_path / "fake.mp3"
    dummy_file.write_text("some random data")

    def fake_probe(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "ffprobe", "Cannot probe audio")

    with patch("subprocess.run", side_effect=fake_probe):
        with pytest.raises(ValueError) as e:
            services.get_audio_duration(dummy_file)
        assert "Error reading audio duration" in str(e.value)


def test_get_audio_duration_ok(monkeypatch, tmp_path):
    """
    ПОПАРНОЕ ТЕСТИРОВАНИЕ: проверяем корректный сценарий и
    сценарий с разными формами входных данных (mp3, wav).
    """
    dummy_file = tmp_path / "fake2.mp3"
    dummy_file.touch()

    def fake_probe_ok(*args, **kwargs):
        return '{"format": {"duration": "123.456"}}'.encode()

    with patch("subprocess.run", side_effect=lambda *args, **kwargs: MagicMock(stdout=fake_probe_ok())):
        dur = services.get_audio_duration(dummy_file)
        assert dur == 123.456


def test_send_transcription_job_to_queue():
    """
    Тест на функцию, отправляющую задание в очередь. (доп. покрытие)
    """
    channel_mock = MagicMock()
    res = services.send_transcription_job_to_queue(
        channel=channel_mock, queue_name="some_queue", transcription_id=11, user_id=22
    )
    assert "transcription_id" in res
    assert "user_id" in res
    channel_mock.basic_publish.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_transcript_ok():
    """
    Тест на cancel_transcript – базовый счастливый путь.
    """
    db = DummyDB()
    # Транскрипция по умолчанию QUEUED
    await services.cancel_transcript(user_id=10, transcript_id=1, db=db)
    assert db.data["transcription"].current_state == TranscriptionState.CANCELLED


@pytest.mark.asyncio
async def test_cancel_transcript_already_finished():
    """
    Причинно-следственный анализ:
    Если транскрипция уже COMPLETED, то при попытке cancel – ValueError.
    """
    db = DummyDB()
    db.data["transcription"].current_state = TranscriptionState.COMPLETED
    with pytest.raises(ValueError) as e:
        await services.cancel_transcript(10, 1, db)
    assert "You can't cancel a finished job" in str(e.value)


@pytest.mark.asyncio
async def test_info_transcript_for_another_user():
    """
    Проверяем, что если user_id != creator_id, будет исключение (ValueError).
    """
    db = DummyDB()
    db.data["transcription"].creator_id = 999
    with pytest.raises(ValueError) as e:
        await services.info_transcript(user_id=10, transcript_id=1, db=db)
    assert "You may cancel processing only of your transcript" in str(e.value)


@pytest.mark.asyncio
async def test_info_transcript_ok():
    """
    Тест «счастливого» пути получения информации.
    """
    db = DummyDB()  # creator_id=10 по умолчанию
    info = await services.info_transcript(user_id=10, transcript_id=1, db=db)
    assert isinstance(info, DummyTranscription)


@pytest.mark.asyncio
async def test_export_transcription_decision_table_txt():
    """
    ТАБЛИЦА ПРИНЯТИЯ РЕШЕНИЙ:
    Проверяем экспорт в «txt».
    """
    db = DummyDB()
    content = await services.export_transcription(1, "txt", db)
    assert isinstance(content, bytes)
    assert b"chunk_text" in content  # т.к. chunk_text – наш фиктивный чанк


@pytest.mark.asyncio
async def test_export_transcription_decision_table_doc():
    """
    ТАБЛИЦА ПРИНЯТИЯ РЕШЕНИЙ:
    Проверяем экспорт в «doc».
    """
    db = DummyDB()
    content = await services.export_transcription(1, "doc", db)
    assert isinstance(content, bytes)
    # Проверяем, что контент не пуст
    assert len(content) > 0


@pytest.mark.asyncio
async def test_export_transcription_no_chunks():
    """
    ПРОГНОЗИРОВАНИЕ ОШИБОК:
    Если нет ни одного чанка, должна вернуться ошибка.
    """
    db = DummyDB()

    async def fake_scalars(query):
        class FakeEmptyResult:
            def all(_):
                return []

        return FakeEmptyResult()

    db.scalars = fake_scalars
    with pytest.raises(ValueError) as e:
        await services.export_transcription(1, "txt", db)
    assert "No transcription chunks" in str(e.value)
