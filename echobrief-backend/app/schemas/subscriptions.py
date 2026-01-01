from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserSubscriptionBase(BaseModel):
    """Base schema for user subscription"""

    subscription_id: str = Field(
        ..., min_length=1, max_length=255, description="Ko-fi subscription ID"
    )
    status: str = Field(..., description="Subscription status")
    start_date: datetime = Field(..., description="Subscription start date")
    end_date: Optional[datetime] = Field(
        None, description="Subscription end date (for fixed-term subscriptions)"
    )
    grace_period_end: Optional[datetime] = Field(
        None, description="Grace period end date"
    )


class UserSubscriptionCreate(BaseModel):
    """Schema for creating a new subscription"""

    subscription_id: str = Field(
        ..., min_length=1, max_length=255, description="Ko-fi subscription ID"
    )
    user_id: UUID = Field(..., description="User ID")
    start_date: Optional[datetime] = Field(
        None, description="Subscription start date (defaults to now)"
    )


class UserSubscriptionUpdate(BaseModel):
    """Schema for updating subscription"""

    status: Optional[str] = Field(None, description="New subscription status")
    end_date: Optional[datetime] = Field(None, description="Subscription end date")
    grace_period_end: Optional[datetime] = Field(
        None, description="Grace period end date"
    )


class UserSubscriptionResponse(UserSubscriptionBase):
    """Response schema for user subscription"""

    id: UUID = Field(..., description="Subscription ID")
    user_id: UUID = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class SubscriptionStats(BaseModel):
    """Schema for subscription statistics"""

    total_active: int = Field(..., description="Total active subscriptions")
    total_cancelled: int = Field(..., description="Total cancelled subscriptions")
    total_expired: int = Field(..., description="Total expired subscriptions")
    recent_subscriptions: int = Field(
        ..., description="New subscriptions in last 30 days"
    )


class WebhookEvent(BaseModel):
    """Schema for webhook event data"""

    type: str = Field(
        ...,
        description="Event type (subscription_created, subscription_cancelled, etc.)",
    )
    data: dict = Field(..., description="Event data payload")


class WebhookResponse(BaseModel):
    """Schema for webhook processing response"""

    event_type: str = Field(..., description="Processed event type")
    processed: bool = Field(..., description="Whether event was processed successfully")
    message: Optional[str] = Field(None, description="Processing message")
