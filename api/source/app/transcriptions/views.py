import os
import typing as tp

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import PlainTextResponse
from source.app.auth.auth import CanInteractCurrentUser, CurrentUser
from source.app.transcriptions.enums import TranscriptionState
from source.app.transcriptions.models import Transcription
from source.app.transcriptions.schemas import (
    TranscriptionChunksPage,
    TranscriptionChunksPagination,
    TranscriptionPage,
    TranscriptionPagination,
    TranscriptionRequest,
    TranscriptionStatusUpdateRequest,
)
from source.app.transcriptions.services import (
    cancel_transcript,
    create_transcription,
    export_transcription,
    get_audio_duration,
    get_current_transcriptions,
    info_transcript,
    list_user_transcript,
    list_user_transcriptions,
    send_transcription_job_to_queue,
    update_transcription_state,
)
from source.core.database import get_db
from source.core.schemas import ExceptionSchema
from source.core.settings import settings
from source.core.task_queue import get_task_queue
from sqlalchemy.ext.asyncio import AsyncSession

from .types import ValidAudioFile, validate_worker_token

transcriptions_router = APIRouter(prefix="", tags=["transcriptions"])


@transcriptions_router.get(
    "/transcriptions",
    response_model=TranscriptionPage,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema}},
)
async def transcriptions_list(
    user: CurrentUser, pagination: TranscriptionPagination = Depends(), db: AsyncSession = Depends(get_db)
) -> TranscriptionPage:
    return await list_user_transcriptions(
        page=pagination.page,
        size=pagination.size,
        user_id=user.id,
        db=db,
    )


@transcriptions_router.get(
    "/transcript",
    response_model=TranscriptionChunksPage,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema}},
)
async def transcript_list(
    user: CurrentUser, pagination: TranscriptionChunksPagination = Depends(), db: AsyncSession = Depends(get_db)
) -> TranscriptionChunksPage:
    return await list_user_transcript(
        page=pagination.page,
        size=pagination.size,
        transcription_id=pagination.task_id,
        db=db,
    )


@transcriptions_router.post(
    "/transcript/export",
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema}},
)
async def transcript_export(
    user: CurrentUser, task_id: int, format: tp.Literal["doc", "txt"], db: AsyncSession = Depends(get_db)
):
    file_bytes: bytes = await export_transcription(task_id, format, db)
    headers = {"Content-Disposition": f'attachment; filename="{user.id}.{format}"'}
    return Response(file_bytes, headers=headers)


@transcriptions_router.post(
    "/worker/transcription_status",
)
async def worker_post_transcription_state(
    data: TranscriptionStatusUpdateRequest,
    secret_worker_token: str = Depends(validate_worker_token),
    db: AsyncSession = Depends(get_db),
):
    transcription = await update_transcription_state(data, db)
    return {"transcription": transcription}


@transcriptions_router.get(
    "/worker/transcription_status",
)
async def worker_get_transcription_state(
    transcription_id: int,
    secret_worker_token: str = Depends(validate_worker_token),
    db: AsyncSession = Depends(get_db),
):
    data = TranscriptionStatusUpdateRequest(transcription_id=transcription_id)
    transcription = await update_transcription_state(data, db)
    return {"transcription": transcription}


@transcriptions_router.post(
    "/upload-audiofile",
)
async def create_upload_file(
    user: CanInteractCurrentUser,
    audiofile: ValidAudioFile,
    task_q: tp.Tuple[tp.Any, str] = Depends(get_task_queue),
    db: AsyncSession = Depends(get_db),
):
    if audiofile.content_type != "audio/mpeg":
        raise HTTPException(400, detail="Invalid audio file")
    user_id = user.id
    out_file_path = os.path.join(settings.OBJECT_STORAGE_PATH, f"{user_id}.mp3")

    async with aiofiles.open(out_file_path, "wb") as out_file:
        while chunk := await audiofile.read(512 * 1024):  # Read in 0.5 MB chunks
            await out_file.write(chunk)  # Write each chunk

    audio_len_sec = get_audio_duration(out_file_path)
    channel, q_name = task_q

    current_transcriptions: tp.List[Transcription] = await get_current_transcriptions(
        user_id=user.id,
        db=db,
    )
    if len(current_transcriptions) != 0:
        raise ValueError(
            f"Transcription {current_transcriptions[0].id} is {current_transcriptions[0].current_state}. Please cancel the job or wait before its completion to start a new one."
        )

    transcription: Transcription = await create_transcription(
        TranscriptionRequest(
            creator_id=user.id,
            audio_len_secs=audio_len_sec,
            chunk_size_secs=settings.DEFAULT_CHUNK_SIZE,
            current_state=TranscriptionState.QUEUED,
        ),
        db,
    )
    if not transcription:
        raise HTTPException(500, detail="failed to create the transcription")
    transcription_id = transcription.id
    send_transcription_job_to_queue(channel, q_name, transcription_id, user_id)
    return {"message": "File uploaded successfully", "task_id": transcription_id, "file": out_file_path}


@transcriptions_router.post("/transcript/cancel")
async def _transcript_cancel(
    user: CurrentUser,
    transcript_id: int,
    db: AsyncSession = Depends(get_db),
):
    _ = await cancel_transcript(transcript_id=transcript_id, user_id=user.id, db=db)
    return PlainTextResponse(content="OK")


@transcriptions_router.get("/transcript/info")
async def _transcript_info(
    user: CurrentUser,
    transcript_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await info_transcript(transcript_id=transcript_id, user_id=user.id, db=db)
