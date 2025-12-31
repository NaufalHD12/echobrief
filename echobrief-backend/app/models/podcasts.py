from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import ClassVar
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Column, Field, SQLModel


class PodcastStatus(PyEnum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class StepName(PyEnum):
    script_generation = "script_generation"
    tts = "tts"
    audio_processing = "audio_processing"


class Podcast(SQLModel, table=True):
    __tablename__: ClassVar[str] = "podcasts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    generated_script: str | None = None
    audio_url: str | None = None
    duration_seconds: int | None = None
    status: PodcastStatus = Field(
        default=PodcastStatus.pending,
        sa_column=Column(
            SQLEnum(PodcastStatus, name="podcast_status"),
            nullable=False,
        ),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )


class PodcastTopic(SQLModel, table=True):
    __tablename__: ClassVar[str] = "podcast_topics"

    podcast_id: UUID = Field(foreign_key="podcasts.id", primary_key=True)
    topic_id: int = Field(foreign_key="topics.id", primary_key=True)


class PodcastArticle(SQLModel, table=True):
    __tablename__: ClassVar[str] = "podcast_articles"

    podcast_id: UUID = Field(foreign_key="podcasts.id", primary_key=True)
    article_id: int = Field(foreign_key="articles.id", primary_key=True)


class PodcastSegment(SQLModel, table=True):
    __tablename__: ClassVar[str] = "podcast_segments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    podcast_id: UUID = Field(foreign_key="podcasts.id")
    title: str = Field(min_length=1, max_length=200)
    start_second: int = Field(ge=0)
    end_second: int = Field(ge=0)


class PodcastJob(SQLModel, table=True):
    __tablename__: ClassVar[str] = "podcast_jobs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    podcast_id: UUID = Field(foreign_key="podcasts.id")
    step_name: StepName = Field(
        default=StepName.script_generation,
        sa_column=Column(
            SQLEnum(StepName, name="job_step_name"),
            nullable=False,
        ),
    )
    status: PodcastStatus = Field(
        default=PodcastStatus.pending,
        sa_column=Column(
            SQLEnum(PodcastStatus, name="podcast_status"),
            nullable=False,
        ),
    )
    error_message: str | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
