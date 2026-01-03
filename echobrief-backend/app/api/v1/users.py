import os
import tempfile
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.auth import get_current_user
from ...core.database import get_session
from ...models.users import User
from ...schemas.common import ApiResponse
from ...schemas.topics import TopicResponse
from ...schemas.users import OnboardingResponse, UserResponse, UserUpdate
from ...services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    return UserService(session)


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[UserResponse]:
    """
    Get current user profile.

    Returns user information including email, username, role, plan_type, avatar, and timestamps.
    """
    avatar_url = await user_service.get_user_avatar_url(current_user.id)
    user_data = current_user.model_dump()
    user_data["avatar_url"] = avatar_url

    return ApiResponse(
        message="Profile retrieved successfully",
        data=UserResponse(**user_data),
    )


@router.put("/me", response_model=ApiResponse[UserResponse])
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[UserResponse]:
    """
    Update current user profile.

    - **username**: New username (3-50 characters)

    Note: Regular users can only update their username.
    """
    updated_user = await user_service.update_user_profile(current_user.id, user_data)
    avatar_url = await user_service.get_user_avatar_url(updated_user.id)
    user_data_dict = updated_user.model_dump()
    user_data_dict["avatar_url"] = avatar_url

    return ApiResponse(
        message="Profile updated successfully",
        data=UserResponse(**user_data_dict),
    )


@router.post("/onboarding", response_model=ApiResponse[OnboardingResponse])
async def complete_user_onboarding(
    plan_type: str,
    topic_ids: str,  # Comma-separated string of topic IDs (e.g., "1,2,3")
    avatar: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[OnboardingResponse]:
    """
    Complete user onboarding process.

    - **plan_type**: Plan type selection ("free" or "paid")
    - **topic_ids**: Comma-separated string of topic IDs (e.g., "1,2,3")
    - **avatar**: Optional avatar image file

    This endpoint handles avatar upload, plan selection, and favorite topic setup in one request.
    """
    # Parse topic_ids from comma-separated string
    try:
        if topic_ids.strip():
            parsed_topic_ids = [
                int(x.strip()) for x in topic_ids.split(",") if x.strip()
            ]
        else:
            parsed_topic_ids = []
    except ValueError:
        raise HTTPException(
            status_code=400, detail="topic_ids must be comma-separated integers"
        )

    # Handle avatar upload if provided
    avatar_file_path = None
    if avatar:
        # Validate file type
        allowed_types = [
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/gif",
            "image/webp",
        ]
        if avatar.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Unsupported avatar file type")

        # Save temporarily
        filename = avatar.filename or "avatar.jpg"
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f"_{filename}"
        ) as temp_file:
            temp_file.write(await avatar.read())
            avatar_file_path = temp_file.name

    try:
        # Complete onboarding
        result = await user_service.complete_onboarding(
            current_user.id, plan_type, parsed_topic_ids, avatar_file_path
        )

        return ApiResponse(
            message="Onboarding completed successfully",
            data=OnboardingResponse(**result),
        )
    finally:
        # Clean up temp file
        if avatar_file_path and os.path.exists(avatar_file_path):
            os.unlink(avatar_file_path)


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


@router.post("/me/avatar", response_model=ApiResponse[dict])
async def upload_current_user_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[dict]:
    """
    Upload avatar for current user.

    - **file**: Image file (JPG, PNG, GIF, WebP, max 5MB)

    Supported formats: JPG, PNG, GIF, WebP
    Maximum file size: 5MB
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    filename = file.filename or "upload.jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name

    try:
        # Upload avatar
        avatar_url = await user_service.upload_user_avatar(
            current_user.id, temp_path, filename
        )

        return ApiResponse(
            message="Avatar uploaded successfully",
            data={"avatar_url": avatar_url},
        )
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@router.delete("/me/avatar", response_model=ApiResponse[dict])
async def delete_current_user_avatar(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[dict]:
    """
    Delete current user's avatar (reset to default).

    This will remove the uploaded avatar and reset to the default generated avatar.
    """
    await user_service.delete_user_avatar(current_user.id)

    # Get new default avatar URL
    avatar_url = await user_service.get_user_avatar_url(current_user.id)

    return ApiResponse(
        message="Avatar deleted successfully, reset to default",
        data={"avatar_url": avatar_url},
    )


@router.get("/{user_id}/avatar", response_model=ApiResponse[dict])
async def get_user_avatar(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[dict]:
    """
    Get user avatar URL by user ID.

    - **user_id**: UUID of the user

    Returns avatar URL for the specified user.
    """
    avatar_url = await user_service.get_user_avatar_url(user_id)
    return ApiResponse(
        message="Avatar URL retrieved successfully",
        data={"avatar_url": avatar_url},
    )
