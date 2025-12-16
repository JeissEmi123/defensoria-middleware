# Models file
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table, Index, Enum, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, UTC
import enum

Base = declarative_base()


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


# ==================== MODELOS DE DETECCIÓN DE SEÑALES ====================

class CategoriaAnalisisSenal(Base):
    """
    Categoría principal de análisis de señales digitales.
    Define los tipos de conductas vulneratorias que se monitorean.
    """
    __tablename__ = 'categoria_analisis_senal'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_categoria_analisis = Column(String(150), nullable=False, index=True)
    propiedades_conductas_vulneratorias = Column(JSON, nullable=True, 
        comment='Definiciones y propiedades de las conductas vulneratorias')
    palabras_clave_categoria = Column(JSON, nullable=True,
        comment='Lista de palabras clave asociadas a esta categoría')
    hashtags_categoria = Column(JSON, nullable=True,
        comment='Hashtags relevantes para detección')
    emoticones_categoria = Column(JSON, nullable=True,
        comment='Emoticones asociados a esta categoría')
    frases_categoria = Column(JSON, nullable=True,
        comment='Frases típicas de esta categoría')
    activo = Column(Boolean, nullable=False, default=True, index=True)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.now)
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    senales_detectadas = relationship('SenalDetectada', back_populates='categoria_analisis')
    
    def __repr__(self):
        return f"<CategoriaAnalisisSenal(id={self.id}, nombre='{self.nombre_categoria_analisis}')>"


class CategoriaSenal(Base):
    """
    Categoría jerárquica de señales (RUIDO, PARACRISIS, CRISIS, etc.).
    Permite clasificación multinivel de señales detectadas.
    """
    __tablename__ = 'categoria_senal'
    
    id_categoria_senal = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_categoria_senal = Column(String(100), nullable=False, index=True)
    parent_categoria_senal_id = Column(Integer, ForeignKey('categoria_senal.id_categoria_senal', ondelete='SET NULL'), 
        nullable=True, index=True)
    nivel = Column(Integer, nullable=False, index=True, 
        comment='Nivel jerárquico: 1=principal, 2=subcategoría, etc.')
    color = Column(String(50), nullable=True,
        comment='Color representativo en hex (#RRGGBB)')
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=False, default=True, index=True)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.now)
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    parent = relationship('CategoriaSenal', remote_side=[id_categoria_senal], backref='subcategorias')
    senales_detectadas = relationship('SenalDetectada', back_populates='categoria_senal')
    
    def __repr__(self):
        return f"<CategoriaSenal(id={self.id_categoria_senal}, nombre='{self.nombre_categoria_senal}', nivel={self.nivel})>"


class SenalDetectada(Base):
    """
    Señal detectada en plataformas digitales.
    Registro principal de eventos de riesgo detectados.
    """
    __tablename__ = 'senal_detectada'
    
    id_senal_detectada = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha_deteccion = Column(DateTime, nullable=False, default=datetime.now, index=True)
    id_categoria_senal = Column(Integer, ForeignKey('categoria_senal.id_categoria_senal', ondelete='SET NULL'), 
        nullable=True, index=True)
    id_categoria_analisis = Column(Integer, ForeignKey('categoria_analisis_senal.id', ondelete='SET NULL'), 
        nullable=True, index=True)
    score_riesgo = Column(Integer, nullable=True, index=True,
        comment='Score de riesgo: 0-100')
    categorias_observacion = Column(JSON, nullable=True,
        comment='Categorías adicionales y metadatos de observación')
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    plataformas_digitales = Column(JSON, nullable=True,
        comment='Lista de plataformas donde se detectó la señal')
    contenido_detectado = Column(Text, nullable=True,
        comment='Contenido que generó la alerta')
    metadatos = Column(JSON, nullable=True,
        comment='Metadatos adicionales: autor, ubicación, etc.')
    estado = Column(String(50), nullable=False, default='DETECTADA', index=True,
        comment='Estados: DETECTADA, EN_REVISION, VALIDADA, RECHAZADA, RESUELTA')
    url_origen = Column(String(500), nullable=True,
        comment='URL del contenido original')
    usuario_asignado_id = Column(Integer, ForeignKey('usuarios.id', ondelete='SET NULL'), 
        nullable=True, index=True)
    fecha_resolucion = Column(DateTime, nullable=True)
    notas_resolucion = Column(Text, nullable=True)
    
    # Relaciones
    categoria_senal = relationship('CategoriaSenal', back_populates='senales_detectadas')
    categoria_analisis = relationship('CategoriaAnalisisSenal', back_populates='senales_detectadas')
    usuario_asignado = relationship('Usuario')
    historial = relationship('HistorialSenal', back_populates='senal', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<SenalDetectada(id={self.id_senal_detectada}, estado='{self.estado}', score={self.score_riesgo})>"


class HistorialSenal(Base):
    """
    Historial de cambios y acciones sobre señales detectadas.
    Proporciona trazabilidad completa de las señales.
    """
    __tablename__ = 'historial_senal'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_senal_detectada = Column(Integer, ForeignKey('senal_detectada.id_senal_detectada', ondelete='CASCADE'), 
        nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='SET NULL'), 
        nullable=True, index=True)
    accion = Column(String(100), nullable=False, index=True,
        comment='Tipo de acción: CREACION, ASIGNACION, CAMBIO_ESTADO, RESOLUCION, etc.')
    descripcion = Column(Text, nullable=True)
    estado_anterior = Column(String(50), nullable=True)
    estado_nuevo = Column(String(50), nullable=True)
    datos_adicionales = Column(JSON, nullable=True,
        comment='Datos adicionales de la acción')
    fecha_registro = Column(DateTime, nullable=False, default=datetime.now, index=True)
    ip_address = Column(String(45), nullable=True)
    
    # Relaciones
    senal = relationship('SenalDetectada', back_populates='historial')
    usuario = relationship('Usuario')
    
    def __repr__(self):
        return f"<HistorialSenal(id={self.id}, senal_id={self.id_senal_detectada}, accion='{self.accion}')>"