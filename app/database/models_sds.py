"""
Modelos SQLAlchemy para el esquema SDS (Sistema de Detección de Señales) v2
"""
from sqlalchemy import Column, SmallInteger, Text, Numeric, ForeignKey, TIMESTAMP, String, Integer, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base

class CategoriaAnalisisSenal(Base):
    __tablename__ = 'categoria_analisis_senal'
    __table_args__ = {'schema': 'sds'}
    
    id_categoria_analisis_senal = Column(SmallInteger, primary_key=True)
    nombre_categoria_analisis = Column(Text, nullable=False)
    descripcion_categoria_analisis = Column(Text)
    
    senales = relationship("SenalDetectada", back_populates="categoria_analisis")

class CategoriaSenal(Base):
    __tablename__ = 'categoria_senal'
    __table_args__ = {'schema': 'sds'}
    
    id_categoria_senales = Column(SmallInteger, primary_key=True)
    id_parent_categoria_senales = Column(SmallInteger)
    nombre_categoria_senal = Column(Text)
    descripcion_categoria_senal = Column(Text)
    color_categoria = Column(String(20))
    nivel = Column(SmallInteger)
    ultimo_usuario_id = Column(Integer, nullable=True)
    ultimo_usuario_nombre = Column(String(100), nullable=True)
    ultima_actualizacion = Column(DateTime, nullable=True, default=datetime.utcnow)
    
    senales = relationship("SenalDetectada", back_populates="categoria_senal")

class SenalDetectada(Base):
    __tablename__ = 'senal_detectada'
    __table_args__ = {'schema': 'sds'}
    
    id_senal_detectada = Column(SmallInteger, primary_key=True)
    id_categoria_senal = Column(SmallInteger, ForeignKey('sds.categoria_senal.id_categoria_senales'), nullable=False)
    fecha_deteccion = Column(TIMESTAMP(timezone=True))
    id_categoria_analisis_senal = Column(SmallInteger, ForeignKey('sds.categoria_analisis_senal.id_categoria_analisis_senal'), nullable=False)
    score_riesgo = Column(Numeric(5, 2))
    fecha_actualizacion = Column(TIMESTAMP(timezone=True))
    
    categoria_senal = relationship("CategoriaSenal", foreign_keys=[id_categoria_senal], lazy="joined")
    categoria_analisis = relationship("CategoriaAnalisisSenal", foreign_keys=[id_categoria_analisis_senal], lazy="joined")
    resultados_observacion = relationship("ResultadoObservacionSenal", back_populates="senal", lazy="joined")

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
