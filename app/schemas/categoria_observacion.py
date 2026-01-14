"""
Schemas para Categoría de Observación
"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class CategoriaObservacionBase(BaseModel):
    codigo_categoria_observacion: str = Field(..., min_length=1, max_length=50)
    nombre_categoria_observacion: str = Field(..., min_length=1, max_length=200)
    descripcion_categoria_observacion: Optional[str] = None
    nivel: int = Field(..., ge=1, le=10)
    peso_categoria_observacion: Decimal = Field(..., ge=0, le=100)
    id_parent_categoria_observacion: Optional[int] = None


class CategoriaObservacionCreate(CategoriaObservacionBase):
    pass


class CategoriaObservacionUpdate(BaseModel):
    codigo_categoria_observacion: Optional[str] = Field(None, min_length=1, max_length=50)
    nombre_categoria_observacion: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion_categoria_observacion: Optional[str] = None
    nivel: Optional[int] = Field(None, ge=1, le=10)
    peso_categoria_observacion: Optional[Decimal] = Field(None, ge=0, le=100)
    id_parent_categoria_observacion: Optional[int] = None


class CategoriaObservacionResponse(CategoriaObservacionBase):
    id_categoria_observacion: int

    class Config:
        from_attributes = True
