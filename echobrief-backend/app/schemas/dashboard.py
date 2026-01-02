from pydantic import BaseModel

from .articles import ArticleResponse
from .common import PaginatedResponse
from .podcasts import PodcastResponse
from .topics import TopicResponse
from .users import UserResponse


class DashboardStats(BaseModel):
    """Dashboard statistics for user"""

    total_podcasts: int
    completed_podcasts: int
    total_topics: int
    plan_type: str
    member_since: str


class GlobalSearchResult(BaseModel):
    """Individual search result item"""

    type: str  # "article", "topic", "source"
    id: int
    title: str
    description: str | None = None
    url: str | None = None


class GlobalSearchResponse(PaginatedResponse[GlobalSearchResult]):
    """Response for global search results"""

    pass


class DashboardResponse(BaseModel):
    """Complete dashboard response"""

    user: UserResponse
    stats: DashboardStats
    recent_podcasts: list[PodcastResponse]
    recent_articles: list[ArticleResponse]
    favorite_topics: list[TopicResponse]

    model_config = {
        "json_schema_extra": {
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "username": "johndoe",
                    "role": "user",
                    "plan_type": "free",
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_login": "2024-01-15T10:30:00Z"
                },
                "stats": {
                    "total_podcasts": 5,
                    "completed_podcasts": 4,
                    "total_topics": 3,
                    "plan_type": "free",
                    "member_since": "2024-01-01"
                },
                "recent_podcasts": [],
                "recent_articles": [],
                "favorite_topics": []
            }
        }
    }
