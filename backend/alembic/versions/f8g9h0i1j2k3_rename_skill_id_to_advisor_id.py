"""rename skill_id to advisor_id

Revision ID: f8g9h0i1j2k3
Revises: e1f2a3b4c5d6
Create Date: 2026-06-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f8g9h0i1j2k3'
down_revision: Union[str, None] = 'e1f2a3b4c5d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename skill_id to advisor_id in chat_sessions
    op.alter_column('chat_sessions', 'skill_id', new_column_name='advisor_id')

    # Rename skill_id to advisor_id in chat_messages
    op.alter_column('chat_messages', 'skill_id', new_column_name='advisor_id')


def downgrade() -> None:
    # Rename advisor_id back to skill_id in chat_messages
    op.alter_column('chat_messages', 'advisor_id', new_column_name='skill_id')

    # Rename advisor_id back to skill_id in chat_sessions
    op.alter_column('chat_sessions', 'advisor_id', new_column_name='skill_id')
