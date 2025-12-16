from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.database.models import Usuario, Sesion
from app.auth.providers import AuthProviderFactory
from app.auth.tokens import TokenManager
from app.schemas.auth import (
    TipoAutenticacion, UsuarioActual, TokenResponse
)
from app.core.logging import get_logger, audit_logger
from app.core.exceptions import (
    AuthenticationError, UserInactiveError,
    ValidationError, InvalidTokenError
)
from app.core.security import (
    verify_password, validate_username, calculate_expiration
)
from app.config import get_settings

settings = get_settings()

# Repository Pattern - Arquitectura Hexagonal
from app.domain.repositories import (
    IUsuarioRepository,
    ISesionRepository,
    IPermisoRepository,
)
from app.core.repository_factories import (
    get_usuario_repository,
    get_sesion_repository,
    get_permiso_repository,
)

logger = get_logger(__name__)


class AuthService:
    
    def __init__(
        self,
        db: AsyncSession,
        usuario_repo: Optional[IUsuarioRepository] = None,
        sesion_repo: Optional[ISesionRepository] = None,
        permiso_repo: Optional[IPermisoRepository] = None
    ):
        self.db = db
        self.token_manager = TokenManager()
        
        # Inyección de dependencias con factories como fallback
        self.usuario_repo = usuario_repo or get_usuario_repository(db)
        self.sesion_repo = sesion_repo or get_sesion_repository(db)
        self.permiso_repo = permiso_repo or get_permiso_repository(db)
    
    async def autenticar_usuario(
        self,
        nombre_usuario: str,
        contrasena: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenResponse:
        logger.info(
            "inicio_autenticacion",
            username=nombre_usuario,
            ip_address=ip_address
        )
        
        # Validar entrada (sin validar palabras reservadas en login)
        is_valid, error = validate_username(nombre_usuario, check_reserved=False)
        if not is_valid:
            raise ValidationError(error)
        
        # Buscar usuario existente usando repositorio
        usuario = await self.usuario_repo.find_by_username(nombre_usuario)
        
        if usuario:
            # Usuario existe, verificar estado
            if not usuario.activo:
                logger.warning("usuario_inactivo_intento_login", user_id=usuario.id)
                audit_logger.log_authentication(
                    username=nombre_usuario,
                    success=False,
                    ip_address=ip_address or "unknown",
                    user_agent=user_agent or "unknown",
                    method=usuario.tipo_autenticacion,
                    reason="usuario_inactivo"
                )
                raise UserInactiveError()
            
            # Verificar bloqueo
            if await self._usuario_bloqueado(usuario):
                raise AuthenticationError("Usuario bloqueado por múltiples intentos fallidos")
            
            # Autenticar según tipo configurado
            auth_exitosa = await self._autenticar_con_provider(usuario, nombre_usuario, contrasena)
            
            if not auth_exitosa:
                await self._registrar_intento_fallido(usuario)
                audit_logger.log_authentication(
                    username=nombre_usuario,
                    success=False,
                    ip_address=ip_address or "unknown",
                    user_agent=user_agent or "unknown",
                    method=usuario.tipo_autenticacion,
                    reason="credenciales_invalidas"
                )
                raise AuthenticationError("Credenciales inválidas")
            
            await self._resetear_intentos_fallidos(usuario)
        
        else:
            # Usuario no existe, intentar con proveedores externos
            usuario = await self._autenticar_usuario_nuevo(nombre_usuario, contrasena)
            
            if not usuario:
                audit_logger.log_authentication(
                    username=nombre_usuario,
                    success=False,
                    ip_address=ip_address or "unknown",
                    user_agent=user_agent or "unknown",
                    method="unknown",
                    reason="usuario_no_encontrado"
                )
                raise AuthenticationError("Credenciales inválidas")
        
        # Actualizar último acceso usando repositorio
        await self.usuario_repo.update_last_login(usuario.id, datetime.utcnow(), ip_address)
        await self.db.commit()
        
        # Crear tokens
        tokens = await self._crear_sesion(usuario, ip_address, user_agent)
        
        audit_logger.log_authentication(
            username=nombre_usuario,
            success=True,
            ip_address=ip_address or "unknown",
            user_agent=user_agent or "unknown",
            method=usuario.tipo_autenticacion
        )
        
        logger.info("autenticacion_exitosa", user_id=usuario.id)
        
        return tokens
    
    async def _usuario_bloqueado(self, usuario: Usuario) -> bool:
        if usuario.fecha_bloqueo is None:
            return False
        tiempo_bloqueado = datetime.utcnow() - usuario.fecha_bloqueo
        if tiempo_bloqueado.total_seconds() > 1800:  # 30 minutos
            # Desbloquear automáticamente usando repositorio
            await self.usuario_repo.unblock_user(usuario.id)
            await self.db.commit()
            return False
        
        return True
    
    async def _autenticar_con_provider(
        self,
        usuario: Usuario,
        nombre_usuario: str,
        contrasena: str
    ) -> bool:
        tipo_auth = TipoAutenticacion(usuario.tipo_autenticacion)
        if tipo_auth == TipoAutenticacion.local:
            if not usuario.contrasena_hash:
                return False
            return verify_password(contrasena, usuario.contrasena_hash)
        else:
            try:
                provider = AuthProviderFactory.get_provider(tipo_auth)
                result = await provider.autenticar(nombre_usuario, contrasena)
                
                if result:
                    await self._actualizar_info_usuario(usuario, result)
                    return True
                
                return False
            except Exception as e:
                logger.error("error_provider_autenticacion", error=str(e))
                return False
    
    async def _autenticar_usuario_nuevo(
        self,
        nombre_usuario: str,
        contrasena: str
    ) -> Optional[Usuario]:
        for provider in AuthProviderFactory.get_available_providers():
            if provider.get_tipo() == TipoAutenticacion.local:
                continue
            try:
                result = await provider.autenticar(nombre_usuario, contrasena)
                
                if result and result.get("nombre_usuario"):
                    usuario = await self._crear_usuario_desde_provider(result, provider.get_tipo())
                    logger.info("usuario_creado_desde_provider", user_id=usuario.id)
                    return usuario
            except Exception as e:
                logger.error("error_autenticacion_provider", error=str(e))
                continue
        
        return None
    
    async def _crear_usuario_desde_provider(
        self,
        datos: Dict[str, Any],
        tipo_auth: TipoAutenticacion
    ) -> Usuario:
        usuario = Usuario(
            nombre_usuario=datos["nombre_usuario"].lower(),
            email=datos.get("email"),
            nombre_completo=datos.get("nombre_completo"),
            telefono=datos.get("telefono"),
            departamento=datos.get("departamento"),
            cargo=datos.get("cargo"),
            tipo_autenticacion=tipo_auth.value,
            id_externo=datos.get("id_externo"),
            activo=True,
            es_superusuario=False
        )
        self.db.add(usuario)
        await self.db.commit()
        await self.db.refresh(usuario)
        
        return usuario
    
    async def _actualizar_info_usuario(self, usuario: Usuario, datos: Dict[str, Any]):
        usuario.email = datos.get("email") or usuario.email
        usuario.nombre_completo = datos.get("nombre_completo") or usuario.nombre_completo
        usuario.fecha_actualizacion = datetime.utcnow()
        await self.db.commit()
    async def _registrar_intento_fallido(self, usuario: Usuario):
        intentos = await self.usuario_repo.increment_failed_login(usuario.id)
        if intentos >= 5:
            await self.usuario_repo.block_user(usuario.id, datetime.utcnow())
            logger.warning("usuario_bloqueado_intentos_fallidos", user_id=usuario.id)
        
        await self.db.commit()
    
    async def _resetear_intentos_fallidos(self, usuario: Usuario):
        await self.usuario_repo.reset_failed_login(usuario.id)
        await self.db.commit()
    async def _crear_sesion(
        self,
        usuario: Usuario,
        ip_address: Optional[str],
        user_agent: Optional[str]
    ) -> TokenResponse:
        # Validar límite de sesiones activas
        sesiones_activas = await self.sesion_repo.get_active_sessions(usuario.id)
        
        if len(sesiones_activas) >= settings.max_active_sessions_per_user:
            # Cerrar la sesión más antigua
            sesion_mas_antigua = min(sesiones_activas, key=lambda s: s.fecha_creacion)
            await self.sesion_repo.invalidate_session(sesion_mas_antigua.id)
            
            logger.info(
                "sesion_antigua_cerrada_por_limite",
                user_id=usuario.id,
                sesion_cerrada_id=sesion_mas_antigua.id,
                limite=settings.max_active_sessions_per_user
            )
        
        token_data = {
            "sub": usuario.nombre_usuario,
            "user_id": usuario.id,
            "tipo_auth": usuario.tipo_autenticacion
        }
        access_token = self.token_manager.crear_access_token(token_data)
        refresh_token = self.token_manager.crear_refresh_token(token_data)
        
        fecha_exp_access = calculate_expiration(minutes=settings.access_token_expire_minutes)
        fecha_exp_refresh = calculate_expiration(days=settings.refresh_token_expire_days)
        
        sesion = Sesion(
            usuario_id=usuario.id,
            token_acceso=access_token,
            token_refresco=refresh_token,
            fecha_expiracion=fecha_exp_access,
            fecha_expiracion_refresco=fecha_exp_refresh,
            valida=True,
            direccion_ip=ip_address,
            user_agent=user_agent
        )
        
        # Usar repositorio para crear sesión
        await self.sesion_repo.create(sesion)
        await self.db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.token_manager.calcular_tiempo_expiracion()
        )
    
    async def obtener_usuario_desde_token(self, token: str) -> Optional[UsuarioActual]:
        payload = self.token_manager.validar_access_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        # Verificar sesión válida usando repositorio
        sesion = await self.sesion_repo.find_by_access_token(token)
        
        if not sesion or not sesion.valida or sesion.fecha_expiracion < datetime.utcnow():
            return None
        
        # Obtener usuario con roles y permisos usando repositorio
        usuario = await self.usuario_repo.get_with_roles_and_permisos(user_id)
        
        if not usuario:
            return None
        
        roles = await self.obtener_roles_usuario(usuario.id)
        permisos = await self.obtener_permisos_usuario(usuario.id)
        
        return UsuarioActual(
            id=usuario.id,
            nombre_usuario=usuario.nombre_usuario,
            email=usuario.email,
            nombre_completo=usuario.nombre_completo,
            activo=usuario.activo,
            es_superusuario=usuario.es_superusuario,
            tipo_autenticacion=TipoAutenticacion(usuario.tipo_autenticacion),
            roles=roles,
            permisos=permisos
        )
    
    async def obtener_roles_usuario(self, user_id: int) -> List[str]:
        usuario = await self.usuario_repo.get_with_roles(user_id)
        if not usuario:
            return []
        
        return [rol.nombre for rol in usuario.roles if rol.activo]
    
    async def obtener_permisos_usuario(self, user_id: int) -> List[str]:
        usuario = await self.usuario_repo.get_by_id(user_id)
        if not usuario:
            return []
        
        if usuario.es_superusuario:
            return ["*"]
        
        # Usar repositorio de permisos para obtener permisos efectivos
        permisos = await self.permiso_repo.get_user_permisos(user_id)
        return [p.codigo for p in permisos]
    
    async def refrescar_token(self, refresh_token: str) -> TokenResponse:
        payload = self.token_manager.validar_refresh_token(refresh_token)
        
        user_id = payload.get("user_id")
        if not user_id:
            raise InvalidTokenError("Token inválido")
        
        # Buscar sesión usando repositorio
        sesion = await self.sesion_repo.find_by_refresh_token(refresh_token)
        
        if not sesion or not sesion.valida or sesion.fecha_expiracion_refresco < datetime.utcnow():
            raise InvalidTokenError("Refresh token inválido o expirado")
        
        # Obtener usuario usando repositorio
        usuario = await self.usuario_repo.get_by_id(user_id)
        
        if not usuario or not usuario.activo:
            raise UserInactiveError()
        
        token_data = {
            "sub": usuario.nombre_usuario,
            "user_id": usuario.id,
            "tipo_auth": usuario.tipo_autenticacion
        }
        
        # Generar NUEVOS tokens (rotación de refresh token)
        nuevo_access_token = self.token_manager.crear_access_token(token_data)
        nuevo_refresh_token = self.token_manager.crear_refresh_token(token_data)
        
        # Actualizar sesión con nuevos tokens
        sesion.token_acceso = nuevo_access_token
        sesion.token_refresco = nuevo_refresh_token
        sesion.fecha_expiracion = calculate_expiration(minutes=settings.access_token_expire_minutes)
        sesion.fecha_expiracion_refresco = calculate_expiration(days=settings.refresh_token_expire_days)
        sesion.fecha_ultimo_acceso = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(
            "token_refrescado_con_rotacion",
            user_id=usuario.id,
            session_id=sesion.id
        )
        
        return TokenResponse(
            access_token=nuevo_access_token,
            refresh_token=nuevo_refresh_token,  #  Retornar NUEVO refresh token
            token_type="bearer",
            expires_in=self.token_manager.calcular_tiempo_expiracion()
        )
    
    async def cerrar_sesion(self, token: str):
        sesion = await self.sesion_repo.find_by_access_token(token)
        if sesion:
            await self.sesion_repo.invalidate_session(sesion.id)
            await self.db.commit()
            
            logger.info("sesion_cerrada", session_id=sesion.id)
