from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.database import get_session
from ...services.news_aggregation_service import NewsAggregationService

router = APIRouter(prefix="/system", tags=["system"])


async def get_news_aggregation_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NewsAggregationService:
    return NewsAggregationService(session)
