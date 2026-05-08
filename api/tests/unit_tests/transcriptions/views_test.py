from unittest.mock import ANY, AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from source.app.transcriptions.enums import TranscriptionState
from source.app.transcriptions.schemas import (
    TranscriptionChunksPagination,
    TranscriptionPagination,
    TranscriptionStatusUpdateRequest,
)
from source.app.transcriptions.views import (
    _transcript_cancel,
    _transcript_info,
    create_upload_file,
    transcript_export,
    transcript_list,
    transcriptions_list,
    worker_get_transcription_state,
    worker_post_transcription_state,
)


class FakeUser:
    id = 10
    can_interact = True


class FakeAudioFile:
    content_type = "audio/mpeg"

    def __init__(self):
        self.chunks = [b"audio", b""]

    async def read(self, size):
        return self.chunks.pop(0)


class FakeAioFile:
    def __init__(self):
        self.writes = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def write(self, chunk):
        self.writes.append(chunk)


def make_transcription(transcription_id=77):
    return type(
        "Transcription",
        (),
        {
            "id": transcription_id,
            "current_state": TranscriptionState.QUEUED,
        },
    )()


@pytest.mark.asyncio
async def test_transcriptions_list_view(monkeypatch):
    expected = object()
    monkeypatch.setattr("source.app.transcriptions.views.list_user_transcriptions", AsyncMock(return_value=expected))

    result = await transcriptions_list(FakeUser(), TranscriptionPagination(page=2, size=5), db=AsyncMock())

    assert result is expected


@pytest.mark.asyncio
async def test_transcript_list_view(monkeypatch):
    expected = object()
    monkeypatch.setattr("source.app.transcriptions.views.list_user_transcript", AsyncMock(return_value=expected))

    result = await transcript_list(FakeUser(), TranscriptionChunksPagination(page=1, size=5, task_id=9), db=AsyncMock())

    assert result is expected


@pytest.mark.asyncio
async def test_transcript_export_view(monkeypatch):
    monkeypatch.setattr("source.app.transcriptions.views.export_transcription", AsyncMock(return_value=b"file-bytes"))

    response = await transcript_export(FakeUser(), task_id=5, format="txt", db=AsyncMock())

    assert response.body == b"file-bytes"
    assert response.headers["content-disposition"] == 'attachment; filename="10.txt"'


@pytest.mark.asyncio
async def test_worker_post_transcription_state_view(monkeypatch):
    transcription = make_transcription()
    monkeypatch.setattr("source.app.transcriptions.views.update_transcription_state", AsyncMock(return_value=transcription))

    result = await worker_post_transcription_state(
        TranscriptionStatusUpdateRequest(transcription_id=1),
        secret_worker_token="token",
        db=AsyncMock(),
    )

    assert result == {"transcription": transcription}


@pytest.mark.asyncio
async def test_worker_get_transcription_state_view(monkeypatch):
    transcription = make_transcription()
    update_mock = AsyncMock(return_value=transcription)
    monkeypatch.setattr("source.app.transcriptions.views.update_transcription_state", update_mock)

    result = await worker_get_transcription_state(transcription_id=1, secret_worker_token="token", db=AsyncMock())

    assert result == {"transcription": transcription}
    assert update_mock.await_args.args[0].transcription_id == 1


@pytest.mark.asyncio
async def test_create_upload_file_rejects_invalid_content_type():
    audio = FakeAudioFile()
    audio.content_type = "audio/wav"

    with pytest.raises(HTTPException) as exc_info:
        await create_upload_file(FakeUser(), audio, task_q=(MagicMock(), "queue"), db=AsyncMock())

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_create_upload_file_normal_queue_path(monkeypatch):
    fake_file = FakeAioFile()
    db = AsyncMock()
    channel = MagicMock()
    send_mock = MagicMock()
    monkeypatch.setattr("source.app.transcriptions.views.aiofiles.open", lambda *args, **kwargs: fake_file)
    monkeypatch.setattr("source.app.transcriptions.views.get_audio_duration", lambda path: 120.0)
    monkeypatch.setattr("source.app.transcriptions.views.get_current_transcriptions", AsyncMock(return_value=[]))
    monkeypatch.setattr("source.app.transcriptions.views.create_transcription", AsyncMock(return_value=make_transcription(77)))
    monkeypatch.setattr("source.app.transcriptions.views.send_transcription_job_to_queue", send_mock)
    monkeypatch.setattr("source.app.transcriptions.views.settings.DISABLE_WORKER", False)
    monkeypatch.setattr("source.app.transcriptions.views.settings.OBJECT_STORAGE_PATH", "/object_storage")

    result = await create_upload_file(FakeUser(), FakeAudioFile(), task_q=(channel, "queue"), db=db)

    assert result["message"] == "File uploaded successfully"
    assert result["task_id"] == 77
    assert fake_file.writes == [b"audio"]
    send_mock.assert_called_once_with(channel, "queue", 77, 10)


@pytest.mark.asyncio
async def test_create_upload_file_raises_when_user_has_active_transcription(monkeypatch):
    monkeypatch.setattr("source.app.transcriptions.views.aiofiles.open", lambda *args, **kwargs: FakeAioFile())
    monkeypatch.setattr("source.app.transcriptions.views.get_audio_duration", lambda path: 120.0)
    monkeypatch.setattr(
        "source.app.transcriptions.views.get_current_transcriptions",
        AsyncMock(return_value=[make_transcription(42)]),
    )

    with pytest.raises(ValueError, match="Please cancel the job"):
        await create_upload_file(FakeUser(), FakeAudioFile(), task_q=(MagicMock(), "queue"), db=AsyncMock())


@pytest.mark.asyncio
async def test_create_upload_file_worker_disabled_path(monkeypatch):
    db = AsyncMock()
    db.add = MagicMock()
    monkeypatch.setattr("source.app.transcriptions.views.aiofiles.open", lambda *args, **kwargs: FakeAioFile())
    monkeypatch.setattr("source.app.transcriptions.views.get_audio_duration", lambda path: 120.0)
    monkeypatch.setattr("source.app.transcriptions.views.get_current_transcriptions", AsyncMock(return_value=[]))
    monkeypatch.setattr("source.app.transcriptions.views.create_transcription", AsyncMock(return_value=make_transcription(88)))
    monkeypatch.setattr("source.app.transcriptions.views.settings.DISABLE_WORKER", True)
    monkeypatch.setattr("source.app.transcriptions.views.settings.OBJECT_STORAGE_PATH", "/object_storage")

    result = await create_upload_file(FakeUser(), FakeAudioFile(), task_q=(None, ""), db=db)

    assert result["message"] == "File uploaded successfully (worker disabled)"
    assert result["task_id"] == 88
    db.add.assert_called_once()


@pytest.mark.asyncio
async def test_transcript_cancel_view(monkeypatch):
    cancel_mock = AsyncMock(return_value=None)
    monkeypatch.setattr("source.app.transcriptions.views.cancel_transcript", cancel_mock)

    response = await _transcript_cancel(FakeUser(), transcript_id=7, db=AsyncMock())

    assert response.body == b"OK"
    cancel_mock.assert_awaited_once_with(transcript_id=7, user_id=10, db=ANY)


@pytest.mark.asyncio
async def test_transcript_info_view(monkeypatch):
    expected = make_transcription()
    info_mock = AsyncMock(return_value=expected)
    monkeypatch.setattr("source.app.transcriptions.views.info_transcript", info_mock)

    result = await _transcript_info(FakeUser(), transcript_id=7, db=AsyncMock())

    assert result is expected
    info_mock.assert_awaited_once_with(transcript_id=7, user_id=10, db=ANY)
