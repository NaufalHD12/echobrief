from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.auth import get_current_user
from ...core.database import get_session
from ...models.users import User
from ...schemas.articles import (
    ArticleListResponse,
    ArticleResponse,
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
    description="Retrieve paginated list of all articles with optional filtering",
)
async def get_articles(
    service: Annotated[ArticleService, Depends(get_article_service)],
    search: Annotated[str | None, Query(description="Search in article title")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
    topic_id: Annotated[int | None, Query(description="Filter by topic ID")] = None,
    current_user: User = Depends(get_current_user),
) -> ApiResponse[ArticleListResponse]:
    """
    Get paginated list of articles with optional filtering.

    - **search**: Optional search term for article title (case-insensitive)
    - **page**: Page number (starts from 1)
    - **per_page**: Number of items per page (max 100, default 10)
    - **topic_id**: Optional topic ID to filter articles by topic
    """
    skip = (page - 1) * per_page
    articles, total = await service.get_articles(
        skip=skip, limit=per_page, topic_id=topic_id, search=search
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
    current_user: User = Depends(get_current_user),
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
