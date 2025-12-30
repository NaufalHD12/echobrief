"""create users and users_topics table

Revision ID: fb262357e4dc
Revises: e1ecb0da4383
Create Date: 2025-12-30 15:22:20.779459

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fb262357e4dc'
down_revision: Union[str, Sequence[str], None] = 'e1ecb0da4383'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('role', sa.String(length=10), nullable=False),
        sa.Column('plan_type', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # Create user_topics table
    op.create_table(
        'user_topics',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'topic_id')
    )


def downgrade() -> None:
    op.drop_table('user_topics')
    op.drop_table('users')