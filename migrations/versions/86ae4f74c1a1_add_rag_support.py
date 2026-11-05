
"""add RAG support

Revision ID: 86ae4f74c1a1
Revises: c212833f0f3d
Create Date: 2026-11-05 11:22:54.975385

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import VECTOR


revision: str = '86ae4f74c1a1'
down_revision: Union[str, Sequence[str], None] = 'c212833f0f3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        'job_application_chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_application_id', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', VECTOR(768), nullable=False),

        sa.ForeignKeyConstraint(
            ['job_application_id'],
            ['job_applications.id'],
            ondelete='CASCADE'
        ),

        sa.PrimaryKeyConstraint('id'),

        sa.UniqueConstraint(
            'job_application_id',
            'chunk_index',
            name='uq_job_application_chunk_index'
        )
    )

    op.create_index(
        'ix_job_application_chunks_job_application_id',
        'job_application_chunks',
        ['job_application_id'],
        unique=False
    )

    op.add_column(
        'job_applications',
        sa.Column('job_description', sa.Text(), nullable=True)
    )


def downgrade() -> None:

    op.drop_column(
        'job_applications',
        'job_description'
    )

    op.drop_index(
        'ix_job_application_chunks_job_application_id',
        table_name='job_application_chunks'
    )

    op.drop_table('job_application_chunks')
