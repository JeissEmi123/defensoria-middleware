"""
CRUD Base Genérico para Parámetros SDS
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.database.session import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseCRUD(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUD genérico para todos los parámetros SDS
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    @property
    @abstractmethod
    def primary_key_name(self) -> str:
        """Nombre de la columna primary key"""
        pass
    
    @property
    @abstractmethod
    def entity_name(self) -> str:
        """Nombre de la entidad para mensajes de error"""
        pass
    
    @property
    @abstractmethod
    def unique_field_name(self) -> str:
        """Campo que debe ser único (para validaciones)"""
        pass

    async def get_by_id(self, db: AsyncSession, id_value: int) -> Optional[ModelType]:
        """Obtener por ID"""
        result = await db.execute(
            select(self.model).where(getattr(self.model, self.primary_key_name) == id_value)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id_or_404(self, db: AsyncSession, id_value: int) -> ModelType:
        """Obtener por ID o lanzar 404"""
        entity = await self.get_by_id(db, id_value)
        if not entity:
            raise HTTPException(status_code=404, detail=f"{self.entity_name} no encontrada")
        return entity

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Listar todas las entidades con filtros opcionales"""
        query = select(self.model)
        
        # Aplicar filtros si existen
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """Crear nueva entidad"""
        # Validar unicidad del campo principal
        await self._ensure_unique_field(db, obj_in)
        
        # Obtener siguiente ID
        next_id = await self._get_next_id(db)
        
        # Crear objeto
        obj_data = obj_in.model_dump()
        obj_data[self.primary_key_name] = next_id
        
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        
        try:
            await db.commit()
            await db.refresh(db_obj)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Error al crear {self.entity_name}")
        
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        id_value: int,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Actualizar entidad existente"""
        db_obj = await self.get_by_id_or_404(db, id_value)
        
        updates = obj_in.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(
                status_code=400,
                detail="Debe enviar al menos un campo para actualizar"
            )
        
        # Validar unicidad si se está actualizando el campo único
        if self.unique_field_name in updates:
            await self._ensure_unique_field(
                db, obj_in, exclude_id=id_value
            )
        
        for field, value in updates.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id_value: int) -> bool:
        """Eliminar entidad (verificar dependencias primero)"""
        db_obj = await self.get_by_id_or_404(db, id_value)
        
        # Verificar dependencias antes de eliminar
        await self._check_dependencies(db, db_obj)
        
        await db.delete(db_obj)
        await db.commit()
        return True

    async def _get_next_id(self, db: AsyncSession) -> int:
        """Obtener siguiente ID disponible"""
        result = await db.execute(
            select(func.coalesce(func.max(getattr(self.model, self.primary_key_name)), 0) + 1)
        )
        return result.scalar()

    async def _ensure_unique_field(
        self,
        db: AsyncSession,
        obj_in: CreateSchemaType,
        exclude_id: Optional[int] = None
    ):
        """Validar que el campo único no esté duplicado"""
        if not hasattr(obj_in, self.unique_field_name):
            return
        
        value = getattr(obj_in, self.unique_field_name)
        if not value:
            return
        
        query = select(self.model).where(
            func.lower(getattr(self.model, self.unique_field_name)) == value.lower()
        )
        
        if exclude_id is not None:
            query = query.where(getattr(self.model, self.primary_key_name) != exclude_id)
        
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"{self.entity_name} con ese valor ya existe"
            )

    async def _check_dependencies(self, db: AsyncSession, db_obj: ModelType):
        """Verificar dependencias antes de eliminar (implementar en subclases si necesario)"""
        pass


class ParametroCRUD(BaseCRUD):
    """
    CRUD específico para parámetros que tienen relación con categoria_analisis_senal
    """
    
    async def get_by_categoria_analisis(
        self,
        db: AsyncSession,
        categoria_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Obtener parámetros filtrados por categoría de análisis"""
        query = select(self.model).where(
            getattr(self.model, "id_categoria_analisis_senal") == categoria_id
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def get_active_only(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Obtener solo parámetros activos"""
        query = select(self.model).where(
            getattr(self.model, "activo") == True
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()