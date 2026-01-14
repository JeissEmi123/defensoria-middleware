from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from sqlalchemy import select, and_, func, desc
from app.database.models import Usuario, Sesion, PasswordHistory
from app.schemas.auth import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse,
    TipoAutenticacion
)
from app.core.security import (
    hash_password, verify_password, validate_password_strength,
    validate_username, validate_email_format, validate_nombre_completo,
    sanitize_email, validate_input_security
)
from app.core.logging import get_logger, audit_logger
from app.core.exceptions import (
    ValidationError, AuthenticationError, UserNotFoundError
)
from app.auth.tokens import TokenManager
from app.config import get_settings

settings = get_settings()

# Repository Pattern - Arquitectura Hexagonal
from app.domain.repositories import (
    IUsuarioRepository,
    ISesionRepository,
)
from app.core.repository_factories import (
    get_usuario_repository,
    get_sesion_repository,
)

logger = get_logger(__name__)
token_manager = TokenManager()


class UserService:
    
    def __init__(
        self,
        db: AsyncSession,
        usuario_repo: Optional[IUsuarioRepository] = None,
        sesion_repo: Optional[ISesionRepository] = None
    ):
        self.db = db
        
        # Inyección de dependencias con factories como fallback
        self.usuario_repo = usuario_repo or get_usuario_repository(db)
        self.sesion_repo = sesion_repo or get_sesion_repository(db)

    async def existen_usuarios(self) -> bool:
        result = await self.db.execute(select(func.count(Usuario.id)))
        return (result.scalar() or 0) > 0

    async def _obtener_usuario_entidad(self, usuario_id: int) -> Usuario:
        usuario = await self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            raise UserNotFoundError(f"Usuario con ID {usuario_id} no encontrado")
        return usuario
    
    async def crear_usuario(
        self,
        usuario_data: UsuarioCreate,
        creado_por_id: int
    ) -> UsuarioResponse:
        # Validar límite de usuarios en el sistema
        if settings.enforce_user_limit:
            result = await self.db.execute(select(func.count(Usuario.id)))
            total_usuarios = result.scalar()
            
            if total_usuarios >= settings.max_users_limit:
                raise ValidationError(
                    f"Se ha alcanzado el límite máximo de {settings.max_users_limit} usuarios en el sistema"
                )
        
        # Validar nombre de usuario
        valid, error = validate_username(usuario_data.nombre_usuario)
        if not valid:
            raise ValidationError(error)
        
        # Validar seguridad del input
        valid, error = validate_input_security(usuario_data.nombre_usuario, "nombre de usuario")
        if not valid:
            raise ValidationError(error)
        
        # Verificar que no exista usando repositorio
        if await self.usuario_repo.is_username_taken(usuario_data.nombre_usuario):
            raise ValidationError(f"Usuario '{usuario_data.nombre_usuario}' ya existe")
        
        # Validar y sanitizar email
        if usuario_data.email:
            usuario_data.email = sanitize_email(usuario_data.email)
            valid, error = validate_email_format(usuario_data.email)
            if not valid:
                raise ValidationError(error)
            
            # Verificar email único
            if await self.usuario_repo.is_email_taken(usuario_data.email):
                raise ValidationError(f"Email '{usuario_data.email}' ya está en uso")
        
        # Validar nombre completo
        if usuario_data.nombre_completo:
            valid, error = validate_nombre_completo(usuario_data.nombre_completo)
            if not valid:
                raise ValidationError(error)
            
            valid, error = validate_input_security(usuario_data.nombre_completo, "nombre completo")
            if not valid:
                raise ValidationError(error)
        
        # Validar fortaleza de contraseña
        valid, error = validate_password_strength(
            usuario_data.contrasena,
            username=usuario_data.nombre_usuario,
            email=usuario_data.email
        )
        if not valid:
            raise ValidationError(error)
        
        # Crear usuario usando repositorio
        nuevo_usuario = Usuario(
            nombre_usuario=usuario_data.nombre_usuario,
            email=usuario_data.email,
            nombre_completo=usuario_data.nombre_completo,
            contrasena_hash=hash_password(usuario_data.contrasena),
            es_superusuario=usuario_data.es_superusuario,
            activo=usuario_data.activo,
            tipo_autenticacion=TipoAutenticacion.local
        )
        
        nuevo_usuario = await self.usuario_repo.create(nuevo_usuario)
        await self.db.commit()
        await self.db.refresh(nuevo_usuario)
        
        # Guardar en historial de contraseñas si está habilitado
        if settings.enforce_password_history:
            password_history = PasswordHistory(
                usuario_id=nuevo_usuario.id,
                contrasena_hash=nuevo_usuario.contrasena_hash
            )
            self.db.add(password_history)
            await self.db.commit()
        
        # Auditoría
        if creado_por_id is not None:
            audit_logger.log_data_access(
                user_id=creado_por_id,
                username="admin",
                resource=f"usuario.{nuevo_usuario.id}",
                action="create"
            )
        
        logger.info(
            "usuario_creado",
            usuario_id=nuevo_usuario.id,
            nombre=nuevo_usuario.nombre_usuario,
            creado_por=creado_por_id
        )
        
        return self._usuario_a_response(nuevo_usuario)
    
    async def obtener_usuario(self, usuario_id: int) -> Optional[UsuarioResponse]:
        usuario = await self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            return None
        
        return self._usuario_a_response(usuario)
    
    async def listar_usuarios(
        self,
        skip: int = 0,
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[UsuarioResponse]:
        if activo is True:
            usuarios = await self.usuario_repo.get_active_users(skip, limit)
        elif activo is not None:
            usuarios = await self.usuario_repo.get_all(skip, limit, activo=activo)
        else:
            usuarios = await self.usuario_repo.get_all(skip, limit)
        return [self._usuario_a_response(u) for u in usuarios]
    
    async def actualizar_usuario(
        self,
        usuario_id: int,
        usuario_data: UsuarioUpdate,
        actualizado_por_id: int
    ) -> UsuarioResponse:
        usuario = await self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            raise UserNotFoundError(f"Usuario con ID {usuario_id} no encontrado")
        
        # Actualizar campos
        if usuario_data.email is not None:
            # Validar y sanitizar email
            usuario_data.email = sanitize_email(usuario_data.email)
            valid, error = validate_email_format(usuario_data.email)
            if not valid:
                raise ValidationError(error)
            
            # Verificar email único usando repositorio
            if await self.usuario_repo.is_email_taken(usuario_data.email, exclude_id=usuario_id):
                raise ValidationError(f"Email '{usuario_data.email}' ya está en uso")
            
            usuario.email = usuario_data.email
        
        if usuario_data.nombre_completo is not None:
            # Validar nombre completo
            valid, error = validate_nombre_completo(usuario_data.nombre_completo)
            if not valid:
                raise ValidationError(error)
            
            valid, error = validate_input_security(usuario_data.nombre_completo, "nombre completo")
            if not valid:
                raise ValidationError(error)
            
            usuario.nombre_completo = usuario_data.nombre_completo
        
        if usuario_data.activo is not None:
            usuario.activo = usuario_data.activo
        
        if usuario_data.es_superusuario is not None:
            usuario.es_superusuario = usuario_data.es_superusuario
        
        usuario.fecha_actualizacion = datetime.utcnow()
        
        await self.usuario_repo.update(usuario)
        await self.db.commit()
        
        # Auditoría
        audit_logger.log_data_access(
            user_id=actualizado_por_id,
            username="admin",
            resource=f"usuario.{usuario_id}",
            action="update"
        )
        
        logger.info(
            "usuario_actualizado",
            usuario_id=usuario_id,
            actualizado_por=actualizado_por_id
        )
        
        return self._usuario_a_response(usuario)
    
    async def eliminar_usuario(
        self,
        usuario_id: int,
        eliminado_por_id: int
    ):
        usuario = await self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            raise UserNotFoundError(f"Usuario con ID {usuario_id} no encontrado")
        
        # No permitir eliminarse a sí mismo
        if usuario_id == eliminado_por_id:
            raise ValidationError("No puedes eliminarte a ti mismo")
        
        # No permitir eliminar el último administrador
        if usuario.es_superusuario:
            # Contar administradores activos
            result = await self.db.execute(
                select(Usuario).where(
                    and_(
                        Usuario.es_superusuario == True,
                        Usuario.activo == True,
                        Usuario.id != usuario_id
                    )
                )
            )
            otros_admins = result.scalars().all()
            
            if len(otros_admins) == 0:
                raise ValidationError("No se puede eliminar el último administrador del sistema")
        
        # Soft delete
        usuario.activo = False
        usuario.fecha_actualizacion = datetime.utcnow()
        
        await self.usuario_repo.update(usuario)
        await self.db.commit()
        
        # Auditoría
        audit_logger.log_data_access(
            user_id=eliminado_por_id,
            username="admin",
            resource=f"usuario.{usuario_id}",
            action="delete"
        )
        
        logger.info(
            "usuario_eliminado",
            usuario_id=usuario_id,
            eliminado_por=eliminado_por_id
        )
    
    async def cambiar_contrasena(
        self,
        usuario_id: int,
        contrasena_actual: str,
        contrasena_nueva: str
    ):
        usuario = await self.usuario_repo.get_by_id(usuario_id)
        
        if not usuario:
            raise UserNotFoundError(f"Usuario con ID {usuario_id} no encontrado")
        
        # Verificar contraseña actual
        if not verify_password(contrasena_actual, usuario.contrasena_hash):
            audit_logger.log_authentication(
                user_id=usuario_id,
                username=usuario.nombre_usuario,
                provider="local",
                result="failed",
                reason="contrasena_actual_incorrecta"
            )
            raise AuthenticationError("Contraseña actual incorrecta")
        
        # Validar fortaleza de nueva contraseña
        valid, error = validate_password_strength(
            contrasena_nueva,
            username=usuario.nombre_usuario,
            email=usuario.email
        )
        if not valid:
            raise ValidationError(error)
        
        # No permitir misma contraseña
        if verify_password(contrasena_nueva, usuario.contrasena_hash):
            raise ValidationError("La nueva contraseña debe ser diferente a la actual")
        
        # Validar historial de contraseñas
        if settings.enforce_password_history:
            result = await self.db.execute(
                select(PasswordHistory)
                .where(PasswordHistory.usuario_id == usuario_id)
                .order_by(desc(PasswordHistory.fecha_creacion))
                .limit(settings.password_history_count)
            )
            historial = result.scalars().all()
            
            for password_record in historial:
                if verify_password(contrasena_nueva, password_record.contrasena_hash):
                    raise ValidationError(
                        f"No puedes reutilizar las últimas {settings.password_history_count} contraseñas"
                    )
        
        # Actualizar contraseña
        nuevo_hash = hash_password(contrasena_nueva)
        usuario.contrasena_hash = nuevo_hash
        usuario.ultimo_cambio_contrasena = datetime.utcnow()
        usuario.fecha_actualizacion = datetime.utcnow()
        
        await self.usuario_repo.update(usuario)
        
        # Guardar en historial de contraseñas
        if settings.enforce_password_history:
            password_history = PasswordHistory(
                usuario_id=usuario_id,
                contrasena_hash=nuevo_hash
            )
            self.db.add(password_history)
            
            # Limpiar historial antiguo (mantener solo las últimas N)
            result = await self.db.execute(
                select(PasswordHistory)
                .where(PasswordHistory.usuario_id == usuario_id)
                .order_by(desc(PasswordHistory.fecha_creacion))
                .offset(settings.password_history_count)
            )
            old_passwords = result.scalars().all()
            for old_pass in old_passwords:
                await self.db.delete(old_pass)
        
        await self.db.commit()
        
        # Auditoría
        audit_logger.log_authentication(
            user_id=usuario_id,
            username=usuario.nombre_usuario,
            provider="local",
            result="success",
            reason="contrasena_cambiada"
        )
        
        logger.info("contrasena_cambiada", usuario_id=usuario_id)
    
    async def obtener_sesiones_activas(self, usuario_id: int) -> List[dict]:
        sesiones = await self.sesion_repo.get_active_sessions(usuario_id)
        return [
            {
                "id": s.id,
                "ip_address": s.direccion_ip,
                "user_agent": s.user_agent,
                "fecha_creacion": s.fecha_creacion.isoformat() if s.fecha_creacion else None,
                "fecha_ultimo_acceso": s.fecha_ultimo_acceso.isoformat() if hasattr(s, 'fecha_ultimo_acceso') and s.fecha_ultimo_acceso else None,
                "fecha_expiracion": s.access_expira_en.isoformat() if s.access_expira_en else None
            }
            for s in sesiones
        ]
    
    async def cerrar_sesion_especifica(self, usuario_id: int, sesion_id: int):
        sesion = await self.sesion_repo.get_by_id(sesion_id)
        if not sesion or sesion.usuario_id != usuario_id:
            raise ValidationError("Sesión no encontrada o no pertenece al usuario")
        
        await self.sesion_repo.invalidate_session(sesion_id)
        await self.db.commit()
        
        logger.info("sesion_cerrada", usuario_id=usuario_id, sesion_id=sesion_id)
    
    async def cerrar_todas_sesiones(
        self,
        usuario_id: int,
        excepto_token: Optional[str] = None
    ) -> int:
        sesion_actual_id = None
        if excepto_token:
            sesion_actual = await self.sesion_repo.find_by_access_token(excepto_token)
            if sesion_actual:
                sesion_actual_id = sesion_actual.id
        
        # Invalidar todas las sesiones excepto la actual
        count = await self.sesion_repo.invalidate_user_sessions(usuario_id, except_session_id=sesion_actual_id)
        await self.db.commit()
        
        logger.info("sesiones_cerradas", usuario_id=usuario_id, cantidad=count)
        return count
    
    async def desbloquear_usuario(self, usuario_id: int, admin_id: int) -> UsuarioResponse:
        usuario = await self._obtener_usuario_entidad(usuario_id)
        
        if usuario.intentos_login_fallidos == 0 and not usuario.fecha_bloqueo:
            logger.warning(
                "intento_desbloquear_usuario_no_bloqueado",
                usuario_id=usuario_id,
                admin_id=admin_id
            )
            raise ValidationError("El usuario no está bloqueado")
        
        # Desbloquear
        usuario.intentos_login_fallidos = 0
        usuario.fecha_bloqueo = None
        usuario.fecha_actualizacion = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(usuario)
        
        audit_logger.info(
            "usuario_desbloqueado",
            admin_id=admin_id,
            usuario_id=usuario_id,
            usuario_nombre=usuario.nombre_usuario
        )
        
        logger.info(
            "usuario_desbloqueado",
            usuario_id=usuario_id,
            admin_id=admin_id
        )
        
        return self._usuario_a_response(usuario)
    
    async def resetear_contrasena_admin(
        self,
        usuario_id: int,
        nueva_contrasena: str,
        admin_id: int
    ) -> UsuarioResponse:
        usuario = await self._obtener_usuario_entidad(usuario_id)
        
        # Validar fortaleza de la contraseña
        errores = validate_password_strength(nueva_contrasena)
        if errores:
            raise ValidationError(f"Contraseña no cumple requisitos: {', '.join(errores)}")
        
        # Actualizar contraseña
        usuario.contrasena_hash = hash_password(nueva_contrasena)
        usuario.requiere_cambio_contrasena = True  # Forzar cambio en próximo login
        usuario.ultimo_cambio_contrasena = datetime.utcnow()
        usuario.fecha_actualizacion = datetime.utcnow()
        
        # Revocar todas las sesiones activas
        result = await self.db.execute(
            select(Sesion).where(
                and_(
                    Sesion.usuario_id == usuario_id,
                    Sesion.activa == True
                )
            )
        )
        sesiones = result.scalars().all()
        
        for sesion in sesiones:
            sesion.activa = False
            sesion.revocada = True
            sesion.razon_revocacion = "Contraseña reseteada por administrador"
        
        await self.db.commit()
        await self.db.refresh(usuario)
        
        audit_logger.info(
            "contrasena_reseteada_por_admin",
            admin_id=admin_id,
            usuario_id=usuario_id,
            usuario_nombre=usuario.nombre_usuario,
            sesiones_revocadas=len(sesiones)
        )
        
        logger.info(
            "contrasena_reseteada_admin",
            usuario_id=usuario_id,
            admin_id=admin_id,
            sesiones_revocadas=len(sesiones)
        )
        
        return self._usuario_a_response(usuario)
    
    def _usuario_a_response(self, usuario: Usuario) -> UsuarioResponse:
        return UsuarioResponse(
            id=usuario.id,
            nombre_usuario=usuario.nombre_usuario,
            email=usuario.email,
            nombre_completo=usuario.nombre_completo,
            activo=usuario.activo,
            es_superusuario=usuario.es_superusuario,
            tipo_autenticacion=usuario.tipo_autenticacion,
            fecha_creacion=usuario.fecha_creacion,
            fecha_actualizacion=usuario.fecha_actualizacion,
            ultimo_acceso=usuario.ultimo_acceso
        )
