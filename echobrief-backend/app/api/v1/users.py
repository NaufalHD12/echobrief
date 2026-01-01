from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
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
    """
    Get current user profile.

    Returns user information including email, username, role, plan_type, and timestamps.
    """
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
    """
    Update current user profile.

    - **username**: New username (optional, 3-50 characters)
    - **plan_type**: Cannot be updated by regular users (admin only)
    - **role**: Cannot be updated by regular users (admin only)

    Note: Regular users can only update their username.
    """
    updated_user = await user_service.update_user(
        current_user.id, user_data, current_user
    )
    return ApiResponse(
        message="Profile updated successfully",
        data=UserResponse(**updated_user.model_dump()),
    )


@router.get("/", response_model=ApiResponse[list[UserResponse]])
async def get_users(
    current_user: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[list[UserResponse]]:
    """
    Get all users (admin only).

    Returns list of all users in the system with their profile information.
    Requires admin privileges.
    """
    users = await user_service.get_all_users()
    return ApiResponse(
        message="Users retrieved successfully",
        data=[UserResponse(**user.model_dump()) for user in users],
    )


@router.put("/{user_id}", response_model=ApiResponse[UserResponse])
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
    from uuid import UUID

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    updated_user = await user_service.update_user(user_uuid, user_data, current_admin)
    return ApiResponse(
        message="User updated successfully",
        data=UserResponse(**updated_user.model_dump()),
    )


@router.post("/topics", response_model=ApiResponse[dict])
async def add_user_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[dict]:
    """
    Add topic to current user's selection.

    - **topic_id**: Topic ID to add to user's favorites

    Note: Free users are limited to 3 favorite topics.
    """
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
    """
    Remove topic from current user's selection.

    - **topic_id**: Topic ID to remove from user's favorites
    """
    await user_service.remove_user_topic(current_user.id, topic_id)
    return ApiResponse(
        message="Topic removed from selection",
        data={"topic_id": topic_id},
    )


@router.get("/topics", response_model=ApiResponse[list[TopicResponse]])
async def get_user_topics(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[list[TopicResponse]]:
    """
    Get current user's selected topics.

    Returns list of topics that the user has selected as favorites.
    """
    topics = await user_service.get_user_topics(current_user.id)
    return ApiResponse(
        message="Topics retrieved successfully",
        data=[TopicResponse(**topic.model_dump()) for topic in topics],
    )
