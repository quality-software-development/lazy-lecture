"""add: processing error counter

Revision ID: 9dea1ae5767c
Revises: 02a75a11fa97
Create Date: 2025-02-02 01:40:04.297699

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9dea1ae5767c"
down_revision = "02a75a11fa97"
branch_labels = None
depends_on = None


def upgrade():
    # Add the new column 'error_count' with a default value of zero
    op.add_column("Transcription", sa.Column("error_count", sa.Integer(), nullable=True, default=0))
    op.execute('UPDATE "Transcription" SET error_count = 0 WHERE error_count IS NULL')
    op.alter_column("Transcription", "error_count", nullable=False)


def downgrade():
    # Remove the column in case of downgrade
    op.drop_column("Transcription", "error_count")
