from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.database.models import Rol, Permiso
from app.schemas.auth import (
    RolCreate, RolUpdate, RolResponse,
    PermisoResponse, AsignarRolesRequest
)
from app.core.logging import get_logger, audit_logger
from app.core.exceptions import (
    ValidationError, DatabaseError, AuthorizationError,
    UserNotFoundError
)

# Repository Pattern - Arquitectura Hexagonal
from app.domain.repositories import (
    IRolRepository,
    IPermisoRepository,
    IUsuarioRepository,
)
from app.core.repository_factories import (
    get_rol_repository,
    get_permiso_repository,
    get_usuario_repository,
)

logger = get_logger(__name__)


class RBACService:
    
    def __init__(
        self,
        db: AsyncSession,
        rol_repo: Optional[IRolRepository] = None,
        permiso_repo: Optional[IPermisoRepository] = None,
        usuario_repo: Optional[IUsuarioRepository] = None
    ):
        self.db = db
        
        # Inyección de dependencias con factories como fallback
        self.rol_repo = rol_repo or get_rol_repository(db)
        self.permiso_repo = permiso_repo or get_permiso_repository(db)
        self.usuario_repo = usuario_repo or get_usuario_repository(db)
    
    # ==================== ROLES ====================
    
    async def crear_rol(
        self,
        rol_data: RolCreate,
        creado_por_id: int
    ) -> RolResponse:
        # Verificar que no exista un rol con ese nombre usando repositorio
        if await self.rol_repo.is_name_taken(rol_data.nombre):
            raise ValidationError(f"Ya existe un rol con el nombre '{rol_data.nombre}'")
        
        # Crear rol usando repositorio
        nuevo_rol = Rol(
            nombre=rol_data.nombre,
            descripcion=rol_data.descripcion,
            activo=rol_data.activo,
            es_sistema=False  # Roles creados por usuario no son de sistema
        )
        
        nuevo_rol = await self.rol_repo.create(nuevo_rol)
        
        # Asignar permisos si se proporcionaron
        if rol_data.permisos:
            await self.rol_repo.assign_permisos(nuevo_rol.id, rol_data.permisos)
        
        await self.db.commit()
        
        # Recargar rol con permisos para respuesta
        nuevo_rol = await self.rol_repo.get_with_permisos(nuevo_rol.id)
        
        # Auditoría
        audit_logger.log_configuration_change(
            user_id=creado_por_id,
            username="system",
            setting=f"rol.{nuevo_rol.nombre}",
            old_value="null",
            new_value="creado"
        )
        
        logger.info(
            "rol_creado",
            rol_id=nuevo_rol.id,
            nombre=nuevo_rol.nombre,
            creado_por=creado_por_id
        )
        
        return await self._rol_a_response(nuevo_rol)
    
    async def obtener_rol(self, rol_id: int) -> Optional[RolResponse]:
        rol = await self.rol_repo.get_with_permisos(rol_id)
        if not rol:
            return None
        
        return await self._rol_a_response(rol)
    
    async def listar_roles(
        self,
        skip: int = 0,
        limit: int = 100,
        solo_activos: bool = False
    ) -> List[RolResponse]:
        if solo_activos:
            roles = await self.rol_repo.get_active_roles(skip, limit)
        else:
            roles = await self.rol_repo.get_all(skip, limit)
        # Cargar permisos para cada rol
        roles_con_permisos = []
        for rol in roles:
            rol_completo = await self.rol_repo.get_with_permisos(rol.id)
            roles_con_permisos.append(rol_completo)
        
        return [await self._rol_a_response(rol) for rol in roles_con_permisos]
    
    async def actualizar_rol(
        self,
        rol_id: int,
        rol_data: RolUpdate,
        actualizado_por_id: int
    ) -> RolResponse:
        rol = await self.rol_repo.get_by_id(rol_id)
        if not rol:
            raise ValidationError(f"Rol con ID {rol_id} no encontrado")
        
        # Verificar si es rol del sistema
        if await self.rol_repo.is_system_role(rol_id):
            raise AuthorizationError("No se pueden modificar roles del sistema")
        
        # Actualizar campos
        if rol_data.nombre is not None:
            # Verificar que no exista otro rol con ese nombre
            if await self.rol_repo.is_name_taken(rol_data.nombre, exclude_id=rol_id):
                raise ValidationError(f"Ya existe otro rol con el nombre '{rol_data.nombre}'")
            
            rol.nombre = rol_data.nombre
        
        if rol_data.descripcion is not None:
            rol.descripcion = rol_data.descripcion
        
        if rol_data.activo is not None:
            rol.activo = rol_data.activo
        
        # Actualizar permisos si se proporcionaron
        if rol_data.permisos is not None:
            # Limpiar permisos actuales y asignar nuevos
            await self.rol_repo.clear_permisos(rol_id)
            await self.rol_repo.assign_permisos(rol_id, rol_data.permisos)
        
        rol.fecha_actualizacion = datetime.utcnow()
        await self.rol_repo.update(rol)
        await self.db.commit()
        await self.db.refresh(rol)
        
        # Auditoría
        audit_logger.log_configuration_change(
            user_id=actualizado_por_id,
            username="system",
            setting=f"rol.{rol.nombre}",
            old_value="actualizado",
            new_value="actualizado"
        )
        
        logger.info(
            "rol_actualizado",
            rol_id=rol.id,
            actualizado_por=actualizado_por_id
        )
        
        return await self._rol_a_response(rol)
    
    async def eliminar_rol(
        self,
        rol_id: int,
        eliminado_por_id: int
    ):
        rol = await self.rol_repo.get_by_id(rol_id)
        if not rol:
            raise ValidationError(f"Rol con ID {rol_id} no encontrado")
        
        if await self.rol_repo.is_system_role(rol_id):
            raise AuthorizationError("No se pueden eliminar roles del sistema")
        
        # Soft delete
        rol.activo = False
        await self.rol_repo.update(rol)
        await self.db.commit()
        
        # Auditoría
        audit_logger.log_configuration_change(
            user_id=eliminado_por_id,
            username="system",
            setting=f"rol.{rol.nombre}",
            old_value="activo",
            new_value="inactivo"
        )
        
        logger.info(
            "rol_eliminado",
            rol_id=rol.id,
            eliminado_por=eliminado_por_id
        )
    
    # ==================== PERMISOS ====================
    
    async def listar_permisos(
        self,
        recurso: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PermisoResponse]:
        if recurso:
            permisos = await self.permiso_repo.find_by_recurso(recurso)
        else:
            permisos = await self.permiso_repo.get_all(skip, limit)
        return [self._permiso_a_response(p) for p in permisos]
    
    async def obtener_permiso(self, permiso_id: int) -> Optional[PermisoResponse]:
        permiso = await self.permiso_repo.get_by_id(permiso_id)
        if not permiso:
            return None
        
        return self._permiso_a_response(permiso)
    
    async def obtener_permisos_por_recurso(self, recurso: str) -> List[PermisoResponse]:
        permisos = await self.permiso_repo.find_by_recurso(recurso)
        return [self._permiso_a_response(p) for p in permisos]
    # ==================== ASIGNACIONES ====================
    
    async def asignar_roles_a_usuario(
        self,
        usuario_id: int,
        roles_ids: List[int],
        asignado_por_id: int
    ):
        # Verificar que el usuario existe
        usuario = await self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            raise UserNotFoundError(f"Usuario con ID {usuario_id} no encontrado")
        
        # Verificar que todos los roles existen y están activos
        for rol_id in roles_ids:
            result = await self.db.execute(
                select(Rol).where(and_(Rol.id == rol_id, Rol.activo == True))
            )
            if not result.scalar_one_or_none():
                raise ValidationError(f"Rol con ID {rol_id} no existe o está inactivo")
        
        # Eliminar roles actuales
        await self.db.execute(
            delete(usuarios_roles).where(usuarios_roles.c.usuario_id == usuario_id)
        )
        
        # Asignar nuevos roles
        for rol_id in roles_ids:
            await self.db.execute(
                usuarios_roles.insert().values(
                    usuario_id=usuario_id,
                    rol_id=rol_id,
                    fecha_asignacion=datetime.utcnow()
                )
            )
        
        await self.db.commit()
        
        # Auditoría
        audit_logger.log_configuration_change(
            user_id=asignado_por_id,
            username="system",
            setting=f"usuario.{usuario_id}.roles",
            old_value="actualizado",
            new_value=str(roles_ids)
        )
        
        logger.info(
            "roles_asignados",
            usuario_id=usuario_id,
            roles=roles_ids,
            asignado_por=asignado_por_id
        )
    
    async def obtener_roles_usuario(self, usuario_id: int) -> List[RolResponse]:
        usuario = await self.usuario_repo.get_with_roles(usuario_id)
        if not usuario:
            raise UserNotFoundError(f"Usuario con ID {usuario_id} no encontrado")
        
        return [await self._rol_a_response(rol) for rol in usuario.roles if rol.activo]
    
    async def obtener_permisos_usuario(self, usuario_id: int) -> List[PermisoResponse]:
        usuario = await self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            raise UserNotFoundError(f"Usuario con ID {usuario_id} no encontrado")
        
        # Superusuarios tienen todos los permisos
        if usuario.es_superusuario:
            todos_permisos = await self.permiso_repo.get_all(skip=0, limit=1000)
            return [self._permiso_a_response(p) for p in todos_permisos]
        
        # Obtener permisos efectivos del usuario
        permisos = await self.permiso_repo.get_user_permisos(usuario_id)
        return [self._permiso_a_response(p) for p in permisos]
    
    async def usuario_tiene_permiso(
        self,
        usuario_id: int,
        codigo_permiso: str
    ) -> bool:
        usuario = await self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            return False
        
        # Superusuarios tienen todos los permisos
        if usuario.es_superusuario:
            return True
        
        # Usar repositorio para verificar permiso
        return await self.permiso_repo.user_has_permiso(usuario_id, codigo_permiso)
    
    async def usuario_tiene_rol(
        self,
        usuario_id: int,
        nombre_rol: str
    ) -> bool:
        usuario = await self.usuario_repo.get_with_roles(usuario_id)
        if not usuario:
            return False
        
        for rol in usuario.roles:
            if rol.activo and rol.nombre == nombre_rol:
                return True
        
        return False
    
    # ==================== HELPERS PRIVADOS ====================
    
    async def _asignar_permisos_a_rol(
        self,
        rol_id: int,
        codigos_permisos: List[str]
    ):
        for codigo in codigos_permisos:
            result = await self.db.execute(
                select(Permiso).where(Permiso.codigo == codigo)
            )
            permiso = result.scalar_one_or_none()
            if not permiso:
                logger.warning(
                    "permiso_no_encontrado",
                    codigo=codigo,
                    rol_id=rol_id
                )
                continue
            
            await self.db.execute(
                roles_permisos.insert().values(
                    rol_id=rol_id,
                    permiso_id=permiso.id,
                    fecha_asignacion=datetime.utcnow()
                )
            )
    
    async def _rol_a_response(self, rol: Rol) -> RolResponse:
        permisos_codigos = [p.codigo for p in rol.permisos]
        return RolResponse(
            id=rol.id,
            nombre=rol.nombre,
            descripcion=rol.descripcion,
            activo=rol.activo,
            fecha_creacion=rol.fecha_creacion,
            permisos=permisos_codigos
        )
    
    def _permiso_a_response(self, permiso: Permiso) -> PermisoResponse:
        return PermisoResponse(
            id=permiso.id,
            codigo=permiso.codigo,
            nombre=permiso.nombre,
            descripcion=permiso.descripcion,
            recurso=permiso.recurso,
            accion=permiso.accion,
            fecha_creacion=permiso.fecha_creacion
        )
    # ==================== INICIALIZACIÓN ====================
    
    async def inicializar_roles_sistema(self):
        logger.info("inicializando_roles_sistema")
        
        # Definir permisos básicos
        permisos_base = [
            # Usuarios
            ("usuarios.leer", "Leer Usuarios", "Ver información de usuarios", "usuarios", "leer"),
            ("usuarios.crear", "Crear Usuarios", "Crear nuevos usuarios", "usuarios", "crear"),
            ("usuarios.actualizar", "Actualizar Usuarios", "Modificar usuarios existentes", "usuarios", "actualizar"),
            ("usuarios.eliminar", "Eliminar Usuarios", "Eliminar usuarios", "usuarios", "eliminar"),
            
            # Roles
            ("roles.leer", "Leer Roles", "Ver roles del sistema", "roles", "leer"),
            ("roles.crear", "Crear Roles", "Crear nuevos roles", "roles", "crear"),
            ("roles.actualizar", "Actualizar Roles", "Modificar roles existentes", "roles", "actualizar"),
            ("roles.eliminar", "Eliminar Roles", "Eliminar roles", "roles", "eliminar"),
            
            # Alertas (ejemplo para el sistema de la Defensoría)
            ("alertas.leer", "Leer Alertas", "Ver alertas del sistema", "alertas", "leer"),
            ("alertas.crear", "Crear Alertas", "Crear nuevas alertas", "alertas", "crear"),
            ("alertas.actualizar", "Actualizar Alertas", "Modificar alertas", "alertas", "actualizar"),
            ("alertas.eliminar", "Eliminar Alertas", "Eliminar alertas", "alertas", "eliminar"),
            ("alertas.clasificar", "Clasificar Alertas", "Clasificar y categorizar alertas", "alertas", "clasificar"),
            
            # Reportes
            ("reportes.leer", "Leer Reportes", "Ver reportes del sistema", "reportes", "leer"),
            ("reportes.generar", "Generar Reportes", "Generar nuevos reportes", "reportes", "generar"),
            
            # Auditoría
            ("auditoria.leer", "Leer Auditoría", "Ver logs de auditoría", "auditoria", "leer"),
            
            ("configuracion.leer", "Leer Configuración", "Ver configuración del sistema", "configuracion", "leer"),
            ("configuracion.actualizar", "Actualizar Configuración", "Modificar configuración", "configuracion", "actualizar"),
        ]
        
        # Crear permisos si no existen
        for codigo, nombre, descripcion, recurso, accion in permisos_base:
            result = await self.db.execute(
                select(Permiso).where(Permiso.codigo == codigo)
            )
            if not result.scalar_one_or_none():
                permiso = Permiso(
                    codigo=codigo,
                    nombre=nombre,
                    descripcion=descripcion,
                    recurso=recurso,
                    accion=accion
                )
                self.db.add(permiso)
        
        await self.db.flush()
        
        # Definir roles del sistema
        roles_sistema = [
            ("Administrador", "Acceso completo al sistema", [
                "usuarios.leer", "usuarios.crear", "usuarios.actualizar", "usuarios.eliminar",
                "roles.leer", "roles.crear", "roles.actualizar", "roles.eliminar",
                "alertas.leer", "alertas.crear", "alertas.actualizar", "alertas.eliminar", "alertas.clasificar",
                "reportes.leer", "reportes.generar",
                "auditoria.leer",
                "configuracion.leer", "configuracion.actualizar"
            ]),
            ("Analista", "Analista de alertas y reportes", [
                "alertas.leer", "alertas.crear", "alertas.actualizar", "alertas.clasificar",
                "reportes.leer", "reportes.generar",
                "usuarios.leer"
            ]),
            ("Operador", "Operador básico del sistema", [
                "alertas.leer", "alertas.crear",
                "reportes.leer"
            ]),
            ("Auditor", "Auditor del sistema", [
                "usuarios.leer",
                "roles.leer",
                "alertas.leer",
                "reportes.leer",
                "auditoria.leer"
            ])
        ]
        
        # Crear roles si no existen
        for nombre, descripcion, permisos_codigos in roles_sistema:
            result = await self.db.execute(
                select(Rol).where(Rol.nombre == nombre)
            )
            rol = result.scalar_one_or_none()
            
            if not rol:
                rol = Rol(
                    nombre=nombre,
                    descripcion=descripcion,
                    activo=True,
                    es_sistema=True
                )
                self.db.add(rol)
                await self.db.flush()
                
                # Asignar permisos
                await self._asignar_permisos_a_rol(rol.id, permisos_codigos)
                
                logger.info("rol_sistema_creado", rol=nombre)
        
        await self.db.commit()
        logger.info("roles_sistema_inicializados")
