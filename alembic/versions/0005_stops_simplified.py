"""[retired] stops schema simplification — superseded by 0001 squash

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-16
"""

from typing import Sequence, Union

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass  # handled by 0001 squash


def downgrade() -> None:
    pass
