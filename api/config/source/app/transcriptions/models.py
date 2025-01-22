from sqlalchemy import Column, Float, Integer, Enum, ForeignKey, Text

from source.app.transcriptions.enums import TranscriptionState
from source.core.models import Model


class Transcription(Model):
    __tablename__ = "Transcription"

    creator_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    audio_len_secs = Column(name="audio_len_secs", type_=Float)
    chunk_size_secs = Column(name="chunk_size_secs", type_=Float)
    current_state = Column(name="current_state", type_=Enum(TranscriptionState))


class TranscriptionChunk(Model):
    __tablename__ = "TranscriptionChunk"

    transcript_id = Column(Integer, ForeignKey("Transcription.id"), nullable=False)
    chunk_no = Column(name="chunk_no", type_=Integer)
    text = Column(name="text", type_=Text)
