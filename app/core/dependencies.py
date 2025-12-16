from typing import Optional, AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    TokenExpiredError,
    InvalidTokenError,
    UserInactiveError
)
from app.core.logging import get_logger, request_id_var, user_id_var
from app.database.session import get_db_session
from app.services.auth_service import AuthService
from app.schemas.auth import UsuarioActual

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> UsuarioActual:
    if not credentials:
        logger.warning("intento_acceso_sin_token", path=request.url.path)
        raise AuthenticationError("Token no proporcionado")
    
    token = credentials.credentials
    auth_service = AuthService(db)
    
    try:
        usuario = await auth_service.obtener_usuario_desde_token(token)
        
        if not usuario:
            logger.warning("token_invalido", path=request.url.path)
            raise InvalidTokenError()
        
        if not usuario.activo:
            logger.warning(
                "usuario_inactivo_intento_acceso",
                user_id=usuario.id,
                username=usuario.nombre_usuario
            )
            raise UserInactiveError()
        
        # Establecer contexto de usuario para logging
        user_id_var.set(usuario.id)
        request_id_var.set(request.headers.get("X-Request-ID", "unknown"))
        
        logger.info(
            "usuario_autenticado",
            user_id=usuario.id,
            username=usuario.nombre_usuario,
            path=request.url.path
        )
        
        return usuario
    
    except TokenExpiredError:
        logger.warning("token_expirado", path=request.url.path)
        raise
    except (InvalidTokenError, AuthenticationError):
        logger.warning("autenticacion_fallida", path=request.url.path)
        raise
    except Exception as e:
        logger.error("error_obteniendo_usuario_actual", error=str(e), path=request.url.path)
        raise AuthenticationError("Error al validar token")


async def get_current_active_superuser(
    current_user: UsuarioActual = Depends(get_current_user)
) -> UsuarioActual:
    if not current_user.es_superusuario:
        logger.warning(
            "acceso_superusuario_denegado",
            user_id=current_user.id,
            username=current_user.nombre_usuario
        )
        raise AuthorizationError("Se requieren privilegios de superusuario")
    
    return current_user


def requiere_permisos(*permisos_requeridos: str):
    async def verificar_permisos(
        current_user: UsuarioActual = Depends(get_current_user),
        db: AsyncSession = Depends(get_db_session)
    ) -> UsuarioActual:
        # Superusuarios tienen acceso automático
        if current_user.es_superusuario:
            logger.info(
                "acceso_autorizado_superusuario",
                user_id=current_user.id,
                username=current_user.nombre_usuario,
                permisos_requeridos=list(permisos_requeridos)
            )
            return current_user
        
        auth_service = AuthService(db)
        
        permisos_usuario = await auth_service.obtener_permisos_usuario(current_user.id)
        
        # Verificar wildcard (por si acaso)
        if "*" in permisos_usuario:
            logger.info(
                "acceso_autorizado_wildcard",
                user_id=current_user.id,
                username=current_user.nombre_usuario,
                permisos_requeridos=list(permisos_requeridos)
            )
            return current_user
        
        permisos_faltantes = set(permisos_requeridos) - set(permisos_usuario)
        
        if permisos_faltantes:
            logger.warning(
                "acceso_denegado_permisos_insuficientes",
                user_id=current_user.id,
                username=current_user.nombre_usuario,
                permisos_requeridos=list(permisos_requeridos),
                permisos_faltantes=list(permisos_faltantes)
            )
            raise AuthorizationError(
                f"Permisos insuficientes. Faltan: {', '.join(permisos_faltantes)}"
            )
        
        logger.info(
            "acceso_autorizado",
            user_id=current_user.id,
            username=current_user.nombre_usuario,
            permisos=list(permisos_requeridos)
        )
        
        return current_user
    
    return verificar_permisos


def requiere_roles(*roles_requeridos: str):
    async def verificar_roles(
        current_user: UsuarioActual = Depends(get_current_user),
        db: AsyncSession = Depends(get_db_session)
    ) -> UsuarioActual:
        auth_service = AuthService(db)
        
        roles_usuario = await auth_service.obtener_roles_usuario(current_user.id)
        
        tiene_rol = any(rol in roles_usuario for rol in roles_requeridos)
        
        if not tiene_rol:
            logger.warning(
                "acceso_denegado_rol_insuficiente",
                user_id=current_user.id,
                username=current_user.nombre_usuario,
                roles_requeridos=list(roles_requeridos),
                roles_usuario=roles_usuario
            )
            raise AuthorizationError(
                f"Se requiere uno de los siguientes roles: {', '.join(roles_requeridos)}"
            )
        
        logger.info(
            "acceso_autorizado_por_rol",
            user_id=current_user.id,
            username=current_user.nombre_usuario,
            roles_requeridos=list(roles_requeridos)
        )
        
        return current_user
    
    return verificar_roles


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> Optional[UsuarioActual]:
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        auth_service = AuthService(db)
        usuario = await auth_service.obtener_usuario_desde_token(token)
        
        if usuario and usuario.activo:
            user_id_var.set(usuario.id)
            return usuario
    except Exception:
        pass
    
    return None
