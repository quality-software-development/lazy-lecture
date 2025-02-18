import typing as tp
from enum import Enum

from pydantic import BaseModel, PositiveInt


class TranscriptionState(str, Enum):
    # start
    QUEUED = "queued"

    # intermediate
    IN_PROGRESS = "in_progress"
    PROCESSING_ERROR = "processing_error"

    # final
    COMPLETED = "completed"
    COMPLETED_PARTIALLY = "completed_partially"
    PROCESSING_FAIL = "processing_fail"
    CANCELLED = "cancelled"


class GetTranscriptionStateRequestData(BaseModel):
    transcription_id: int


class TranscriptionInfo(BaseModel):
    creator_id: int
    audio_len_secs: float
    chunk_size_secs: int
    current_state: TranscriptionState
    error_count: int


class TranscriptionChunk(BaseModel):
    text: str
    chunk_no: int


class UpdateTranscriptionStateRequestData(BaseModel):
    transcription_id: int
    current_state: tp.Optional[TranscriptionState] = None
    new_chunk: tp.Optional[TranscriptionChunk] = None


class TaskData(BaseModel):
    transcription_id: PositiveInt
    user_id: PositiveInt
