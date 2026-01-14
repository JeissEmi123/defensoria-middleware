from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Usuario, Rol, Permiso
from app.domain.repositories.usuario_repository import IUsuarioRepository
from .sqlalchemy_base_repository import SQLAlchemyBaseRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class SQLAlchemyUsuarioRepository(SQLAlchemyBaseRepository[Usuario], IUsuarioRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Usuario)
    
    async def find_by_username(self, nombre_usuario: str) -> Optional[Usuario]:
        result = await self.db.execute(
            select(Usuario).where(Usuario.nombre_usuario == nombre_usuario)
        )
        return result.scalar_one_or_none()
    async def find_by_email(self, email: str) -> Optional[Usuario]:
        result = await self.db.execute(
            select(Usuario).where(Usuario.email == email)
        )
        return result.scalar_one_or_none()
    async def find_by_external_id(self, id_externo: str, tipo_autenticacion: str) -> Optional[Usuario]:
        result = await self.db.execute(
            select(Usuario).where(
                and_(
                    Usuario.id_externo == id_externo,
                    Usuario.tipo_autenticacion == tipo_autenticacion
                )
            )
        )
        return result.scalar_one_or_none()
    async def get_with_roles(self, usuario_id: int) -> Optional[Usuario]:
        result = await self.db.execute(
            select(Usuario)
            .options(selectinload(Usuario.roles))
            .where(Usuario.id == usuario_id)
        )
        return result.scalar_one_or_none()
    async def get_with_roles_and_permisos(self, usuario_id: int) -> Optional[Usuario]:
        result = await self.db.execute(
            select(Usuario)
            .options(
                selectinload(Usuario.roles).selectinload(Rol.permisos)
            )
            .where(Usuario.id == usuario_id)
        )
        return result.scalar_one_or_none()
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[Usuario]:
        result = await self.db.execute(
            select(Usuario)
            .where(Usuario.activo == True)
            .offset(skip)
            .limit(limit)
            .order_by(Usuario.nombre_usuario)
        )
        return list(result.scalars().all())
    async def update_last_login(self, usuario_id: int, fecha: datetime, ip: Optional[str] = None) -> bool:
        usuario = await self.get_by_id(usuario_id)
        if not usuario:
            return False
        usuario.ultimo_acceso = fecha
        if ip:
            usuario.ultima_ip = ip
        
        await self.db.flush()
        return True
    
    async def increment_failed_login(self, usuario_id: int) -> int:
        usuario = await self.get_by_id(usuario_id)
        if not usuario:
            return 0
        usuario.intentos_login_fallidos += 1
        await self.db.flush()
        return usuario.intentos_login_fallidos
    
    async def reset_failed_login(self, usuario_id: int) -> bool:
        usuario = await self.get_by_id(usuario_id)
        if not usuario:
            return False
        usuario.intentos_login_fallidos = 0
        usuario.fecha_bloqueo = None
        await self.db.flush()
        return True
    
    async def block_user(self, usuario_id: int, fecha_bloqueo: datetime) -> bool:
        usuario = await self.get_by_id(usuario_id)
        if not usuario:
            return False
        usuario.fecha_bloqueo = fecha_bloqueo
        await self.db.flush()
        logger.warning(f"Usuario bloqueado: {usuario.nombre_usuario} (ID: {usuario_id})")
        return True
    
    async def unblock_user(self, usuario_id: int) -> bool:
        usuario = await self.get_by_id(usuario_id)
        if not usuario:
            return False
        usuario.fecha_bloqueo = None
        usuario.intentos_login_fallidos = 0
        await self.db.flush()
        logger.info(f"Usuario desbloqueado: {usuario.nombre_usuario} (ID: {usuario_id})")
        return True
    
    async def is_username_taken(self, nombre_usuario: str, exclude_id: Optional[int] = None) -> bool:
        query = select(func.count()).select_from(Usuario).where(
            Usuario.nombre_usuario == nombre_usuario
        )
        if exclude_id:
            query = query.where(Usuario.id != exclude_id)
        
        result = await self.db.execute(query)
        count = result.scalar()
        return count > 0
    
    async def is_email_taken(self, email: str, exclude_id: Optional[int] = None) -> bool:
        query = select(func.count()).select_from(Usuario).where(
            Usuario.email == email
        )
        if exclude_id:
            query = query.where(Usuario.id != exclude_id)
        
        result = await self.db.execute(query)
        count = result.scalar()
        return count > 0
