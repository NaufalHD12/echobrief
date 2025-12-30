from datetime import datetime
from typing import Annotated
from uuid import UUID

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, EmailStr, field_validator

from .validators import validate_password_strength


class UserBaseSchema(BaseModel):
    """Base schema with common fields"""

    email: EmailStr
    username: Annotated[str, MinLen(3), MaxLen(50)]


class UserBase(UserBaseSchema):
    """Inherits base user fields"""

    pass


class UserCreate(UserBase):
    """Schema for creating new user"""

    password: Annotated[str, MinLen(8), MaxLen(128)]

    _validate_password = field_validator("password")(validate_password_strength)


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response"""

    id: UUID
    role: str
    plan_type: str
    created_at: datetime
    last_login: datetime | None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "johndoe",
                "role": "user",
                "plan_type": "free",
                "created_at": "2025-01-15T10:30:00Z",
                "last_login": "2025-01-15T14:45:22Z",
            }
        }
    }


class UserUpdate(BaseModel):
    """Schema for updating user profile"""

    username: Annotated[str | None, MinLen(3), MaxLen(50)] = None
