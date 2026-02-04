"""
Endpoint CRUD Consolidado para Parámetros SDS
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.models import Usuario
from app.database.session import get_db_session
from app.core.crud.parametro_factory import ParametroFactory, TipoParametro
from pydantic import BaseModel


router = APIRouter(prefix="/api/v2/parametros", tags=["Parámetros SDS Consolidado"])

# Alias para compatibilidad con frontend
@router.get("/crud/categorias-senal")
async def listar_categorias_senal_crud(
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Alias para listar categorías de señal (compatibilidad)"""
    from app.services.senal_service_v2 import SenalServiceV2
    service = SenalServiceV2(db)
    categorias = await service.listar_categorias_senal()
    return [
        {
            "id_categoria_senales": categoria.id_categoria_senales,
            "id_parent_categoria_senales": categoria.id_parent_categoria_senales,
            "nombre_categoria_senal": categoria.nombre_categoria_senal,
            "descripcion_categoria_senal": categoria.descripcion_categoria_senal,
            "color": categoria.color,
            "nivel": categoria.nivel,
            "umbral_bajo": categoria.umbral_bajo,
            "umbral_alto": categoria.umbral_alto,
        }
        for categoria in categorias
    ]

@router.post("/crud/categorias-senal", status_code=201)
async def crear_categoria_senal(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db_session)
):
    """Crear categoría de señal (sin autenticación para debug)"""
    from sqlalchemy import text
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Creando categoría con payload: {payload}")
        
        # Obtener el siguiente ID
        max_id_result = await db.execute(
            text("SELECT COALESCE(MAX(id_categoria_senales), 0) + 1 FROM sds.categoria_senal")
        )
        next_id = max_id_result.scalar()
        
        result = await db.execute(
            text("""
                INSERT INTO sds.categoria_senal (
                    id_categoria_senales, id_parent_categoria_senales, nombre_categoria_senal, 
                    descripcion_categoria_senal, color, nivel, umbral_bajo, umbral_alto,
                    fecha_actualizacion
                ) VALUES (:id, :parent, :nombre, :desc, :color, :nivel, :bajo, :alto, NOW())
                RETURNING id_categoria_senales
            """),
            {
                "id": next_id,
                "parent": payload.get("id_parent_categoria_senales", 0),
                "nombre": payload.get("nombre_categoria_senal", ""),
                "desc": payload.get("descripcion_categoria_senal"),
                "color": payload.get("color", "#CCCCCC"),
                "nivel": payload.get("nivel", 1),
                "bajo": payload.get("umbral_bajo", 0.0),
                "alto": payload.get("umbral_alto", 100.0)
            }
        )
        await db.commit()
        id_creado = result.scalar()
        logger.info(f"Categoría creada con ID: {id_creado}")
        return {"id_categoria_senales": id_creado}
    except Exception as e:
        logger.error(f"Error creando categoría: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/crud/categorias-senal/{id_categoria}")
async def actualizar_categoria_senal(
    id_categoria: int,
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db_session)
):
    """Actualizar categoría de señal"""
    from sqlalchemy import text
    try:
        updates = []
        params = {"id": id_categoria}
        
        if "nombre_categoria_senal" in payload:
            updates.append("nombre_categoria_senal = :nombre")
            params["nombre"] = payload["nombre_categoria_senal"]
        if "descripcion_categoria_senal" in payload:
            updates.append("descripcion_categoria_senal = :desc")
            params["desc"] = payload["descripcion_categoria_senal"]
        if "color" in payload:
            updates.append("color = :color")
            params["color"] = payload["color"]
        if "nivel" in payload:
            updates.append("nivel = :nivel")
            params["nivel"] = payload["nivel"]
        if "umbral_bajo" in payload:
            updates.append("umbral_bajo = :bajo")
            params["bajo"] = payload["umbral_bajo"]
        if "umbral_alto" in payload:
            updates.append("umbral_alto = :alto")
            params["alto"] = payload["umbral_alto"]
        
        if not updates:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
        result = await db.execute(
            text(f"""
                UPDATE sds.categoria_senal
                SET {', '.join(updates)}
                WHERE id_categoria_senales = :id
                RETURNING id_categoria_senales
            """),
            params
        )
        await db.commit()
        
        if not result.scalar():
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        
        return {"id_categoria_senales": id_categoria}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/crud/categorias-senal/{id_categoria}", status_code=204)
async def eliminar_categoria_senal(
    id_categoria: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Eliminar categoría de señal"""
    from sqlalchemy import text
    try:
        result = await db.execute(
            text("DELETE FROM sds.categoria_senal WHERE id_categoria_senales = :id RETURNING id_categoria_senales"),
            {"id": id_categoria}
        )
        await db.commit()
        
        if not result.scalar():
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crud/categorias-senal/arbol")
async def obtener_arbol_categorias_senal(
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener árbol jerárquico de categorías de señal"""
    from app.services.senal_service_v2 import SenalServiceV2
    service = SenalServiceV2(db)
    categorias = await service.listar_categorias_senal()
    
    # Construir árbol
    categorias_dict = {cat.id_categoria_senales: {
        "id_categoria_senales": cat.id_categoria_senales,
        "id_parent_categoria_senales": cat.id_parent_categoria_senales,
        "nombre_categoria_senal": cat.nombre_categoria_senal,
        "descripcion_categoria_senal": cat.descripcion_categoria_senal,
        "color": cat.color,
        "nivel": cat.nivel,
        "umbral_bajo": cat.umbral_bajo,
        "umbral_alto": cat.umbral_alto,
        "hijos": []
    } for cat in categorias}
    
    raices = []
    for cat in categorias:
        if cat.id_parent_categoria_senales == 0:
            raices.append(categorias_dict[cat.id_categoria_senales])
        elif cat.id_parent_categoria_senales in categorias_dict:
            categorias_dict[cat.id_parent_categoria_senales]["hijos"].append(
                categorias_dict[cat.id_categoria_senales]
            )
    
    return raices


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
