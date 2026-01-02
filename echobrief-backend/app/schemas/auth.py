from typing import Annotated
from uuid import UUID

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token response containing access and refresh tokens"""

    access_token: Annotated[str, MinLen(10), MaxLen(1000)]
    refresh_token: Annotated[str, MinLen(10), MaxLen(1000)]
    token_type: str = "bearer"

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    }


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token"""

    refresh_token: Annotated[str, MinLen(10), MaxLen(1000)]


class TokenData(BaseModel):
    """Data extracted from JWT token"""

    user_id: UUID | None = None


class GoogleAuthURL(BaseModel):
    """Response containing Google OAuth authorization URL"""

    auth_url: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "auth_url": "https://accounts.google.com/o/oauth2/auth?client_id=...",
            }
        }
    }


class OAuthCallback(BaseModel):
    """Request schema for OAuth callback"""

    code: Annotated[str, MinLen(10), MaxLen(1000)] = Field(description="Authorization code from Google")
    state: str | None = Field(default=None, description="State parameter for CSRF protection")
