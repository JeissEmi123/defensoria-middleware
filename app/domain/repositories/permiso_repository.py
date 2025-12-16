from abc import abstractmethod
from typing import Optional, List

from app.database.models import Permiso
from .base_repository import IBaseRepository


class IPermisoRepository(IBaseRepository[Permiso]):
    
    @abstractmethod
    async def find_by_codigo(self, codigo: str) -> Optional[Permiso]:
        pass
    @abstractmethod
    async def find_by_recurso(self, recurso: str) -> List[Permiso]:
        pass
    @abstractmethod
    async def find_by_recurso_accion(self, recurso: str, accion: str) -> Optional[Permiso]:
        pass
    @abstractmethod
    async def get_user_permisos(self, usuario_id: int) -> List[Permiso]:
        pass
    @abstractmethod
    async def get_rol_permisos(self, rol_id: int) -> List[Permiso]:
        pass
    @abstractmethod
    async def user_has_permiso(self, usuario_id: int, codigo_permiso: str) -> bool:
        pass
    @abstractmethod
    async def get_all_recursos(self) -> List[str]:
        pass
    @abstractmethod
    async def get_all_acciones(self) -> List[str]:
        pass
    @abstractmethod
    async def is_codigo_taken(self, codigo: str, exclude_id: Optional[int] = None) -> bool:
        pass
