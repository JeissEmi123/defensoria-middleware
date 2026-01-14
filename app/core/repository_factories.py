from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import (
    IUsuarioRepository,
    IRolRepository,
    IPermisoRepository,
    ISesionRepository,
)
from app.infrastructure.repositories import (
    SQLAlchemyUsuarioRepository,
    SQLAlchemyRolRepository,
    SQLAlchemyPermisoRepository,
    SQLAlchemySesionRepository,
)


def get_usuario_repository(db: AsyncSession) -> IUsuarioRepository:
    return SQLAlchemyUsuarioRepository(db)

def get_rol_repository(db: AsyncSession) -> IRolRepository:
    return SQLAlchemyRolRepository(db)

def get_permiso_repository(db: AsyncSession) -> IPermisoRepository:
    return SQLAlchemyPermisoRepository(db)

def get_sesion_repository(db: AsyncSession) -> ISesionRepository:
    return SQLAlchemySesionRepository(db)
