import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.auth import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    exchange_code_for_token,
    get_google_auth_url,
    get_google_user_info,
    verify_token,
)
from ...core.database import get_session
from ...schemas.auth import (
    ForgotPasswordRequest,
    GoogleAuthURL,
    RefreshTokenRequest,
    ResetPasswordRequest,
    Token,
)
from ...schemas.common import ApiResponse
from ...schemas.users import UserCreate, UserLogin, UserResponse
from ...services.user_service import UserService
from ...tasks.email_tasks import send_password_reset_email_task

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


@router.get("/google", response_model=ApiResponse[GoogleAuthURL])
async def google_auth_url() -> ApiResponse[GoogleAuthURL]:
    """
    Get Google OAuth authorization URL for login.

    Returns a URL that redirects users to Google for authentication.
    Frontend should redirect users to this URL to start the OAuth flow.
    """
    try:
        auth_url = await get_google_auth_url()
        return ApiResponse(
            message="Google auth URL generated successfully",
            data=GoogleAuthURL(auth_url=auth_url),
        )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating Google auth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Google auth URL",
        )


@router.get("/google/callback", response_model=ApiResponse[Token])
async def google_auth_callback(
    code: str,
    state: str | None = None,
    error: str | None = None,
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[Token]:
    """
    Handle Google OAuth callback and authenticate/create user.

    Query parameters:
    - **code**: Authorization code received from Google OAuth redirect
    - **state**: Optional state parameter for CSRF protection
    - **error**: Error parameter if OAuth failed
    """
    try:
        # Check for OAuth errors
        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"OAuth error: {error}"
            )

        # Exchange code for token
        token_data = await exchange_code_for_token(code)

        # Get user info from Google
        user_info = await get_google_user_info(token_data["access_token"])

        # Get or create user
        user = await user_service.get_or_create_oauth_user(
            google_id=user_info["id"],
            email=user_info["email"],
            name=user_info["name"],
            picture_url=user_info.get("picture"),
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
            message="Google login successful",
            data=Token(access_token=access_token, refresh_token=refresh_token),
        )

    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error during Google OAuth callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication failed",
        )


@router.post("/forgot-password", response_model=ApiResponse[dict])
async def forgot_password(
    request: ForgotPasswordRequest,
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[dict]:
    """
    Request password reset.

    - **email**: User email address

    If the email exists, a password reset link will be sent.
    For security reasons, the response is the same regardless of whether the email exists.
    """
    try:
        # Check if user exists
        user = await user_service.get_user_by_email(request.email)

        if user:
            # Generate reset token
            reset_token = create_password_reset_token(user.id)

            # Send email asynchronously via Celery
            send_password_reset_email_task.delay(request.email, reset_token)

        # Always return the same response for security
        return ApiResponse(
            message="If an account with this email exists, a password reset link has been sent.",
            data={"email": request.email},
        )

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error during password reset request: {e}")
        # Don't reveal errors to prevent email enumeration
        return ApiResponse(
            message="If an account with this email exists, a password reset link has been sent.",
            data={"email": request.email},
        )


@router.post("/reset-password", response_model=ApiResponse[dict])
async def reset_password(
    request: ResetPasswordRequest,
    user_service: UserService = Depends(get_user_service),
) -> ApiResponse[dict]:
    """
    Reset password using token.

    - **token**: Password reset token from email
    - **new_password**: New password (min 8 characters)
    """
    try:
        # Verify token
        token_data = verify_token(request.token, "password_reset")
        if not token_data or not token_data.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        # Get user
        user = await user_service.get_user_by_id(token_data.user_id)

        # Update password directly
        from ...core.security import hash_password

        hashed_password = hash_password(request.new_password)

        user.password_hash = hashed_password
        await user_service.session.commit()

        return ApiResponse(
            message="Password has been reset successfully",
            data={"user_id": str(token_data.user_id)},
        )

    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error during password reset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed due to server error",
        )
