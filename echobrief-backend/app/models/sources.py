from typing import ClassVar

from sqlmodel import Field, SQLModel


class Source(SQLModel, table=True):
    __tablename__: ClassVar[str] = "sources"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=2, max_length=50)
    base_url: str = Field(min_length=2, max_length=250)
    is_active: bool = Field(default=True)
