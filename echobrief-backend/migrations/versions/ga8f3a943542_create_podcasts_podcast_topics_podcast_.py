"""create podcasts, podcast_topics, podcast_articles, podcast_segments, podcast_jobs table

Revision ID: ga8f3a943542
Revises: fb262357e4dc
Create Date: 2025-12-31 12:01:08.092363

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'ga8f3a943542'
down_revision: Union[str, Sequence[str], None] = 'fb262357e4dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM types (SQLAlchemy will create them automatically when used in columns)
    podcast_status_enum = sa.Enum('pending', 'processing', 'completed', 'failed', name='podcast_status')
    job_step_name_enum = sa.Enum('script_generation', 'tts', 'audio_processing', name='job_step_name')
    
    # Create podcasts table
    op.create_table(
        'podcasts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('generated_script', sa.Text(), nullable=True),
        sa.Column('audio_url', sa.String(length=500), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('status', podcast_status_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )

    # Create podcast_topics table
    op.create_table(
        'podcast_topics',
        sa.Column('podcast_id', sa.UUID(), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['podcast_id'], ['podcasts.id'], ),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
        sa.PrimaryKeyConstraint('podcast_id', 'topic_id')
    )

    # Create podcast_articles table
    op.create_table(
        'podcast_articles',
        sa.Column('podcast_id', sa.UUID(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['podcast_id'], ['podcasts.id'], ),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
        sa.PrimaryKeyConstraint('podcast_id', 'article_id')
    )

    # Create podcast_segments table
    op.create_table(
        'podcast_segments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('podcast_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('start_second', sa.Integer(), nullable=False),
        sa.Column('end_second', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['podcast_id'], ['podcasts.id'], )
    )

    # Create podcast_jobs table
    op.create_table(
        'podcast_jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('podcast_id', sa.UUID(), nullable=False),
        sa.Column('step_name', job_step_name_enum, nullable=False),
        sa.Column('status', podcast_status_enum, nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['podcast_id'], ['podcasts.id'], )
    )


def downgrade() -> None:
    op.drop_table('podcast_jobs')
    op.drop_table('podcast_segments')
    op.drop_table('podcast_articles')
    op.drop_table('podcast_topics')
    op.drop_table('podcasts')
    
    # Drop ENUM types (checkfirst=True will handle if they don't exist)
    podcast_status_enum = sa.Enum(name='podcast_status')
    podcast_status_enum.drop(op.get_bind(), checkfirst=True)
    
    job_step_name_enum = sa.Enum(name='job_step_name')
    job_step_name_enum.drop(op.get_bind(), checkfirst=True)
