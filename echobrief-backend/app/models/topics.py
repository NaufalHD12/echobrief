from typing import ClassVar

from sqlmodel import Field, SQLModel


class Topic(SQLModel, table=True):
    __tablename__: ClassVar[str] = "topics"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=2, max_length=50)
    slug: str = Field(index=True, min_length=2, max_length=50, unique=True)
