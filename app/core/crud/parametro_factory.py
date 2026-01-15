"""
Factory Pattern para Parámetros SDS
"""
from enum import Enum
from typing import Dict, Type, Union

from app.core.crud.base_crud import BaseCRUD, ParametroCRUD
from app.database.models_sds import (
    CategoriaAnalisisSenal,
    CategoriaSenal, 
    CategoriaObservacion,
    ConductaVulneratoria,
    PalabraClave,
    Emoticon,
    FraseClave,
    FiguraPublica,
    Influencer,
    MedioDigital,
    Entidad
)
from app.schemas.parametros_sds import *


class TipoParametro(str, Enum):
    """Tipos de parámetros disponibles"""
    CATEGORIAS_ANALISIS = "categorias-analisis"
    CATEGORIAS_SENAL = "categorias-senal"
    CATEGORIAS_OBSERVACION = "categorias-observacion"
    CONDUCTAS_VULNERATORIAS = "conductas-vulneratorias"
    PALABRAS_CLAVE = "palabras-clave"
    EMOTICONOS = "emoticonos"
    FRASES_CLAVE = "frases-clave"
    FIGURAS_PUBLICAS = "figuras-publicas"
    INFLUENCERS = "influencers"
    MEDIOS_DIGITALES = "medios-digitales"
    ENTIDADES = "entidades"


# ==================== CRUD ESPECÍFICOS ====================

class CategoriaAnalisisCRUD(BaseCRUD):
    @property
    def primary_key_name(self) -> str:
        return "id_categoria_analisis_senal"
    
    @property
    def entity_name(self) -> str:
        return "Categoría de análisis"
    
    @property
    def unique_field_name(self) -> str:
        return "nombre_categoria_analisis"


class CategoriaSenalCRUD(BaseCRUD):
    @property
    def primary_key_name(self) -> str:
        return "id_categoria_senal"
    
    @property
    def entity_name(self) -> str:
        return "Categoría de señal"
    
    @property
    def unique_field_name(self) -> str:
        return "nombre_categoria_senal"


class CategoriaObservacionCRUD(BaseCRUD):
    @property
    def primary_key_name(self) -> str:
        return "id_categoria_observacion"
    
    @property
    def entity_name(self) -> str:
        return "Categoría de observación"
    
    @property
    def unique_field_name(self) -> str:
        return "codigo_categoria_observacion"


class ConductaVulneratoriaCRUD(ParametroCRUD):
    @property
    def primary_key_name(self) -> str:
        return "id_conducta_vulneratoria"
    
    @property
    def entity_name(self) -> str:
        return "Conducta vulneratoria"
    
    @property
    def unique_field_name(self) -> str:
        return "nombre_conducta"


class PalabraClaveCRUD(ParametroCRUD):
    @property
    def primary_key_name(self) -> str:
        return "id_palabra_clave"
    
    @property
    def entity_name(self) -> str:
        return "Palabra clave"
    
    @property
    def unique_field_name(self) -> str:
        return "palabra_clave"


class EmoticonCRUD(ParametroCRUD):
    @property
    def primary_key_name(self) -> str:
        return "id_emoticon"
    
    @property
    def entity_name(self) -> str:
        return "Emoticon"
    
    @property
    def unique_field_name(self) -> str:
        return "codigo_emoticon"


class FraseClaveCRUD(ParametroCRUD):
    @property
    def primary_key_name(self) -> str:
        return "id_frase_clave"
    
    @property
    def entity_name(self) -> str:
        return "Frase clave"
    
    @property
    def unique_field_name(self) -> str:
        return "frase"


class FiguraPublicaCRUD(BaseCRUD):
    @property
    def primary_key_name(self) -> str:
        return "id_figura_publica"
    
    @property
    def entity_name(self) -> str:
        return "Figura pública"
    
    @property
    def unique_field_name(self) -> str:
        return "nombre_actor"


class InfluencerCRUD(BaseCRUD):
    @property
    def primary_key_name(self) -> str:
        return "id_influencer"
    
    @property
    def entity_name(self) -> str:
        return "Influencer"
    
    @property
    def unique_field_name(self) -> str:
        return "nombre_influencer"


class MedioDigitalCRUD(BaseCRUD):
    @property
    def primary_key_name(self) -> str:
        return "id_medio_digital"
    
    @property
    def entity_name(self) -> str:
        return "Medio digital"
    
    @property
    def unique_field_name(self) -> str:
        return "nombre_medio_digital"


class EntidadCRUD(BaseCRUD):
    @property
    def primary_key_name(self) -> str:
        return "id_entidades"
    
    @property
    def entity_name(self) -> str:
        return "Entidad"
    
    @property
    def unique_field_name(self) -> str:
        return "nombre_entidad"


# ==================== FACTORY REGISTRY ====================

class ParametroFactory:
    """Factory para crear instancias CRUD según el tipo de parámetro"""
    
    _registry: Dict[TipoParametro, Dict] = {
        TipoParametro.CATEGORIAS_ANALISIS: {
            "model": CategoriaAnalisisSenal,
            "crud_class": CategoriaAnalisisCRUD,
            "create_schema": CategoriaAnalisisCreate,
            "update_schema": CategoriaAnalisisUpdate,
            "response_schema": CategoriaAnalisisResponse
        },
        TipoParametro.CATEGORIAS_SENAL: {
            "model": CategoriaSenal,
            "crud_class": CategoriaSenalCRUD,
            "create_schema": CategoriaSenalCreate,
            "update_schema": CategoriaSenalUpdate,
            "response_schema": CategoriaSenalResponse
        },
        TipoParametro.CONDUCTAS_VULNERATORIAS: {
            "model": ConductaVulneratoria,
            "crud_class": ConductaVulneratoriaCRUD,
            "create_schema": ConductaVulneratoriaCreate,
            "update_schema": ConductaVulneratoriaUpdate,
            "response_schema": ConductaVulneratoriaResponse
        },
        TipoParametro.PALABRAS_CLAVE: {
            "model": PalabraClave,
            "crud_class": PalabraClaveCRUD,
            "create_schema": PalabraClaveCreate,
            "update_schema": PalabraClaveUpdate,
            "response_schema": PalabraClaveResponse
        },
        TipoParametro.EMOTICONOS: {
            "model": Emoticon,
            "crud_class": EmoticonCRUD,
            "create_schema": EmoticonCreate,
            "update_schema": EmoticonUpdate,
            "response_schema": EmoticonResponse
        },
        TipoParametro.FRASES_CLAVE: {
            "model": FraseClave,
            "crud_class": FraseClaveCRUD,
            "create_schema": FraseClaveCreate,
            "update_schema": FraseClaveUpdate,
            "response_schema": FraseClaveResponse
        },
        TipoParametro.FIGURAS_PUBLICAS: {
            "model": FiguraPublica,
            "crud_class": FiguraPublicaCRUD,
            "create_schema": FiguraPublicaCreate,
            "update_schema": FiguraPublicaUpdate,
            "response_schema": FiguraPublicaResponse
        },
        TipoParametro.INFLUENCERS: {
            "model": Influencer,
            "crud_class": InfluencerCRUD,
            "create_schema": InfluencerCreate,
            "update_schema": InfluencerUpdate,
            "response_schema": InfluencerResponse
        },
        TipoParametro.MEDIOS_DIGITALES: {
            "model": MedioDigital,
            "crud_class": MedioDigitalCRUD,
            "create_schema": MedioDigitalCreate,
            "update_schema": MedioDigitalUpdate,
            "response_schema": MedioDigitalResponse
        },
        TipoParametro.ENTIDADES: {
            "model": Entidad,
            "crud_class": EntidadCRUD,
            "create_schema": EntidadCreate,
            "update_schema": EntidadUpdate,
            "response_schema": EntidadResponse
        }
    }
    
    @classmethod
    def get_crud(cls, tipo: TipoParametro) -> BaseCRUD:
        """Obtener instancia CRUD para el tipo especificado"""
        if tipo not in cls._registry:
            raise ValueError(f"Tipo de parámetro no soportado: {tipo}")
        
        config = cls._registry[tipo]
        crud_class = config["crud_class"]
        model = config["model"]
        
        return crud_class(model)
    
    @classmethod
    def get_schemas(cls, tipo: TipoParametro) -> Dict[str, Type]:
        """Obtener schemas para el tipo especificado"""
        if tipo not in cls._registry:
            raise ValueError(f"Tipo de parámetro no soportado: {tipo}")
        
        config = cls._registry[tipo]
        return {
            "create": config["create_schema"],
            "update": config["update_schema"],
            "response": config["response_schema"]
        }
    
    @classmethod
    def get_available_types(cls) -> list[str]:
        """Obtener lista de tipos disponibles"""
        return [tipo.value for tipo in TipoParametro]
    
    @classmethod
    def is_valid_type(cls, tipo: str) -> bool:
        """Verificar si un tipo es válido"""
        try:
            TipoParametro(tipo)
            return True
        except ValueError:
            return False
