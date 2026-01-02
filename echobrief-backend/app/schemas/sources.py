from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel
from pydantic import Field as PydanticField
from pydantic import field_validator

from .common import PaginatedResponse
from .validators import validate_url, validate_url_optional


class SourceBaseSchema(BaseModel):
    """Base schema with common fields and validators"""

    name: Annotated[str, MinLen(2), MaxLen(50)]
    base_url: Annotated[str, MinLen(2), MaxLen(250)]

    _validate_url = field_validator("base_url")(validate_url)


class SourceBase(SourceBaseSchema):
    pass


class SourceCreate(SourceBase):
    """Schema for create new source"""

    pass


class SourceCreateBulk(BaseModel):
    """Schema for bulk create sources"""

    sources: list[SourceCreate]

    model_config = {
        "json_schema_extra": {
            "example": {
                "sources": [
                    {
                        "name": "CNN",
                        "base_url": "http://rss.cnn.com/rss/edition.rss"
                    },
                    {
                        "name": "BBC News",
                        "base_url": "http://feeds.bbci.co.uk/news/rss.xml"
                    }
                ]
            }
        }
    }


class SourceUpdate(BaseModel):
    """Schema for update source (All field are optional)"""

    name: Annotated[str | None, MinLen(2), MaxLen(50)] = None
    base_url: Annotated[str | None, MinLen(2), MaxLen(250)] = None

    _validate_url = field_validator("base_url")(validate_url_optional)


class SourceResponse(SourceBase):
    """Schema response for source"""

    id: Annotated[int, PydanticField(description="Unique source identifier")]
    is_active: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "CNN",
                "base_url": "http://rss.cnn.com/rss/edition.rss",
                "is_active": True,
            }
        }
    }


class SourceListResponse(PaginatedResponse[SourceResponse]):
    """Schema for list of source with pagination"""

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "name": "CNN",
                        "base_url": "http://rss.cnn.com/rss/edition.rss",
                        "is_active": True,
                    },
                    {
                        "id": 2,
                        "name": "Google News",
                        "base_url": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
                        "is_active": True,
                    },
                ],
                "total": 2,
                "page": 1,
                "per_page": 10,
            }
        }
    }
