from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.auth import get_current_admin
from ...core.database import get_session
from ...models.users import User
from ...schemas.articles import ArticleCreate, ArticleResponse, ArticleUpdate
from ...schemas.common import ApiResponse
from ...schemas.sources import SourceCreate, SourceCreateBulk, SourceResponse, SourceUpdate
from ...schemas.topics import TopicCreate, TopicCreateBulk, TopicResponse, TopicUpdate
from ...schemas.users import UserResponse, UserUpdate
from ...services.article_service import ArticleService
from ...services.news_aggregation_service import NewsAggregationService
from ...services.podcast_service import PodcastService
from ...services.source_service import SourceService
from ...services.subscription_service import SubscriptionService
from ...services.topic_service import TopicService
from ...services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["admin"])


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    return UserService(session)


async def get_article_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ArticleService:
    return ArticleService(session)


async def get_source_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SourceService:
    return SourceService(session)


async def get_topic_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TopicService:
    return TopicService(session)


async def get_podcast_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PodcastService:
    return PodcastService(session)


async def get_news_aggregation_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NewsAggregationService:
    return NewsAggregationService(session)


async def get_subscription_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SubscriptionService:
    return SubscriptionService(session)


@router.get("/users", response_model=ApiResponse[list[UserResponse]])
async def get_users(
    search: Annotated[str | None, Query(description="Search in username or email")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
    current_user: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[list[UserResponse]]:
    """
    Get all users (admin only) with optional search and pagination.

    - **search**: Optional search term for username or email (case-insensitive)
    - **page**: Page number (starts from 1)
    - **per_page**: Number of items per page (max 100, default 10)

    Returns paginated list of users in the system with their profile information.
    Requires admin privileges.
    """
    skip = (page - 1) * per_page
    users, total = await user_service.get_all_users(
        search=search, skip=skip, limit=per_page
    )
    return ApiResponse(
        message=f"Users retrieved successfully ({total} total)",
        data=[UserResponse(**user.model_dump()) for user in users],
    )


@router.put("/users/{user_id}", response_model=ApiResponse[UserResponse])
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_admin: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[UserResponse]:
    """
    Update user profile (admin only).

    - **user_id**: User ID in UUID format
    - **username**: New username (optional, 3-50 characters)
    - **plan_type**: New plan type - "free" or "paid" (optional)
    - **role**: New role - "user" or "admin" (optional)

    Requires admin privileges.
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    updated_user = await user_service.update_user_admin(user_uuid, user_data)
    return ApiResponse(
        message="User updated successfully",
        data=UserResponse(**updated_user.model_dump()),
    )


@router.post("/articles", response_model=ApiResponse[ArticleResponse], status_code=201)
async def create_article(
    article_data: ArticleCreate,
    service: Annotated[ArticleService, Depends(get_article_service)],
    current_user: User = Depends(get_current_admin),
) -> ApiResponse[ArticleResponse]:
    """
    Create a new article. (admin only)

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


@router.put("/articles/{article_id}", response_model=ApiResponse[ArticleResponse])
async def update_article(
    article_id: Annotated[int, Path(description="Article ID")],
    article_data: ArticleUpdate,
    service: Annotated[ArticleService, Depends(get_article_service)],
    current_user: User = Depends(get_current_admin),
) -> ApiResponse[ArticleResponse]:
    """
    Update article information. (admin only)

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


@router.delete("/articles/{article_id}", response_model=ApiResponse[None])
async def delete_article(
    article_id: Annotated[int, Path(description="Article ID")],
    service: Annotated[ArticleService, Depends(get_article_service)],
    current_user: User = Depends(get_current_admin),
) -> ApiResponse[None]:
    """
    Delete an article. (admin only)

    - **article_id**: Unique identifier of the article to delete
    """
    await service.delete_article(article_id)
    return ApiResponse(message="Article deleted successfully")


@router.post("/sources", response_model=ApiResponse[SourceResponse], status_code=201)
async def create_source(
    source_data: SourceCreate,
    service: Annotated[SourceService, Depends(get_source_service)],
    current_user: User = Depends(get_current_admin),
) -> ApiResponse[SourceResponse]:
    """
    Create a new source. (admin only)

    - **name**: Source name (2-50 characters)
    - **base_url**: Base URL of the news source
    """
    source = await service.create_source(source_data)
    return ApiResponse(
        message="Source created successfully",
        data=SourceResponse(**source.model_dump()),
    )


@router.post("/sources/bulk", response_model=ApiResponse[list[SourceResponse]], status_code=201)
async def create_sources_bulk(
    bulk_data: SourceCreateBulk,
    service: Annotated[SourceService, Depends(get_source_service)],
    current_user: User = Depends(get_current_admin),
) -> ApiResponse[list[SourceResponse]]:
    """
    Create multiple sources in bulk. (admin only)

    - **sources**: List of source objects to create
    """
    sources = await service.create_sources_bulk(bulk_data.sources)
    return ApiResponse(
        message=f"{len(sources)} sources created successfully",
        data=[SourceResponse(**source.model_dump()) for source in sources],
    )


@router.put("/sources/{source_id}", response_model=ApiResponse[SourceResponse])
async def update_source(
    source_id: Annotated[int, Path(description="Source ID")],
    source_data: SourceUpdate,
    service: Annotated[SourceService, Depends(get_source_service)],
    current_user: User = Depends(get_current_admin),
) -> ApiResponse[SourceResponse]:
    """
    Update source information. (admin only)

    - **source_id**: Unique identifier of the source to update
    - **name**: New source name (optional)
    - **base_url**: New base URL (optional)
    """
    source = await service.update_source(source_id, source_data)
    return ApiResponse(
        message="Source updated successfully",
        data=SourceResponse(**source.model_dump()),
    )


@router.delete("/sources/{source_id}", response_model=ApiResponse[None])
async def delete_source(
    source_id: Annotated[int, Path(description="Source ID")],
    service: Annotated[SourceService, Depends(get_source_service)],
    current_user: User = Depends(get_current_admin),
) -> ApiResponse[None]:
    """
    Delete a source. (admin only)

    - **source_id**: Unique identifier of the source to delete
    """
    await service.delete_source(source_id)
    return ApiResponse(message="Source deleted successfully")


@router.post("/topics", response_model=ApiResponse[TopicResponse], status_code=201)
async def create_topic(
    topic_data: TopicCreate,
    service: Annotated[TopicService, Depends(get_topic_service)],
    current_user: User = Depends(get_current_admin),
) -> ApiResponse[TopicResponse]:
    """
    Create a new topic. (admin only)

    - **name**: Topic name (2-50 characters)
    - **slug**: URL-friendly identifier (auto-generated if not provided)
    """
    topic = await service.create_topic(topic_data)
    return ApiResponse(
        message="Topic created successfully", data=TopicResponse(**topic.model_dump())
    )


@router.post("/topics/bulk", response_model=ApiResponse[list[TopicResponse]], status_code=201)
async def create_topics_bulk(
    bulk_data: TopicCreateBulk,
    service: Annotated[TopicService, Depends(get_topic_service)],
    current_user: User = Depends(get_current_admin),
) -> ApiResponse[list[TopicResponse]]:
    """
    Create multiple topics in bulk. (admin only)

    - **topics**: List of topic objects to create
    """
    topics = await service.create_topics_bulk(bulk_data.topics)
    return ApiResponse(
        message=f"{len(topics)} topics created successfully",
        data=[TopicResponse(**topic.model_dump()) for topic in topics],
    )


@router.put("/topics/{topic_id}", response_model=ApiResponse[TopicResponse])
async def update_topic(
    topic_id: Annotated[int, Path(description="Topic ID")],
    topic_data: TopicUpdate,
    service: Annotated[TopicService, Depends(get_topic_service)],
    current_user: User = Depends(get_current_admin),
) -> ApiResponse[TopicResponse]:
    """
    Update topic information. (admin only)

    - **topic_id**: Unique identifier of the topic to update
    - **name**: New topic name (optional)
    - **slug**: New slug (optional)
    """
    topic = await service.update_topic(topic_id, topic_data)
    return ApiResponse(
        message="Topic updated successfully", data=TopicResponse(**topic.model_dump())
    )


@router.delete("/topics/{topic_id}", response_model=ApiResponse[None])
async def delete_topic(
    topic_id: Annotated[int, Path(description="Topic ID")],
    service: Annotated[TopicService, Depends(get_topic_service)],
    current_user: User = Depends(get_current_admin),
) -> ApiResponse[None]:
    """
    Delete a topic. (admin only)

    - **topic_id**: Unique identifier of the topic to delete
    """
    await service.delete_topic(topic_id)
    return ApiResponse(message="Topic deleted successfully")


@router.delete("/podcasts/{podcast_id}", response_model=ApiResponse[dict])
async def delete_podcast(
    podcast_id: Annotated[UUID, Path(description="Podcast ID")],
    service: Annotated[PodcastService, Depends(get_podcast_service)],
    current_admin: User = Depends(get_current_admin),
) -> ApiResponse[dict]:
    """
    Delete a podcast and all related data. (admin only)

    - **podcast_id**: Unique identifier of the podcast
    - Requires admin privileges
    """
    deleted = await service.delete_podcast(podcast_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Podcast not found")

    return ApiResponse(message="Podcast deleted successfully", data={"deleted": True})


@router.post("/system/aggregate-news", response_model=ApiResponse[dict])
async def aggregate_news(
    current_user: User = Depends(get_current_admin),
    service: NewsAggregationService = Depends(get_news_aggregation_service),
):
    """Trigger news aggregation (system operation - admin only)"""
    result = await service.aggregate_news()
    return ApiResponse(message="News aggregation completed", data=result)


@router.post("/subscriptions/check-expired", response_model=ApiResponse[dict])
async def check_expired_subscriptions(
    current_admin: User = Depends(get_current_admin),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> ApiResponse[dict]:
    """
    Check and update expired subscriptions (admin endpoint).

    This should be called periodically (e.g., daily) to clean up expired subscriptions.
    """
    expired_subs = await subscription_service.check_and_update_expired_subscriptions()

    return ApiResponse(
        message="Checked expired subscriptions",
        data={
            "expired_count": len(expired_subs),
            "expired_subscription_ids": [str(sub.id) for sub in expired_subs],
        },
    )
