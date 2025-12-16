from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_, update, delete as sql_delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Sesion
from app.domain.repositories.sesion_repository import ISesionRepository
from .sqlalchemy_base_repository import SQLAlchemyBaseRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class SQLAlchemySesionRepository(SQLAlchemyBaseRepository[Sesion], ISesionRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Sesion)
    
    async def find_by_access_token(self, token: str) -> Optional[Sesion]:
        result = await self.db.execute(
            select(Sesion).where(Sesion.token_acceso == token)
        )
        return result.scalar_one_or_none()
    async def find_by_refresh_token(self, token: str) -> Optional[Sesion]:
        result = await self.db.execute(
            select(Sesion).where(Sesion.token_refresco == token)
        )
        return result.scalar_one_or_none()
    async def find_by_jti(self, jti: str) -> Optional[Sesion]:
        result = await self.db.execute(
            select(Sesion).where(Sesion.jti == jti)
        )
        return result.scalar_one_or_none()
    async def get_user_sessions(self, usuario_id: int, only_valid: bool = True) -> List[Sesion]:
        query = select(Sesion).where(Sesion.usuario_id == usuario_id)
        if only_valid:
            query = query.where(Sesion.valida == True)
        
        query = query.order_by(Sesion.fecha_creacion.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_active_sessions(self, usuario_id: int) -> List[Sesion]:
        now = datetime.now()
        result = await self.db.execute(
            select(Sesion).where(
                and_(
                    Sesion.usuario_id == usuario_id,
                    Sesion.valida == True,
                    Sesion.fecha_expiracion_refresco > now
                )
            ).order_by(Sesion.fecha_creacion.desc())
        )
        return list(result.scalars().all())
    async def invalidate_session(self, sesion_id: int) -> bool:
        result = await self.db.execute(
            update(Sesion)
            .where(Sesion.id == sesion_id)
            .values(valida=False)
        )
        await self.db.flush()
        if result.rowcount > 0:
            logger.info(f"Sesión invalidada: ID {sesion_id}")
            return True
        return False
    
    async def invalidate_user_sessions(self, usuario_id: int, except_session_id: Optional[int] = None) -> int:
        query = update(Sesion).where(Sesion.usuario_id == usuario_id)
        if except_session_id:
            query = query.where(Sesion.id != except_session_id)
        
        query = query.values(valida=False)
        result = await self.db.execute(query)
        await self.db.flush()
        
        count = result.rowcount
        logger.info(f"Sesiones invalidadas del usuario {usuario_id}: {count}")
        return count
    
    async def invalidate_by_token(self, token: str) -> bool:
        result = await self.db.execute(
            update(Sesion)
            .where(
                and_(
                    Sesion.access_token == token,
                    Sesion.valida == True
                )
            )
            .values(valida=False)
        )
        await self.db.flush()
        return result.rowcount > 0
    async def cleanup_expired_sessions(self) -> int:
        now = datetime.now()
        # Eliminar sesiones con refresh token expirado
        result = await self.db.execute(
            sql_delete(Sesion).where(Sesion.fecha_expiracion_refresco < now)
        )
        await self.db.flush()
        
        count = result.rowcount
        if count > 0:
            logger.info(f"Sesiones expiradas limpiadas: {count}")
        
        return count
    
    async def update_refresh_token(self, sesion_id: int, new_refresh_token: str, new_expiry: datetime) -> bool:
        result = await self.db.execute(
            update(Sesion)
            .where(Sesion.id == sesion_id)
            .values(
                token_refresco=new_refresh_token,
                fecha_expiracion_refresco=new_expiry
            )
        )
        await self.db.flush()
        return result.rowcount > 0
    async def count_active_sessions(self, usuario_id: int) -> int:
        now = datetime.now()
        result = await self.db.execute(
            select(func.count())
            .select_from(Sesion)
            .where(
                and_(
                    Sesion.usuario_id == usuario_id,
                    Sesion.valida == True,
                    Sesion.fecha_expiracion_refresco > now
                )
            )
        )
        return result.scalar()
    async def is_token_valid(self, token: str) -> bool:
        now = datetime.now()
        result = await self.db.execute(
            select(func.count())
            .select_from(Sesion)
            .where(
                and_(
                    Sesion.access_token == token,
                    Sesion.valida == True,
                    Sesion.fecha_expiracion > now
                )
            )
        )
        count = result.scalar()
        return count > 0
