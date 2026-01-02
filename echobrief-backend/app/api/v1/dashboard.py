from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.auth import get_current_user
from ...core.database import get_session
from ...models.users import User
from ...schemas.articles import ArticleResponse
from ...schemas.common import ApiResponse
from ...schemas.dashboard import DashboardResponse, GlobalSearchResponse
from ...schemas.podcasts import PodcastResponse
from ...schemas.topics import TopicResponse
from ...schemas.users import UserResponse
from ...services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


async def get_dashboard_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DashboardService:
    return DashboardService(session)


@router.get("/", response_model=ApiResponse[DashboardResponse])
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> ApiResponse[DashboardResponse]:
    """
    Get user dashboard with statistics, recent podcasts, articles, and favorite topics.

    Returns comprehensive dashboard data including:
    - User profile information
    - Podcast statistics (total, completed, plan type, member since)
    - Recent podcasts (last 5)
    - Recent articles from favorite topics (last 10)
    - User's favorite topics
    """
    dashboard_data = await service.get_user_dashboard_data(current_user.id)

    # Convert model objects to response schemas
    response_data = DashboardResponse(
        user=UserResponse(**dashboard_data["user"].model_dump()),
        stats=dashboard_data["stats"],
        recent_podcasts=[
            PodcastResponse(
                id=podcast.id,
                user_id=podcast.user_id,
                generated_script=podcast.generated_script,
                audio_url=podcast.audio_url,
                duration_seconds=podcast.duration_seconds,
                status=podcast.status,
                created_at=podcast.created_at,
                topics=[],  # Will be populated if needed
                articles=[],
                segments=[],
            )
            for podcast in dashboard_data["recent_podcasts"]
        ],
        recent_articles=[
            ArticleResponse(**article.model_dump())
            for article in dashboard_data["recent_articles"]
        ],
        favorite_topics=[
            TopicResponse(**topic.model_dump())
            for topic in dashboard_data["favorite_topics"]
        ],
    )

    return ApiResponse(
        message="Dashboard data retrieved successfully",
        data=response_data,
    )


@router.get("/search", response_model=ApiResponse[GlobalSearchResponse])
async def global_search(
    q: Annotated[str, Query(description="Search query", min_length=1)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    current_user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> ApiResponse[GlobalSearchResponse]:
    """
    Perform global search across articles, topics, and sources.

    Search is performed on:
    - Article titles (limited to user's favorite topics)
    - Topic names
    - Source names

    Results are sorted by relevance (articles first, then topics, then sources).
    """
    skip = (page - 1) * per_page
    search_results, total = await service.global_search(q, current_user.id, skip, per_page)

    return ApiResponse(
        message=f"Found {total} results for '{q}'",
        data=GlobalSearchResponse(
            items=search_results,
            total=total,
            page=page,
            per_page=per_page,
        ),
    )
