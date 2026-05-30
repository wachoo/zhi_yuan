"""add exam_type to admission_records

Revision ID: a1b2c3d4e5f6
Revises: 30c59b30f67b
Create Date: 2026-05-30
"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "30c59b30f67b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "admission_records",
        sa.Column("exam_type", sa.String(20), nullable=False, server_default="普通类"),
    )
    op.create_index("ix_admission_records_exam_type", "admission_records", ["exam_type"])


def downgrade():
    op.drop_index("ix_admission_records_exam_type", table_name="admission_records")
    op.drop_column("admission_records", "exam_type")
