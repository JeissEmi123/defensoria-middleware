"""
Endpoint independiente para detalle completo
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database.session import get_db_session
from app.core.dependencies import get_current_user
from app.database.models import Usuario

router = APIRouter()

@router.get("/{id_senal}/detalle-completo")
async def obtener_detalle_completo_senal(
    id_senal: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Detalle completo de señal con todas sus observaciones multidimensionales"""
    try:
        # Datos básicos de la señal
        result = await db.execute(text("""
            SELECT 
                sd.id_senal_detectada,
                sd.fecha_deteccion,
                sd.score_riesgo,
                cs.nombre_categoria_senal,
                cas.nombre_categoria_analisis
            FROM sds.senal_detectada sd
            JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales
            JOIN sds.categoria_analisis_senal cas ON sd.id_categoria_analisis_senal = cas.id_categoria_analisis_senal
            WHERE sd.id_senal_detectada = :id_senal
        """), {"id_senal": id_senal})
        
        senal_data = result.fetchone()
        if not senal_data:
            return {"status": "error", "error": "Señal no encontrada"}
        
        # Resultados de observación (16 evaluaciones)
        result = await db.execute(text("""
            SELECT 
                ros.resultado_observacion_categoria,
                co.codigo_categoria_observacion,
                co.nombre_categoria_observacion,
                co.nivel,
                co.peso_categoria_observacion
            FROM sds.resultado_observacion_senal ros
            JOIN sds.categoria_observacion co ON ros.id_categoria_observacion = co.id_categoria_observacion
            WHERE ros.id_senal_detectada = :id_senal
            ORDER BY co.nivel, co.id_categoria_observacion
        """), {"id_senal": id_senal})
        
        observaciones = []
        for row in result:
            observaciones.append({
                "resultado": float(row[0]) if row[0] else 0,
                "codigo": row[1],
                "nombre": row[2],
                "nivel": row[3],
                "peso": float(row[4]) if row[4] else 0
            })
        
        return {
            "senal": {
                "id_senal_detectada": senal_data[0],
                "fecha_deteccion": senal_data[1].isoformat(),
                "score_riesgo": float(senal_data[2]),
                "categoria_senal": senal_data[3],
                "categoria_analisis": senal_data[4]
            },
            "observaciones": observaciones,
            "total_observaciones": len(observaciones),
            "promedio_observaciones": sum(obs["resultado"] for obs in observaciones) / len(observaciones) if observaciones else 0
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/{id_senal}/observaciones/series")
async def obtener_series_observaciones_senal(
    id_senal: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Series de conteo por categoría de observación para una señal específica"""
    try:
        result = await db.execute(text("""
            SELECT
                co.id_categoria_observacion,
                co.codigo_categoria_observacion,
                co.nombre_categoria_observacion,
                co.nivel,
                COUNT(ros.id_resultado_observacion_senal) AS total
            FROM sds.resultado_observacion_senal ros
            JOIN sds.categoria_observacion co
                ON ros.id_categoria_observacion = co.id_categoria_observacion
            WHERE ros.id_senal_detectada = :id_senal
            GROUP BY
                co.id_categoria_observacion,
                co.codigo_categoria_observacion,
                co.nombre_categoria_observacion,
                co.nivel
            ORDER BY co.nivel, co.id_categoria_observacion
        """), {"id_senal": id_senal})

        series = []
        for row in result:
            series.append({
                "id_categoria_observacion": row[0],
                "codigo": row[1],
                "nombre": row[2],
                "nivel": row[3],
                "conteo": int(row[4])
            })

        return {
            "id_senal_detectada": id_senal,
            "total_observaciones": sum(item["conteo"] for item in series),
            "series": series,
            "labels": [item["nombre"] for item in series],
            "values": [item["conteo"] for item in series]
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/{id_senal}/observaciones/grafica")
async def obtener_grafica_observaciones_senal(
    id_senal: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Series para gráfica: usa descripcion_categoria_observacion en X y resultado_observacion_categoria en Y"""
    try:
        result = await db.execute(text("""
            SELECT
                COALESCE(co.descripcion_categoria_observacion, co.nombre_categoria_observacion, ros.codigo_categoria_observacion) AS label,
                ros.resultado_observacion_categoria,
                ros.id_categoria_observacion
            FROM sds.resultado_observacion_senal ros
            LEFT JOIN sds.categoria_observacion co ON ros.id_categoria_observacion = co.id_categoria_observacion
            WHERE ros.id_senal_detectada = :id_senal
            ORDER BY co.nivel NULLS LAST, co.id_categoria_observacion NULLS LAST, ros.id_categoria_observacion
        """), {"id_senal": id_senal})

        rows = result.fetchall()
        if not rows:
            return {
                "id_senal_detectada": id_senal,
                "labels": [],
                "datasets": []
            }

        labels = []
        data = []
        for label, valor, _ in rows:
            labels.append(label)
            data.append(float(valor) if valor is not None else 0.0)

        return {
            "id_senal_detectada": id_senal,
            "labels": labels,
            "datasets": [
                {
                    "label": "Observaciones",
                    "data": data
                }
            ]
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}
