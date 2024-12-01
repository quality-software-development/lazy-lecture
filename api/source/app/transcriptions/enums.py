from enum import Enum


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
