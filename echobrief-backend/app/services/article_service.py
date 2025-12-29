from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence
from fastapi import HTTPException
from ..models.articles import Article
from ..models.sources import Source
from ..models.topics import Topic
from ..schemas.articles import ArticleCreate, ArticleUpdate

class ArticleService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_articles(
        self,
        skip: int = 0,
        limit: int = 10,
        topic_id: int | None = None
    ) -> tuple[Sequence[Article], int]:
        """Get paginated list of articles"""
        query = select(Article)
        
        if topic_id is not None:
            query = query.where(Article.topic_id == topic_id)
            
        query = query.offset(skip).limit(limit)
        result = await self.session.exec(query)
        articles = result.all()

        # Get total count
        count_query = select(func.count()).select_from(Article)
        if topic_id is not None:
            count_query = count_query.where(Article.topic_id == topic_id)
        total_result = await self.session.exec(count_query)
        total = total_result.one()

        return articles, total

    async def get_article_by_id(self, article_id: int) -> Article:
        """Get article by ID"""
        article = await self.session.get(Article, article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return article

    async def create_article(self, article_data: ArticleCreate) -> Article:
        """Create new article"""
        # Validate source exists
        source = await self.session.get(Source, article_data.source_id)
        if not source:
            raise HTTPException(status_code=400, detail="Source not found")

        # Validate topic exists
        topic = await self.session.get(Topic, article_data.topic_id)
        if not topic:
            raise HTTPException(status_code=400, detail="Topic not found")

        # Check if URL already exists
        existing_query = select(Article).where(Article.url == article_data.url)
        existing_result = await self.session.exec(existing_query)
        existing = existing_result.first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Article with URL '{article_data.url}' already exists")

        article = Article(**article_data.model_dump())
        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)
        return article

    async def update_article(self, article_id: int, article_data: ArticleUpdate) -> Article:
        """Update existing article"""
        article = await self.get_article_by_id(article_id)

        update_data = article_data.model_dump(exclude_unset=True)

        # Validate source exists if source_id is being updated
        if "source_id" in update_data:
            source = await self.session.get(Source, update_data["source_id"])
            if not source:
                raise HTTPException(status_code=400, detail="Source not found")

        # Validate topic exists if topic_id is being updated
        if "topic_id" in update_data:
            topic = await self.session.get(Topic, update_data["topic_id"])
            if not topic:
                raise HTTPException(status_code=400, detail="Topic not found")

        # Check URL uniqueness if URL is being updated
        if "url" in update_data:
            existing_query = select(Article).where(
                Article.url == update_data["url"],
                Article.id != article_id
            )
            existing_result = await self.session.exec(existing_query)
            existing = existing_result.first()
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Article with URL '{update_data['url']}' already exists"
                )

        article.sqlmodel_update(update_data)
        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)
        return article

    async def delete_article(self, article_id: int) -> None:
        """Delete article"""
        article = await self.get_article_by_id(article_id)
        await self.session.delete(article)
        await self.session.commit()
