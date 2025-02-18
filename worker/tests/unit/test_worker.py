from unittest.mock import AsyncMock, Mock, patch
import pytest

from worker.api.schemas import TaskData, TranscriptionInfo, TranscriptionState
from worker.core.worker import LazyLectureWorker

"""
Техника тест-дизайна: попарное тестирование, граничные значения
Автор: Илья Тампио
Чанки транскрипций при чанке в N секунд
Классы эквивалентности:
- Аудио до N секунд (1 чанк)
- Аудио от N до N*2 секунд (2 чанка)
Чанки транскрипций при чанке в N секунд

Граничные случаи: N-0.01, N, N+0.01 секунды
"""
CHUNK_LENS = [900, 60, 1800]
SHIFTS = [-0.01, 0, 0.01]


@pytest.mark.asyncio
@pytest.mark.parametrize("chunk_len", CHUNK_LENS)
@pytest.mark.parametrize("shift", SHIFTS)
@patch("worker.core.task_consumer.AioPikaTaskConsumer.from_settings")
@patch("worker.api.client.APIClient.from_settings")
@patch("worker.core.object_storage.SimpleObjectStorage.from_settings")
@patch("worker.core.asr_predictor.WhisperASRPredictor.from_settings")
async def test_chunk_len(tc, api, objs, asr, chunk_len, shift, test_settings):
    worker = LazyLectureWorker(test_settings)
    audio_len = chunk_len + shift
    worker.asr_predictor.transcribe_audio_file = Mock(return_value="text")
    chunks = list(worker._infer_audio(Mock(), audio_len, chunk_len))
    awaited_chunk_count = audio_len // chunk_len + 1
    assert len(chunks) == awaited_chunk_count


"""
Техника тест-дизайна: граничные значения
Автор: Илья Тампио
Классы эквивалентности:
- Ошибочные транскрипции, где меньше чем 3 срабатывания
- Ошибочные транскрипции, где 3 и больше
Граничные случаи: 2, 3, 4
"""


@pytest.mark.asyncio
@pytest.mark.parametrize("error_count", [2, 3, 4])
@patch("worker.core.task_consumer.AioPikaTaskConsumer.from_settings")
@patch("worker.api.client.APIClient.from_settings")
@patch("worker.core.object_storage.SimpleObjectStorage.from_settings")
@patch("worker.core.asr_predictor.WhisperASRPredictor.from_settings")
async def test_nack_for_boundary(tc, api, objs, asr, error_count, test_settings):
    awaited = error_count >= 3
    worker = LazyLectureWorker(test_settings)
    message = AsyncMock()
    nacked = await worker._nack_for_state(
        message,
        TranscriptionInfo(
            creator_id=42,
            audio_len_secs=42,
            chunk_size_secs=9000,
            current_state=TranscriptionState.PROCESSING_ERROR,
            error_count=error_count,
        ),
        TaskData(transcription_id=42, user_id=42),
    )
    assert nacked == awaited


"""
Техника тест-дизайна: классы эквивалентности
Автор: Илья Тампио
Классы эквивалентности:
- Транскрипции которые не надо обрабатывать
- Транскрипции которые надо обрабатывать
"""


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "transcription_state",
    [
        TranscriptionState.COMPLETED,
        TranscriptionState.COMPLETED_PARTIALLY,
        TranscriptionState.PROCESSING_FAIL,
        TranscriptionState.CANCELLED,
        TranscriptionState.IN_PROGRESS,  # уже в обработке
    ],
)
@patch("worker.core.task_consumer.AioPikaTaskConsumer.from_settings")
@patch("worker.api.client.APIClient.from_settings")
@patch("worker.core.object_storage.SimpleObjectStorage.from_settings")
@patch("worker.core.asr_predictor.WhisperASRPredictor.from_settings")
async def test_terminal_nack(tc, api, objs, asr, transcription_state, test_settings):
    awaited = True
    worker = LazyLectureWorker(test_settings)
    message = AsyncMock()
    nacked = await worker._nack_for_state(
        message,
        TranscriptionInfo(
            creator_id=42, audio_len_secs=42, chunk_size_secs=9000, current_state=transcription_state, error_count=0
        ),
        TaskData(transcription_id=42, user_id=42),
    )
    assert nacked == awaited


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "transcription_state",
    [
        TranscriptionState.QUEUED,
        TranscriptionState.PROCESSING_ERROR,
    ],
)
@patch("worker.core.task_consumer.AioPikaTaskConsumer.from_settings")
@patch("worker.api.client.APIClient.from_settings")
@patch("worker.core.object_storage.SimpleObjectStorage.from_settings")
@patch("worker.core.asr_predictor.WhisperASRPredictor.from_settings")
async def test_nonterminal_not_nack(tc, api, objs, asr, transcription_state, test_settings):
    awaited = False
    worker = LazyLectureWorker(test_settings)
    message = AsyncMock()
    nacked = await worker._nack_for_state(
        message,
        TranscriptionInfo(
            creator_id=42, audio_len_secs=42, chunk_size_secs=9000, current_state=transcription_state, error_count=0
        ),
        TaskData(transcription_id=42, user_id=42),
    )
    assert nacked == awaited
