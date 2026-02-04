"""
Schemas Pydantic para el módulo de señales v2
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# ==================== SCHEMAS BASE ====================

class CategoriaAnalisisSenalBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_categoria_analisis_senal: int
    nombre_categoria_analisis: str
    descripcion_categoria_analisis: Optional[str] = None

class CategoriaSenalBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_categoria_senales: int
    nombre_categoria_senal: Optional[str] = None
    descripcion_categoria_senal: Optional[str] = None
    nivel: Optional[int] = None
    color_categoria: Optional[str] = None
    ultimo_usuario_id: Optional[int] = None
    ultimo_usuario_nombre: Optional[str] = None
    ultima_actualizacion: Optional[datetime] = None

class CategoriaSenalUpdate(BaseModel):
    color_categoria: Optional[str] = Field(default=None, min_length=4, max_length=20)
    descripcion_categoria_senal: Optional[str] = Field(default=None, min_length=1)

class SenalDetectadaUpdate(BaseModel):
    id_categoria_senal: Optional[int] = None
    id_categoria_analisis_senal: Optional[int] = None
    score_riesgo: Optional[Decimal] = Field(default=None, ge=0, le=100)
    fecha_deteccion: Optional[datetime] = None
    estado: Optional[str] = None
    descripcion_cambio: Optional[str] = None
    confirmo_revision: Optional[bool] = Field(default=None, description="El revisor confirma haber validado el cambio de tipo de señal")
    email_revisor: Optional[str] = Field(default=None, description="Email del usuario que está modificando la señal para recibir notificaciones")

class CategoriaObservacionBase(BaseModel):
    id_categoria_observacion: int
    codigo_categoria_observacion: str
    nombre_categoria_observacion: Optional[str] = None
    nivel: Optional[int] = None
    peso_categoria_observacion: Optional[Decimal] = None

class ResultadoObservacionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    codigo_categoria_observacion: str
    resultado_observacion_categoria: Decimal
    nombre_categoria_observacion: Optional[str] = None

# ==================== SCHEMAS DE RESPUESTA ====================

class SenalDetectadaListItem(BaseModel):
    """Schema para items en lista de señales (HU-DF001, HU-DF002)"""
    model_config = ConfigDict(from_attributes=True)
    
    id_senal_detectada: int
    fecha_deteccion: datetime
    score_riesgo: Decimal
    categoria_analisis: CategoriaAnalisisSenalBase
    categoria_senal: CategoriaSenalBase

class SenalDetectadaDetalle(BaseModel):
    """Schema para detalle completo de señal (HU-DF003)"""
    model_config = ConfigDict(from_attributes=True)
    
    id_senal_detectada: int
    fecha_deteccion: datetime
    fecha_actualizacion: datetime
    score_riesgo: Decimal
    categoria_analisis: CategoriaAnalisisSenalBase
    categoria_senal: CategoriaSenalBase
    resultados_observacion: List[ResultadoObservacionBase] = []

class AlertaCritica(BaseModel):
    """Schema para alertas críticas del home (HU-DF008)"""
    model_config = ConfigDict(from_attributes=True)
    
    id_senal_detectada: int
    fecha_deteccion: datetime
    score_riesgo: Decimal
    categoria_analisis: CategoriaAnalisisSenalBase
    categoria_senal: CategoriaSenalBase

# ==================== SCHEMAS DE FILTROS ====================

class FiltrosSenales(BaseModel):
    """Filtros para búsqueda de señales (HU-DF007)"""
    id_categoria_analisis_senal: Optional[int] = None
    id_categoria_senal: Optional[int] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    score_min: Optional[Decimal] = Field(None, ge=0, le=100)
    score_max: Optional[Decimal] = Field(None, ge=0, le=100)

# ==================== SCHEMAS DE RESPUESTA PAGINADA ====================

class SenalesListResponse(BaseModel):
    """Respuesta paginada de señales"""
    items: List[SenalDetectadaListItem]
    total: int
    skip: int
    limit: int
    has_more: bool

class HomeResponse(BaseModel):
    """Respuesta para el home (HU-DF008)"""
    alertas_criticas: List[AlertaCritica]
    total_senales_hoy: int
    total_crisis: int
    total_paracrisis: int

class HistorialSenalItem(BaseModel):
    """Schema para items del historial de señales"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    id_senal_detectada: int
    usuario_id: Optional[int] = None
    usuario_nombre: Optional[str] = None
    accion: str
    descripcion: Optional[str] = None
    estado_anterior: Optional[str] = None
    estado_nuevo: Optional[str] = None
    datos_adicionales: Optional[dict] = None
    fecha_registro: datetime
    ip_address: Optional[str] = None
