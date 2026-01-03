from typing import Sequence

from fastapi import HTTPException
from slugify import slugify
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.topics import Topic
from ..schemas.topics import TopicCreate, TopicUpdate


class TopicService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_topics(
        self, skip: int = 0, limit: int = 10, search: str | None = None
    ) -> tuple[Sequence[Topic], int]:
        """Get paginated list of topics with optional search"""
        query = select(Topic)

        if search:
            search_lower = search.lower()
            # Search in topic name using case-insensitive comparison
            query = query.where(func.lower(Topic.name).like(f"%{search_lower}%"))

        # Get total count
        total_result = await self.session.exec(
            select(func.count()).select_from(query.subquery())
        )
        total = total_result.one()

        # Apply pagination
        query = query.offset(skip).limit(limit)
        result = await self.session.exec(query)
        topics = result.all()

        return topics, total

    async def get_topic_by_id(self, topic_id: int) -> Topic:
        """Get topic by ID"""
        topic = await self.session.get(Topic, topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        return topic

    async def get_topic_by_slug(self, slug: str) -> Topic:
        """Get topic by slug"""
        query = select(Topic).where(Topic.slug == slug)
        result = await self.session.exec(query)
        topic = result.first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        return topic

    async def create_topic(self, topic_data: TopicCreate) -> Topic:
        """Create new topic"""
        # Generate slug if not provided
        slug = topic_data.slug or slugify(topic_data.name)

        existing_query = select(Topic).where(Topic.slug == slug)
        existing_result = await self.session.exec(existing_query)
        existing = existing_result.first()
        if existing:
            raise HTTPException(
                status_code=400, detail=f"Topic with '{slug}' already exists"
            )
        topic = Topic(name=topic_data.name, slug=slug)
        self.session.add(topic)
        await self.session.commit()
        await self.session.refresh(topic)
        return topic

    async def create_topics_bulk(self, topics_data: list[TopicCreate]) -> list[Topic]:
        """Create multiple topics in bulk"""
        created_topics = []
        errors = []

        for i, topic_data in enumerate(topics_data):
            try:
                # Generate slug if not provided
                slug = topic_data.slug or slugify(topic_data.name)

                existing_query = select(Topic).where(Topic.slug == slug)
                existing_result = await self.session.exec(existing_query)
                existing = existing_result.first()
                if existing:
                    errors.append(
                        f"Topic with slug '{slug}' at index {i} already exists"
                    )
                    continue

                topic = Topic(name=topic_data.name, slug=slug)
                self.session.add(topic)
                created_topics.append(topic)

            except Exception as e:
                errors.append(
                    f"Error creating topic '{topic_data.name}' at index {i}: {str(e)}"
                )

        if created_topics:
            await self.session.commit()
            # Refresh all created topics
            for topic in created_topics:
                await self.session.refresh(topic)

        if errors:
            # If there were errors but some topics were created, we still commit
            # but return information about errors
            pass  # Could log errors or handle differently

        return created_topics

    async def update_topic(self, topic_id: int, topic_data: TopicUpdate) -> Topic:
        """Update existing topic"""
        topic = await self.get_topic_by_id(topic_id)

        update_data = topic_data.model_dump(exclude_unset=True)
        if "slug" in update_data:
            existing_query = select(Topic).where(
                Topic.slug == update_data["slug"], Topic.id != topic_id
            )
            existing_result = await self.session.exec(existing_query)
            existing = existing_result.first()
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Topic with slug '{update_data['slug']}' already exists",
                )
        topic.sqlmodel_update(update_data)
        self.session.add(topic)
        await self.session.commit()
        await self.session.refresh(topic)
        return topic

    async def delete_topic(self, topic_id: int) -> None:
        """Delete topic"""
        topic = await self.get_topic_by_id(topic_id)
        await self.session.delete(topic)
        await self.session.commit()
