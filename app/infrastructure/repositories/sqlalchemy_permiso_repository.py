from typing import Optional, List
from sqlalchemy import select, and_, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Permiso, Rol, Usuario, usuarios_roles, roles_permisos
from app.domain.repositories.permiso_repository import IPermisoRepository
from .sqlalchemy_base_repository import SQLAlchemyBaseRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class SQLAlchemyPermisoRepository(SQLAlchemyBaseRepository[Permiso], IPermisoRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Permiso)
    
    async def find_by_codigo(self, codigo: str) -> Optional[Permiso]:
        result = await self.db.execute(
            select(Permiso).where(Permiso.codigo == codigo)
        )
        return result.scalar_one_or_none()
    async def find_by_recurso(self, recurso: str) -> List[Permiso]:
        result = await self.db.execute(
            select(Permiso)
            .where(Permiso.recurso == recurso)
            .order_by(Permiso.accion)
        )
        return list(result.scalars().all())
    async def find_by_recurso_accion(self, recurso: str, accion: str) -> Optional[Permiso]:
        result = await self.db.execute(
            select(Permiso).where(
                and_(
                    Permiso.recurso == recurso,
                    Permiso.accion == accion
                )
            )
        )
        return result.scalar_one_or_none()
    async def get_user_permisos(self, usuario_id: int) -> List[Permiso]:
        # Query complejo: Usuario -> Roles -> Permisos
        result = await self.db.execute(
            select(Permiso)
            .join(roles_permisos)
            .join(Rol)
            .join(usuarios_roles)
            .where(
                and_(
                    usuarios_roles.c.usuario_id == usuario_id,
                    Rol.activo == True
                )
            )
            .distinct()
            .order_by(Permiso.codigo)
        )
        return list(result.scalars().all())
    async def get_rol_permisos(self, rol_id: int) -> List[Permiso]:
        result = await self.db.execute(
            select(Permiso)
            .join(roles_permisos)
            .where(roles_permisos.c.rol_id == rol_id)
            .order_by(Permiso.codigo)
        )
        return list(result.scalars().all())
    async def user_has_permiso(self, usuario_id: int, codigo_permiso: str) -> bool:
        result = await self.db.execute(
            select(func.count())
            .select_from(Permiso)
            .join(roles_permisos)
            .join(Rol)
            .join(usuarios_roles)
            .where(
                and_(
                    usuarios_roles.c.usuario_id == usuario_id,
                    Permiso.codigo == codigo_permiso,
                    Rol.activo == True
                )
            )
        )
        count = result.scalar()
        return count > 0
    async def get_all_recursos(self) -> List[str]:
        result = await self.db.execute(
            select(distinct(Permiso.recurso)).order_by(Permiso.recurso)
        )
        return list(result.scalars().all())
    async def get_all_acciones(self) -> List[str]:
        result = await self.db.execute(
            select(distinct(Permiso.accion)).order_by(Permiso.accion)
        )
        return list(result.scalars().all())
    async def is_codigo_taken(self, codigo: str, exclude_id: Optional[int] = None) -> bool:
        query = select(func.count()).select_from(Permiso).where(Permiso.codigo == codigo)
        if exclude_id:
            query = query.where(Permiso.id != exclude_id)
        
        result = await self.db.execute(query)
        count = result.scalar()
        return count > 0
