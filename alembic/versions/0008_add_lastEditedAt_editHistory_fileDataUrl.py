"""add_lastEditedAt_editHistory_fileDataUrl

Revision ID: 0008
Revises: 0007
Create Date: 2026-05-16
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # api_van_requests: edit tracking fields
    op.add_column(
        "api_van_requests",
        sa.Column("lastEditedAt", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "api_van_requests",
        sa.Column("editHistory", sa.JSON(), nullable=False, server_default="'[]'"),
    )

    # api_mission_admin_panels: base64 file data URL
    op.add_column(
        "api_mission_admin_panels",
        sa.Column("requestPlanFileDataUrl", sa.Text(), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("api_mission_admin_panels", "requestPlanFileDataUrl")
    op.drop_column("api_van_requests", "editHistory")
    op.drop_column("api_van_requests", "lastEditedAt")
