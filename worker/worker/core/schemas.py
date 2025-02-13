from pydantic import BaseModel


class CreateTranscriptionChunk(BaseModel):
    text: str
    chunk_no: int
