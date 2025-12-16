from typing import Optional, List
from sqlalchemy import select, and_, delete as sql_delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Rol, Permiso, Usuario, usuarios_roles, roles_permisos
from app.domain.repositories.rol_repository import IRolRepository
from .sqlalchemy_base_repository import SQLAlchemyBaseRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class SQLAlchemyRolRepository(SQLAlchemyBaseRepository[Rol], IRolRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Rol)
    
    async def find_by_name(self, nombre: str) -> Optional[Rol]:
        result = await self.db.execute(
            select(Rol).where(Rol.nombre == nombre)
        )
        return result.scalar_one_or_none()
    async def get_with_permisos(self, rol_id: int) -> Optional[Rol]:
        result = await self.db.execute(
            select(Rol)
            .options(selectinload(Rol.permisos))
            .where(Rol.id == rol_id)
        )
        return result.scalar_one_or_none()
    async def get_active_roles(self, skip: int = 0, limit: int = 100) -> List[Rol]:
        result = await self.db.execute(
            select(Rol)
            .where(Rol.activo == True)
            .offset(skip)
            .limit(limit)
            .order_by(Rol.nombre)
        )
        return list(result.scalars().all())
    async def get_system_roles(self) -> List[Rol]:
        result = await self.db.execute(
            select(Rol)
            .where(Rol.es_sistema == True)
            .order_by(Rol.nombre)
        )
        return list(result.scalars().all())
    async def get_user_roles(self, usuario_id: int) -> List[Rol]:
        result = await self.db.execute(
            select(Rol)
            .join(usuarios_roles)
            .where(usuarios_roles.c.usuario_id == usuario_id)
            .order_by(Rol.nombre)
        )
        return list(result.scalars().all())
    async def assign_permisos(self, rol_id: int, permiso_ids: List[int]) -> bool:
        try:
            # Verificar que el rol existe
            rol = await self.get_by_id(rol_id)
            if not rol:
                return False
            # Obtener permisos existentes
            permisos_result = await self.db.execute(
                select(Permiso).where(Permiso.id.in_(permiso_ids))
            )
            permisos = list(permisos_result.scalars().all())
            
            # Agregar nuevos permisos (SQLAlchemy maneja duplicados)
            rol.permisos.extend([p for p in permisos if p not in rol.permisos])
            await self.db.flush()
            
            logger.info(f"Permisos asignados al rol {rol.nombre}: {len(permisos)}")
            return True
        except Exception as e:
            logger.error(f"Error asignando permisos al rol {rol_id}: {e}")
            return False
    
    async def remove_permisos(self, rol_id: int, permiso_ids: List[int]) -> bool:
        try:
            rol = await self.get_with_permisos(rol_id)
            if not rol:
                return False
            # Remover permisos
            rol.permisos = [p for p in rol.permisos if p.id not in permiso_ids]
            await self.db.flush()
            
            logger.info(f"Permisos removidos del rol {rol.nombre}: {len(permiso_ids)}")
            return True
        except Exception as e:
            logger.error(f"Error removiendo permisos del rol {rol_id}: {e}")
            return False
    
    async def clear_permisos(self, rol_id: int) -> bool:
        try:
            rol = await self.get_with_permisos(rol_id)
            if not rol:
                return False
            rol.permisos.clear()
            await self.db.flush()
            
            logger.info(f"Permisos limpiados del rol {rol.nombre}")
            return True
        except Exception as e:
            logger.error(f"Error limpiando permisos del rol {rol_id}: {e}")
            return False
    
    async def is_name_taken(self, nombre: str, exclude_id: Optional[int] = None) -> bool:
        query = select(func.count()).select_from(Rol).where(Rol.nombre == nombre)
        if exclude_id:
            query = query.where(Rol.id != exclude_id)
        
        result = await self.db.execute(query)
        count = result.scalar()
        return count > 0
    
    async def is_system_role(self, rol_id: int) -> bool:
        result = await self.db.execute(
            select(Rol.es_sistema).where(Rol.id == rol_id)
        )
        es_sistema = result.scalar_one_or_none()
        return es_sistema == True if es_sistema is not None else False
