"""add_audit_log

Revision ID: 0010
Revises: 0009
Create Date: 2026-05-16
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "api_audit_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target", sa.String(255), nullable=False, server_default=""),
        sa.Column("detail", sa.Text(), nullable=False, server_default=""),
        sa.Column("performedBy", sa.String(150), nullable=False, server_default=""),
        sa.Column(
            "createdAt",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_api_audit_logs_createdAt", "api_audit_logs", ["createdAt"])
    op.create_index("ix_api_audit_logs_action", "api_audit_logs", ["action"])


def downgrade() -> None:
    op.drop_index("ix_api_audit_logs_action", table_name="api_audit_logs")
    op.drop_index("ix_api_audit_logs_createdAt", table_name="api_audit_logs")
    op.drop_table("api_audit_logs")
