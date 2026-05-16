"""[placeholder] HEAD marker after squash — no DDL

This file exists only to mark the tail of the migration chain after
the 0001-0005 squash. No DDL runs here.

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-16
"""

from typing import Sequence, Union

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
