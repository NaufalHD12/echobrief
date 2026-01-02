from typing import Sequence
from uuid import UUID

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.articles import Article
from ..models.podcasts import Podcast, PodcastStatus
from ..models.sources import Source
from ..models.topics import Topic
from ..models.users import User, UserTopic
from ..schemas.dashboard import DashboardStats, GlobalSearchResult


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_dashboard_data(self, user_id: UUID) -> dict:
        """Get all dashboard data for a user"""
        user = await self.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")

        # Get stats
        stats = await self._get_user_stats(user_id)

        # Get recent podcasts (last 5)
        recent_podcasts = await self._get_recent_podcasts(user_id, limit=5)

        # Get recent articles from user's topics (last 10)
        recent_articles = await self._get_recent_articles_for_user(user_id, limit=10)

        # Get favorite topics
        favorite_topics = await self._get_user_favorite_topics(user_id)

        return {
            "user": user,
            "stats": stats,
            "recent_podcasts": recent_podcasts,
            "recent_articles": recent_articles,
            "favorite_topics": favorite_topics,
        }

    async def global_search(
        self, query: str, user_id: UUID, skip: int = 0, limit: int = 20
    ) -> tuple[list[GlobalSearchResult], int]:
        """Perform global search across articles, topics, and sources"""
        query_lower = query.lower()
        results = []

        # Search articles (user can only see articles from their topics)
        user_topic_ids = await self._get_user_topic_ids(user_id)
        if user_topic_ids:
            article_results = await self._search_articles(query_lower, user_topic_ids, skip, limit)
            results.extend(article_results)

        # Search topics
        topic_results = await self._search_topics(query_lower, skip, limit)
        results.extend(topic_results)

        # Search sources
        source_results = await self._search_sources(query_lower, skip, limit)
        results.extend(source_results)

        # Sort by relevance (simple: articles first, then topics, then sources)
        # In a more advanced implementation, you could add scoring
        sorted_results = sorted(results, key=lambda x: (x.type != "article", x.type != "topic"))

        # Apply pagination after collecting all results
        total = len(sorted_results)
        paginated_results = sorted_results[skip : skip + limit]

        return paginated_results, total

    async def _get_user_stats(self, user_id: UUID) -> DashboardStats:
        """Get user statistics"""
        # Total podcasts
        total_podcasts_query = select(Podcast).where(Podcast.user_id == user_id)
        total_podcasts_result = await self.session.exec(total_podcasts_query)
        total_podcasts = len(total_podcasts_result.all())

        # Completed podcasts
        completed_podcasts_query = select(Podcast).where(
            Podcast.user_id == user_id, Podcast.status == PodcastStatus.completed
        )
        completed_podcasts_result = await self.session.exec(completed_podcasts_query)
        completed_podcasts = len(completed_podcasts_result.all())

        # Total favorite topics
        favorite_topics_query = select(UserTopic).where(UserTopic.user_id == user_id)
        favorite_topics_result = await self.session.exec(favorite_topics_query)
        total_topics = len(favorite_topics_result.all())

        # User info for plan and member since
        user = await self.session.get(User, user_id)
        plan_type = user.plan_type if user else "free"
        member_since = user.created_at.strftime("%Y-%m-%d") if user and user.created_at else ""

        return DashboardStats(
            total_podcasts=total_podcasts,
            completed_podcasts=completed_podcasts,
            total_topics=total_topics,
            plan_type=plan_type,
            member_since=member_since,
        )

    async def _get_recent_podcasts(self, user_id: UUID, limit: int = 5) -> Sequence[Podcast]:
        """Get user's recent podcasts"""
        query = (
            select(Podcast)
            .where(Podcast.user_id == user_id)
            .order_by(desc(Podcast.created_at))
            .limit(limit)
        )
        result = await self.session.exec(query)
        return result.all()

    async def _get_recent_articles_for_user(self, user_id: UUID, limit: int = 10) -> Sequence[Article]:
        """Get recent articles from user's favorite topics"""
        user_topic_ids = await self._get_user_topic_ids(user_id)
        if not user_topic_ids:
            return []

        topic_attr = getattr(Article, "topic_id")
        query = (
            select(Article)
            .where(topic_attr.in_(user_topic_ids))
            .order_by(desc(Article.published_at))
            .limit(limit)
        )
        result = await self.session.exec(query)
        return result.all()

    async def _get_user_favorite_topics(self, user_id: UUID) -> Sequence[Topic]:
        """Get user's favorite topics"""
        query = select(Topic).join(UserTopic).where(UserTopic.user_id == user_id)
        result = await self.session.exec(query)
        return result.all()

    async def _get_user_topic_ids(self, user_id: UUID) -> list[int]:
        """Get list of topic IDs for user"""
        query = select(UserTopic.topic_id).where(UserTopic.user_id == user_id)
        result = await self.session.exec(query)
        return list(result.all())

    async def _search_articles(self, query_lower: str, topic_ids: list[int], skip: int, limit: int) -> list[GlobalSearchResult]:
        """Search articles by title"""
        topic_attr = getattr(Article, "topic_id")
        query = select(Article).where(topic_attr.in_(topic_ids))
        result = await self.session.exec(query)
        articles = result.all()

        results = []
        for article in articles:
            if query_lower in article.title.lower() and article.id is not None:
                results.append(GlobalSearchResult(
                    type="article",
                    id=article.id,
                    title=article.title,
                    description=article.summary_text,
                    url=article.url,
                ))

        return results[skip : skip + limit]

    async def _search_topics(self, query_lower: str, skip: int, limit: int) -> list[GlobalSearchResult]:
        """Search topics by name"""
        query = select(Topic)
        result = await self.session.exec(query)
        topics = result.all()

        results = []
        for topic in topics:
            if query_lower in topic.name.lower() and topic.id is not None:
                results.append(GlobalSearchResult(
                    type="topic",
                    id=topic.id,
                    title=topic.name,
                    description=f"Topic slug: {topic.slug}",
                ))

        return results[skip : skip + limit]

    async def _search_sources(self, query_lower: str, skip: int, limit: int) -> list[GlobalSearchResult]:
        """Search sources by name"""
        query = select(Source)
        result = await self.session.exec(query)
        sources = result.all()

        results = []
        for source in sources:
            if query_lower in source.name.lower() and source.id is not None:
                results.append(GlobalSearchResult(
                    type="source",
                    id=source.id,
                    title=source.name,
                    description=source.base_url,
                    url=source.base_url,
                ))

        return results[skip : skip + limit]
