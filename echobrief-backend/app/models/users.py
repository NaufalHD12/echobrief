from datetime import datetime, timezone
from enum import Enum
from typing import ClassVar
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime
from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class PlanType(str, Enum):
    FREE = "free"
    PAID = "paid"


class User(SQLModel, table=True):
    __tablename__: ClassVar[str] = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, min_length=5, max_length=255)
    password_hash: str = Field(min_length=60, max_length=255)
    username: str = Field(unique=True, min_length=3, max_length=50)
    role: str = Field(
        default=UserRole.USER.value,
        sa_column_kwargs={"server_default": UserRole.USER.value, "nullable": False},
    )
    plan_type: str = Field(
        default=PlanType.FREE.value,
        sa_column_kwargs={"server_default": PlanType.FREE.value, "nullable": False},
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
    last_login: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("role IN ('user', 'admin')", name="ck_user_role"),
        CheckConstraint("plan_type IN ('free', 'paid')", name="ck_plan_type"),
    )


class UserTopic(SQLModel, table=True):
    __tablename__: ClassVar[str] = "user_topics"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    topic_id: int = Field(foreign_key="topics.id", primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
