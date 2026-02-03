"""
Endpoints REST API v2 para el módulo de detección de señales
Rutas: /api/v2/senales
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.session import get_db_session
from app.services.senal_service_v2 import SenalServiceV2
from app.core.json_utils import serialize_decimal
from app.schemas.senales_v2 import (
    SenalesListResponse,
    SenalDetectadaListItem,
    SenalDetectadaDetalle,
    HomeResponse,
    AlertaCritica,
    FiltrosSenales,
    CategoriaAnalisisSenalBase,
    CategoriaSenalBase,
    CategoriaSenalUpdate,
    SenalDetectadaUpdate
)
from app.core.dependencies import get_current_user
from app.database.models import Usuario
from app.database.models_sds import SenalDetectada

router = APIRouter()

@router.get("/recientes")
async def obtener_senales_recientes(
    limite: int = Query(5, ge=1, le=20, description="Número de señales recientes"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener las últimas señales insertadas (por defecto 5)"""
    try:
        service = SenalServiceV2(db)
        senales = await service.obtener_senales_recientes(limite=limite)
        return {
            "total": len(senales),
            "senales": senales
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.get("/panel-control")
async def panel_control(
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Panel de control con alertas críticas y métricas operacionales"""
    return await _build_home_dashboard_payload(db)


async def _build_home_dashboard_payload(db: AsyncSession) -> HomeResponse:
    service = SenalServiceV2(db)

    alertas = await service.obtener_alertas_criticas(limite=5)
    estadisticas = await service.obtener_estadisticas_home()

    def construir_categoria_senal(senal) -> dict:
        if isinstance(senal, dict):
            categoria = senal.get("categoria_senal") or {}
            return {
                "id_categoria_senales": (
                    categoria.get("id_categoria_senales")
                    or categoria.get("id_categoria_senal")
                    or senal.get("id_categoria_senal")
                    or 0
                ),
                "nombre_categoria_senal": categoria.get("nombre_categoria_senal") or "Desconocido",
                "descripcion_categoria_senal": categoria.get("descripcion_categoria_senal"),
                "nivel": categoria.get("nivel"),
                "color_categoria": categoria.get("color"),
                "ultimo_usuario_id": categoria.get("ultimo_usuario_id"),
                "ultimo_usuario_nombre": categoria.get("ultimo_usuario_nombre"),
                "ultima_actualizacion": categoria.get("ultima_actualizacion"),
            }

        categoria = getattr(senal, "categoria_senal", None)
        return {
            "id_categoria_senales": (
                getattr(categoria, "id_categoria_senales", None)
                or getattr(senal, "id_categoria_senal", None)
                or 0
            ),
            "nombre_categoria_senal": getattr(categoria, "nombre_categoria_senal", None) or "Desconocido",
            "descripcion_categoria_senal": getattr(categoria, "descripcion_categoria_senal", None),
            "nivel": getattr(categoria, "nivel", None),
            "color_categoria": getattr(categoria, "color", None),
            "ultimo_usuario_id": getattr(categoria, "ultimo_usuario_id", None),
            "ultimo_usuario_nombre": getattr(categoria, "ultimo_usuario_nombre", None),
            "ultima_actualizacion": getattr(categoria, "ultima_actualizacion", None),
        }

    def construir_categoria_analisis(senal) -> dict:
        if isinstance(senal, dict):
            categoria = senal.get("categoria_analisis") or {}
            return {
                "id_categoria_analisis_senal": (
                    categoria.get("id_categoria_analisis_senal")
                    or senal.get("id_categoria_analisis")
                    or 0
                ),
                "nombre_categoria_analisis": categoria.get("nombre_categoria_analisis") or "Desconocido",
                "descripcion_categoria_analisis": categoria.get("descripcion_categoria_analisis"),
            }

        categoria = getattr(senal, "categoria_analisis", None)
        return {
            "id_categoria_analisis_senal": (
                getattr(categoria, "id_categoria_analisis_senal", None)
                or getattr(senal, "id_categoria_analisis", None)
                or 0
            ),
            "nombre_categoria_analisis": getattr(categoria, "nombre_categoria_analisis", None) or "Desconocido",
            "descripcion_categoria_analisis": getattr(categoria, "descripcion_categoria_analisis", None),
        }

    alertas_criticas = []
    for alerta in alertas:
        if isinstance(alerta, dict):
            alerta_payload = {
                "id_senal_detectada": alerta.get("id_senal_detectada"),
                "fecha_deteccion": alerta.get("fecha_deteccion"),
                "score_riesgo": alerta.get("score_riesgo"),
                "categoria_analisis": construir_categoria_analisis(alerta),
                "categoria_senal": construir_categoria_senal(alerta),
            }
        else:
            alerta_payload = {
                "id_senal_detectada": alerta.id_senal_detectada,
                "fecha_deteccion": alerta.fecha_deteccion,
                "score_riesgo": alerta.score_riesgo,
                "categoria_analisis": construir_categoria_analisis(alerta),
                "categoria_senal": construir_categoria_senal(alerta),
            }
        alertas_criticas.append(AlertaCritica.model_validate(alerta_payload))

    return HomeResponse(
        alertas_criticas=alertas_criticas,
        total_senales_hoy=estadisticas["total_senales_hoy"],
        total_crisis=estadisticas["total_crisis"],
        total_paracrisis=estadisticas["total_paracrisis"]
    )

@router.get("/consultar")
async def consultar_senales(
    id_senal_detectada: Optional[str] = Query(None, description="IDs de señales separados por coma: 1,2,3"),
    categoria: Optional[str] = Query(None, description="IDs de categorías separados por coma: 2,3"),
    fecha_desde: Optional[str] = Query(None, description="Fecha desde YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta YYYY-MM-DD"),
    puntuacion_min: Optional[float] = Query(None, ge=0, le=100, description="Puntuación mínima"),
    puntuacion_max: Optional[float] = Query(None, ge=0, le=100, description="Puntuación m��xima"),
    limite: int = Query(50, ge=1, le=100, description="Límite de resultados"),
    desplazamiento: int = Query(0, ge=0, description="Desplazamiento para paginación"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Consulta avanzada de señales con filtros multidimensionales"""
    return await listar_senales_original(id_senal_detectada, categoria, fecha_desde, fecha_hasta, puntuacion_min, puntuacion_max, limite, desplazamiento, db, current_user)

async def listar_senales_original(
    id_senal_detectada: Optional[str],
    categoria: Optional[str],
    fecha_desde: Optional[str],
    fecha_hasta: Optional[str],
    score_min: Optional[float],
    score_max: Optional[float],
    limit: int,
    offset: int,
    db: AsyncSession,
    current_user: Usuario
):
    """
    HU-DF001: Lista ordenada por fecha y score descendente
    HU-DF002: Cards con título, categoría, color
    HU-DF007: Filtros combinables
    """
    try:
        service = SenalServiceV2(db)
        return await service.consultar_senales(
            id_senal_detectada=id_senal_detectada,
            categoria=categoria,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            score_min=score_min,
            score_max=score_max,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/tendencias")
async def obtener_tendencias(
    tipo: str = Query("categoria_senal", description="categoria_senal o categoria_analisis"),
    granularity: str = Query("day", description="day, hour o month"),
    fecha_desde: Optional[str] = Query(None, description="Fecha desde YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Tendencias: conteo de señales por categoría de señal o análisis"""
    try:
        service = SenalServiceV2(db)
        return await service.obtener_tendencias(
            tipo=tipo,
            granularity=granularity,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== HU-DF003: DETALLE DE SEÑAL ====================

@router.get("/{id_senal}")
async def obtener_detalle_senal(
    id_senal: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    HU-DF003: Ver detalle completo de una señal
    """
    try:
        service = SenalServiceV2(db)
        detalle = await service.obtener_detalle_senal(id_senal=id_senal)
        if not detalle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Señal {id_senal} no encontrada"
            )
        return detalle
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener detalle: {str(e)}"
        )

@router.get("/{id_senal}/resumen")
async def obtener_resumen_senal(
    id_senal: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Resumen para UI (tarjeta) usando descripcion de categoria"""
    try:
        service = SenalServiceV2(db)
        resumen = await service.obtener_resumen_senal(id_senal=id_senal)
        if not resumen:
            raise HTTPException(status_code=404, detail="Señal no encontrada")
        return resumen
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener resumen: {str(e)}")

@router.patch("/{id_senal}")
async def actualizar_senal(
    id_senal: int,
    payload: SenalDetectadaUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualizar campos básicos de una señal (categoría, análisis, score, fecha).

    Si se modifica el tipo de señal, se requiere marcar "Confirmó revisión" y se notifica
    automáticamente al correo configurado del coordinador."""
    if (
        payload.id_categoria_senal is None
        and payload.id_categoria_analisis_senal is None
        and payload.score_riesgo is None
        and payload.fecha_deteccion is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos un campo: id_categoria_senal, id_categoria_analisis_senal, score_riesgo o fecha_deteccion"
        )

    if payload.id_categoria_senal is not None and payload.confirmo_revision is not True:
        raise HTTPException(
            status_code=400,
            detail="Debe marcar 'Confirmó revisión' al cambiar el tipo de señal"
        )

    usuario_nombre = getattr(current_user, "nombre_usuario", None) or getattr(current_user, "username", None)

    try:
        service = SenalServiceV2(db)
        resultado = await service.actualizar_senal(
            id_senal=id_senal,
            payload=payload,
            usuario_id=getattr(current_user, "id", None),
            usuario_nombre=usuario_nombre,
            usuario_email=getattr(current_user, "email", None),
            email_revisor=payload.email_revisor,
            ip_address=request.client.host if request.client else None
        )
        if not resultado:
            raise HTTPException(status_code=404, detail="Señal no encontrada")
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar señal: {str(e)}")

@router.get("/{id_senal}/analisis-completo")
async def analisis_completo_senal(
    id_senal: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Análisis completo multidimensional de una señal específica"""
    try:
        service = SenalServiceV2(db)
        analisis = await service.obtener_analisis_completo(id_senal=id_senal)
        if not analisis:
            return {"status": "error", "error": "Señal no encontrada"}
        return analisis
        
    except Exception as e:
        import traceback
        return {
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }

# ==================== HU-DF008: HOME CON ALERTAS CRÍTICAS ====================

@router.get("/home/dashboard", response_model=HomeResponse)
async def obtener_home_dashboard(
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    HU-DF008: Home con las 5 alertas más graves del día
    """
    return await _build_home_dashboard_payload(db)

# ==================== CATÁLOGOS ====================

@router.get("/catalogos/categorias-analisis")
async def listar_categorias_analisis(
    id_categoria_analisis_senal: Optional[int] = Query(None, description="Filtrar por ID de categoría de análisis"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar categorías de análisis (derechos priorizados)"""
    try:
        service = SenalServiceV2(db)
        categorias = await service.listar_categorias_analisis(
            id_categoria_analisis_senal=id_categoria_analisis_senal
        )
        return [
            {
                "id_categoria_analisis_senal": categoria.id_categoria_analisis_senal,
                "nombre_categoria_analisis": categoria.nombre_categoria_analisis,
                "descripcion_categoria_analisis": categoria.descripcion_categoria_analisis,
            }
            for categoria in categorias
        ]
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.get("/catalogos/categorias-senal")
async def listar_categorias_senal(
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar tipos de señal (Ruido, Paracrisis, Crisis)"""
    try:
        service = SenalServiceV2(db)
        categorias = await service.listar_categorias_senal()
        return [
            {
                "id_categoria_senales": categoria.id_categoria_senales,
                "nombre_categoria_senal": categoria.nombre_categoria_senal,
                "descripcion_categoria_senal": categoria.descripcion_categoria_senal,
                "color_categoria": categoria.color,
                "nivel": categoria.nivel,
            }
            for categoria in categorias
        ]
    except Exception as e:
        import traceback
        return {"status": "error", "detail": str(e), "trace": traceback.format_exc()}

@router.patch("/catalogos/categorias-senal/{id_categoria_senal}")
async def actualizar_categoria_senal(
    id_categoria_senal: int,
    payload: CategoriaSenalUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualizar color y/o descripción de una categoría de señal"""
    if payload.color_categoria is None and payload.descripcion_categoria_senal is None:
        raise HTTPException(status_code=400, detail="Debe enviar color_categoria o descripcion_categoria_senal")
    try:
        usuario_nombre = getattr(current_user, "nombre_usuario", None) or getattr(current_user, "username", None)
        if not usuario_nombre:
            raise HTTPException(status_code=400, detail="Usuario inválido para auditoría")
        service = SenalServiceV2(db)
        resultado = await service.actualizar_categoria_senal(
            id_categoria_senal=id_categoria_senal,
            payload=payload,
            usuario_id=current_user.id,
            usuario_nombre=usuario_nombre,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        if not resultado:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar categoria: {str(e)}")
