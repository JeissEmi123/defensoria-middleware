from typing import TypeVar, Generic, Optional, List, Any, Dict, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete as sql_delete
from sqlalchemy.orm import selectinload

from app.domain.repositories.base_repository import IBaseRepository
from app.core.logging import get_logger

T = TypeVar('T')
logger = get_logger(__name__)


class SQLAlchemyBaseRepository(IBaseRepository[T], Generic[T]):
    
    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.model = model
    
    async def get_by_id(self, id: int) -> Optional[T]:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    async def get_all(self, skip: int = 0, limit: int = 100, **filters) -> List[T]:
        query = select(self.model)
        # Aplicar filtros dinámicamente
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def create(self, entity: T) -> T:
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity
    async def update(self, entity: T) -> T:
        await self.db.flush()
        await self.db.refresh(entity)
        return entity
    async def delete(self, id: int) -> bool:
        result = await self.db.execute(
            sql_delete(self.model).where(self.model.id == id)
        )
        await self.db.flush()
        return result.rowcount > 0
    async def exists(self, id: int) -> bool:
        result = await self.db.execute(
            select(func.count()).select_from(self.model).where(self.model.id == id)
        )
        count = result.scalar()
        return count > 0
    async def count(self, **filters) -> int:
        query = select(func.count()).select_from(self.model)
        # Aplicar filtros
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.execute(query)
        return result.scalar()
