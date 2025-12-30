from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.database import get_session
from ...schemas.articles import (
    ArticleCreate,
    ArticleListResponse,
    ArticleResponse,
    ArticleUpdate,
)
from ...schemas.common import ApiResponse
from ...services.article_service import ArticleService

router = APIRouter(prefix="/articles", tags=["articles"])


async def get_article_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ArticleService:
    return ArticleService(session)


@router.get(
    "/",
    response_model=ApiResponse[ArticleListResponse],
    summary="Get list of articles",
    description="Retrieve paginated list of all articles with optional filtering by topic",
)
async def get_articles(
    service: Annotated[ArticleService, Depends(get_article_service)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
    topic_id: Annotated[int | None, Query(description="Filter by topic ID")] = None,
) -> ApiResponse[ArticleListResponse]:
    """
    Get paginated list of articles.

    - **page**: Page number (starts from 1)
    - **per_page**: Number of items per page (max 100, default 10)
    - **topic_id**: Optional topic ID to filter articles by topic
    """
    skip = (page - 1) * per_page
    articles, total = await service.get_articles(
        skip=skip, limit=per_page, topic_id=topic_id
    )

    return ApiResponse(
        message="Articles retrieved successfully",
        data=ArticleListResponse(
            items=[ArticleResponse(**article.model_dump()) for article in articles],
            total=total,
            page=page,
            per_page=per_page,
        ),
    )


@router.get(
    "/{article_id}",
    response_model=ApiResponse[ArticleResponse],
    summary="Get article by ID",
    description="Retrieve a specific article by its ID",
)
async def get_article(
    article_id: Annotated[int, Path(description="Article ID")],
    service: Annotated[ArticleService, Depends(get_article_service)],
) -> ApiResponse[ArticleResponse]:
    """
    Get article by ID.

    - **article_id**: Unique identifier of the article
    """
    article = await service.get_article_by_id(article_id)
    return ApiResponse(
        message="Article retrieved successfully",
        data=ArticleResponse(**article.model_dump()),
    )


@router.post(
    "/",
    response_model=ApiResponse[ArticleResponse],
    status_code=201,
    summary="Create new article",
    description="Create a new article",
)
async def create_article(
    article_data: ArticleCreate,
    service: Annotated[ArticleService, Depends(get_article_service)],
) -> ApiResponse[ArticleResponse]:
    """
    Create a new article.

    - **source_id**: ID of the news source
    - **topic_id**: ID of the topic
    - **title**: Article title (1-500 characters)
    - **url**: Article URL (must be HTTP/HTTPS)
    """
    article = await service.create_article(article_data)
    return ApiResponse(
        message="Article created successfully",
        data=ArticleResponse(**article.model_dump()),
    )


@router.put(
    "/{article_id}",
    response_model=ApiResponse[ArticleResponse],
    summary="Update article",
    description="Update an existing article's information",
)
async def update_article(
    article_id: Annotated[int, Path(description="Article ID")],
    article_data: ArticleUpdate,
    service: Annotated[ArticleService, Depends(get_article_service)],
) -> ApiResponse[ArticleResponse]:
    """
    Update article information.

    - **article_id**: Unique identifier of the article to update
    - **title**: New article title (optional)
    - **summary_text**: New summary text (optional)
    - **url**: New article URL (optional)
    - **published_at**: Publication date (optional)
    """
    article = await service.update_article(article_id, article_data)
    return ApiResponse(
        message="Article updated successfully",
        data=ArticleResponse(**article.model_dump()),
    )


@router.delete(
    "/{article_id}",
    response_model=ApiResponse[None],
    summary="Delete article",
    description="Delete an article by its ID",
)
async def delete_article(
    article_id: Annotated[int, Path(description="Article ID")],
    service: Annotated[ArticleService, Depends(get_article_service)],
) -> ApiResponse[None]:
    """
    Delete an article.

    - **article_id**: Unique identifier of the article to delete
    """
    await service.delete_article(article_id)
    return ApiResponse(message="Article deleted successfully")
