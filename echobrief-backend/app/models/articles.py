from sqlmodel import SQLModel, Field
from sqlalchemy import BigInteger, DateTime
from datetime import datetime, timezone
from typing import ClassVar

class Article(SQLModel, table=True):
    __tablename__: ClassVar[str] = "articles"

    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_type=BigInteger()
    )
    source_id: int = Field(foreign_key="sources.id")
    topic_id: int = Field(foreign_key="topics.id")
    title: str = Field(min_length=1, max_length=500)
    summary_text: str | None = None
    url: str = Field(unique=True, min_length=10, max_length=1000)
    published_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_type=DateTime(timezone=True))
