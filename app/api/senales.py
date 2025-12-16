"""
Endpoints REST API para el módulo de detección de señales
Rutas: /api/v1/senales
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.services.senal_service import SenalService
from app.schemas.senales import (
    SenalDetectadaCreate,
    SenalDetectadaUpdate,
    SenalDetectadaResponse,
    SenalDetectadaDetalle,
    SenalDetectadaFiltros,
    EstadisticasSenales,
    AsignacionMasiva,
    CambioEstadoMasivo,
    CategoriaSenalResponse,
    CategoriaAnalisisSenalResponse
)
from app.core.dependencies import get_current_user
from app.database.models import Usuario
from datetime import datetime
from decimal import Decimal

router = APIRouter()


# ==================== ENDPOINTS DE LISTADO ====================

@router.get("", response_model=dict)
@router.get("/", response_model=dict)
async def listar_senales(
    skip: int = Query(0, ge=0, description="Offset para paginación"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de resultados"),
    orden: str = Query("fecha_desc", description="Ordenamiento: fecha_desc, fecha_asc, score_desc, score_asc"),
    # Filtros opcionales
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    id_categoria_senal: Optional[int] = Query(None, description="Filtrar por categoría de señal"),
    id_categoria_analisis: Optional[int] = Query(None, description="Filtrar por categoría de análisis"),
    score_min: Optional[Decimal] = Query(None, ge=0, le=100, description="Score mínimo"),
    score_max: Optional[Decimal] = Query(None, ge=0, le=100, description="Score máximo"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde (ISO format)"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta (ISO format)"),
    plataforma: Optional[str] = Query(None, description="Filtrar por plataforma digital"),
    usuario_asignado_id: Optional[int] = Query(None, description="Filtrar por usuario asignado"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Listar señales detectadas con paginación, ordenamiento y filtros
    
    **Ordenamiento disponible:**
    - `fecha_desc`: Por fecha de detección descendente (más reciente primero)
    - `fecha_asc`: Por fecha de detección ascendente
    - `score_desc`: Por score de riesgo descendente (más crítico primero)
    - `score_asc`: Por score de riesgo ascendente
    
    **Estados válidos:**
    - DETECTADA, EN_REVISION, VALIDADA, RECHAZADA, RESUELTA
    """
    # Construir filtros
    filtros = SenalDetectadaFiltros(
        estado=estado,
        id_categoria_senal=id_categoria_senal,
        id_categoria_analisis=id_categoria_analisis,
        score_riesgo_min=score_min,
        score_riesgo_max=score_max,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        plataforma=plataforma,
        usuario_asignado_id=usuario_asignado_id,
        skip=skip,
        limit=limit
    )
    
    service = SenalService(db)
    senales, total = await service.listar_senales(
        skip=skip,
        limit=limit,
        orden=orden,
        filtros=filtros
    )
    
    return {
        "senales": [SenalDetectadaResponse.model_validate(s) for s in senales],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


@router.get("/buscar", response_model=dict)
async def buscar_senales(
    q: str = Query(..., min_length=3, description="Término de búsqueda (mínimo 3 caracteres)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Búsqueda full-text en señales detectadas
    
    Busca en los campos:
    - Contenido detectado
    - URL de origen
    - Notas de resolución
    """
    service = SenalService(db)
    senales, total = await service.buscar_senales(
        busqueda=q,
        skip=skip,
        limit=limit
    )
    
    return {
        "items": [SenalDetectadaResponse.model_validate(s) for s in senales],
        "total": total,
        "skip": skip,
        "limit": limit,
        "query": q
    }


@router.get("/alertas/criticas", response_model=List[SenalDetectadaResponse])
async def obtener_alertas_criticas(
    limite: int = Query(5, ge=1, le=20, description="Número de alertas a retornar"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener top alertas críticas del día actual
    
    Retorna señales de categorías CRISIS y PARACRISIS
    detectadas en el día actual, ordenadas por score de riesgo.
    """
    service = SenalService(db)
    senales = await service.obtener_alertas_criticas(limite=limite)
    
    return [SenalDetectadaResponse.model_validate(s) for s in senales]


@router.get("/indicadores", response_model=dict)
async def obtener_indicadores(
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener indicadores del sistema de detección de señales
    
    Retorna:
    - Total de señales activas
    - Señales en revisión
    - Distribución por categoría
    """
    service = SenalService(db)
    indicadores = await service.obtener_indicadores()
    
    return indicadores


@router.get("/estadisticas", response_model=EstadisticasSenales)
async def obtener_estadisticas(
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener estadísticas completas del sistema
    
    Incluye:
    - Totales por estado
    - Distribución por categorías
    - Scores promedio
    - Tendencias temporales
    """
    service = SenalService(db)
    estadisticas = await service.obtener_estadisticas(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )
    
    return estadisticas


# ==================== ENDPOINTS DE DETALLE ====================

@router.get("/{id_senal}", response_model=SenalDetectadaDetalle)
async def obtener_senal(
    id_senal: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener detalle completo de una señal por ID
    
    Incluye:
    - Información completa de la señal
    - Categorías relacionadas
    - Historial de cambios
    - Usuario asignado
    """
    service = SenalService(db)
    senal = await service.obtener_senal(id_senal)
    
    if not senal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Señal {id_senal} no encontrada"
        )
    
    return SenalDetectadaDetalle.model_validate(senal)


@router.get("/{id_senal}/historial", response_model=dict)
async def obtener_historial_senal(
    id_senal: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener historial de cambios de una señal
    
    Retorna todas las modificaciones realizadas sobre la señal,
    ordenadas por fecha descendente (más reciente primero).
    """
    service = SenalService(db)
    senal = await service.obtener_senal(id_senal)
    
    if not senal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Señal {id_senal} no encontrada"
        )
    
    # El historial ya viene cargado por selectinload
    historial_total = senal.historial
    historial_paginado = historial_total[skip:skip + limit]
    
    return {
        "items": historial_paginado,
        "total": len(historial_total),
        "skip": skip,
        "limit": limit
    }


# ==================== ENDPOINTS DE CREACIÓN Y ACTUALIZACIÓN ====================

@router.post("/", response_model=SenalDetectadaResponse, status_code=status.HTTP_201_CREATED)
async def crear_senal(
    senal_data: SenalDetectadaCreate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear nueva señal detectada
    
    Registra automáticamente:
    - Usuario creador
    - Fecha de creación
    - Entrada en historial
    """
    service = SenalService(db)
    
    senal = await service.crear_senal(
        senal_data=senal_data,
        usuario_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )
    
    return SenalDetectadaResponse.model_validate(senal)


@router.put("/{id_senal}", response_model=SenalDetectadaResponse)
async def actualizar_senal(
    id_senal: int,
    senal_data: SenalDetectadaUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar señal existente
    
    Registra automáticamente:
    - Campos modificados
    - Usuario que modificó
    - Entrada en historial con cambios
    """
    service = SenalService(db)
    
    senal = await service.actualizar_senal(
        id_senal=id_senal,
        senal_data=senal_data,
        usuario_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )
    
    if not senal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Señal {id_senal} no encontrada"
        )
    
    return SenalDetectadaResponse.model_validate(senal)


@router.put("/{id_senal}/categoria", response_model=SenalDetectadaResponse)
async def cambiar_categoria_senal(
    id_senal: int,
    nueva_categoria_id: int,
    comentario: Optional[str] = None,
    confirmo_revision: bool = Query(..., description="Debe confirmar que revisó la señal"),
    request: Request = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cambiar categoría de una señal (RUIDO, PARACRISIS, CRISIS)
    
    Requiere:
    - Confirmación de revisión (confirmo_revision=true)
    - Comentario opcional explicando el cambio
    
    Si la nueva categoría es CRISIS, se envía notificación al coordinador.
    """
    service = SenalService(db)
    
    try:
        senal = await service.cambiar_categoria(
            id_senal=id_senal,
            nueva_categoria_id=nueva_categoria_id,
            comentario=comentario,
            confirmo_revision=confirmo_revision,
            usuario_id=current_user.id,
            ip_address=request.client.host if request and request.client else None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    if not senal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Señal {id_senal} no encontrada"
        )
    
    return SenalDetectadaResponse.model_validate(senal)


# ==================== ENDPOINTS DE OPERACIONES MASIVAS ====================

@router.post("/asignacion-masiva", response_model=dict)
async def asignar_senales_masivo(
    asignacion: AsignacionMasiva,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Asignar múltiples señales a un usuario
    
    Útil para:
    - Distribuir carga de trabajo
    - Asignar señales por especialidad
    - Reasignaciones masivas
    """
    service = SenalService(db)
    
    try:
        count = await service.asignar_masivo(
            asignacion=asignacion,
            usuario_id=current_user.id,
            ip_address=request.client.host if request.client else None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return {
        "message": f"{count} señales asignadas exitosamente",
        "count": count,
        "usuario_asignado_id": asignacion.usuario_asignado_id
    }


@router.post("/cambio-estado-masivo", response_model=dict)
async def cambiar_estado_masivo(
    cambio: CambioEstadoMasivo,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cambiar estado de múltiples señales
    
    Estados válidos:
    - DETECTADA
    - EN_REVISION
    - VALIDADA
    - RECHAZADA
    - RESUELTA
    """
    service = SenalService(db)
    
    try:
        count = await service.cambiar_estado_masivo(
            cambio=cambio,
            usuario_id=current_user.id,
            ip_address=request.client.host if request.client else None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return {
        "message": f"{count} señales actualizadas exitosamente",
        "count": count,
        "nuevo_estado": cambio.nuevo_estado
    }


# ==================== ENDPOINTS DE CATÁLOGOS ====================

@router.get("/catalogos/categorias-senal", response_model=List[CategoriaSenalResponse])
async def listar_categorias_senal(
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Listar todas las categorías de señal disponibles
    
    Incluye:
    - RUIDO, PARACRISIS, CRISIS (nivel 1)
    - Subcategorías (nivel 2+)
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.database.models import CategoriaSenal
    
    result = await db.execute(
        select(CategoriaSenal)
        .options(selectinload(CategoriaSenal.subcategorias))
        .where(CategoriaSenal.activo == True)
        .order_by(CategoriaSenal.nivel, CategoriaSenal.nombre_categoria_senal)
    )
    categorias = result.scalars().all()
    
    return [CategoriaSenalResponse.model_validate(c) for c in categorias]


@router.get("/catalogos/categorias-analisis", response_model=List[CategoriaAnalisisSenalResponse])
async def listar_categorias_analisis(
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Listar todas las categorías de análisis disponibles
    
    Incluye:
    - Reclutamiento de menores
    - Violencia política
    - Violencia digital basada en género
    """
    from sqlalchemy import select
    from app.database.models import CategoriaAnalisisSenal
    
    result = await db.execute(
        select(CategoriaAnalisisSenal)
        .where(CategoriaAnalisisSenal.activo == True)
        .order_by(CategoriaAnalisisSenal.nombre_categoria_analisis)
    )
    categorias = result.scalars().all()
    
    return [CategoriaAnalisisSenalResponse.model_validate(c) for c in categorias]
