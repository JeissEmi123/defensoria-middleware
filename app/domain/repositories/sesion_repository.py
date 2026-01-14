from abc import abstractmethod
from typing import Optional, List
from datetime import datetime

from app.database.models import Sesion
from .base_repository import IBaseRepository


class ISesionRepository(IBaseRepository[Sesion]):
    
    @abstractmethod
    async def find_by_access_token(self, token: str) -> Optional[Sesion]:
        pass
    @abstractmethod
    async def find_by_refresh_token(self, token: str) -> Optional[Sesion]:
        pass
    @abstractmethod
    async def find_by_jti(self, jti: str) -> Optional[Sesion]:
        pass
    @abstractmethod
    async def get_user_sessions(self, usuario_id: int, only_valid: bool = True) -> List[Sesion]:
        pass
    @abstractmethod
    async def get_active_sessions(self, usuario_id: int) -> List[Sesion]:
        pass
    @abstractmethod
    async def invalidate_session(self, sesion_id: int) -> bool:
        pass
    @abstractmethod
    async def invalidate_user_sessions(self, usuario_id: int, except_session_id: Optional[int] = None) -> int:
        pass
    @abstractmethod
    async def invalidate_by_token(self, token: str) -> bool:
        pass
    @abstractmethod
    async def cleanup_expired_sessions(self) -> int:
        pass
    @abstractmethod
    async def update_refresh_token(self, sesion_id: int, new_refresh_token: str, new_expiry: datetime) -> bool:
        pass
    @abstractmethod
    async def count_active_sessions(self, usuario_id: int) -> int:
        pass
    @abstractmethod
    async def is_token_valid(self, token: str) -> bool:
        pass
