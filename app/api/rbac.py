from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db_session
from app.schemas.auth import (
    RolCreate, RolUpdate, RolResponse,
    PermisoResponse,
    AsignarRolesRequest,
    UsuarioActual
)
from app.services.rbac_service import RBACService
from app.core.dependencies import get_current_user, requiere_permisos
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    tags=["rbac"],
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "No autorizado"},
    }
)


# ==================== ROLES ====================

@router.post(
    "/roles",
    response_model=RolResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear rol",
    description="Crea un nuevo rol en el sistema"
)
async def crear_rol(
    rol_data: RolCreate,
    db: AsyncSession = Depends(get_db_session),
    usuario_actual: UsuarioActual = Depends(requiere_permisos(["roles.crear"]))
):
    rbac_service = RBACService(db)
    
    try:
        rol = await rbac_service.crear_rol(rol_data, usuario_actual.id)
        return rol
    except Exception as e:
        logger.error("error_crear_rol", error=str(e), usuario=usuario_actual.nombre_usuario)
        raise


@router.get(
    "/roles",
    response_model=List[RolResponse],
    summary="Listar roles",
    description="Lista todos los roles del sistema"
)
async def listar_roles(
    skip: int = Query(0, ge=0, description="Elementos a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de elementos"),
    solo_activos: bool = Query(False, description="Solo roles activos"),
    db: AsyncSession = Depends(get_db_session),
    usuario_actual: UsuarioActual = Depends(requiere_permisos(["roles.leer"]))
):
    rbac_service = RBACService(db)
    return await rbac_service.listar_roles(skip, limit, solo_activos)


@router.get(
    "/roles/{rol_id}",
    response_model=RolResponse,
    summary="Obtener rol",
    description="Obtiene un rol por su ID"
)
async def obtener_rol(
    rol_id: int,
    db: AsyncSession = Depends(get_db_session),
    usuario_actual: UsuarioActual = Depends(requiere_permisos(["roles.leer"]))
):
    rbac_service = RBACService(db)
    rol = await rbac_service.obtener_rol(rol_id)
    
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rol con ID {rol_id} no encontrado"
        )
    
    return rol


@router.put(
    "/roles/{rol_id}",
    response_model=RolResponse,
    summary="Actualizar rol",
    description="Actualiza un rol existente"
)
async def actualizar_rol(
    rol_id: int,
    rol_data: RolUpdate,
    db: AsyncSession = Depends(get_db_session),
    usuario_actual: UsuarioActual = Depends(requiere_permisos(["roles.actualizar"]))
):
    rbac_service = RBACService(db)
    
    try:
        rol = await rbac_service.actualizar_rol(rol_id, rol_data, usuario_actual.id)
        return rol
    except Exception as e:
        logger.error("error_actualizar_rol", error=str(e), rol_id=rol_id)
        raise


@router.delete(
    "/roles/{rol_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar rol",
    description="Elimina (desactiva) un rol"
)
async def eliminar_rol(
    rol_id: int,
    db: AsyncSession = Depends(get_db_session),
    usuario_actual: UsuarioActual = Depends(requiere_permisos(["roles.eliminar"]))
):
    rbac_service = RBACService(db)
    
    try:
        await rbac_service.eliminar_rol(rol_id, usuario_actual.id)
    except Exception as e:
        logger.error("error_eliminar_rol", error=str(e), rol_id=rol_id)
        raise


# ==================== PERMISOS ====================

@router.get(
    "/permisos",
    response_model=List[PermisoResponse],
    summary="Listar permisos",
    description="Lista todos los permisos disponibles"
)
async def listar_permisos(
    recurso: str = Query(None, description="Filtrar por recurso"),
    skip: int = Query(0, ge=0, description="Elementos a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de elementos"),
    db: AsyncSession = Depends(get_db_session),
    usuario_actual: UsuarioActual = Depends(requiere_permisos(["roles.leer"]))
):
    rbac_service = RBACService(db)
    return await rbac_service.listar_permisos(recurso, skip, limit)


@router.get(
    "/permisos/{permiso_id}",
    response_model=PermisoResponse,
    summary="Obtener permiso",
    description="Obtiene un permiso por su ID"
)
async def obtener_permiso(
    permiso_id: int,
    db: AsyncSession = Depends(get_db_session),
    usuario_actual: UsuarioActual = Depends(requiere_permisos(["roles.leer"]))
):
    rbac_service = RBACService(db)
    permiso = await rbac_service.obtener_permiso(permiso_id)
    
    if not permiso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permiso con ID {permiso_id} no encontrado"
        )
    
    return permiso


@router.get(
    "/recursos/{recurso}/permisos",
    response_model=List[PermisoResponse],
    summary="Permisos por recurso",
    description="Obtiene todos los permisos de un recurso"
)
async def obtener_permisos_recurso(
    recurso: str,
    db: AsyncSession = Depends(get_db_session),
    usuario_actual: UsuarioActual = Depends(requiere_permisos(["roles.leer"]))
):
    rbac_service = RBACService(db)
    return await rbac_service.obtener_permisos_por_recurso(recurso)


# ==================== ASIGNACIONES ====================

@router.post(
    "/usuarios/{usuario_id}/roles",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Asignar roles",
    description="Asigna roles a un usuario"
)
async def asignar_roles(
    usuario_id: int,
    request: AsignarRolesRequest,
    db: AsyncSession = Depends(get_db_session),
    usuario_actual: UsuarioActual = Depends(requiere_permisos(["usuarios.actualizar"]))
):
    rbac_service = RBACService(db)
    
    try:
        await rbac_service.asignar_roles_a_usuario(
            usuario_id,
            request.roles,
            usuario_actual.id
        )
    except Exception as e:
        logger.error("error_asignar_roles", error=str(e), usuario_id=usuario_id)
        raise


@router.get(
    "/usuarios/{usuario_id}/roles",
    response_model=List[RolResponse],
    summary="Roles de usuario",
    description="Obtiene roles asignados a un usuario"
)
async def obtener_roles_usuario(
    usuario_id: int,
    db: AsyncSession = Depends(get_db_session),
    usuario_actual: UsuarioActual = Depends(requiere_permisos(["usuarios.leer"]))
):
    rbac_service = RBACService(db)
    
    try:
        return await rbac_service.obtener_roles_usuario(usuario_id)
    except Exception as e:
        logger.error("error_obtener_roles_usuario", error=str(e), usuario_id=usuario_id)
        raise


@router.get(
    "/usuarios/{usuario_id}/permisos",
    response_model=List[PermisoResponse],
    summary="Permisos de usuario",
    description="Obtiene permisos efectivos de un usuario"
)
async def obtener_permisos_usuario(
    usuario_id: int,
    db: AsyncSession = Depends(get_db_session),
    usuario_actual: UsuarioActual = Depends(requiere_permisos(["usuarios.leer"]))
):
    rbac_service = RBACService(db)
    
    try:
        return await rbac_service.obtener_permisos_usuario(usuario_id)
    except Exception as e:
        logger.error("error_obtener_permisos_usuario", error=str(e), usuario_id=usuario_id)
        raise


@router.get(
    "/usuarios/{usuario_id}/permisos/{codigo_permiso}/verificar",
    response_model=dict,
    summary="Verificar permiso",
    description="Verifica si un usuario tiene un permiso específico"
)
async def verificar_permiso_usuario(
    usuario_id: int,
    codigo_permiso: str,
    db: AsyncSession = Depends(get_db_session),
    usuario_actual: UsuarioActual = Depends(requiere_permisos(["usuarios.leer"]))
):
    rbac_service = RBACService(db)
    
    tiene_permiso = await rbac_service.usuario_tiene_permiso(usuario_id, codigo_permiso)
    
    return {
        "usuario_id": usuario_id,
        "permiso": codigo_permiso,
        "tiene_permiso": tiene_permiso
    }


@router.get(
    "/usuarios/{usuario_id}/roles/{nombre_rol}/verificar",
    response_model=dict,
    summary="Verificar rol",
    description="Verifica si un usuario tiene un rol específico"
)
async def verificar_rol_usuario(
    usuario_id: int,
    nombre_rol: str,
    db: AsyncSession = Depends(get_db_session),
    usuario_actual: UsuarioActual = Depends(requiere_permisos(["usuarios.leer"]))
):
    rbac_service = RBACService(db)
    
    tiene_rol = await rbac_service.usuario_tiene_rol(usuario_id, nombre_rol)
    
    return {
        "usuario_id": usuario_id,
        "rol": nombre_rol,
        "tiene_rol": tiene_rol
    }
