from fastapi import APIRouter, Depends, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.services.user_service import UserService
from app.schemas.auth import UsuarioResponse, UsuarioActual
from app.core.dependencies import requiere_permisos
from app.core.logging import get_logger
from app.core.middleware import limiter

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/usuarios/{usuario_id}/desbloquear",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Desbloquear usuario",
    description="Desbloquea un usuario bloqueado por intentos fallidos de login"
)
@limiter.limit("10/minute")
async def desbloquear_usuario(
    request: Request,
    usuario_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UsuarioActual = Depends(requiere_permisos(["usuarios.actualizar"]))
):
    user_service = UserService(db)
    
    try:
        usuario = await user_service.desbloquear_usuario(usuario_id, current_user.id)
        
        logger.info(
            "usuario_desbloqueado_endpoint",
            usuario_id=usuario_id,
            admin_id=current_user.id
        )
        
        return usuario
    except Exception as e:
        logger.error(
            "error_desbloquear_usuario",
            error=str(e),
            usuario_id=usuario_id,
            admin_id=current_user.id
        )
        raise


@router.post(
    "/usuarios/{usuario_id}/resetear-contrasena",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Resetear contraseña (admin)",
    description="Resetea la contraseña de un usuario y revoca todas sus sesiones"
)
@limiter.limit("5/minute")
async def resetear_contrasena_admin(
    request: Request,
    usuario_id: int,
    nueva_contrasena: str = Query(..., min_length=8, description="Nueva contraseña"),
    db: AsyncSession = Depends(get_db_session),
    current_user: UsuarioActual = Depends(requiere_permisos(["usuarios.actualizar"]))
):
    user_service = UserService(db)
    
    try:
        usuario = await user_service.resetear_contrasena_admin(
            usuario_id=usuario_id,
            nueva_contrasena=nueva_contrasena,
            admin_id=current_user.id
        )
        
        logger.info(
            "contrasena_reseteada_endpoint",
            usuario_id=usuario_id,
            admin_id=current_user.id
        )
        
        return usuario
    except Exception as e:
        logger.error(
            "error_resetear_contrasena",
            error=str(e),
            usuario_id=usuario_id,
            admin_id=current_user.id
        )
        raise
