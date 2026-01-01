from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.config import settings
from ..core.database import get_session
from ..models.users import User, UserRole
from ..schemas.auth import TokenData
from ..services.user_service import UserService

security = HTTPBearer()


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> TokenData | None:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_type_in_payload = payload.get("type")
        if token_type_in_payload != token_type:
            return None
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return TokenData(user_id=UUID(user_id))
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    token_data = verify_token(token, "access")
    if not token_data or not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_service = UserService(session)
    user = await user_service.get_user_by_id(token_data.user_id)
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify admin role"""
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
