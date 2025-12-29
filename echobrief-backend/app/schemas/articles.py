from pydantic import BaseModel, field_validator
from typing import Annotated
from annotated_types import MinLen, MaxLen
from datetime import datetime

from .validators import validate_url, validate_url_optional, ensure_timezone_aware, ensure_timezone_aware_required
from .common import PaginatedResponse


class ArticleBaseSchema(BaseModel):
    """Base schema with common fields and validators"""
    title: Annotated[str, MinLen(1), MaxLen(500)]
    url: Annotated[str, MinLen(10), MaxLen(1000)]

    _validate_url = field_validator('url')(validate_url)
    

class ArticleBase(ArticleBaseSchema):
    source_id: int
    topic_id: int
    summary_text: str | None = None
    

class ArticleCreate(ArticleBaseSchema):
    """Schema for create new article"""
    source_id: int
    topic_id: int
    summary_text: str | None = None
    published_at: datetime | None = None
    # summary_text will be generate by AI
    # fetched_at auto-generated
    
    
class ArticleUpdate(BaseModel):
    """Schema for update article (All field are optional)"""
    title: Annotated[str | None, MinLen(1), MaxLen(500)] = None
    summary_text: str | None = None
    url: Annotated[str | None, MinLen(10), MaxLen(1000)] = None
    published_at: datetime | None = None

    _validate_url = field_validator('url')(validate_url_optional)
    _ensure_timezone = field_validator('published_at')(ensure_timezone_aware)
    

class ArticleResponse(ArticleBase):
    id: int
    published_at: datetime | None
    fetched_at: datetime

    _ensure_published_at_timezone = field_validator('published_at')(ensure_timezone_aware)
    _ensure_fetched_at_timezone = field_validator('fetched_at')(ensure_timezone_aware_required)

    model_config = {
        'json_schema_extra': {
            "example": {
                "id": 1,
                "source_id": 1,
                "topic_id": 2,
                "title": "AI Breakthrough in Healthcare",
                "summary_text": "Scientists developed new AI system that can detect diseases 3x faster...",
                "url": "https://example.com/ai-healthcare",
                "published_at": "2025-01-15T10:30:00Z",
                "fetched_at": "2025-01-15T14:45:22Z"
            }
        }
    }
    

class ArticleListResponse(PaginatedResponse[ArticleResponse]):
    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "source_id": 1,
                        "topic_id": 2,
                        "title": "AI Breakthrough",
                        "summary_text": "Summary...",
                        "url": "https://example.com/article1",
                        "published_at": "2025-01-15T10:30:00Z",
                        "fetched_at": "2025-01-15T14:45:22Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "per_page": 10
            }
        }
    }
