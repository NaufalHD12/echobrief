import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

from ..core.celery_app import celery_app
from ..core.database import async_session
from ..models.users import PlanType
from ..schemas.podcasts import PodcastCreate
from ..services.podcast_service import PodcastService
from ..services.user_service import UserService

logger = logging.getLogger(__name__)


@celery_app.task
def generate_daily_podcasts():
    """Background task to generate daily podcasts for all users at 3 AM"""
    logger.info("=== DAILY PODCAST GENERATION TASK STARTED ===")

    try:
        # Use asyncio.run() for fresh event loop in Celery context
        result = asyncio.run(_generate_daily_podcasts_async())
        logger.info(f"Daily podcast generation completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in daily podcast generation task: {e}", exc_info=True)
        raise
    finally:
        logger.info("=== DAILY PODCAST GENERATION TASK FINISHED ===")


async def _generate_daily_podcasts_async():
    """Async wrapper for daily podcast generation"""
    async with async_session() as session:
        user_service = UserService(session)
        podcast_service = PodcastService(session)

        # Get all users
        all_users = await user_service.get_all_users()
        logger.info(f"Found {len(all_users)} users for daily podcast generation")

        results = {
            "total_users": len(all_users),
            "successful_generations": 0,
            "failed_generations": 0,
            "skipped_users": 0,
            "details": [],
        }

        for user in all_users:
            try:
                # Get user's favorite topics
                user_topics = await user_service.get_user_topics(user.id)
                if not user_topics:
                    logger.info(f"User {user.id} has no favorite topics, skipping")
                    results["skipped_users"] += 1
                    results["details"].append(
                        {
                            "user_id": str(user.id),
                            "status": "skipped",
                            "reason": "no_favorite_topics",
                        }
                    )
                    continue

                topic_ids = [topic.id for topic in user_topics if topic.id is not None]

                # Apply free plan restrictions for topic count
                if user.plan_type == PlanType.FREE.value and len(topic_ids) > 3:
                    topic_ids = topic_ids[:3]  # Take first 3 topics for free users
                    logger.info(f"Free user {user.id}: limited to 3 topics")

                # Check if user already has a podcast today
                today = datetime.now(timezone.utc).date()
                todays_podcasts = await podcast_service._get_user_podcasts_today(
                    user.id, today
                )

                if todays_podcasts:
                    logger.info(f"User {user.id} already has podcast today, skipping")
                    results["skipped_users"] += 1
                    results["details"].append(
                        {
                            "user_id": str(user.id),
                            "status": "skipped",
                            "reason": "already_has_podcast_today",
                        }
                    )
                    continue

                # Create podcast for user
                podcast_data = PodcastCreate(topic_ids=topic_ids)
                podcast = await podcast_service.create_podcast_request(
                    user.id, podcast_data, user
                )

                # Generate script and audio
                try:
                    await podcast_service.generate_podcast_script(podcast.id)
                    await podcast_service.generate_podcast_audio(podcast.id)

                    logger.info(f"Successfully generated podcast for user {user.id}")
                    results["successful_generations"] += 1
                    results["details"].append(
                        {
                            "user_id": str(user.id),
                            "status": "success",
                            "podcast_id": str(podcast.id),
                            "topics_count": len(topic_ids),
                        }
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to generate script/audio for user {user.id}: {e}"
                    )
                    results["failed_generations"] += 1
                    results["details"].append(
                        {"user_id": str(user.id), "status": "failed", "reason": str(e)}
                    )

            except Exception as e:
                logger.error(f"Failed to process user {user.id}: {e}")
                results["failed_generations"] += 1
                results["details"].append(
                    {"user_id": str(user.id), "status": "failed", "reason": str(e)}
                )

        return results


async def generate_podcast_for_user(user_id: str) -> dict:
    """Generate podcast for a specific user (for testing or manual trigger)"""
    async with async_session() as session:
        user_service = UserService(session)
        podcast_service = PodcastService(session)

        user_uuid = UUID(user_id)

        user = await user_service.get_user_by_id(user_uuid)
        if not user:
            return {"success": False, "error": "User not found"}

        # Get user's favorite topics
        user_topics = await user_service.get_user_topics(user_uuid)
        if not user_topics:
            return {"success": False, "error": "User has no favorite topics"}

        topic_ids = [topic.id for topic in user_topics if topic.id is not None]

        # Apply free plan restrictions
        if user.plan_type == PlanType.FREE.value and len(topic_ids) > 3:
            topic_ids = topic_ids[:3]

        # Create podcast
        podcast_data = PodcastCreate(topic_ids=topic_ids)
        podcast = await podcast_service.create_podcast_request(
            user_uuid, podcast_data, user
        )

        # Generate script and audio
        try:
            await podcast_service.generate_podcast_script(podcast.id)
            await podcast_service.generate_podcast_audio(podcast.id)

            return {
                "success": True,
                "podcast_id": str(podcast.id),
                "user_id": str(user_uuid),
                "topics_count": len(topic_ids),
                "plan_type": user.plan_type,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "podcast_id": str(podcast.id)}
