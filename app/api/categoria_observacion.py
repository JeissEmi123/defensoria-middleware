"""
CRUD Endpoints para Categoría de Observación
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func
from app.database.session import get_db_session
from app.database.models_sds import CategoriaObservacion
from app.schemas.categoria_observacion import (
    CategoriaObservacionCreate,
    CategoriaObservacionUpdate,
    CategoriaObservacionResponse
)
from app.core.dependencies import get_current_user
from app.database.models import Usuario

router = APIRouter()


@router.get("", response_model=List[CategoriaObservacionResponse])
async def listar_categorias(
    nivel: Optional[int] = Query(None, ge=1, le=10),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar todas las categorías de observación"""
    query = select(CategoriaObservacion).order_by(CategoriaObservacion.nivel, CategoriaObservacion.codigo_categoria_observacion)
    
    if nivel:
        query = query.where(CategoriaObservacion.nivel == nivel)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{id_categoria}", response_model=CategoriaObservacionResponse)
async def obtener_categoria(
    id_categoria: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener una categoría por ID"""
    result = await db.execute(
        select(CategoriaObservacion).where(CategoriaObservacion.id_categoria_observacion == id_categoria)
    )
    categoria = result.scalar_one_or_none()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    return categoria


@router.post("", response_model=CategoriaObservacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_categoria(
    data: CategoriaObservacionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Crear nueva categoría de observación"""
    # Verificar código único
    result = await db.execute(
        select(CategoriaObservacion).where(
            CategoriaObservacion.codigo_categoria_observacion == data.codigo_categoria_observacion
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El código ya existe")
    
    # Obtener siguiente ID
    result = await db.execute(text("SELECT COALESCE(MAX(id_categoria_observacion), 0) + 1 FROM sds.categoria_observacion"))
    nuevo_id = result.scalar()
    
    nueva_categoria = CategoriaObservacion(
        id_categoria_observacion=nuevo_id,
        **data.model_dump()
    )
    
    db.add(nueva_categoria)
    await db.commit()
    await db.refresh(nueva_categoria)
    
    return nueva_categoria


@router.put("/{id_categoria}", response_model=CategoriaObservacionResponse)
async def actualizar_categoria(
    id_categoria: int,
    data: CategoriaObservacionUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualizar categoría existente"""
    result = await db.execute(
        select(CategoriaObservacion).where(CategoriaObservacion.id_categoria_observacion == id_categoria)
    )
    categoria = result.scalar_one_or_none()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Verificar código único si se actualiza
    if data.codigo_categoria_observacion and data.codigo_categoria_observacion != categoria.codigo_categoria_observacion:
        result = await db.execute(
            select(CategoriaObservacion).where(
                CategoriaObservacion.codigo_categoria_observacion == data.codigo_categoria_observacion
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="El código ya existe")
    
    # Actualizar campos
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(categoria, field, value)
    
    await db.commit()
    await db.refresh(categoria)
    
    return categoria


@router.delete("/{id_categoria}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_categoria(
    id_categoria: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Eliminar categoría de observación"""
    # Verificar si tiene resultados asociados
    result = await db.execute(
        text("SELECT COUNT(*) FROM sds.resultado_observacion_senal WHERE id_categoria_observacion = :id"),
        {"id": id_categoria}
    )
    count = result.scalar()
    
    if count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar. Tiene {count} resultados asociados"
        )
    
    result = await db.execute(
        select(CategoriaObservacion).where(CategoriaObservacion.id_categoria_observacion == id_categoria)
    )
    categoria = result.scalar_one_or_none()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    await db.delete(categoria)
    await db.commit()


@router.get("/jerarquia/arbol", response_model=dict)
async def obtener_arbol_jerarquico(
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener estructura jerárquica completa"""
    result = await db.execute(
        select(CategoriaObservacion).order_by(CategoriaObservacion.nivel, CategoriaObservacion.codigo_categoria_observacion)
    )
    categorias = result.scalars().all()
    
    # Construir árbol
    arbol = {}
    for cat in categorias:
        if cat.nivel == 1:
            arbol[cat.id_categoria_observacion] = {
                "categoria": CategoriaObservacionResponse.model_validate(cat),
                "hijos": []
            }
    
    for cat in categorias:
        if cat.nivel > 1 and cat.id_parent_categoria_observacion in arbol:
            arbol[cat.id_parent_categoria_observacion]["hijos"].append(
                CategoriaObservacionResponse.model_validate(cat)
            )
    
    return {"arbol": list(arbol.values())}
