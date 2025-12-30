from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Generic API response with message and data"""

    message: str
    data: T | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""

    items: list[T]
    total: int
    page: int
    per_page: int
