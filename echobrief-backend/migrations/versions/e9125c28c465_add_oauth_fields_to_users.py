"""add_oauth_fields_to_users

Revision ID: e9125c28c465
Revises: h949cd6b73ac
Create Date: 2026-01-02 19:12:09.179124

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9125c28c465'
down_revision: Union[str, Sequence[str], None] = 'h949cd6b73ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add OAuth fields to users table
    op.add_column('users', sa.Column('google_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('auth_provider', sa.String(), nullable=False, server_default='local'))

    # Make password_hash nullable for OAuth users
    op.alter_column('users', 'password_hash', nullable=True)

    # Add unique constraint to google_id
    op.create_unique_constraint('uq_users_google_id', 'users', ['google_id'])


def downgrade() -> None:
    """Downgrade schema."""
    pass
