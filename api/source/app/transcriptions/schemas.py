from datetime import datetime

from pydantic import BaseModel

from source.core.schemas import PageSchema, PaginationSchema, ResponseSchema
from source.app.transcriptions.enums import TranscriptionState


class TranscriptionResponse(ResponseSchema):
    id: int
    creator_id: int
    audio_len_secs: float
    chunk_size_secs: float
    current_state: TranscriptionState
    create_date: datetime
    update_date: datetime
    description: str


class SingleTranscriptionResponse(ResponseSchema):
    chunk_order: int
    chunk_size_secs: int
    transcription: str


# Pagination
class TranscriptionPagination(PaginationSchema):
    pass


class SingleTranscriptionPagination(PaginationSchema):
    task_id: int
    pass


class TranscriptionPage(PageSchema):
    transcriptions: list[TranscriptionResponse]


class SingleTranscriptionPage(PageSchema):
    transcriptions: list[SingleTranscriptionResponse]


class TranscriptionRequest(BaseModel):
    creator_id: int
    audio_len_secs: float
    chunk_size_secs: float
    current_state: TranscriptionState
