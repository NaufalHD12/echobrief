import asyncio
import logging
from datetime import datetime, timezone

from sqlmodel import select

from ..core.database import async_session, engine
from ..models.subscriptions import SubscriptionStatus, UserSubscription
from ..services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)


async def check_expired_subscriptions_task():
    """Background task to check and update expired subscriptions"""
    logger.info("=== CHECK EXPIRED SUBSCRIPTIONS TASK STARTED ===")

    try:
        # Use asyncio.run() for fresh event loop in task context
        result = asyncio.run(_check_expired_async_wrapper())
        logger.info(f"Expired subscription check completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in expired subscription check task: {e}", exc_info=True)
        raise
    finally:
        logger.info("=== CHECK EXPIRED SUBSCRIPTIONS TASK FINISHED ===")


async def _check_expired_async_wrapper():
    """Wrapper for asyncio.run with proper cleanup"""
    try:
        return await _check_expired_async()
    finally:
        # Cleanup database connections
        await engine.dispose()


async def _check_expired_async():
    """Run expired subscription check in async context with explicit transaction"""
    async with async_session() as session:
        # Start transaction manually
        try:
            await session.begin()
            logger.info("Database transaction started")
            subscription_service = SubscriptionService(session)
            expired_subs = (
                await subscription_service.check_and_update_expired_subscriptions()
            )
            logger.info(
                f"Expired subscription check result: {len(expired_subs)} subscriptions expired"
            )

            # Log details of expired subscriptions
            for sub in expired_subs:
                logger.info(f"Expired subscription {sub.id} for user {sub.user_id}")

            await session.commit()
            logger.info("Transaction committed successfully")
            return len(expired_subs)
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            await session.rollback()
            raise


async def cleanup_old_subscriptions_task():
    """Background task to clean up old expired subscriptions"""
    logger.info("=== CLEANUP OLD SUBSCRIPTIONS TASK STARTED ===")

    try:
        # Use asyncio.run() for fresh event loop in task context
        result = asyncio.run(_cleanup_old_async_wrapper())
        logger.info(f"Old subscription cleanup completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in old subscription cleanup task: {e}", exc_info=True)
        raise
    finally:
        logger.info("=== CLEANUP OLD SUBSCRIPTIONS TASK FINISHED ===")


async def _cleanup_old_async_wrapper():
    """Wrapper for asyncio.run with proper cleanup"""
    try:
        return await _cleanup_old_async()
    finally:
        # Cleanup database connections
        await engine.dispose()


async def _cleanup_old_async():
    """Run old subscription cleanup in async context with explicit transaction"""
    async with async_session() as session:
        # Start transaction manually
        try:
            await session.begin()
            logger.info("Database transaction started")

            # Keep only last 6 months of expired subscriptions for audit purposes
            cutoff_date = datetime.now(timezone.utc).replace(
                month=datetime.now(timezone.utc).month - 6
            )

            query = select(UserSubscription).where(
                UserSubscription.status == SubscriptionStatus.expired,
                UserSubscription.updated_at < cutoff_date,
            )

            result = await session.exec(query)
            old_subs = result.all()

            if old_subs:
                # Delete old expired subscriptions one by one
                for sub in old_subs:
                    await session.delete(sub)

                logger.info(f"Cleaned up {len(old_subs)} old expired subscriptions")
                result_count = len(old_subs)
            else:
                logger.info("No old subscriptions to clean up")
                result_count = 0

            await session.commit()
            logger.info("Transaction committed successfully")
            return result_count
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            await session.rollback()
            raise
