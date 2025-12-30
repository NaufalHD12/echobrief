from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.database import get_session
from ...schemas.common import ApiResponse
from ...schemas.topics import TopicCreate, TopicListResponse, TopicResponse, TopicUpdate
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
    description="Retrieve paginated list of all topics with optional filtering",
)
async def get_topics(
    service: Annotated[TopicService, Depends(get_topic_service)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
) -> ApiResponse[TopicListResponse]:
    """
    Get paginated list of topics.

    - **page**: Page number (starts from 1)
    - **per_page**: Number of items per page (max 100, default 10)
    """
    skip = (page - 1) * per_page
    topics, total = await service.get_topics(skip=skip, limit=per_page)

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
) -> ApiResponse[TopicResponse]:
    """
    Get topic by slug.

    - **slug**: URL-friendly identifier of the topic
    """
    topic = await service.get_topic_by_slug(slug)
    return ApiResponse(
        message="Topic retrieved successfully", data=TopicResponse(**topic.model_dump())
    )


@router.post(
    "/",
    response_model=ApiResponse[TopicResponse],
    status_code=201,
    summary="Create new topic",
    description="Create a new topic with name and slug",
)
async def create_topic(
    topic_data: TopicCreate,
    service: Annotated[TopicService, Depends(get_topic_service)],
) -> ApiResponse[TopicResponse]:
    """
    Create a new topic.

    - **name**: Topic name (2-50 characters)
    - **slug**: URL-friendly identifier (auto-generated if not provided)
    """
    topic = await service.create_topic(topic_data)
    return ApiResponse(
        message="Topic created successfully", data=TopicResponse(**topic.model_dump())
    )


@router.put(
    "/{topic_id}",
    response_model=ApiResponse[TopicResponse],
    summary="Update topic",
    description="Update an existing topic's information",
)
async def update_topic(
    topic_id: Annotated[int, Path(description="Topic ID")],
    topic_data: TopicUpdate,
    service: Annotated[TopicService, Depends(get_topic_service)],
) -> ApiResponse[TopicResponse]:
    """
    Update topic information.

    - **topic_id**: Unique identifier of the topic to update
    - **name**: New topic name (optional)
    - **slug**: New slug (optional)
    """
    topic = await service.update_topic(topic_id, topic_data)
    return ApiResponse(
        message="Topic updated successfully", data=TopicResponse(**topic.model_dump())
    )


@router.delete(
    "/{topic_id}",
    response_model=ApiResponse[None],
    summary="Delete topic",
    description="Delete a topic by its ID",
)
async def delete_topic(
    topic_id: Annotated[int, Path(description="Topic ID")],
    service: Annotated[TopicService, Depends(get_topic_service)],
) -> ApiResponse[None]:
    """
    Delete a topic.

    - **topic_id**: Unique identifier of the topic to delete
    """
    await service.delete_topic(topic_id)
    return ApiResponse(message="Topic deleted successfully")
