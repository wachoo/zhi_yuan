"""add skill_id to chat_sessions

Revision ID: e1f2a3b4c5d6
Revises: d4e5f6a7b8c9
Create Date: 2026-06-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chat_sessions', sa.Column('skill_id', sa.String(length=50), nullable=True))
    # Backfill: set skill_id from the first assistant message in each session
    op.execute("""
        UPDATE chat_sessions cs
        SET skill_id = sub.skill_id
        FROM (
            SELECT DISTINCT ON (session_id) session_id, skill_id
            FROM chat_messages
            WHERE role = 'assistant' AND skill_id IS NOT NULL
            ORDER BY session_id, created_at ASC
        ) sub
        WHERE cs.session_id = sub.session_id
    """)


def downgrade() -> None:
    op.drop_column('chat_sessions', 'skill_id')
