import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from ...core.database import get_session
from ...schemas.auth import RefreshTokenRequest, Token
from ...schemas.common import ApiResponse
from ...schemas.users import UserCreate, UserLogin, UserResponse
from ...services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["authentication"])


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    return UserService(session)


@router.post("/register", response_model=ApiResponse[UserResponse])
async def register(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[UserResponse]:
    """
    Register new user.
    
    - **email**: User email (must be valid email format)
    - **username**: Username (3-50 characters)
    - **password**: Password (min 8 characters, must contain uppercase, lowercase, number, and special character)
    """
    try:
        user = await user_service.create_user(user_data)
        return ApiResponse(
            message="User registered successfully",
            data=UserResponse(**user.model_dump()),
        )
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error",
        )


@router.post("/login", response_model=ApiResponse[Token])
async def login(
    user_data: UserLogin,
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[Token]:
    """Login user and return access & refresh token"""
    user = await user_service.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    await user_service.update_last_login(user.id)

    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=15),
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return ApiResponse(
        message="Login successful",
        data=Token(access_token=access_token, refresh_token=refresh_token),
    )


@router.post("/refresh", response_model=ApiResponse[Token])
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[Token]:
    """Refresh access token using refresh token"""
    # Verify refresh token
    token_data = verify_token(refresh_request.refresh_token, "refresh")
    if not token_data or not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # Get user
    user = await user_service.get_user_by_id(token_data.user_id)

    # Create new tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=15),
    )
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return ApiResponse(
        message="Token refreshed successfully",
        data=Token(access_token=access_token, refresh_token=new_refresh_token),
    )
