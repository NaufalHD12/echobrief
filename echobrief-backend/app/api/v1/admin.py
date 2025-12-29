from fastapi import APIRouter, Depends
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
from ...core.database import get_session
from ...services.news_aggregation_service import NewsAggregationService

router = APIRouter(prefix="/admin", tags=["admin"])

async def get_news_aggregation_service(session: Annotated[AsyncSession, Depends(get_session)]) -> NewsAggregationService:
    return NewsAggregationService(session)

@router.post("/aggregate-news")
async def aggregate_news(service: NewsAggregationService = Depends(get_news_aggregation_service)):
    result = await service.aggregate_news()
    return result
