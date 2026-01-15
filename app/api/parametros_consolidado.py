"""
Endpoint CRUD Consolidado para Parámetros SDS
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.models import Usuario
from app.database.session import get_db_session
from app.core.crud.parametro_factory import ParametroFactory, TipoParametro
from pydantic import BaseModel


router = APIRouter(prefix="/api/v2/parametros", tags=["Parámetros SDS Consolidado"])


@router.get("/tipos")
async def listar_tipos_disponibles():
    """Listar todos los tipos de parámetros disponibles"""
    return {
        "tipos_disponibles": ParametroFactory.get_available_types(),
        "descripcion": "Tipos de parámetros que se pueden gestionar através del CRUD consolidado"
    }


@router.get("/{tipo}", response_model=List[Any])
async def listar_parametros(
    tipo: str = Path(..., description="Tipo de parámetro"),
    categoria_analisis: Optional[int] = Query(None, description="Filtrar por categoría de análisis"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar parámetros de un tipo específico"""
    
    # Validar tipo
    if not ParametroFactory.is_valid_type(tipo):
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de parámetro no válido. Tipos disponibles: {ParametroFactory.get_available_types()}"
        )
    
    tipo_enum = TipoParametro(tipo)
    crud = ParametroFactory.get_crud(tipo_enum)
    
    # Aplicar filtros específicos
    if categoria_analisis is not None and hasattr(crud, 'get_by_categoria_analisis'):
        items = await crud.get_by_categoria_analisis(db, categoria_analisis, skip, limit)
    elif activo is not None and hasattr(crud, 'get_active_only') and activo:
        items = await crud.get_active_only(db, skip, limit)
    else:
        # Crear filtros dinámicos
        filters = {}
        if categoria_analisis is not None:
            filters["id_categoria_analisis_senal"] = categoria_analisis
        if activo is not None:
            filters["activo"] = activo
            
        items = await crud.get_all(db, skip=skip, limit=limit, filters=filters)
    
    return items


@router.get("/{tipo}/{id_item}", response_model=Any)
async def obtener_parametro(
    tipo: str = Path(..., description="Tipo de parámetro"),
    id_item: int = Path(..., description="ID del parámetro"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener un parámetro específico por ID"""
    
    if not ParametroFactory.is_valid_type(tipo):
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de parámetro no válido. Tipos disponibles: {ParametroFactory.get_available_types()}"
        )
    
    tipo_enum = TipoParametro(tipo)
    crud = ParametroFactory.get_crud(tipo_enum)
    
    item = await crud.get_by_id_or_404(db, id_item)
    return item


@router.post("/{tipo}", response_model=Any, status_code=status.HTTP_201_CREATED)
async def crear_parametro(
    payload: BaseModel,  # Será validado dinámicamente
    tipo: str = Path(..., description="Tipo de parámetro"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Crear un nuevo parámetro"""
    
    if not ParametroFactory.is_valid_type(tipo):
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de parámetro no válido. Tipos disponibles: {ParametroFactory.get_available_types()}"
        )
    
    tipo_enum = TipoParametro(tipo)
    crud = ParametroFactory.get_crud(tipo_enum)
    schemas = ParametroFactory.get_schemas(tipo_enum)
    
    # Validar payload contra el schema correcto
    try:
        validated_payload = schemas["create"](**payload.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Datos de entrada inválidos: {str(e)}"
        )
    
    item = await crud.create(db, validated_payload)
    return item


@router.put("/{tipo}/{id_item}", response_model=Any)
async def actualizar_parametro(
    payload: BaseModel,  # Será validado dinámicamente
    tipo: str = Path(..., description="Tipo de parámetro"),
    id_item: int = Path(..., description="ID del parámetro"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualizar un parámetro existente"""
    
    if not ParametroFactory.is_valid_type(tipo):
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de parámetro no válido. Tipos disponibles: {ParametroFactory.get_available_types()}"
        )
    
    tipo_enum = TipoParametro(tipo)
    crud = ParametroFactory.get_crud(tipo_enum)
    schemas = ParametroFactory.get_schemas(tipo_enum)
    
    # Validar payload contra el schema correcto
    try:
        validated_payload = schemas["update"](**payload.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Datos de entrada inválidos: {str(e)}"
        )
    
    item = await crud.update(db, id_item, validated_payload)
    return item


@router.delete("/{tipo}/{id_item}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_parametro(
    tipo: str = Path(..., description="Tipo de parámetro"),
    id_item: int = Path(..., description="ID del parámetro"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Eliminar un parámetro"""
    
    if not ParametroFactory.is_valid_type(tipo):
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de parámetro no válido. Tipos disponibles: {ParametroFactory.get_available_types()}"
        )
    
    tipo_enum = TipoParametro(tipo)
    crud = ParametroFactory.get_crud(tipo_enum)
    
    await crud.delete(db, id_item)


# ==================== ENDPOINTS BATCH (BONUS) ====================

class BatchOperation(BaseModel):
    """Schema para operaciones en lote"""
    ids: List[int]
    operation: str  # 'activate', 'deactivate', 'delete'


@router.post("/{tipo}/batch")
async def operacion_lote(
    operation: BatchOperation,
    tipo: str = Path(..., description="Tipo de parámetro"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Realizar operaciones en lote sobre múltiples parámetros"""
    
    if not ParametroFactory.is_valid_type(tipo):
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de parámetro no válido. Tipos disponibles: {ParametroFactory.get_available_types()}"
        )
    
    tipo_enum = TipoParametro(tipo)
    crud = ParametroFactory.get_crud(tipo_enum)
    schemas = ParametroFactory.get_schemas(tipo_enum)
    
    results = {"success": [], "errors": []}
    
    for item_id in operation.ids:
        try:
            if operation.operation == "delete":
                await crud.delete(db, item_id)
                results["success"].append(item_id)
            elif operation.operation in ["activate", "deactivate"]:
                # Solo para parámetros que tienen campo 'activo'
                try:
                    update_payload = schemas["update"](activo=operation.operation == "activate")
                    await crud.update(db, item_id, update_payload)
                    results["success"].append(item_id)
                except Exception:
                    results["errors"].append({
                        "id": item_id,
                        "error": f"Operación {operation.operation} no soportada para este tipo"
                    })
            else:
                results["errors"].append({
                    "id": item_id,
                    "error": f"Operación no válida: {operation.operation}"
                })
        except Exception as e:
            results["errors"].append({
                "id": item_id,
                "error": str(e)
            })
    
    return {
        "operation": operation.operation,
        "processed": len(operation.ids),
        "successful": len(results["success"]),
        "failed": len(results["errors"]),
        "results": results
    }


# ==================== ENDPOINTS ESTADÍSTICAS ====================

@router.get("/{tipo}/estadisticas")
async def obtener_estadisticas(
    tipo: str = Path(..., description="Tipo de parámetro"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener estadísticas del tipo de parámetro"""
    
    if not ParametroFactory.is_valid_type(tipo):
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de parámetro no válido. Tipos disponibles: {ParametroFactory.get_available_types()}"
        )
    
    tipo_enum = TipoParametro(tipo)
    crud = ParametroFactory.get_crud(tipo_enum)
    
    # Obtener totales
    total_items = await crud.get_all(db, limit=999999)  # Obtener todos para contar
    total = len(total_items)
    
    # Contar activos si aplica
    activos = 0
    if hasattr(crud.model, 'activo'):
        activos_items = await crud.get_all(db, filters={"activo": True}, limit=999999)
        activos = len(activos_items)
    
    return {
        "tipo": tipo,
        "total": total,
        "activos": activos,
        "inactivos": total - activos if hasattr(crud.model, 'activo') else 0,
        "tiene_estado_activo": hasattr(crud.model, 'activo')
    }