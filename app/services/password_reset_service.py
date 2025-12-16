from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
import secrets

from app.database.models import Usuario
from app.core.security import hash_password, validate_password_strength
from app.core.logging import get_logger, audit_logger
from app.core.exceptions import ValidationError, UserNotFoundError
from app.config import settings

logger = get_logger(__name__)


class PasswordResetService:
    # Tiempo de expiración del token (1 hora)
    TOKEN_EXPIRATION_MINUTES = 60
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def solicitar_reset(self, email: str) -> Optional[str]:
        # Buscar usuario por email
        result = await self.db.execute(
            select(Usuario).where(Usuario.email == email)
        )
        usuario = result.scalar_one_or_none()
        
        if not usuario:
            # Log pero no informar al cliente (anti-enumeración)
            logger.warning("reset_solicitado_email_inexistente", email=email)
            
            # En desarrollo, informar. En producción, silencio
            if settings.is_development:
                raise UserNotFoundError(f"No existe usuario con email {email}")
            else:
                return None
        
        # No permitir reset si usuario inactivo
        if not usuario.activo:
            logger.warning("reset_solicitado_usuario_inactivo", usuario_id=usuario.id)
            
            if settings.is_development:
                raise ValidationError("Usuario inactivo")
            else:
                return None
        
        # No permitir reset para auth no local
        if usuario.tipo_autenticacion != "local":
            logger.warning(
                "reset_solicitado_auth_no_local",
                usuario_id=usuario.id,
                tipo=usuario.tipo_autenticacion
            )
            
            if settings.is_development:
                raise ValidationError(
                    f"Usuario con autenticación {usuario.tipo_autenticacion} "
                    "no puede cambiar contraseña localmente"
                )
            else:
                return None
        
        # Generar token seguro
        reset_token = secrets.token_urlsafe(32)
        
        # Guardar token en usuario
        usuario.reset_token = reset_token
        usuario.reset_token_expira = datetime.utcnow() + timedelta(
            minutes=self.TOKEN_EXPIRATION_MINUTES
        )
        usuario.fecha_actualizacion = datetime.utcnow()
        
        await self.db.commit()
        
        # Auditoría
        audit_logger.log_authentication(
            user_id=usuario.id,
            username=usuario.nombre_usuario,
            provider="password_reset",
            result="success",
            reason="token_generado"
        )
        
        logger.info(
            "reset_token_generado",
            usuario_id=usuario.id,
            email=email,
            expira=usuario.reset_token_expira.isoformat()
        )
        
        # TODO: Enviar email con el token
        # await email_service.enviar_reset_password(email, reset_token)
        
        # En desarrollo, retornar el token
        # En producción, retornar None (el token se envía por email)
        if settings.is_development:
            return reset_token
        else:
            return None
    
    async def validar_token(self, token: str) -> Optional[Usuario]:
        result = await self.db.execute(
            select(Usuario).where(
                and_(
                    Usuario.reset_token == token,
                    Usuario.reset_token_expira > datetime.utcnow()
                )
            )
        )
        usuario = result.scalar_one_or_none()
        
        if not usuario:
            logger.warning("token_reset_invalido_o_expirado", token=token[:10] + "...")
            return None
        
        return usuario
    
    async def resetear_contrasena(
        self,
        token: str,
        nueva_contrasena: str
    ):
        # Validar token
        usuario = await self.validar_token(token)
        
        if not usuario:
            raise ValidationError("Token inválido o expirado")
        
        # Validar fortaleza de contraseña
        validate_password_strength(nueva_contrasena)
        
        # Actualizar contraseña
        usuario.contrasena_hash = hash_password(nueva_contrasena)
        usuario.reset_token = None
        usuario.reset_token_expira = None
        usuario.fecha_actualizacion = datetime.utcnow()
        
        # Resetear intentos fallidos si existían
        usuario.intentos_fallidos = 0
        usuario.fecha_bloqueo = None
        
        await self.db.commit()
        
        # Auditoría
        audit_logger.log_authentication(
            user_id=usuario.id,
            username=usuario.nombre_usuario,
            provider="password_reset",
            result="success",
            reason="contrasena_reseteada"
        )
        
        logger.info(
            "contrasena_reseteada",
            usuario_id=usuario.id,
            username=usuario.nombre_usuario
        )
        
        # TODO: Enviar email de confirmación
        # await email_service.enviar_confirmacion_reset(usuario.email)
    
    async def cancelar_reset(self, usuario_id: int):
        result = await self.db.execute(
            select(Usuario).where(Usuario.id == usuario_id)
        )
        usuario = result.scalar_one_or_none()
        
        if not usuario:
            return
        
        if usuario.reset_token:
            usuario.reset_token = None
            usuario.reset_token_expira = None
            usuario.fecha_actualizacion = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info("reset_cancelado", usuario_id=usuario_id)
