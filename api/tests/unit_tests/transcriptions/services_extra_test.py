from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from source.app.transcriptions.enums import TranscriptionState
from source.app.transcriptions.models import Transcription, TranscriptionChunk
from source.app.transcriptions.schemas import CreateTranscriptionChunk, TranscriptionRequest, TranscriptionStatusUpdateRequest
from source.app.transcriptions.services import (
    add_new_chunk,
    create_transcription,
    get_current_transcriptions,
    get_transcritption_descrtiption,
    list_user_transcript,
    list_user_transcriptions,
    update_transcription_state,
)


class ResultList:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


def make_transcription(transcription_id=1, creator_id=10):
    now = datetime.now(timezone.utc)
    transcription = Transcription()
    transcription.id = transcription_id
    transcription.creator_id = creator_id
    transcription.audio_len_secs = 120.0
    transcription.chunk_size_secs = 60.0
    transcription.current_state = TranscriptionState.QUEUED
    transcription.error_count = 0
    transcription.create_date = now
    transcription.update_date = now
    return transcription


def make_chunk(chunk_id=1, transcript_id=1, chunk_no=0, text="first chunk"):
    chunk = TranscriptionChunk()
    chunk.id = chunk_id
    chunk.transcript_id = transcript_id
    chunk.chunk_no = chunk_no
    chunk.text = text
    return chunk


@pytest.mark.asyncio
async def test_get_transcription_description_returns_first_chunk_text():
    db = MagicMock()
    db.scalar = AsyncMock(return_value=make_chunk(text="x" * 300))

    result = await get_transcritption_descrtiption(1, db)

    assert result == "x" * 256


@pytest.mark.asyncio
async def test_get_transcription_description_empty_when_no_chunk():
    db = MagicMock()
    db.scalar = AsyncMock(return_value=None)

    assert await get_transcritption_descrtiption(1, db) == ""


@pytest.mark.asyncio
async def test_list_user_transcriptions_builds_page(monkeypatch):
    db = MagicMock()
    db.scalars = AsyncMock(return_value=ResultList([make_transcription()]))
    db.scalar = AsyncMock(return_value=1)
    monkeypatch.setattr(
        "source.app.transcriptions.services.get_transcritption_descrtiption",
        AsyncMock(return_value="description"),
    )

    page = await list_user_transcriptions(page=1, size=10, user_id=10, db=db)

    assert page.total == 1
    assert page.pages == 1
    assert page.transcriptions[0].description == "description"


@pytest.mark.asyncio
async def test_list_user_transcript_builds_chunks_page():
    db = MagicMock()
    db.get_one = AsyncMock(return_value=make_transcription())
    db.scalars = AsyncMock(return_value=ResultList([make_chunk(text="chunk text")]))
    db.scalar = AsyncMock(return_value=1)

    page = await list_user_transcript(page=1, size=10, transcription_id=1, db=db)

    assert page.total == 1
    assert page.transcriptions[0].transcription == "chunk text"
    assert page.transcriptions[0].chunk_size_secs == 60


@pytest.mark.asyncio
async def test_create_transcription_integrity_error_rolls_back():
    db = MagicMock()
    db.add = MagicMock()
    db.scalars = AsyncMock(return_value=ResultList([]))
    db.commit = AsyncMock(side_effect=IntegrityError("statement", "params", Exception("duplicate")))
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()
    request = TranscriptionRequest(
        creator_id=10,
        audio_len_secs=120.0,
        chunk_size_secs=60.0,
        current_state=TranscriptionState.QUEUED,
    )

    result = await create_transcription(request, db)

    assert result is None
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_new_chunk_success():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    chunk = make_chunk()

    result = await add_new_chunk(chunk, db)

    assert result is chunk
    db.add.assert_called_once_with(chunk)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(chunk)


@pytest.mark.asyncio
async def test_add_new_chunk_integrity_error_rolls_back():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock(side_effect=IntegrityError("statement", "params", Exception("duplicate")))
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()

    assert await add_new_chunk(make_chunk(), db) is None
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_transcription_state_adds_new_chunk():
    db = MagicMock()
    transcription = make_transcription()
    db.get_one = AsyncMock(return_value=transcription)
    db.scalar = AsyncMock(return_value=None)
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    result = await update_transcription_state(
        TranscriptionStatusUpdateRequest(
            transcription_id=1,
            new_chunk=CreateTranscriptionChunk(chunk_no=1, text="new text"),
        ),
        db,
    )

    assert result is transcription
    db.add.assert_called_once()


@pytest.mark.asyncio
async def test_update_transcription_state_raises_when_transcription_missing():
    db = MagicMock()
    db.get_one = AsyncMock(return_value=None)

    with pytest.raises(ValueError, match="Transcription does not exist"):
        await update_transcription_state(
            TranscriptionStatusUpdateRequest(
                transcription_id=404,
                current_state=TranscriptionState.IN_PROGRESS,
            ),
            db,
        )


@pytest.mark.asyncio
async def test_update_transcription_state_updates_existing_chunk():
    db = MagicMock()
    transcription = make_transcription()
    old_chunk = make_chunk(text="old")
    db.get_one = AsyncMock(side_effect=[transcription, old_chunk, transcription])
    db.scalar = AsyncMock(return_value=old_chunk)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    result = await update_transcription_state(
        TranscriptionStatusUpdateRequest(
            transcription_id=1,
            new_chunk=CreateTranscriptionChunk(chunk_no=0, text="updated"),
        ),
        db,
    )

    assert result is transcription
    assert old_chunk.text == "updated"
    db.refresh.assert_awaited_once_with(old_chunk)


@pytest.mark.asyncio
async def test_update_transcription_state_raises_when_add_chunk_fails(monkeypatch):
    db = MagicMock()
    db.get_one = AsyncMock(return_value=make_transcription())
    db.scalar = AsyncMock(return_value=None)
    monkeypatch.setattr("source.app.transcriptions.services.add_new_chunk", AsyncMock(return_value=None))

    with pytest.raises(ValueError, match="Failed to add new chunk"):
        await update_transcription_state(
            TranscriptionStatusUpdateRequest(
                transcription_id=1,
                new_chunk=CreateTranscriptionChunk(chunk_no=0, text="text"),
            ),
            db,
        )


@pytest.mark.asyncio
async def test_get_current_transcriptions_returns_active_items():
    db = MagicMock()
    active = [make_transcription()]
    db.scalars = AsyncMock(return_value=ResultList(active))

    assert await get_current_transcriptions(user_id=10, db=db) == active
