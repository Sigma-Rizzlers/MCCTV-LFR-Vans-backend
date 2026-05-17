"""add_drafts_and_user_profiles

Revision ID: 0011
Revises: 0010
Create Date: 2026-05-17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "api_report_drafts",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(150), nullable=False),
        sa.Column("formData", sa.JSON(), nullable=False, server_default="'{}'"),
        sa.Column(
            "savedAt",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint("username", name="uq_api_report_drafts_username"),
    )
    op.create_index("ix_api_report_drafts_username", "api_report_drafts", ["username"])

    op.create_table(
        "api_user_profiles",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "userId",
            sa.BigInteger(),
            sa.ForeignKey("api_users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False, server_default=""),
        sa.Column("phone", sa.String(20), nullable=False, server_default=""),
        sa.Column("gender", sa.String(10), nullable=False, server_default=""),
        sa.Column("role", sa.String(255), nullable=False, server_default=""),
        sa.Column("supportFileName", sa.String(255), nullable=False, server_default=""),
        sa.Column(
            "updatedAt",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint("userId", name="uq_api_user_profiles_userId"),
    )
    op.create_index("ix_api_user_profiles_userId", "api_user_profiles", ["userId"])


def downgrade() -> None:
    op.drop_index("ix_api_user_profiles_userId", table_name="api_user_profiles")
    op.drop_table("api_user_profiles")
    op.drop_index("ix_api_report_drafts_username", table_name="api_report_drafts")
    op.drop_table("api_report_drafts")
