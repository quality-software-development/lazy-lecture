import os
import random
import typing as tp

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile

from source.app.transcriptions.enums import TranscriptionState
from source.app.transcriptions.models import Transcription
from source.core.task_queue import get_task_queue
from source.app.transcriptions.schemas import (
    SingleTranscriptionPage,
    SingleTranscriptionPagination,
    TranscriptionPage,
    TranscriptionPagination,
    TranscriptionRequest,
)
from source.app.transcriptions.services import (
    create_transcription,
    get_audio_len,
    list_user_transcript,
    list_user_transcriptions,
    send_transcription_job_to_queue,
)
from source.core.database import get_db
from source.app.auth.auth import CanInteractCurrentUser, CurrentUser
from source.core.schemas import ExceptionSchema
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.responses import FileResponse
import aiofiles

from source.core.settings import settings
from .types import ValidAudioFile

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
    response_model=SingleTranscriptionPage,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema}},
)
async def transcript_list(
    user: CurrentUser, pagination: SingleTranscriptionPagination = Depends(), db: AsyncSession = Depends(get_db)
) -> SingleTranscriptionPage:
    return await list_user_transcript(
        page=pagination.page,
        size=pagination.size,
        task_id=pagination.task_id,
        db=db,
    )


@transcriptions_router.get(
    "/transcript/export",
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema}},
)
async def transcript_list(
    user: CurrentUser, task_id: int, format: tp.Literal["doc", "txt"], db: AsyncSession = Depends(get_db)
) -> SingleTranscriptionPage:
    # TODO: return actual list

    if format == "doc":
        return FileResponse("mock/mock.docx", filename=f"transcription_{task_id}.docx")
    else:
        return FileResponse("mock/mock.txt", filename=f"transcription_{task_id}.txt")


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
        while chunk := await audiofile.read(1024 * 1024):  # Read in 1MB chunks
            await out_file.write(chunk)  # Write each chunk

    # with aiofiles.open(out_file_path, "wb") as out_file:
    #     content = await audiofile.read()  # async read
    #     await out_file.write(content)  # async write

    audio_len_sec = get_audio_len(out_file_path)

    channel, q_name = task_q

    # TODO: create transcription
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
