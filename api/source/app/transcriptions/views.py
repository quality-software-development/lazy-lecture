from fastapi import APIRouter, Depends, status

from source.app.transcriptions.schemas import TranscriptionPage, TranscriptionPagination
from source.app.transcriptions.services import list_user_transcriptions
from source.core.database import get_db
from source.app.auth.auth import CanInteractCurrentUser
from source.core.schemas import ExceptionSchema
from sqlalchemy.ext.asyncio import AsyncSession

transcriptions_router = APIRouter(prefix="/transcriptions", tags=["transcriptions"])


@transcriptions_router.get(
    "/",
    response_model=TranscriptionPage,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema}},
)
async def transcriptions_list(
    user: CanInteractCurrentUser, pagination: TranscriptionPagination = Depends(), db: AsyncSession = Depends(get_db)
) -> TranscriptionPage:
    return await list_user_transcriptions(
        page=pagination.page,
        size=pagination.size,
        user_id=user.id,
        db=db,
    )
