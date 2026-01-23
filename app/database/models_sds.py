"""
Modelos SQLAlchemy para el esquema SDS (Sistema de Detección de Señales) v2
"""
from sqlalchemy import Column, SmallInteger, Text, Numeric, ForeignKey, TIMESTAMP, String, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from sqlalchemy.orm import relationship

from app.database.session import Base

class CategoriaAnalisisSenal(Base):
    __tablename__ = 'categoria_analisis_senal'
    __table_args__ = {'schema': 'sds'}
    
    id_categoria_analisis_senal = Column(SmallInteger, primary_key=True)
    nombre_categoria_analisis = Column(Text, nullable=False)
    descripcion_categoria_analisis = Column(Text)
    
    senales = relationship("SenalDetectada", back_populates="categoria_analisis")
    conductas = relationship("ConductaVulneratoria", back_populates="categoria_analisis")
    palabras_clave = relationship("PalabraClave", back_populates="categoria_analisis")
    emoticones = relationship("Emoticon", back_populates="categoria_analisis")
    frases_clave = relationship("FraseClave", back_populates="categoria_analisis")

class CategoriaSenal(Base):
    __tablename__ = 'categoria_senal'
    __table_args__ = {'schema': 'sds'}
    
    id_categoria_senales = Column(SmallInteger, primary_key=True)
    id_parent_categoria_senales = Column(SmallInteger)
    nombre_categoria_senal = Column(String(100), nullable=False)
    descripcion_categoria_senal = Column(Text)
    color = Column(String(50))
    nivel = Column(SmallInteger, nullable=False)
    umbral_bajo = Column(Numeric(5, 2))
    umbral_alto = Column(Numeric(5, 2))
    
    senales = relationship("SenalDetectada", back_populates="categoria_senal")

    @property
    def id_categoria_senal(self) -> int:
        return self.id_categoria_senales

    @property
    def descripcion(self) -> str:
        return self.descripcion_categoria_senal

    @property
    def color_categoria(self) -> str:
        return self.color

    @color_categoria.setter
    def color_categoria(self, value: str):
        self.color = value

    @property
    def parent_categoria_senal_id(self) -> int:
        return self.id_parent_categoria_senales

class SenalDetectada(Base):
    __tablename__ = 'senal_detectada'
    __table_args__ = {'schema': 'sds'}
    
    id_senal_detectada = Column(SmallInteger, primary_key=True)
    id_categoria_senal = Column(SmallInteger, ForeignKey('sds.categoria_senal.id_categoria_senales'), nullable=False)
    fecha_deteccion = Column(TIMESTAMP(timezone=True))
    id_categoria_analisis = Column(SmallInteger, ForeignKey('sds.categoria_analisis_senal.id_categoria_analisis_senal'), nullable=True)
    score_riesgo = Column(Numeric(5, 2))
    fecha_actualizacion = Column(TIMESTAMP(timezone=True))
    categorias_observacion = Column(Text)  # JSONB en la base de datos pero usando Text por compatibilidad
    plataformas_digitales = Column(Text)   # JSONB en la base de datos pero usando Text por compatibilidad
    contenido_detectado = Column(Text)
    metadatos = Column(Text)               # JSONB en la base de datos pero usando Text por compatibilidad
    estado = Column(String(50), nullable=False, default='DETECTADA')
    url_origen = Column(String(500))
    usuario_asignado_id = Column(Integer, ForeignKey('usuarios.id'))
    fecha_resolucion = Column(TIMESTAMP(timezone=True))
    notas_resolucion = Column(Text)
    
    categoria_senal = relationship("CategoriaSenal", foreign_keys=[id_categoria_senal], lazy="joined")
    categoria_analisis = relationship("CategoriaAnalisisSenal", foreign_keys=[id_categoria_analisis], lazy="joined")
    resultados_observacion = relationship("ResultadoObservacionSenal", back_populates="senal", lazy="joined")
    historial = relationship("HistorialSenal", back_populates="senal", cascade="all, delete-orphan")

class CategoriaObservacion(Base):
    __tablename__ = 'categoria_observacion'
    __table_args__ = {'schema': 'sds'}
    
    id_categoria_observacion = Column(SmallInteger, primary_key=True)
    id_parent_categoria_observacion = Column(SmallInteger)
    codigo_categoria_observacion = Column(Text, nullable=False)
    nombre_categoria_observacion = Column(Text)
    descripcion_categoria_observacion = Column(Text)
    nivel = Column(SmallInteger)
    peso_categoria_observacion = Column(Numeric(5, 2))
    figuras_publicas = relationship("FiguraPublica", back_populates="categoria_observacion")
    influencers = relationship("Influencer", back_populates="categoria_observacion")
    medios_digitales = relationship("MedioDigital", back_populates="categoria_observacion")
    entidades = relationship("Entidad", back_populates="categoria_observacion")
    
    resultados = relationship("ResultadoObservacionSenal", back_populates="categoria_observacion")

class ResultadoObservacionSenal(Base):
    __tablename__ = 'resultado_observacion_senal'
    __table_args__ = {'schema': 'sds'}
    
    id_resultado_observacion_senal = Column(SmallInteger, primary_key=True)
    id_senal_detectada = Column(SmallInteger, ForeignKey('sds.senal_detectada.id_senal_detectada'), nullable=False)
    id_categoria_observacion = Column(SmallInteger, ForeignKey('sds.categoria_observacion.id_categoria_observacion'), nullable=False)
    resultado_observacion_categoria = Column(Numeric(5, 2))
    codigo_categoria_observacion = Column(Text)
    
    senal = relationship("SenalDetectada", back_populates="resultados_observacion")
    categoria_observacion = relationship("CategoriaObservacion", back_populates="resultados")


class ConductaVulneratoria(Base):
    __tablename__ = 'conducta_vulneratoria'
    __table_args__ = {'schema': 'sds'}

    id_conducta_vulneratoria = Column(
        'id_conducta_vulneratorias',
        SmallInteger,
        primary_key=True
    )
    nombre_conducta = Column(Text, nullable=False)
    descripcion_conducta = Column(Text)
    codigo_conducta = Column(Text)
    peso_conducta = Column(Numeric(5, 2))
    id_categoria_analisis_senal = Column(SmallInteger, ForeignKey('sds.categoria_analisis_senal.id_categoria_analisis_senal'), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)

    categoria_analisis = relationship("CategoriaAnalisisSenal", back_populates="conductas")


class PalabraClave(Base):
    __tablename__ = 'palabra_clave'
    __table_args__ = {'schema': 'sds'}

    id_palabra_clave = Column(SmallInteger, primary_key=True)
    palabra_clave = Column(Text, nullable=False)
    contexto = Column(Text)
    id_categoria_analisis_senal = Column(SmallInteger, ForeignKey('sds.categoria_analisis_senal.id_categoria_analisis_senal'), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)

    categoria_analisis = relationship("CategoriaAnalisisSenal", back_populates="palabras_clave")


class Emoticon(Base):
    __tablename__ = 'emoticon'
    __table_args__ = {'schema': 'sds'}

    id_emoticon = Column(SmallInteger, primary_key=True)
    codigo_emoticon = Column(Text, nullable=False)
    descripcion_emoticon = Column(Text)
    id_categoria_analisis_senal = Column(SmallInteger, ForeignKey('sds.categoria_analisis_senal.id_categoria_analisis_senal'), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)

    categoria_analisis = relationship("CategoriaAnalisisSenal", back_populates="emoticones")


class FraseClave(Base):
    __tablename__ = 'frase_clave'
    __table_args__ = {'schema': 'sds'}

    id_frase_clave = Column(SmallInteger, primary_key=True)
    frase = Column(Text, nullable=False)
    contexto = Column(Text)
    id_categoria_analisis_senal = Column(SmallInteger, ForeignKey('sds.categoria_analisis_senal.id_categoria_analisis_senal'), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)

    categoria_analisis = relationship("CategoriaAnalisisSenal", back_populates="frases_clave")


class FiguraPublica(Base):
    __tablename__ = 'figuras_publicas'
    __table_args__ = {'schema': 'sds'}

    id_figura_publica = Column(SmallInteger, primary_key=True)
    nombre_actor = Column(Text)
    peso_actor = Column(Numeric(5, 2))
    id_categoria_observacion = Column(SmallInteger, ForeignKey('sds.categoria_observacion.id_categoria_observacion'))

    categoria_observacion = relationship("CategoriaObservacion", back_populates="figuras_publicas")


class Influencer(Base):
    __tablename__ = 'influencers'
    __table_args__ = {'schema': 'sds'}

    id_influencer = Column(SmallInteger, primary_key=True)
    nombre_influencer = Column(Text)
    peso_influencer = Column(Numeric(5, 2))
    id_categoria_observacion = Column(SmallInteger, ForeignKey('sds.categoria_observacion.id_categoria_observacion'))

    categoria_observacion = relationship("CategoriaObservacion", back_populates="influencers")


class MedioDigital(Base):
    __tablename__ = 'medios_digitales'
    __table_args__ = {'schema': 'sds'}

    id_medio_digital = Column(SmallInteger, primary_key=True)
    nombre_medio_digital = Column(Text)
    peso_medio_digital = Column(Numeric(5, 2))
    id_categoria_observacion = Column(SmallInteger, ForeignKey('sds.categoria_observacion.id_categoria_observacion'))

    categoria_observacion = relationship("CategoriaObservacion", back_populates="medios_digitales")


class Entidad(Base):
    __tablename__ = 'entidades'
    __table_args__ = {'schema': 'sds'}

    id_entidad = Column('id_entidades', SmallInteger, primary_key=True)
    nombre_entidad = Column(Text)
    peso_entidad = Column(Numeric(5, 2))
    id_categoria_observacion = Column(SmallInteger, ForeignKey('sds.categoria_observacion.id_categoria_observacion'))

    categoria_observacion = relationship("CategoriaObservacion", back_populates="entidades")


class HistorialSenal(Base):
    """
    Historial de cambios y acciones sobre señales detectadas en esquema SDS.
    Proporciona trazabilidad completa de las señales.
    """
    __tablename__ = 'historial_senal'
    __table_args__ = {'schema': 'sds'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_senal_detectada = Column(Integer, ForeignKey('sds.senal_detectada.id_senal_detectada', ondelete='CASCADE'), 
        nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='SET NULL'), 
        nullable=True)
    accion = Column(String(100), nullable=False,
        comment='Tipo de acción: CREACION, ASIGNACION, CAMBIO_ESTADO, RESOLUCION, actualizacion_senal, etc.')
    descripcion = Column(Text, nullable=True)
    estado_anterior = Column(String(50), nullable=True)
    estado_nuevo = Column(String(50), nullable=True)
    datos_adicionales = Column(JSONB, nullable=True,
        comment='Datos adicionales de la acción en formato JSON')
    fecha_registro = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now)
    ip_address = Column(String(45), nullable=True)
    
    # Relación con señal detectada
    senal = relationship("SenalDetectada", back_populates="historial")
    
    def __repr__(self):
        return f"<HistorialSenal(id={self.id}, senal_id={self.id_senal_detectada}, accion='{self.accion}')>"
