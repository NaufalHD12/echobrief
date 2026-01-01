import logging
import os
from datetime import date, datetime, timedelta, timezone
from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException
from openai import OpenAI
from sqlmodel import delete, desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.config import settings
from ..models.articles import Article
from ..models.podcasts import (
    Podcast,
    PodcastArticle,
    PodcastSegment,
    PodcastStatus,
    PodcastTopic,
)
from ..models.topics import Topic
from ..models.users import User, UserTopic
from ..schemas.podcasts import PodcastCreate
from .article_service import ArticleService
from .subscription_service import SubscriptionService
from .tts_service import TTSService

logger = logging.getLogger(__name__)


class PodcastService:
    def __init__(self, session: AsyncSession):
        self.session = session  # Fixed typo: sesssion -> session
        self.article_service = ArticleService(session)
        self.tts_service = TTSService(session)
        self.openai_client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY, base_url=settings.DEEPSEEK_BASE_URL
        )

    async def create_podcast_request(
        self, user_id: UUID, podcast_data: PodcastCreate, user: Optional[User] = None
    ) -> Podcast:
        """Create a new podcast request with plan-based restrictions"""
        # Check if topic_ids is None
        if podcast_data.topic_ids is None:
            raise HTTPException(
                status_code=400,
                detail="Topic IDs cannot be None. Please provide topic_ids or use favorite topics.",
            )

        # Get user object if not provided
        if user is None:
            user = await self.session.get(User, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

        # Apply plan restrictions
        await self._validate_plan_restrictions(user, podcast_data.topic_ids)

        # Validate user has access to topics
        user_topics = await self._get_user_topic_ids(user_id)
        for topic_id in podcast_data.topic_ids:
            if topic_id not in user_topics:
                raise HTTPException(
                    status_code=400,
                    detail=f"User does not have access to topic {topic_id}",
                )

        # Create podcast record
        podcast = Podcast(user_id=user_id)
        self.session.add(podcast)
        await self.session.commit()
        await self.session.refresh(podcast)

        # Associate topics
        for topic_id in podcast_data.topic_ids:
            podcast_topic = PodcastTopic(podcast_id=podcast.id, topic_id=topic_id)
            self.session.add(podcast_topic)

        await self.session.commit()
        return podcast

    async def generate_podcast_script(self, podcast_id: UUID) -> str:
        """Generate podcast script using AI"""
        podcast = await self.get_podcast_by_id(podcast_id)
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")

        # Get articles for this podcast's topics
        articles = await self._get_articles_for_podcast(podcast_id)
        if not articles:
            raise HTTPException(
                status_code=400, detail="No articles found for selected topics"
            )

        # Create script generation prompt
        articles_text = "\n".join(
            [
                f"- {article.title}: {article.summary_text or "No summary"}"
                for article in articles[:10]
            ]
        )

        prompt = f"""
        Create an engaging podcast script about recent news that will be read aloud by text-to-speech. The script should be pure spoken text without any formatting, markdown, or structural elements.

        Structure the script naturally as follows:

        1. Opening: Start with a warm welcome (Podcast Name is EchoBrief Podcast) and brief overview of today's topics (about 30-45 seconds when spoken)
        2. Main content: Summarize 3-5 key news stories in a conversational way (about 5-10 minutes total)
        3. Closing: Brief wrap-up and sign-off (about 15-30 seconds)

        Available news articles:
        {articles_text}

        Requirements:
        - Write in a natural, conversational tone as if speaking to a listener
        - Keep total script length to maximum 10 minutes when spoken (roughly 1200-1500 words)
        - Use smooth, natural transitions between stories
        - Include brief pauses between major sections (but don't write them out)
        - End with a thoughtful reflection or call to action
        - Write as continuous prose - no bullet points, no markdown, no section headers, no sound effect notes
        - Make it sound like a real podcast host speaking naturally

        The output should be pure text that can be directly fed to a text-to-speech engine.
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0,
            )

            script = response.choices[0].message.content
            if not script:
                raise HTTPException(
                    status_code=500, detail="Failed to generate podcast script"
                )

            script = script.strip()

            # Update podcast with script
            podcast.generated_script = script
            podcast.status = (
                PodcastStatus.processing
            )  # Script generated, now processing TTS
            self.session.add(podcast)

            for article in articles:
                if article.id is not None:
                    podcast_article = PodcastArticle(
                        podcast_id=podcast_id, article_id=article.id
                    )
                    self.session.add(podcast_article)

            await self.session.commit()
            return script

        except Exception as e:
            logger.error(f"Script generation failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail="Failed to generate podcast script"
            )

    async def generate_podcast_audio(self, podcast_id: UUID) -> dict:
        """Generate audio for podcast"""
        podcast = await self.get_podcast_by_id(podcast_id)
        if not podcast or not podcast.generated_script:
            raise HTTPException(status_code=400, detail="Podcast script not available")

        # Generate audio file path
        audio_filename = f"podcast_{podcast_id}.mp3"
        audio_dir = os.path.join(os.path.dirname(__file__), "..", "..", "audio")
        os.makedirs(audio_dir, exist_ok=True)
        audio_path = os.path.join(audio_dir, audio_filename)

        # Generate audio
        result = await self.tts_service.generate_audio(
            text=podcast.generated_script, output_path=audio_path
        )

        if result["success"]:
            # Update podcast with audio info
            podcast.audio_url = f"/audio/{audio_filename}"
            podcast.duration_seconds = result["duration_seconds"]
            podcast.status = PodcastStatus.completed
            self.session.add(podcast)
            await self.session.commit()

            return {
                "audio_url": podcast.audio_url,
                "duration_seconds": podcast.duration_seconds,
            }
        else:
            podcast.status = PodcastStatus.failed
            self.session.add(podcast)
            await self.session.commit()
            raise HTTPException(status_code=500, detail="Audio generation failed")

    async def get_podcast_by_id(self, podcast_id: UUID) -> Optional[Podcast]:
        """Get podcast by ID"""
        query = select(Podcast).where(Podcast.id == podcast_id)
        result = await self.session.exec(query)
        return result.first()

    async def get_user_podcasts(
        self, user_id: UUID, skip: int = 0, limit: int = 10
    ) -> Sequence[Podcast]:
        """Get podcasts for a user"""
        query = (
            select(Podcast).where(Podcast.user_id == user_id).offset(skip).limit(limit)
        )
        result = await self.session.exec(query)
        return result.all()

    async def get_podcast_with_relations(self, podcast_id: UUID) -> Optional[dict]:
        """Get podcast with all related data"""
        podcast = await self.get_podcast_by_id(podcast_id)
        if not podcast:
            return None

        # Get topics
        topics_query = (
            select(Topic)
            .join(PodcastTopic)
            .where(PodcastTopic.podcast_id == podcast_id)
        )
        topics_result = await self.session.exec(topics_query)
        topics = topics_result.all()

        # Get articles
        articles_query = (
            select(Article)
            .join(PodcastArticle)
            .where(PodcastArticle.podcast_id == podcast_id)
        )
        articles_result = await self.session.exec(articles_query)
        articles = articles_result.all()

        # Get segments
        segments_query = select(PodcastSegment).where(
            PodcastSegment.podcast_id == podcast_id
        )
        segments_result = await self.session.exec(segments_query)
        segments = segments_result.all()

        return {
            "podcast": podcast,
            "topics": topics,
            "articles": articles,
            "segments": segments,
        }

    async def _get_user_topic_ids(self, user_id: UUID) -> list[int]:
        """Get topic IDs accessible by user"""
        query = select(UserTopic.topic_id).where(UserTopic.user_id == user_id)
        result = await self.session.exec(query)
        return list(result.all())

    async def _get_articles_for_podcast(self, podcast_id: UUID) -> Sequence[Article]:
        """Get articles related to podcast topics"""
        # Get podcast topics
        topics_query = select(PodcastTopic.topic_id).where(
            PodcastTopic.podcast_id == podcast_id
        )
        topics_result = await self.session.exec(topics_query)
        topic_ids = list(topics_result.all())

        if not topic_ids:
            return []

        # Get recent articles for these topics
        topic_attr = getattr(Article, "topic_id")
        query = (
            select(Article)
            .where(topic_attr.in_(topic_ids))
            .order_by(desc(Article.published_at))
            .limit(20)
        )
        result = await self.session.exec(query)
        return result.all()

    async def delete_podcast(self, podcast_id: UUID) -> bool:
        """Delete a podcast and all related data"""
        podcast = await self.get_podcast_by_id(podcast_id)
        if not podcast:
            return False

        # Delete related records first (due to foreign key constraints)
        # Delete podcast articles
        await self.session.exec(delete(PodcastArticle).where(PodcastArticle.podcast_id == podcast_id))  # type: ignore
        # Delete podcast topics
        await self.session.exec(delete(PodcastTopic).where(PodcastTopic.podcast_id == podcast_id))  # type: ignore
        # Delete podcast segments
        await self.session.exec(delete(PodcastSegment).where(PodcastSegment.podcast_id == podcast_id))  # type: ignore

        # Delete the podcast
        await self.session.delete(podcast)
        await self.session.commit()

        # Optionally delete the audio file if it exists
        if podcast.audio_url:
            try:
                audio_filename = f"podcast_{podcast_id}.mp3"
                audio_dir = os.path.join(os.path.dirname(__file__), "..", "..", "audio")
                audio_path = os.path.join(audio_dir, audio_filename)
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except Exception as e:
                logger.warning(f"Failed to delete audio file: {e}")

        return True

    async def _validate_plan_restrictions(
        self, user: User, topic_ids: list[int]
    ) -> None:
        """Validate plan-based restrictions for podcast creation"""
        # Check user's effective plan (considering active subscriptions)
        subscription_service = SubscriptionService(self.session)
        effective_plan = await subscription_service.get_user_plan_type(user.id)

        if effective_plan == "free":
            # Free plan: max 3 topics
            if len(topic_ids) > 3:
                raise HTTPException(
                    status_code=400,
                    detail="Free plan limited to 3 topics. Upgrade to add more.",
                )

            # Free plan: check daily limit (1 podcast/day)
            today = datetime.now(timezone.utc).date()
            todays_podcasts = await self._get_user_podcasts_today(user.id, today)
            if len(todays_podcasts) >= 1:  # 1 podcast/day for free
                raise HTTPException(
                    status_code=400,
                    detail="Free plan limited to 1 podcast per day. Upgrade for unlimited.",
                )

        # Paid plan: no restrictions

    async def _get_user_podcasts_today(
        self, user_id: UUID, date: date
    ) -> list[Podcast]:
        """Get user's podcasts for a specific date"""
        start_of_day = datetime.combine(date, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        end_of_day = datetime.combine(
            date + timedelta(days=1), datetime.min.time()
        ).replace(tzinfo=timezone.utc)

        query = (
            select(Podcast)
            .where(Podcast.user_id == user_id)
            .where(Podcast.created_at >= start_of_day)
            .where(Podcast.created_at < end_of_day)
        )
        result = await self.session.exec(query)
        return list(result.all())

    async def update_podcast_status(
        self,
        podcast_id: UUID,
        status: PodcastStatus,
        error_message: Optional[str] = None,
    ):
        """Update podcast status"""
        podcast = await self.get_podcast_by_id(podcast_id)
        if podcast:
            podcast.status = status
            self.session.add(podcast)
            await self.session.commit()
