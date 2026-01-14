from abc import abstractmethod
from typing import Optional, List

from app.database.models import Rol
from .base_repository import IBaseRepository


class IRolRepository(IBaseRepository[Rol]):
    
    @abstractmethod
    async def find_by_name(self, nombre: str) -> Optional[Rol]:
        pass
    @abstractmethod
    async def get_with_permisos(self, rol_id: int) -> Optional[Rol]:
        pass
    @abstractmethod
    async def get_active_roles(self, skip: int = 0, limit: int = 100) -> List[Rol]:
        pass
    @abstractmethod
    async def get_system_roles(self) -> List[Rol]:
        pass
    @abstractmethod
    async def get_user_roles(self, usuario_id: int) -> List[Rol]:
        pass
    @abstractmethod
    async def assign_permisos(self, rol_id: int, permiso_ids: List[int]) -> bool:
        pass
    @abstractmethod
    async def remove_permisos(self, rol_id: int, permiso_ids: List[int]) -> bool:
        pass
    @abstractmethod
    async def clear_permisos(self, rol_id: int) -> bool:
        pass
    @abstractmethod
    async def is_name_taken(self, nombre: str, exclude_id: Optional[int] = None) -> bool:
        pass
    @abstractmethod
    async def is_system_role(self, rol_id: int) -> bool:
        pass
