from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.auth import get_current_admin
from ...core.database import get_session
from ...models.users import User
from ...schemas.common import ApiResponse
from ...services.news_aggregation_service import NewsAggregationService

router = APIRouter(prefix="/system", tags=["system"])


async def get_news_aggregation_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NewsAggregationService:
    return NewsAggregationService(session)


@router.post("/aggregate-news", response_model=ApiResponse[dict])
async def aggregate_news(
    current_user: User = Depends(get_current_admin),
    service: NewsAggregationService = Depends(get_news_aggregation_service),
):
    """Trigger news aggregation (system operation - admin only)"""
    result = await service.aggregate_news()
    return ApiResponse(message="News aggregation completed", data=result)
