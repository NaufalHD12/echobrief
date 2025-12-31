from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from ..models.podcasts import PodcastStatus
from .articles import ArticleResponse
from .topics import TopicResponse


class PodcastBase(BaseModel):
    """Base podcast schema"""

    pass


class PodcastCreate(BaseModel):
    """Schema for creating podcast request"""

    topic_ids: list[int] | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "topic_ids": [1, 2, 3]  # Optional, jika tidak diisi pakai favorite topics
            }
        }
    }


class PodcastQuickCreate(BaseModel):
    """Schema for quick podcast generation (hybrid approach)"""
    
    use_cached: bool = True  # Default true untuk hybrid approach
    custom_topic_ids: list[int] | None = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "use_cached": True,
                "custom_topic_ids": None
            }
        }
    }


class PodcastResponse(PodcastBase):
    """Schema for podcast response"""

    id: UUID
    user_id: UUID
    generated_script: str | None
    audio_url: str | None
    duration_seconds: int | None
    status: PodcastStatus
    created_at: datetime
    topics: list[TopicResponse]
    articles: list[ArticleResponse]
    segments: list["PodcastSegmentResponse"]

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "generated_script": "Welcome to today's podcast...",
                "audio_url": "https://storage.example.com/podcast.mp3",
                "duration_seconds": 300,
                "status": "completed",
                "created_at": "2025-01-15T10:30:00Z",
                "topics": [],
                "articles": [],
                "segments": [],
            }
        }
    }


class PodcastListResponse(BaseModel):
    """Schema for paginated podcast list"""

    items: list[PodcastResponse]
    total: int
    page: int
    per_page: int


class PodcastSegmentResponse(BaseModel):
    """Schema for podcast segment response"""

    id: UUID
    podcast_id: UUID
    title: str
    start_second: int
    end_second: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "podcast_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Introduction",
                "start_second": 0,
                "end_second": 30,
            }
        }
    }


class PodcastJobResponse(BaseModel):
    """Schema for podcast job response"""

    id: UUID
    podcast_id: UUID
    step_name: str
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "podcast_id": "550e8400-e29b-41d4-a716-446655440000",
                "step_name": "script_generation",
                "status": "completed",
                "error_message": None,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:35:00Z",
            }
        }
    }
