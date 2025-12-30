from typing import Annotated
from uuid import UUID

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel


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
