from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Sequence
from fastapi import HTTPException
from ..models.sources import Source
from ..schemas.sources import SourceCreate, SourceUpdate

class SourceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_sources(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[Sequence[Source], int]:
        """Get paginated list of sources"""
        query = select(Source).offset(skip).limit(limit)
        result = await self.session.exec(query)
        sources = result.all()
        
        # Get total count
        count_query = select(func.count()).select_from(Source)
        total_result = await self.session.exec(count_query)
        total = total_result.one()
        
        return sources, total
    
    async def get_source_by_id(self, source_id: int) -> Source:
        """Get source by ID"""
        source = await self.session.get(Source, source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        return source
    
    async def get_active_sources(self) -> Sequence[Source]:
        """Get active sources"""
        query = select(Source).where(Source.is_active)
        result = await self.session.exec(query)
        return result.all()
    
    async def create_source(self, source_data: SourceCreate) -> Source:
        """Create new source"""
        # Check if source already exists
        source_name = source_data.name
        existing_query = select(Source).where(func.lower(Source.name) == source_name.lower())
        existing_result = await self.session.exec(existing_query)
        existing = existing_result.first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Source with '{source_name}' already exists")
        
        source = Source(**source_data.model_dump())
        self.session.add(source)
        await self.session.commit()
        await self.session.refresh(source)
        return source
    
    async def update_source(self, source_id: int, source_data: SourceUpdate) -> Source:
        """Update existing source"""
        source = await self.get_source_by_id(source_id)
        
        update_data = source_data.model_dump(exclude_unset=True)
        if "name" in update_data:
            existing_query = select(Source).where(
                func.lower(Source.name) == update_data["name"].lower(),
                Source.id != source_id
            )
            existing_result = await self.session.exec(existing_query)
            existing = existing_result.first()
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Source with '{update_data['name']}' already exists"
                )
        source.sqlmodel_update(update_data)
        self.session.add(source)
        await self.session.commit()
        await self.session.refresh(source)
        return source
    
    async def delete_source(self, source_id: int) -> None:
        """Delete source"""
        source = await self.get_source_by_id(source_id)
        await self.session.delete(source)
        await self.session.commit()