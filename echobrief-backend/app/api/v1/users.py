from typing import Annotated, List

from fastapi import APIRouter, Depends

from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.auth import get_current_admin, get_current_user
from ...core.database import get_session
from ...models.users import User
from ...schemas.common import ApiResponse
from ...schemas.topics import TopicResponse
from ...schemas.users import UserResponse, UserUpdate
from ...services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    return UserService(session)



@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[UserResponse]:
    """Get current user profile"""
    return ApiResponse(
        message="Profile retrieved successfully",
        data=UserResponse(**current_user.model_dump()),
    )


@router.put("/me", response_model=ApiResponse[UserResponse])
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[UserResponse]:
    """Update current user profile"""
    updated_user = await user_service.update_user(current_user.id, user_data)
    return ApiResponse(
        message="Profile updated successfully",
        data=UserResponse(**updated_user.model_dump()),
    )


@router.get("/", response_model=ApiResponse[List[UserResponse]])
async def get_users(
    current_user: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[List[UserResponse]]:
    """Get all users (admin only)"""
    users = await user_service.get_all_users()
    return ApiResponse(
        message="Users retrieved successfully",
        data=[UserResponse(**user.model_dump()) for user in users],
    )


@router.post("/topics", response_model=ApiResponse[dict])
async def add_user_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[dict]:
    """Add topic to current user's selection"""
    await user_service.add_user_topic(current_user.id, topic_id)
    return ApiResponse(
        message="Topic added to selection",
        data={"topic_id": topic_id},
    )


@router.delete("/topics/{topic_id}", response_model=ApiResponse[dict])
async def remove_user_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[dict]:
    """Remove topic from current user's selection"""
    await user_service.remove_user_topic(current_user.id, topic_id)
    return ApiResponse(
        message="Topic removed from selection",
        data={"topic_id": topic_id},
    )


@router.get("/topics", response_model=ApiResponse[List[TopicResponse]])
async def get_user_topics(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[List[TopicResponse]]:
    """Get current user's selected topics"""
    topics = await user_service.get_user_topics(current_user.id)
    return ApiResponse(
        message="Topics retrieved successfully",
        data=[TopicResponse(**topic.model_dump()) for topic in topics],
    )
