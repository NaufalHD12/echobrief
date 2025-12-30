import asyncio
import logging

from ..core.celery_app import celery_app
from ..core.database import async_session, engine
from ..services.news_aggregation_service import NewsAggregationService

logger = logging.getLogger(__name__)


@celery_app.task
def aggregate_news_task():
    """Background task to aggregate news"""
    logger.info("=== CELERY TASK STARTED ===")

    try:
        # Use asyncio.run() for fresh event loop in Celery context
        result = asyncio.run(_aggregate_async_wrapper())
        logger.info(f"News aggregation completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in news aggregation task: {e}", exc_info=True)
        raise
    finally:
        logger.info("=== CELERY TASK FINISHED ===")


async def _aggregate_async_wrapper():
    """Wrapper for asyncio.run with proper cleanup"""
    try:
        return await _aggregate_async()
    finally:
        # Cleanup database connections
        await engine.dispose()


async def _aggregate_async():
    """Run aggregation in async context with explicit transaction"""
    async with async_session() as session:
        # Start transaction manually
        try:
            await session.begin()
            logger.info("Database transaction started")
            service = NewsAggregationService(session)
            result = await service.aggregate_news()
            logger.info(f"Aggregation service result: {result}")
            await session.commit()
            logger.info("Transaction committed successfully")
            return result
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            await session.rollback()
            raise
