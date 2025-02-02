from datetime import datetime
import typing as tp

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
    error_count: int


class TranscriptionChunkResponse(ResponseSchema):
    chunk_order: int
    chunk_size_secs: int
    transcription: str


# Pagination
class TranscriptionPagination(PaginationSchema):
    pass


class TranscriptionChunksPagination(PaginationSchema):
    task_id: int
    pass


class TranscriptionPage(PageSchema):
    transcriptions: list[TranscriptionResponse]


class TranscriptionChunksPage(PageSchema):
    transcriptions: list[TranscriptionChunkResponse]


class TranscriptionRequest(BaseModel):
    creator_id: int
    audio_len_secs: float
    chunk_size_secs: float
    current_state: TranscriptionState


class CreateTranscriptionChunk(BaseModel):
    text: str
    chunk_no: int


class TranscriptionStatusUpdateRequest(BaseModel):
    transcription_id: int
    current_state: tp.Optional[TranscriptionState] = None
    new_chunk: tp.Optional[CreateTranscriptionChunk] = None
