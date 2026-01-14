from fastapi import APIRouter, Depends, status, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db_session
from app.services.user_service import UserService
from app.schemas.auth import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse,
    CambiarContrasenaRequest, UsuarioActual
)
from app.core.dependencies import (
    get_current_user,
    get_optional_current_user,
    requiere_permisos
)
from app.core.logging import get_logger
from app.core.middleware import limiter

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/list",
    response_model=List[UsuarioResponse],
    summary="Listar usuarios",
    description="Lista todos los usuarios del sistema"
)
async def listar_usuarios(
    skip: int = Query(0, ge=0, description="Elementos a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de elementos"),
    activo: bool = Query(None, description="Filtrar por estado activo"),
    db: AsyncSession = Depends(get_db_session),
    current_user: UsuarioActual = Depends(requiere_permisos(["usuarios.leer"]))
):
    user_service = UserService(db)
    return await user_service.listar_usuarios(skip, limit, activo)


@router.post(
    "/create",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario en el sistema"
)
@limiter.limit("10/minute")
async def crear_usuario(
    request: Request,
    usuario_data: UsuarioCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: UsuarioActual = Depends(get_optional_current_user)
):
    user_service = UserService(db)
    try:
        if not await user_service.existen_usuarios():
            # Si no hay usuarios, crear el primero sin autenticación
            usuario = await user_service.crear_usuario(usuario_data, creado_por_id=None)
            return usuario
        # Si ya hay usuarios, requerir permisos y autenticación
        if not current_user or not current_user.es_superusuario:
            raise HTTPException(status_code=403, detail="No autorizado para crear usuarios")
        usuario = await user_service.crear_usuario(usuario_data, current_user.id)
        return usuario
    except Exception as e:
        logger.error("error_crear_usuario", error=str(e))
        raise


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Obtener usuario",
    description="Obtiene un usuario por su ID"
)
async def obtener_usuario(
    usuario_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UsuarioActual = Depends(requiere_permisos(["usuarios.leer"]))
):
    user_service = UserService(db)
    usuario = await user_service.obtener_usuario(usuario_id)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    return usuario


@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Actualizar usuario",
    description="Actualiza un usuario existente"
)
@limiter.limit("10/minute")
async def actualizar_usuario(
    request: Request,
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: UsuarioActual = Depends(requiere_permisos(["usuarios.actualizar"]))
):
    user_service = UserService(db)
    
    try:
        usuario = await user_service.actualizar_usuario(usuario_id, usuario_data, current_user.id)
        return usuario
    except Exception as e:
        logger.error("error_actualizar_usuario", error=str(e), usuario_id=usuario_id)
        raise


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina (desactiva) un usuario"
)
@limiter.limit("5/minute")
async def eliminar_usuario(
    request: Request,
    usuario_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UsuarioActual = Depends(requiere_permisos(["usuarios.eliminar"]))
):
    user_service = UserService(db)
    
    try:
        await user_service.eliminar_usuario(usuario_id, current_user.id)
    except Exception as e:
        logger.error("error_eliminar_usuario", error=str(e), usuario_id=usuario_id)
        raise


@router.post(
    "/me/cambiar-contrasena",
    status_code=status.HTTP_200_OK,
    summary="Cambiar contraseña",
    description="Permite al usuario actual cambiar su contraseña"
)
@limiter.limit("3/hour")
async def cambiar_contrasena(
    request: Request,
    cambio_data: CambiarContrasenaRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: UsuarioActual = Depends(get_current_user)
):
    user_service = UserService(db)
    
    try:
        await user_service.cambiar_contrasena(
            usuario_id=current_user.id,
            contrasena_actual=cambio_data.contrasena_actual,
            contrasena_nueva=cambio_data.contrasena_nueva
        )
        
        logger.info("contrasena_cambiada", user_id=current_user.id)
        
        return {
            "message": "Contraseña cambiada exitosamente",
            "user_id": current_user.id
        }
    except Exception as e:
        logger.error("error_cambiar_contrasena", error=str(e), user_id=current_user.id)
        raise


@router.get(
    "/me/sesiones",
    summary="Sesiones activas",
    description="Lista todas las sesiones activas del usuario actual"
)
async def listar_sesiones(
    db: AsyncSession = Depends(get_db_session),
    current_user: UsuarioActual = Depends(get_current_user)
):
    user_service = UserService(db)
    sesiones = await user_service.obtener_sesiones_activas(current_user.id)
    
    return {
        "usuario_id": current_user.id,
        "sesiones_activas": len(sesiones),
        "sesiones": sesiones
    }


@router.delete(
    "/me/sesiones/{sesion_id}",
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión específica",
    description="Cierra una sesión activa específica"
)
async def cerrar_sesion_especifica(
    sesion_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UsuarioActual = Depends(get_current_user)
):
    user_service = UserService(db)
    
    try:
        await user_service.cerrar_sesion_especifica(current_user.id, sesion_id)
        
        logger.info("sesion_cerrada", user_id=current_user.id, sesion_id=sesion_id)
        
        return {
            "message": "Sesión cerrada exitosamente",
            "sesion_id": sesion_id
        }
    except Exception as e:
        logger.error("error_cerrar_sesion", error=str(e), sesion_id=sesion_id)
        raise


@router.delete(
    "/me/sesiones",
    status_code=status.HTTP_200_OK,
    summary="Cerrar todas las sesiones",
    description="Cierra todas las sesiones activas excepto la actual"
)
@limiter.limit("3/hour")
async def cerrar_todas_sesiones(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: UsuarioActual = Depends(get_current_user)
):
    user_service = UserService(db)
    
    # Extraer token actual
    auth_header = request.headers.get("authorization", "")
    token_actual = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None
    
    try:
        sesiones_cerradas = await user_service.cerrar_todas_sesiones(
            current_user.id,
            excepto_token=token_actual
        )
        
        logger.info("todas_sesiones_cerradas", user_id=current_user.id, count=sesiones_cerradas)
        
        return {
            "message": f"{sesiones_cerradas} sesión(es) cerrada(s) exitosamente",
            "sesiones_cerradas": sesiones_cerradas
        }
    except Exception as e:
        logger.error("error_cerrar_todas_sesiones", error=str(e), user_id=current_user.id)
        raise
