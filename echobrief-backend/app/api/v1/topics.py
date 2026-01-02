from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.auth import get_current_user
from ...core.database import get_session
from ...models.users import User
from ...schemas.common import ApiResponse
from ...schemas.topics import TopicListResponse, TopicResponse
from ...services.topic_service import TopicService

router = APIRouter(prefix="/topics", tags=["topics"])


async def get_topic_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TopicService:
    return TopicService(session)


@router.get(
    "/",
    response_model=ApiResponse[TopicListResponse],
    summary="Get list of topics",
    description="Retrieve paginated list of all topics with optional search",
)
async def get_topics(
    service: Annotated[TopicService, Depends(get_topic_service)],
    search: Annotated[str | None, Query(description="Search in topic name")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
    current_user: User = Depends(get_current_user),
) -> ApiResponse[TopicListResponse]:
    """
    Get paginated list of topics with optional search.

    - **search**: Optional search term for topic name (case-insensitive)
    - **page**: Page number (starts from 1)
    - **per_page**: Number of items per page (max 100, default 10)
    """
    skip = (page - 1) * per_page
    topics, total = await service.get_topics(skip=skip, limit=per_page, search=search)

    return ApiResponse(
        message="Topics retrieved successfully",
        data=TopicListResponse(
            items=[TopicResponse(**topic.model_dump()) for topic in topics],
            total=total,
            page=page,
            per_page=per_page,
        ),
    )


@router.get(
    "/{topic_id}",
    response_model=ApiResponse[TopicResponse],
    summary="Get topic by ID",
    description="Retrieve a specific topic by its ID",
)
async def get_topic(
    service: Annotated[TopicService, Depends(get_topic_service)],
    topic_id: Annotated[int, Path(description="Topic ID")],
    current_user: User = Depends(get_current_user),
) -> ApiResponse[TopicResponse]:
    """
    Get topic by ID

    - **topic_id**: Unique identifier of the topic
    """
    topic = await service.get_topic_by_id(topic_id)
    return ApiResponse(
        message="Topic retrieved successfully", data=TopicResponse(**topic.model_dump())
    )


@router.get(
    "/slug/{slug}",
    response_model=ApiResponse[TopicResponse],
    summary="Get topic by slug",
    description="Retrieve a specific topic by its slug",
)
async def get_topic_by_slug(
    slug: Annotated[str, Path(description="Topic slug")],
    service: Annotated[TopicService, Depends(get_topic_service)],
    current_user: User = Depends(get_current_user),
) -> ApiResponse[TopicResponse]:
    """
    Get topic by slug.

    - **slug**: URL-friendly identifier of the topic
    """
    topic = await service.get_topic_by_slug(slug)
    return ApiResponse(
        message="Topic retrieved successfully", data=TopicResponse(**topic.model_dump())
    )
