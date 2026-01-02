"""add_avatar_filename_to_users

Revision ID: a87523e99078
Revises: e9125c28c465
Create Date: 2026-01-02 19:40:34.209257

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a87523e99078'
down_revision: Union[str, Sequence[str], None] = 'e9125c28c465'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add avatar_filename column to users table
    op.add_column('users', sa.Column('avatar_filename', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
