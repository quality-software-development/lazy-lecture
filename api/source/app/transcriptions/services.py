from datetime import datetime
from math import ceil
import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc, func, select

from source.app.transcriptions.enums import TranscriptionState
from source.app.transcriptions.models import Transcription
from source.app.auth.auth import CanInteractCurrentUser
from source.app.transcriptions.schemas import (
    SingleTranscriptionPage,
    SingleTranscriptionResponse,
    TranscriptionPage,
    TranscriptionResponse,
)


async def list_user_transcriptions(page: int, size: int, user_id: int, db: AsyncSession) -> TranscriptionPage:
    order = desc("create_date")
    transcriptions = await db.scalars(
        select(Transcription)
        .order_by(order)
        .offset((page - 1) * size)
        .limit(size)
        .where(Transcription.creator_id == user_id)
    )
    total = await db.scalar(select(func.count(Transcription.id)))

    # TODO: remove mock
    if transcriptions.all() == [] and True:
        mock_count = 5
        transcriptions = [
            TranscriptionResponse(
                id=random.randint(0, 100),
                creator_id=random.randint(0, 100),
                audio_len_secs=random.randint(60, 60 * 120),
                chunk_size_secs=60 * 15,
                current_state=random.choice(list(TranscriptionState)),
                create_date=datetime.now(),
                update_date=datetime.now(),
                description="Enim in consequatur est commodi illum sint repellat. Recusandae dolores sint a quod deserunt est voluptatibus. Impedit vero recusandae enim. Et id qui eos cum vel veritatis.",
            )
            for _ in range(mock_count)
        ]

    return TranscriptionPage(
        transcriptions=transcriptions,
        page=page,
        size=size,
        total=total,
        pages=(ceil(total / size)),
    )


async def list_user_transcript(page: int, size: int, task_id: int, db: AsyncSession) -> TranscriptionPage:
    # TODO: remove mock
    if True:
        chunk_size = 60 * random.randint(0, 10)
        total = random.randint(0, 100)
        transcriptions = [
            SingleTranscriptionResponse(
                id=random.randint(0, 100),
                chunk_order=(page - 1) * size + i,
                chunk_size_secs=chunk_size,
                transcription="Enim in consequatur est commodi illum sint repellat. Recusandae dolores sint a quod deserunt est voluptatibus. Impedit vero recusandae enim. Et id qui eos cum vel veritatis."
                * random.randint(1, 5),
            )
            for i in range(min(total, page * size) - (page - 1) * size)
        ]
        return SingleTranscriptionPage(
            transcriptions=transcriptions,
            page=page,
            size=size,
            total=total,
            pages=(ceil(total / size)),
        )
