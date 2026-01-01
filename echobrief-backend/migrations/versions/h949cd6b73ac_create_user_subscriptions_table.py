"""create user_subscriptions table

Revision ID: h949cd6b73ac
Revises: ga8f3a943542
Create Date: 2026-01-01 17:00:08.429324

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h949cd6b73ac'
down_revision: Union[str, Sequence[str], None] = 'ga8f3a943542'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create ENUM for subscription status
    subscription_status_enum = sa.Enum('active', 'cancelled', 'expired', 'pending', name='subscription_status')

    # Create user_subscriptions table
    op.create_table(
        'user_subscriptions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('subscription_id', sa.String(length=255), nullable=False),
        sa.Column('status', subscription_status_enum, nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('grace_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.UniqueConstraint('subscription_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_subscriptions')

    # Drop ENUM type
    subscription_status_enum = sa.Enum(name='subscription_status')
    subscription_status_enum.drop(op.get_bind(), checkfirst=True)
