from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import ClassVar
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Column, Field, SQLModel


class SubscriptionStatus(PyEnum):
    active = "active"
    cancelled = "cancelled"
    expired = "expired"
    pending = "pending"


class UserSubscription(SQLModel, table=True):
    __tablename__: ClassVar[str] = "user_subscriptions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    subscription_id: str = Field(unique=True, min_length=1, max_length=255)
    status: SubscriptionStatus = Field(
        default=SubscriptionStatus.pending,
        sa_column=Column(
            SQLEnum(SubscriptionStatus, name="subscription_status"),
            nullable=False,
        ),
    )
    start_date: datetime = Field(sa_type=DateTime(timezone=True))
    end_date: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    grace_period_end: datetime | None = Field(
        default=None, sa_type=DateTime(timezone=True)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
