from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any, Dict

T = TypeVar('T')


class IBaseRepository(ABC, Generic[T]):
    
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        pass
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100, **filters) -> List[T]:
        pass
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass
    @abstractmethod
    async def update(self, entity: T) -> T:
        pass
    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass
    @abstractmethod
    async def exists(self, id: int) -> bool:
        pass
    @abstractmethod
    async def count(self, **filters) -> int:
        pass
