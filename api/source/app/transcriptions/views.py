import os
import random
import typing as tp

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile

from source.app.transcriptions.schemas import (
    SingleTranscriptionPage,
    SingleTranscriptionPagination,
    TranscriptionPage,
    TranscriptionPagination,
)
from source.app.transcriptions.services import list_user_transcript, list_user_transcriptions
from source.core.database import get_db
from source.app.auth.auth import CanInteractCurrentUser, CurrentUser
from source.core.schemas import ExceptionSchema
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.responses import FileResponse
import aiofiles

from source.core.settings import settings

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
    if format == "doc":
        return FileResponse("mock/mock.docx", filename=f"transcription_{task_id}.docx")
    else:
        return FileResponse("mock/mock.txt", filename=f"transcription_{task_id}.txt")


@transcriptions_router.post(
    "/upload-audiofile",
)
async def create_upload_file(user: CanInteractCurrentUser, audiofile: UploadFile):
    if audiofile.content_type != "audio/mpeg":
        raise HTTPException(400, detail="Invalid audio file")
    out_file_path = os.path.join(settings.OBJECT_STORAGE_PATH, f"{user.id}.mp3")
    async with aiofiles.open(out_file_path, "wb") as out_file:
        content = await audiofile.read()  # async read
        await out_file.write(content)  # async write

    # TODO: set task for inference

    return {"message": "File uploaded successfully", "task_id": str(random.randint(0, 10000)), "file": out_file_path}
