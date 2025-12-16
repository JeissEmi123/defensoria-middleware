"""
Schemas Pydantic para el Sistema de Detección de Señales
Schemas de validación para las entidades del módulo de señales
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# ==================== CATEGORIA ANALISIS SENAL ====================

class CategoriaAnalisisSenalBase(BaseModel):
    """Schema base para categoría de análisis de señales"""
    nombre_categoria_analisis: str = Field(..., min_length=1, max_length=150, 
        description="Nombre de la categoría de análisis")
    propiedades_conductas_vulneratorias: Optional[Dict[str, Any]] = Field(None, 
        description="Definiciones de conductas vulneratorias")
    palabras_clave_categoria: Optional[List[str]] = Field(None, 
        description="Palabras clave para detección")
    hashtags_categoria: Optional[List[str]] = Field(None, 
        description="Hashtags relevantes")
    emoticones_categoria: Optional[List[str]] = Field(None, 
        description="Emoticones asociados")
    frases_categoria: Optional[List[str]] = Field(None, 
        description="Frases típicas")


class CategoriaAnalisisSenalCreate(CategoriaAnalisisSenalBase):
    """Schema para crear categoría de análisis"""
    activo: bool = Field(True, description="Estado activo de la categoría")


class CategoriaAnalisisSenalUpdate(BaseModel):
    """Schema para actualizar categoría de análisis"""
    nombre_categoria_analisis: Optional[str] = Field(None, min_length=1, max_length=150)
    propiedades_conductas_vulneratorias: Optional[Dict[str, Any]] = None
    palabras_clave_categoria: Optional[List[str]] = None
    hashtags_categoria: Optional[List[str]] = None
    emoticones_categoria: Optional[List[str]] = None
    frases_categoria: Optional[List[str]] = None
    activo: Optional[bool] = None


class CategoriaAnalisisSenalResponse(CategoriaAnalisisSenalBase):
    """Schema de respuesta para categoría de análisis"""
    id: int
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== CATEGORIA SENAL ====================

class CategoriaSenalBase(BaseModel):
    """Schema base para categoría de señal"""
    nombre_categoria_senal: str = Field(..., min_length=1, max_length=100,
        description="Nombre de la categoría de señal")
    parent_categoria_senal_id: Optional[int] = Field(None,
        description="ID de la categoría padre (para jerarquía)")
    nivel: int = Field(..., ge=1, le=10,
        description="Nivel jerárquico de la categoría")
    color: Optional[str] = Field(None, max_length=50,
        description="Color en formato hex (#RRGGBB)")
    descripcion: Optional[str] = Field(None,
        description="Descripción de la categoría")


class CategoriaSenalCreate(CategoriaSenalBase):
    """Schema para crear categoría de señal"""
    activo: bool = Field(True, description="Estado activo")


class CategoriaSenalUpdate(BaseModel):
    """Schema para actualizar categoría de señal"""
    nombre_categoria_senal: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_categoria_senal_id: Optional[int] = None
    nivel: Optional[int] = Field(None, ge=1, le=10)
    color: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class CategoriaSenalResponse(CategoriaSenalBase):
    """Schema de respuesta para categoría de señal"""
    id_categoria_senal: int
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    subcategorias: List['CategoriaSenalResponse'] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ==================== SENAL DETECTADA ====================

class SenalDetectadaBase(BaseModel):
    """Schema base para señal detectada"""
    id_categoria_senal: Optional[int] = Field(None,
        description="ID de la categoría de señal (RUIDO, PARACRISIS, CRISIS)")
    id_categoria_analisis: Optional[int] = Field(None,
        description="ID de la categoría de análisis (tipo de violencia)")
    score_riesgo: Optional[Decimal] = Field(None, ge=0, le=100,
        description="Score de riesgo (0-100)")
    categorias_observacion: Optional[Dict[str, Any]] = Field(None,
        description="Categorías adicionales y observaciones")
    plataformas_digitales: Optional[List[str]] = Field(None,
        description="Plataformas donde se detectó: Twitter, Facebook, etc.")
    contenido_detectado: Optional[str] = Field(None,
        description="Contenido que generó la alerta")
    metadatos: Optional[Dict[str, Any]] = Field(None,
        description="Metadatos: autor, ubicación, fecha_publicacion, etc.")
    url_origen: Optional[str] = Field(None, max_length=500,
        description="URL del contenido original")


class SenalDetectadaCreate(SenalDetectadaBase):
    """Schema para crear señal detectada"""
    fecha_deteccion: Optional[datetime] = Field(None,
        description="Fecha de detección (por defecto: ahora)")
    estado: str = Field('DETECTADA',
        description="Estado inicial: DETECTADA, EN_REVISION, VALIDADA, RECHAZADA, RESUELTA")

    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v: str) -> str:
        estados_validos = ['DETECTADA', 'EN_REVISION', 'VALIDADA', 'RECHAZADA', 'RESUELTA']
        if v not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {", ".join(estados_validos)}')
        return v


class SenalDetectadaUpdate(BaseModel):
    """Schema para actualizar señal detectada"""
    id_categoria_senal: Optional[int] = None
    id_categoria_analisis: Optional[int] = None
    score_riesgo: Optional[Decimal] = Field(None, ge=0, le=100)
    categorias_observacion: Optional[Dict[str, Any]] = None
    plataformas_digitales: Optional[List[str]] = None
    contenido_detectado: Optional[str] = None
    metadatos: Optional[Dict[str, Any]] = None
    estado: Optional[str] = None
    url_origen: Optional[str] = Field(None, max_length=500)
    usuario_asignado_id: Optional[int] = None
    notas_resolucion: Optional[str] = None

    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        estados_validos = ['DETECTADA', 'EN_REVISION', 'VALIDADA', 'RECHAZADA', 'RESUELTA']
        if v not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {", ".join(estados_validos)}')
        return v


class SenalDetectadaResponse(SenalDetectadaBase):
    """Schema de respuesta para señal detectada"""
    id_senal_detectada: int
    fecha_deteccion: datetime
    fecha_actualizacion: datetime
    estado: str
    usuario_asignado_id: Optional[int]
    fecha_resolucion: Optional[datetime]
    notas_resolucion: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class SenalDetectadaDetalle(SenalDetectadaResponse):
    """Schema detallado con relaciones"""
    categoria_senal: Optional[CategoriaSenalResponse]
    categoria_analisis: Optional[CategoriaAnalisisSenalResponse]
    historial: List['HistorialSenalResponse'] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ==================== HISTORIAL SENAL ====================

class HistorialSenalBase(BaseModel):
    """Schema base para historial de señal"""
    id_senal_detectada: int = Field(...,
        description="ID de la señal detectada")
    accion: str = Field(..., min_length=1, max_length=100,
        description="Tipo de acción: CREACION, ASIGNACION, CAMBIO_ESTADO, RESOLUCION")
    descripcion: Optional[str] = Field(None,
        description="Descripción de la acción")
    estado_anterior: Optional[str] = Field(None, max_length=50)
    estado_nuevo: Optional[str] = Field(None, max_length=50)
    datos_adicionales: Optional[Dict[str, Any]] = Field(None,
        description="Datos adicionales de contexto")


class HistorialSenalCreate(HistorialSenalBase):
    """Schema para crear entrada en historial"""
    usuario_id: Optional[int] = Field(None,
        description="ID del usuario que realiza la acción")
    ip_address: Optional[str] = Field(None, max_length=45)


class HistorialSenalResponse(HistorialSenalBase):
    """Schema de respuesta para historial"""
    id: int
    usuario_id: Optional[int]
    fecha_registro: datetime
    ip_address: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# ==================== SCHEMAS DE FILTROS Y BÚSQUEDA ====================

class SenalDetectadaFiltros(BaseModel):
    """Filtros para búsqueda de señales"""
    estado: Optional[str] = None
    id_categoria_senal: Optional[int] = None
    id_categoria_analisis: Optional[int] = None
    score_riesgo_min: Optional[Decimal] = Field(None, ge=0, le=100)
    score_riesgo_max: Optional[Decimal] = Field(None, ge=0, le=100)
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    plataforma: Optional[str] = None
    usuario_asignado_id: Optional[int] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class EstadisticasSenales(BaseModel):
    """Estadísticas de señales detectadas"""
    total_senales: int
    por_estado: Dict[str, int]
    por_categoria_senal: Dict[str, int]
    por_categoria_analisis: Dict[str, int]
    score_promedio: Optional[float]
    senales_ultima_semana: int
    senales_ultimo_mes: int


# ==================== SCHEMAS DE OPERACIONES MASIVAS ====================

class AsignacionMasiva(BaseModel):
    """Schema para asignación masiva de señales"""
    ids_senales: List[int] = Field(..., min_length=1)
    usuario_asignado_id: int
    notas: Optional[str] = None


class CambioEstadoMasivo(BaseModel):
    """Schema para cambio de estado masivo"""
    ids_senales: List[int] = Field(..., min_length=1)
    nuevo_estado: str
    notas: Optional[str] = None

    @field_validator('nuevo_estado')
    @classmethod
    def validar_estado(cls, v: str) -> str:
        estados_validos = ['DETECTADA', 'EN_REVISION', 'VALIDADA', 'RECHAZADA', 'RESUELTA']
        if v not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {", ".join(estados_validos)}')
        return v


# Resolver forward references para relaciones circulares
CategoriaSenalResponse.model_rebuild()
SenalDetectadaDetalle.model_rebuild()
