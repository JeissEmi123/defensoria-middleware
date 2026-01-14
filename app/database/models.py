# Models file
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table, Index, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
import enum

from app.database.session import Base


class TipoAutenticacion(str, enum.Enum):
    local = "local"
    ldap = "ldap"
    azure_ad = "azure_ad"

# Tabla de asociación usuarios-roles
usuarios_roles = Table(
    'usuarios_roles',
    Base.metadata,
    Column('usuario_id', Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True),
    Column('rol_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('fecha_asignacion', DateTime, nullable=False, default=datetime.now),
    Index('ix_usuarios_roles_usuario_id', 'usuario_id'),
    Index('ix_usuarios_roles_rol_id', 'rol_id')
)


# Tabla de asociación roles-permisos
roles_permisos = Table(
    'roles_permisos',
    Base.metadata,
    Column('rol_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permiso_id', Integer, ForeignKey('permisos.id', ondelete='CASCADE'), primary_key=True),
    Column('fecha_asignacion', DateTime, nullable=False, default=datetime.now),
    Index('ix_roles_permisos_rol_id', 'rol_id'),
    Index('ix_roles_permisos_permiso_id', 'permiso_id')
)


class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    nombre_completo = Column(String(255), nullable=True)
    contrasena_hash = Column(String(255), nullable=True)
    tipo_autenticacion = Column(Enum(TipoAutenticacion, name='tipo_autenticacion'), nullable=False, default='local')
    id_externo = Column(String(255), nullable=True, index=True)
    activo = Column(Boolean, nullable=False, default=True, index=True)
    es_superusuario = Column(Boolean, nullable=False, default=False)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.now)
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    ultimo_acceso = Column(DateTime, nullable=True)
    ultimo_cambio_contrasena = Column(DateTime, nullable=True)
    intentos_login_fallidos = Column(Integer, nullable=False, default=0)
    fecha_bloqueo = Column(DateTime, nullable=True)
    requiere_cambio_contrasena = Column(Boolean, nullable=False, default=False)
    telefono = Column(String(20), nullable=True)
    departamento = Column(String(100), nullable=True)
    cargo = Column(String(100), nullable=True)

    reset_token = Column(String(255), nullable=True, index=True)

    # Relaciones
    roles = relationship('Rol', secondary=usuarios_roles, back_populates='usuarios')
    sesiones = relationship('Sesion', back_populates='usuario', cascade='all, delete-orphan')
    eventos_auditoria = relationship('EventoAuditoria', back_populates='usuario')

    def __repr__(self):
        return f"<Usuario(id={self.id}, nombre_usuario='{self.nombre_usuario}')>"


class Rol(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False, index=True)
    descripcion = Column(String(255), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, index=True)
    es_sistema = Column(Boolean, nullable=False, default=False)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.now)
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relaciones
    usuarios = relationship('Usuario', secondary=usuarios_roles, back_populates='roles')
    permisos = relationship('Permiso', secondary=roles_permisos, back_populates='roles')

    def __repr__(self):
        return f"<Rol(id={self.id}, nombre='{self.nombre}')>"


class Permiso(Base):
    __tablename__ = 'permisos'
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(100), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=True)
    recurso = Column(String(50), nullable=False, index=True)
    accion = Column(String(50), nullable=False)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.now)

    # Relaciones
    roles = relationship('Rol', secondary=roles_permisos, back_populates='permisos')

    def __repr__(self):
        return f"<Permiso(id={self.id}, codigo='{self.codigo}')>"


class Sesion(Base):
    __tablename__ = 'sesiones'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False, index=True)
    token_acceso = Column(Text, nullable=False)
    access_token = Column(Text, nullable=True, index=True)
    token_refresco = Column(Text, nullable=False)
    fecha_expiracion = Column(DateTime, nullable=False, index=True)
    fecha_expiracion_refresco = Column(DateTime, nullable=False)
    valida = Column(Boolean, nullable=False, default=True, index=True)
    direccion_ip = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.now)
    fecha_ultimo_acceso = Column(DateTime, nullable=True)
    fecha_invalidacion = Column(DateTime, nullable=True)
    razon_invalidacion = Column(String(255), nullable=True)

    # Relaciones
    usuario = relationship('Usuario', back_populates='sesiones')

    def __repr__(self):
        return f"<Sesion(id={self.id}, usuario_id={self.usuario_id}, valida={self.valida})>"


class EventoAuditoria(Base):
    __tablename__ = 'eventos_auditoria'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True, index=True)
    tipo_evento = Column(String(50), nullable=False, index=True)
    recurso = Column(String(100), nullable=True)
    accion = Column(String(50), nullable=True)
    resultado = Column(String(20), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    detalles = Column(JSON, nullable=True)
    fecha_evento = Column(DateTime, nullable=False, default=datetime.now, index=True)

    # Relaciones
    usuario = relationship('Usuario', back_populates='eventos_auditoria')

    def __repr__(self):
        return f"<EventoAuditoria(id={self.id}, tipo_evento='{self.tipo_evento}', resultado='{self.resultado}')>"


class PasswordHistory(Base):
    """Historial de contraseñas para evitar reutilización"""
    __tablename__ = 'password_history'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False, index=True)
    contrasena_hash = Column(String(255), nullable=False)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.now, index=True)
    
    def __repr__(self):
        return f"<PasswordHistory(id={self.id}, usuario_id={self.usuario_id})>"


class ConfiguracionSistema(Base):
    __tablename__ = 'configuracion_sistema'
    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(100), unique=True, nullable=False, index=True)
    valor = Column(Text, nullable=True)
    tipo_dato = Column(String(20), nullable=False, default='string')
    descripcion = Column(String(255), nullable=True)
    categoria = Column(String(50), nullable=True, index=True)
    es_sensible = Column(Boolean, nullable=False, default=False)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.now)
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<ConfiguracionSistema(id={self.id}, clave='{self.clave}')>"
