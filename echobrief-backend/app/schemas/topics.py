from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel
from pydantic import Field as PydanticField

from .common import PaginatedResponse


class TopicBaseSchema(BaseModel):
    """Base schema with common fields"""

    name: Annotated[str, MinLen(2), MaxLen(50)]
    slug: Annotated[str, MinLen(2), MaxLen(50)]


class TopicBase(TopicBaseSchema):
    pass


class TopicCreate(TopicBase):
    """Schema for create new topic"""

    slug: str | None = PydanticField(None, min_length=2, max_length=50)


class TopicCreateBulk(BaseModel):
    """Schema for bulk create topics"""

    topics: list[TopicCreate]

    model_config = {
        "json_schema_extra": {
            "example": {
                "topics": [
                    {
                        "name": "Technology",
                        "slug": "technology"
                    },
                    {
                        "name": "Science",
                        "slug": "science"
                    }
                ]
            }
        }
    }


class TopicUpdate(BaseModel):
    """Schema for update topic (All field are optional)"""

    name: Annotated[str | None, MinLen(2), MaxLen(50)] = None
    slug: Annotated[str | None, MinLen(2), MaxLen(50)] = None


class TopicResponse(TopicBase):
    """Schema response for topic"""

    id: Annotated[int, PydanticField(description="Unique topic identifier")]

    model_config = {
        "json_schema_extra": {
            "example": {"id": 1, "name": "Technology", "slug": "technology"}
        }
    }


class TopicListResponse(PaginatedResponse[TopicResponse]):
    """Schema for list of topic with pagination"""

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {"id": 1, "name": "Technology", "slug": "technology"},
                    {"id": 2, "name": "Science", "slug": "science"},
                ],
                "total": 2,
                "page": 1,
                "per_page": 10,
            }
        }
    }
