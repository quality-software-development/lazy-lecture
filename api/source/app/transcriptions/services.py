import json
import typing as tp
from io import BytesIO
from math import ceil, floor
from pathlib import Path
from typing import Any, Mapping, Union

import pika
import pika.channel
from docx import Document
from mutagen.mp3 import MP3
from source.app.transcriptions.models import Transcription, TranscriptionChunk
from source.app.transcriptions.schemas import (
    TranscriptionChunkResponse,
    TranscriptionChunksPage,
    TranscriptionPage,
    TranscriptionRequest,
    TranscriptionResponse,
    TranscriptionStatusUpdateRequest,
)
from sqlalchemy import asc, desc, func, select, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .enums import TranscriptionState


async def get_transcritption_descrtiption(transcription_id: int, db: AsyncSession) -> str:
    transcription_first_chunk: TranscriptionChunk = await db.scalar(
        select(TranscriptionChunk).where(
            and_(TranscriptionChunk.transcript_id == transcription_id, TranscriptionChunk.chunk_no == 0)
        )
    )
    return transcription_first_chunk.text[:256] if transcription_first_chunk else ""


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d


async def list_user_transcriptions(page: int, size: int, user_id: int, db: AsyncSession) -> TranscriptionPage:
    order = desc("create_date")
    transcriptions = await db.scalars(
        select(Transcription)
        .order_by(order)
        .offset((page - 1) * size)
        .limit(size)
        .where(Transcription.creator_id == user_id)
    )
    transcriptions: tp.List[Transcription] = transcriptions.all()
    total = await db.scalar(select(func.count(Transcription.id)).where(Transcription.creator_id == user_id))
    return TranscriptionPage(
        transcriptions=[
            TranscriptionResponse(
                **transcript.__dict__, description=await get_transcritption_descrtiption(transcript.id, db)
            )
            for transcript in transcriptions
        ],
        page=page,
        size=size,
        total=total,
        pages=(ceil(total / size)),
    )


async def list_user_transcript(
    page: int, size: int, transcription_id: int, db: AsyncSession
) -> TranscriptionChunksPage:
    transcription = await db.get_one(Transcription, transcription_id)
    transcription_chunks = await db.scalars(
        select(TranscriptionChunk).where(TranscriptionChunk.transcript_id == transcription_id).order_by(asc("chunk_no"))
    )
    transcription_chunks = transcription_chunks.all()
    chunk_size_secs = transcription.chunk_size_secs
    total = await db.scalar(
        select(func.count(TranscriptionChunk.id)).where(TranscriptionChunk.transcript_id == transcription_id)
    )

    return TranscriptionChunksPage(
        transcriptions=[
            TranscriptionChunkResponse(
                id=tc.id, chunk_order=tc.chunk_no, chunk_size_secs=chunk_size_secs, transcription=tc.text
            )
            for tc in transcription_chunks
        ],
        page=page,
        size=size,
        total=total,
        pages=(ceil(total / size)),
    )


def send_transcription_job_to_queue(
    channel: pika.channel.Channel,
    queue_name: str,
    transcription_id: int,
    user_id: int,
) -> Mapping[str, Any]:
    job_dict = {
        "transcription_id": transcription_id,
        "user_id": user_id,
    }
    channel.basic_publish(exchange="", routing_key=queue_name, body=json.dumps(job_dict))
    return job_dict


def get_audio_len(fpath: Union[str, Path]) -> float:
    p = Path(fpath)
    if not p.exists():
        raise FileNotFoundError(str(p))
    return MP3(str(p)).info.length


async def create_transcription(create_transcription: TranscriptionRequest, db: AsyncSession) -> Transcription | None:
    try:
        transcription = Transcription(**create_transcription.model_dump())
        db.add(transcription)
        await db.commit()
        await db.refresh(transcription)
        return transcription
    except IntegrityError as e:
        await db.rollback()  # Rollback transaction on failure
        print(f"IntegrityError occurred: {e}")
        return None


async def add_new_chunk(chunk: TranscriptionChunk, db: AsyncSession):
    try:
        db.add(chunk)
        await db.commit()
        await db.refresh(chunk)
        return chunk
    except IntegrityError as e:
        await db.rollback()  # Rollback transaction on failure
        print(f"IntegrityError occurred: {e}")
        return None


async def update_transcription_state(data: TranscriptionStatusUpdateRequest, db: AsyncSession) -> Transcription:
    transcription_id = data.transcription_id
    new_state = data.current_state
    new_chunk = data.new_chunk

    if new_state is not None:
        transcription = await db.get_one(Transcription, transcription_id)
        if transcription is None:
            raise ValueError("Transcription does not exist")

        if new_state == TranscriptionState.PROCESSING_ERROR:
            error_count = transcription.error_count + 1
            transcription.error_count = error_count
            if error_count >= 3:
                transcription.current_state = TranscriptionState.PROCESSING_FAIL
            else:
                transcription.current_state = new_state
        else:
            transcription.current_state = new_state

        await db.commit()

    if new_chunk is not None:
        # Check if the chunk is proper
        transcription = await db.get_one(Transcription, transcription_id)
        audio_len_secs = transcription.audio_len_secs
        chunk_size_secs = transcription.chunk_size_secs
        max_chunk_no = floor(audio_len_secs / chunk_size_secs)
        if new_chunk.chunk_no > max_chunk_no:
            raise ValueError(f"Chunk no is bigger than max chunk no {new_chunk.chunk_no} > {max_chunk_no}")
        # Add chunk
        transcription_chunk = TranscriptionChunk(
            transcript_id=transcription_id,
            chunk_no=new_chunk.chunk_no,
            text=new_chunk.text,
        )
        possible_old_chunk = await db.scalar(
            select(TranscriptionChunk).where(
                and_(
                    TranscriptionChunk.transcript_id == transcription_id,
                    TranscriptionChunk.chunk_no == new_chunk.chunk_no,
                )
            )
        )
        if possible_old_chunk is not None:
            old_chunk_id = possible_old_chunk.id
            chunk_for_update = await db.get_one(TranscriptionChunk, old_chunk_id)
            chunk_for_update.text = new_chunk.text
            await db.commit()
            await db.refresh(chunk_for_update)
        else:
            new_chunk = await add_new_chunk(transcription_chunk, db)
            if new_chunk is None:
                raise ValueError("Failed to add new chunk")

    transcription = await db.get_one(Transcription, transcription_id)
    return transcription


def get_transcription_doc(transcription_text: str) -> bytes:
    doc = Document()
    doc.add_paragraph(transcription_text)
    byte_io = BytesIO()
    doc.save(byte_io)
    byte_io.seek(0)
    return byte_io.read()


async def export_transcription(transcription_id: int, format: tp.Literal["doc", "txt"], db: AsyncSession) -> bytes:
    transcription = await db.get_one(Transcription, transcription_id)
    transcription_chunks = await db.scalars(
        select(TranscriptionChunk).where(TranscriptionChunk.transcript_id == transcription_id).order_by(asc("chunk_no"))
    )
    transcription_chunks = transcription_chunks.all()
    if len(transcription_chunks) == 0:
        raise ValueError("No transcription chunks for this transcription is available right now. Try again later.")

    transcription_text: str = "\n\n".join([chunk.text for chunk in transcription_chunks])
    if format == "txt":
        return transcription_text.encode("utf-8")
    else:
        return get_transcription_doc(transcription_text)


async def get_user_trancsript(user_id: int, transcript_id: int, db: AsyncSession):
    transcript = await db.get_one(Transcription, transcript_id)
    if transcript.creator_id != user_id:
        raise ValueError("You may cancel processing only of your transcript")
    return transcript


async def cancel_transcript(user_id: int, transcript_id: int, db: AsyncSession) -> None:
    transcript = await get_user_trancsript(user_id, transcript_id, db)
    if transcript.current_state in [
        TranscriptionState.COMPLETED,
        TranscriptionState.COMPLETED_PARTIALLY,
        TranscriptionState.PROCESSING_FAIL,
        TranscriptionState.CANCELLED,
    ]:
        raise ValueError("You can't cancel a finished job")
    transcript.current_state = TranscriptionState.CANCELLED

    await db.commit()
    await db.refresh(transcript)


async def info_transcript(
    user_id: int,
    transcript_id: int,
    db: AsyncSession,
) -> TranscriptionResponse:
    return await get_user_trancsript(user_id, transcript_id, db)
