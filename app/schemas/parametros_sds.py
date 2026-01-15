"""
Schemas para la configuración de parámetros SDS (categorías y catálogos).
"""
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CategoriaAnalisisBase(BaseModel):
    nombre_categoria_analisis: str = Field(..., min_length=1, max_length=200)
    descripcion_categoria_analisis: Optional[str] = None


class CategoriaAnalisisCreate(CategoriaAnalisisBase):
    pass


class CategoriaAnalisisUpdate(BaseModel):
    nombre_categoria_analisis: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion_categoria_analisis: Optional[str] = None


class CategoriaAnalisisResponse(CategoriaAnalisisBase):
    id_categoria_analisis_senal: int

    model_config = ConfigDict(from_attributes=True)


class ConductaVulneratoriaBase(BaseModel):
    nombre_conducta: str = Field(..., min_length=1, max_length=200)
    descripcion_conducta: Optional[str] = None
    codigo_conducta: Optional[str] = None
    peso_conducta: Optional[Decimal] = Field(None, ge=0, le=100)
    id_categoria_analisis_senal: int
    activo: Optional[bool] = True


class ConductaVulneratoriaCreate(ConductaVulneratoriaBase):
    pass


class ConductaVulneratoriaUpdate(BaseModel):
    nombre_conducta: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion_conducta: Optional[str] = None
    codigo_conducta: Optional[str] = None
    peso_conducta: Optional[Decimal] = Field(None, ge=0, le=100)
    id_categoria_analisis_senal: Optional[int] = None
    activo: Optional[bool] = None


class ConductaVulneratoriaResponse(ConductaVulneratoriaBase):
    id_conducta_vulneratoria: int

    model_config = ConfigDict(from_attributes=True)


class PalabraClaveBase(BaseModel):
    palabra_clave: str = Field(..., min_length=1, max_length=150)
    contexto: Optional[str] = None
    id_categoria_analisis_senal: int
    activo: Optional[bool] = True


class PalabraClaveCreate(PalabraClaveBase):
    pass


class PalabraClaveUpdate(BaseModel):
    palabra_clave: Optional[str] = Field(None, min_length=1, max_length=150)
    contexto: Optional[str] = None
    id_categoria_analisis_senal: Optional[int] = None
    activo: Optional[bool] = None


class PalabraClaveResponse(PalabraClaveBase):
    id_palabra_clave: int

    model_config = ConfigDict(from_attributes=True)


class EmoticonBase(BaseModel):
    codigo_emoticon: str = Field(..., min_length=1, max_length=50)
    descripcion_emoticon: Optional[str] = None
    id_categoria_analisis_senal: int
    activo: Optional[bool] = True


class EmoticonCreate(EmoticonBase):
    pass


class EmoticonUpdate(BaseModel):
    codigo_emoticon: Optional[str] = Field(None, min_length=1, max_length=50)
    descripcion_emoticon: Optional[str] = None
    id_categoria_analisis_senal: Optional[int] = None
    activo: Optional[bool] = None


class EmoticonResponse(EmoticonBase):
    id_emoticon: int

    model_config = ConfigDict(from_attributes=True)


class FraseClaveBase(BaseModel):
    frase: str = Field(..., min_length=1, max_length=250)
    contexto: Optional[str] = None
    id_categoria_analisis_senal: int
    activo: Optional[bool] = True


class FraseClaveCreate(FraseClaveBase):
    pass


class FraseClaveUpdate(BaseModel):
    nombre_frase_clave: Optional[str] = Field(None, min_length=1, max_length=250)
    peso_frase_clave: Optional[Decimal] = Field(None, ge=0, le=100)
    id_categoria_analisis_senal: Optional[int] = None


class FraseClaveResponse(FraseClaveBase):
    id_frase_clave: int

    model_config = ConfigDict(from_attributes=True)


class CategoriaSenalBase(BaseModel):
    nombre_categoria_senal: str = Field(..., min_length=1, max_length=200)
    descripcion_categoria_senal: Optional[str] = None
    color_categoria: Optional[str] = Field(None, max_length=50)
    nivel: int = Field(..., ge=1)
    id_parent_categoria_senales: Optional[int] = None
    umbral_bajo: Optional[Decimal] = Field(None, ge=0, le=100)
    umbral_alto: Optional[Decimal] = Field(None, ge=0, le=100)


class CategoriaSenalCreate(CategoriaSenalBase):
    pass


class CategoriaSenalUpdate(BaseModel):
    nombre_categoria_senal: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion_categoria_senal: Optional[str] = None
    color_categoria: Optional[str] = Field(None, max_length=50)
    nivel: Optional[int] = Field(None, ge=1)
    id_parent_categoria_senales: Optional[int] = None
    umbral_bajo: Optional[Decimal] = Field(None, ge=0, le=100)
    umbral_alto: Optional[Decimal] = Field(None, ge=0, le=100)


class CategoriaSenalResponse(CategoriaSenalBase):
    id_categoria_senal: int

    model_config = ConfigDict(from_attributes=True)


class FiguraPublicaBase(BaseModel):
    nombre_actor: Optional[str] = None
    peso_actor: Optional[Decimal] = Field(None, ge=0, le=100)
    id_categoria_observacion: Optional[int] = None


class FiguraPublicaCreate(FiguraPublicaBase):
    pass


class FiguraPublicaUpdate(BaseModel):
    nombre_actor: Optional[str] = None
    peso_actor: Optional[Decimal] = Field(None, ge=0, le=100)
    id_categoria_observacion: Optional[int] = None


class FiguraPublicaResponse(FiguraPublicaBase):
    id_figura_publica: int

    model_config = ConfigDict(from_attributes=True)


class InfluencerBase(BaseModel):
    nombre_influencer: Optional[str] = None
    peso_influencer: Optional[Decimal] = Field(None, ge=0, le=100)
    id_categoria_observacion: Optional[int] = None


class InfluencerCreate(InfluencerBase):
    pass


class InfluencerUpdate(BaseModel):
    nombre_influencer: Optional[str] = None
    peso_influencer: Optional[Decimal] = Field(None, ge=0, le=100)
    id_categoria_observacion: Optional[int] = None


class InfluencerResponse(InfluencerBase):
    id_influencer: int

    model_config = ConfigDict(from_attributes=True)


class MedioDigitalBase(BaseModel):
    nombre_medio_digital: Optional[str] = None
    peso_medio_digital: Optional[Decimal] = Field(None, ge=0, le=100)
    id_categoria_observacion: Optional[int] = None


class MedioDigitalCreate(MedioDigitalBase):
    pass


class MedioDigitalUpdate(BaseModel):
    nombre_medio_digital: Optional[str] = None
    peso_medio_digital: Optional[Decimal] = Field(None, ge=0, le=100)
    id_categoria_observacion: Optional[int] = None


class MedioDigitalResponse(MedioDigitalBase):
    id_medio_digital: int

    model_config = ConfigDict(from_attributes=True)


class EntidadBase(BaseModel):
    nombre_entidad: Optional[str] = None
    peso_entidad: Optional[Decimal] = Field(None, ge=0, le=100)
    id_categoria_observacion: Optional[int] = None


class EntidadCreate(EntidadBase):
    pass


class EntidadUpdate(BaseModel):
    nombre_entidad: Optional[str] = None
    peso_entidad: Optional[Decimal] = Field(None, ge=0, le=100)
    id_categoria_observacion: Optional[int] = None


class EntidadResponse(EntidadBase):
    id_entidades: int

    model_config = ConfigDict(from_attributes=True)
