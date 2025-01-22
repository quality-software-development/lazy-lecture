"""Add TranscriptionChunk table

Revision ID: 02a75a11fa97
Revises: 43703d06f36e
Create Date: 2025-01-22 01:06:10.922391

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "02a75a11fa97"
down_revision = "43703d06f36e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "TranscriptionChunk",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("transcript_id", sa.Integer(), nullable=False),
        sa.Column("chunk_no", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("create_date", sa.DateTime(), nullable=True),
        sa.Column("update_date", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["transcript_id"], ["Transcription.id"], name="fk_transcriptionchunk_transcription"),
        sa.UniqueConstraint("transcript_id", "chunk_no", name="uq_transcript_chunk"),
    )


def downgrade() -> None:
    op.drop_table("TranscriptionChunk")
