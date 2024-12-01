from datetime import datetime

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


# Pagination
class TranscriptionPagination(PaginationSchema):
    pass


class TranscriptionPage(PageSchema):
    transcriptions: list[TranscriptionResponse]
