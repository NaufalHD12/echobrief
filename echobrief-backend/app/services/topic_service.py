from typing import Sequence

from fastapi import HTTPException
from slugify import slugify
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.topics import Topic
from ..schemas.topics import TopicCreate, TopicUpdate


class TopicService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_topics(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[Sequence[Topic], int]:
        """Get paginated list of topics"""
        query = select(Topic).offset(skip).limit(limit)
        result = await self.session.exec(query)
        topics = result.all()

        # Get total count
        count_query = select(func.count()).select_from(Topic)
        total_result = await self.session.exec(count_query)
        total = total_result.one()

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
