from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.auth import get_current_admin, get_current_user
from ...core.database import get_session
from ...models.users import User
from ...schemas.common import ApiResponse
from ...schemas.sources import (
    SourceCreate,
    SourceListResponse,
    SourceResponse,
    SourceUpdate,
)
from ...services.source_service import SourceService

router = APIRouter(prefix="/sources", tags=["sources"])


async def get_source_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SourceService:
    return SourceService(session)


@router.get(
    "/",
    response_model=ApiResponse[SourceListResponse],
    summary="Get list of sources",
    description="Retrieve paginated list of all sources with optional filtering",
)
async def get_sources(
    service: Annotated[SourceService, Depends(get_source_service)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
    current_user: User = Depends(get_current_user)
) -> ApiResponse[SourceListResponse]:
    """
    Get paginated list of sources.

    - **page**: Page number (starts from 1)
    - **per_page**: Number of items per page (max 100, default 10)
    """
    skip = (page - 1) * per_page
    sources, total = await service.get_sources(skip=skip, limit=per_page)

    return ApiResponse(
        message="Sources retrieved successfully",
        data=SourceListResponse(
            items=[SourceResponse(**source.model_dump()) for source in sources],
            total=total,
            page=page,
            per_page=per_page,
        ),
    )


@router.get(
    "/{source_id}",
    response_model=ApiResponse[SourceResponse],
    summary="Get source by ID",
    description="Retrieve a specific source by its ID",
)
async def get_source(
    source_id: Annotated[int, Path(description="Source ID")],
    service: Annotated[SourceService, Depends(get_source_service)],
    current_user: User = Depends(get_current_user)
) -> ApiResponse[SourceResponse]:
    """
    Get source by ID.

    - **source_id**: Unique identifier of the source
    """
    source = await service.get_source_by_id(source_id)
    return ApiResponse(
        message="Source retrieved successfully",
        data=SourceResponse(**source.model_dump()),
    )


@router.post(
    "/",
    response_model=ApiResponse[SourceResponse],
    status_code=201,
    summary="Create new source",
    description="Create a new news source (admin only)",
)
async def create_source(
    source_data: SourceCreate,
    service: Annotated[SourceService, Depends(get_source_service)],
    current_user: User = Depends(get_current_admin),
) -> ApiResponse[SourceResponse]:
    """
    Create a new source.

    - **name**: Source name (2-50 characters)
    - **base_url**: Base URL of the news source
    """
    source = await service.create_source(source_data)
    return ApiResponse(
        message="Source created successfully",
        data=SourceResponse(**source.model_dump()),
    )


@router.put(
    "/{source_id}",
    response_model=ApiResponse[SourceResponse],
    summary="Update source",
    description="Update an existing source's information (admin only)",
)
async def update_source(
    source_id: Annotated[int, Path(description="Source ID")],
    source_data: SourceUpdate,
    service: Annotated[SourceService, Depends(get_source_service)],
    current_user: User = Depends(get_current_admin),
) -> ApiResponse[SourceResponse]:
    """
    Update source information.

    - **source_id**: Unique identifier of the source to update
    - **name**: New source name (optional)
    - **base_url**: New base URL (optional)
    """
    source = await service.update_source(source_id, source_data)
    return ApiResponse(
        message="Source updated successfully",
        data=SourceResponse(**source.model_dump()),
    )


@router.delete(
    "/{source_id}",
    response_model=ApiResponse[None],
    summary="Delete source",
    description="Delete a source by its ID (admin only)",
)
async def delete_source(
    source_id: Annotated[int, Path(description="Source ID")],
    service: Annotated[SourceService, Depends(get_source_service)],
    current_user: User = Depends(get_current_admin),
) -> ApiResponse[None]:
    """
    Delete a source.

    - **source_id**: Unique identifier of the source to delete
    """
    await service.delete_source(source_id)
    return ApiResponse(message="Source deleted successfully")
