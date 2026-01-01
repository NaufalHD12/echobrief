import logging
from datetime import datetime, timedelta, timezone
from typing import Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.subscriptions import SubscriptionStatus, UserSubscription
from ..models.users import PlanType, User


class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_subscription(
        self, user_id: UUID, subscription_id: str, start_date: datetime | None = None
    ) -> UserSubscription:
        """Create new subscription for user"""
        # Check if subscription already exists
        existing = await self.get_subscription_by_id(subscription_id)
        if existing:
            raise HTTPException(status_code=400, detail="Subscription already exists")

        if start_date is None:
            start_date = datetime.now(timezone.utc)

        subscription = UserSubscription(
            user_id=user_id,
            subscription_id=subscription_id,
            status=SubscriptionStatus.active,
            start_date=start_date,
        )

        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        return subscription

    async def get_subscription_by_id(
        self, subscription_id: str
    ) -> UserSubscription | None:
        """Get subscription by Ko-fi subscription ID"""
        query = select(UserSubscription).where(
            UserSubscription.subscription_id == subscription_id
        )
        result = await self.session.exec(query)
        return result.first()

    async def get_user_subscription(self, user_id: UUID) -> UserSubscription | None:
        """Get active subscription for user"""
        query = select(UserSubscription).where(
            UserSubscription.user_id == user_id,
            UserSubscription.status == SubscriptionStatus.active,
        )
        result = await self.session.exec(query)
        return result.first()

    async def cancel_subscription(self, subscription_id: str) -> UserSubscription:
        """Cancel subscription with grace period"""
        subscription = await self.get_subscription_by_id(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        now = datetime.now(timezone.utc)
        
        # Set grace period (2 days from now)
        grace_period_end = now + timedelta(days=2)

        subscription.status = SubscriptionStatus.cancelled
        subscription.grace_period_end = grace_period_end
        subscription.end_date = grace_period_end  # Update end_date to grace period end
        subscription.updated_at = now

        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Cancelled subscription: {subscription_id}, "
                   f"end_date={grace_period_end}, grace_period_end={grace_period_end}")
        
        return subscription

    async def expire_subscription(self, subscription_id: str) -> UserSubscription:
        """Mark subscription as expired"""
        subscription = await self.get_subscription_by_id(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        now = datetime.now(timezone.utc)
        subscription.status = SubscriptionStatus.expired
        subscription.end_date = now  # Set end_date to expiration time
        subscription.updated_at = now

        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Expired subscription: {subscription_id}, end_date={now}")
        
        return subscription

    async def check_and_update_expired_subscriptions(
        self,
    ) -> Sequence[UserSubscription]:
        """Check for expired subscriptions and update user plans"""
        now = datetime.now(timezone.utc)

        # Find all cancelled subscriptions
        query = select(UserSubscription).where(
            UserSubscription.status == SubscriptionStatus.cancelled
        )
        result = await self.session.exec(query)
        cancelled_subs = result.all()

        # Filter those where grace period has ended
        expired_subs = [
            sub
            for sub in cancelled_subs
            if sub.grace_period_end and sub.grace_period_end <= now
        ]

        if expired_subs:
            # Update each subscription and user
            for sub in expired_subs:
                sub.status = SubscriptionStatus.expired
                sub.end_date = now  # Set end_date to expiration time
                sub.updated_at = now
                self.session.add(sub)

                # Update user plan
                user = await self.session.get(User, sub.user_id)
                if user:
                    user.plan_type = PlanType.FREE.value
                    self.session.add(user)

            await self.session.commit()
            
            logger = logging.getLogger(__name__)
            logger.info(f"Expired {len(expired_subs)} subscriptions: "
                       f"{[str(sub.id) for sub in expired_subs]}")

        return expired_subs

    async def get_user_plan_type(self, user_id: UUID) -> str:
        """Get effective plan type for user (considering active subscription)"""
        user = await self.session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check for active subscription
        subscription = await self.get_user_subscription(user_id)
        if subscription:
            return "paid"

        return user.plan_type

    async def get_subscription_by_kofi_transaction_id(
        self, kofi_transaction_id: str
    ) -> UserSubscription | None:
        """Get subscription by Ko-fi transaction ID"""
        # Using subscription_id field to store kofi_transaction_id
        query = select(UserSubscription).where(
            UserSubscription.subscription_id == kofi_transaction_id
        )
        result = await self.session.exec(query)
        return result.first()

    async def create_kofi_subscription(
        self,
        user_id: UUID,
        kofi_transaction_id: str,
        tier_name: str | None = None,
        amount: str | None = None,
    ) -> UserSubscription:
        """Create new subscription from Ko-fi webhook"""
        # Check if subscription already exists
        existing = await self.get_subscription_by_kofi_transaction_id(kofi_transaction_id)
        if existing:
            raise HTTPException(status_code=400, detail="Subscription already exists")

        # Calculate end date: 30 days from now for monthly subscriptions
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=30)  # Monthly subscription

        # Create subscription with kofi_transaction_id as subscription_id
        subscription = UserSubscription(
            user_id=user_id,
            subscription_id=kofi_transaction_id,
            status=SubscriptionStatus.active,
            start_date=start_date,
            end_date=end_date,  # Set end date for monthly subscription
        )

        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        
        # Log additional info (could be stored in separate table if needed)
        if tier_name or amount:
            logger = logging.getLogger(__name__)
            logger.info(f"Created Ko-fi subscription: transaction={kofi_transaction_id}, "
                       f"user={user_id}, tier={tier_name}, amount={amount}, "
                       f"end_date={end_date}")
        
        return subscription
