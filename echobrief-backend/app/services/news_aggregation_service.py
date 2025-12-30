import html
import logging
import re
from datetime import datetime, timezone
from typing import Optional

import feedparser
from openai import OpenAI
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.config import settings
from ..models.articles import Article
from ..models.sources import Source
from ..models.topics import Topic
from ..schemas.articles import ArticleCreate
from .article_service import ArticleService
from .source_service import SourceService
from .topic_service import TopicService

logger = logging.getLogger(__name__)


class NewsAggregationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.article_service = ArticleService(session)
        self.source_service = SourceService(session)
        self.topic_service = TopicService(session)
        self.openai_client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY, base_url=settings.DEEPSEEK_BASE_URL
        )

    async def aggregate_news(self) -> dict:
        """Aggregate news from all active sources"""
        active_sources = await self.source_service.get_active_sources()
        total_processed = 0
        total_new = 0

        for source in active_sources:
            try:
                processed, new = await self._process_source(source)
                total_processed += processed
                total_new += new
            except Exception as e:
                logger.error(f"Error processing source {source.name}: {e}")
                continue

        return {"total_processed": total_processed, "total_new_articles": total_new}

    async def _process_source(self, source: Source) -> tuple[int, int]:
        """Process RSS feed from a source"""
        assert source.id is not None
        logger.info(f"Processing source: {source.name} (ID: {source.id})")
        feed = feedparser.parse(source.base_url)
        logger.info(f"Found {len(feed.entries)} entries in RSS feed")

        processed = 0
        new_articles = 0

        for i, entry in enumerate(feed.entries):
            try:
                article_dict = self._extract_article_data(entry, source.id)
                if not article_dict:
                    logger.debug(f"Entry {i}: Failed to extract article data")
                    processed += 1
                    continue

                logger.debug(f"Entry {i}: Extracted - {article_dict['title'][:50]}...")

                # Check for duplicates first to save LLM costs
                if await self._is_duplicate(article_dict["url"]):
                    logger.debug(f"Entry {i}: Skipped duplicate article")
                    processed += 1
                    continue

                topic_id, generated_summary = await self._determine_topic_and_summary(
                    article_dict["title"], article_dict["summary_text"] or ""
                )
                logger.debug(
                    f"Entry {i}: AI result - topic_id: {topic_id}, has_summary: {bool(generated_summary)}"
                )

                if topic_id and generated_summary:
                    article_data = ArticleCreate(
                        source_id=article_dict["source_id"],
                        topic_id=topic_id,
                        title=article_dict["title"],
                        summary_text=generated_summary,
                        url=article_dict["url"],
                        published_at=article_dict["published_at"],
                    )
                    try:
                        await self.article_service.create_article(article_data)
                        new_articles += 1
                        logger.info(
                            f"Entry {i}: Created article - {article_dict['title'][:50]}..."
                        )
                    except Exception as e:
                        logger.error(
                            f"Entry {i}: Error creating article: {e}", exc_info=True
                        )
                else:
                    logger.warning(f"Entry {i}: AI processing failed or no topic found")

                processed += 1
            except Exception as e:
                logger.error(f"Error processing entry {i}: {e}", exc_info=True)
                continue

        logger.info(f"Source {source.name}: Processed {processed}, New: {new_articles}")
        return processed, new_articles

    def _extract_article_data(self, entry, source_id: int) -> Optional[dict]:
        """Extract article data from RSS entry"""
        title = getattr(entry, "title", "").strip()
        summary = (
            getattr(entry, "summary", "").strip()
            or getattr(entry, "description", "").strip()
        )
        url = getattr(entry, "link", "").strip()
        published = getattr(entry, "published_parsed", None)

        if not title or not url:
            return None

        # Clean HTML from summary
        summary = html.unescape(summary)
        summary = re.sub(r"<[^>]+>", "", summary).strip()

        published_at = (
            datetime(*published[:6]) if published else datetime.now(timezone.utc)
        )

        return {
            "source_id": source_id,
            "title": title,
            "summary_text": summary,
            "url": url,
            "published_at": published_at,
        }

    async def _is_duplicate(self, url: str) -> bool:
        """Check if article URL already exists"""
        query = select(Article).where(Article.url == url)
        result = await self.session.exec(query)
        return result.first() is not None

    async def _determine_topic_and_summary(
        self, title: str, summary: str
    ) -> tuple[Optional[int], str]:
        """Determine topic ID and generate meaningful summary using AI with fallback"""
        # Get all topics
        topics_result = await self.session.exec(select(Topic))
        topics = topics_result.all()
        topic_names = {topic.name.lower(): topic.id for topic in topics}

        # AI Classification and Summary Generation
        prompt = f"""
        Analyze the news article and provide:
        1. Topic: Choose from these topics: {', '.join([t.name for t in topics])}
        2. Summary: Write a brief, meaningful summary in 2-5 sentences based on the title and related articles

        Title: {title}
        Related Articles: {summary}

        Format your response as:
        Topic: [topic name]
        Summary: [summary text]
        """

        try:
            import asyncio
            from asyncio import TimeoutError

            # Create a wrapper for async execution with timeout
            async def call_ai_api():
                response = self.openai_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    timeout=30.0,  # 30 second timeout
                )
                return response

            try:
                # Run with timeout
                response = await asyncio.wait_for(call_ai_api(), timeout=35.0)
                content = response.choices[0].message.content

                if content:
                    # Parse response
                    lines = content.strip().split("\n")
                    topic_name = None
                    summary_text = ""
                    for line in lines:
                        if line.startswith("Topic:"):
                            topic_name = line.replace("Topic:", "").strip().lower()
                        elif line.startswith("Summary:"):
                            summary_text = line.replace("Summary:", "").strip()

                    topic_id = topic_names.get(topic_name) if topic_name else None
                    if topic_id and summary_text:
                        logger.debug(
                            f"AI success: topic_id={topic_id}, summary_length={len(summary_text)}"
                        )
                        return topic_id, summary_text
                    else:
                        logger.warning(
                            f"AI response incomplete: topic_name={topic_name}, has_summary={bool(summary_text)}"
                        )
                        # Fallback to default topic and simple summary
                        return self._fallback_topic_and_summary(title, summary, topics)
                else:
                    logger.warning("AI returned empty content")
                    return self._fallback_topic_and_summary(title, summary, topics)

            except TimeoutError:
                logger.error("AI API timeout after 35 seconds")
                return self._fallback_topic_and_summary(title, summary, topics)

        except Exception as e:
            logger.error(f"AI processing failed: {e}", exc_info=True)
            return self._fallback_topic_and_summary(title, summary, topics)

    def _fallback_topic_and_summary(
        self, title: str, summary: str, topics
    ) -> tuple[Optional[int], str]:
        """Fallback method when AI processing fails"""
        # Default to first topic if available
        default_topic_id = topics[0].id if topics else None

        # Create simple summary from title
        simple_summary = f"{title}. {summary[:100]}..." if summary else f"{title}."

        logger.info(
            f"Using fallback: topic_id={default_topic_id}, summary_length={len(simple_summary)}"
        )
        return default_topic_id, simple_summary
