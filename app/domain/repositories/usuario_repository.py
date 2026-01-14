from abc import abstractmethod
from typing import Optional, List
from datetime import datetime

from app.database.models import Usuario
from .base_repository import IBaseRepository


class IUsuarioRepository(IBaseRepository[Usuario]):
    
    @abstractmethod
    async def find_by_username(self, nombre_usuario: str) -> Optional[Usuario]:
        pass
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[Usuario]:
        pass
    @abstractmethod
    async def find_by_external_id(self, id_externo: str, tipo_autenticacion: str) -> Optional[Usuario]:
        pass
    @abstractmethod
    async def get_with_roles(self, usuario_id: int) -> Optional[Usuario]:
        pass
    @abstractmethod
    async def get_with_roles_and_permisos(self, usuario_id: int) -> Optional[Usuario]:
        pass
    @abstractmethod
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[Usuario]:
        pass
    @abstractmethod
    async def update_last_login(self, usuario_id: int, fecha: datetime, ip: Optional[str] = None) -> bool:
        pass
    @abstractmethod
    async def increment_failed_login(self, usuario_id: int) -> int:
        pass
    @abstractmethod
    async def reset_failed_login(self, usuario_id: int) -> bool:
        pass
    @abstractmethod
    async def block_user(self, usuario_id: int, fecha_bloqueo: datetime) -> bool:
        pass
    @abstractmethod
    async def unblock_user(self, usuario_id: int) -> bool:
        pass
    @abstractmethod
    async def is_username_taken(self, nombre_usuario: str, exclude_id: Optional[int] = None) -> bool:
        pass
    @abstractmethod
    async def is_email_taken(self, email: str, exclude_id: Optional[int] = None) -> bool:
        pass
