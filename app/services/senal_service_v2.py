"""
Servicio para gestión de señales v2
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.orm import selectinload
from typing import List, Tuple, Optional
from datetime import datetime, date
import json
import logging

from app.database.models_sds import (
    SenalDetectada,
    CategoriaSenal,
    CategoriaAnalisisSenal,
    ResultadoObservacionSenal
)
from app.schemas.senales_v2 import FiltrosSenales
from app.database.models import EventoAuditoria
from app.config import settings
from app.services.email_service import email_service

logger = logging.getLogger(__name__)

class SenalServiceV2:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def listar_senales(
        self,
        skip: int = 0,
        limit: int = 100,
        orden: str = "fecha_desc",
        filtros: Optional[FiltrosSenales] = None
    ) -> Tuple[List[SenalDetectada], int]:
        """Listar señales con filtros y paginación (HU-DF001, HU-DF007)"""
        
        query = select(SenalDetectada).options(
            selectinload(SenalDetectada.categoria_senal),
            selectinload(SenalDetectada.categoria_analisis)
        )
        
        # Aplicar filtros
        if filtros:
            conditions = []
            if filtros.id_categoria_analisis_senal:
                conditions.append(SenalDetectada.id_categoria_analisis_senal == filtros.id_categoria_analisis_senal)
            if filtros.id_categoria_senal:
                conditions.append(SenalDetectada.id_categoria_senal == filtros.id_categoria_senal)
            if filtros.fecha_desde:
                conditions.append(SenalDetectada.fecha_deteccion >= filtros.fecha_desde)
            if filtros.fecha_hasta:
                conditions.append(SenalDetectada.fecha_deteccion <= filtros.fecha_hasta)
            if filtros.score_min is not None:
                conditions.append(SenalDetectada.score_riesgo >= filtros.score_min)
            if filtros.score_max is not None:
                conditions.append(SenalDetectada.score_riesgo <= filtros.score_max)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Contar total
        count_query = select(func.count()).select_from(SenalDetectada)
        if filtros:
            conditions = []
            if filtros.id_categoria_analisis_senal:
                conditions.append(SenalDetectada.id_categoria_analisis_senal == filtros.id_categoria_analisis_senal)
            if filtros.id_categoria_senal:
                conditions.append(SenalDetectada.id_categoria_senal == filtros.id_categoria_senal)
            if filtros.fecha_desde:
                conditions.append(SenalDetectada.fecha_deteccion >= filtros.fecha_desde)
            if filtros.fecha_hasta:
                conditions.append(SenalDetectada.fecha_deteccion <= filtros.fecha_hasta)
            if filtros.score_min is not None:
                conditions.append(SenalDetectada.score_riesgo >= filtros.score_min)
            if filtros.score_max is not None:
                conditions.append(SenalDetectada.score_riesgo <= filtros.score_max)
            if conditions:
                count_query = count_query.where(and_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Ordenamiento
        if orden == "fecha_desc":
            query = query.order_by(SenalDetectada.fecha_deteccion.desc())
        elif orden == "fecha_asc":
            query = query.order_by(SenalDetectada.fecha_deteccion.asc())
        elif orden == "score_desc":
            query = query.order_by(SenalDetectada.score_riesgo.desc())
        elif orden == "score_asc":
            query = query.order_by(SenalDetectada.score_riesgo.asc())
        
        # Paginación
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        senales = result.unique().scalars().all()
        
        return senales, total
    
    async def obtener_senal_detalle(self, id_senal: int) -> Optional[SenalDetectada]:
        """Obtener detalle completo de una señal (HU-DF003)"""
        from sqlalchemy.orm import joinedload
        
        query = select(SenalDetectada).options(
            joinedload(SenalDetectada.categoria_senal),
            joinedload(SenalDetectada.categoria_analisis),
            selectinload(SenalDetectada.resultados_observacion).joinedload(
                ResultadoObservacionSenal.categoria_observacion
            )
        ).where(SenalDetectada.id_senal_detectada == id_senal)
        
        result = await self.db.execute(query)
        senal = result.unique().scalar_one_or_none()
        
        # Enriquecer resultados con nombres de categorías
        if senal and senal.resultados_observacion:
            for resultado in senal.resultados_observacion:
                if resultado.categoria_observacion:
                    resultado.nombre_categoria_observacion = resultado.categoria_observacion.nombre_categoria_observacion
        
        return senal
    
    async def obtener_alertas_criticas(self, limite: int = 5) -> List[SenalDetectada]:
        """Obtener top alertas críticas del día (HU-DF008)"""
        hoy = date.today()
        
        query = select(SenalDetectada).options(
            selectinload(SenalDetectada.categoria_senal),
            selectinload(SenalDetectada.categoria_analisis)
        ).where(
            and_(
                func.date(SenalDetectada.fecha_deteccion) == hoy,
                or_(
                    SenalDetectada.id_categoria_senal == 3,  # Crisis
                    SenalDetectada.id_categoria_senal == 2   # Paracrisis
                )
            )
        ).order_by(
            SenalDetectada.score_riesgo.desc(),
            SenalDetectada.fecha_deteccion.desc()
        ).limit(limite)
        
        result = await self.db.execute(query)
        # unique() evita duplicados cuando hay cargas selectin/joinedload
        return result.unique().scalars().all()
    
    async def obtener_estadisticas_home(self) -> dict:
        """Obtener estadísticas para el home (HU-DF008)"""
        hoy = date.today()
        
        # Total señales hoy
        total_hoy_query = select(func.count()).select_from(SenalDetectada).where(
            func.date(SenalDetectada.fecha_deteccion) == hoy
        )
        total_hoy_result = await self.db.execute(total_hoy_query)
        total_hoy = total_hoy_result.scalar()
        
        # Total crisis hoy
        crisis_query = select(func.count()).select_from(SenalDetectada).where(
            and_(
                func.date(SenalDetectada.fecha_deteccion) == hoy,
                SenalDetectada.id_categoria_senal == 3
            )
        )
        crisis_result = await self.db.execute(crisis_query)
        total_crisis = crisis_result.scalar()
        
        # Total paracrisis hoy
        paracrisis_query = select(func.count()).select_from(SenalDetectada).where(
            and_(
                func.date(SenalDetectada.fecha_deteccion) == hoy,
                SenalDetectada.id_categoria_senal == 2
            )
        )
        paracrisis_result = await self.db.execute(paracrisis_query)
        total_paracrisis = paracrisis_result.scalar()
        
        return {
            "total_senales_hoy": total_hoy,
            "total_crisis": total_crisis,
            "total_paracrisis": total_paracrisis
        }
    
    async def listar_categorias_analisis(
        self,
        id_categoria_analisis_senal: Optional[int] = None
    ) -> List[CategoriaAnalisisSenal]:
        """Listar categorías de análisis"""
        query = select(CategoriaAnalisisSenal)
        if id_categoria_analisis_senal is not None:
            query = query.where(
                CategoriaAnalisisSenal.id_categoria_analisis_senal == id_categoria_analisis_senal
            )
        query = query.order_by(CategoriaAnalisisSenal.nombre_categoria_analisis)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def listar_categorias_senal(self) -> List[CategoriaSenal]:
        """Listar categorías de señal"""
        query = select(CategoriaSenal).order_by(CategoriaSenal.nivel, CategoriaSenal.nombre_categoria_senal)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def obtener_senales_recientes(self, limite: int) -> List[dict]:
        result = await self.db.execute(text("""
            SELECT 
                sd.id_senal_detectada,
                CONCAT('Señal #', sd.id_senal_detectada) as titulo,
                cs.nombre_categoria_senal,
                COALESCE(
                    cs.color_categoria,
                    CASE 
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%ruido%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%ruido%' THEN '#808080'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%problemas menores%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%problemas menores%' OR LOWER(cs.nombre_categoria_senal) LIKE '%problema menor%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%problema menor%' THEN '#00FF00'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%paracrisis%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%paracrisis%' THEN '#FFA500' 
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%crisis%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%crisis%' THEN '#FF0000'
                        ELSE '#CCCCCC'
                    END
                ) as color,
                sd.score_riesgo,
                sd.fecha_deteccion,
                cas.nombre_categoria_analisis,
                COALESCE(hist.usuario_nombre, 'prueba') as usuario,
                hist.fecha_registro as fecha_evento
            FROM sds.senal_detectada sd
            JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales
            JOIN sds.categoria_analisis_senal cas ON sd.id_categoria_analisis_senal = cas.id_categoria_analisis_senal
            LEFT JOIN LATERAL (
                SELECT 
                    COALESCE(u.nombre_usuario, 'prueba') as usuario_nombre,
                    hs.fecha_registro
                FROM sds.historial_senal hs
                LEFT JOIN usuarios u ON u.id = hs.usuario_id
                WHERE hs.id_senal_detectada = sd.id_senal_detectada
                ORDER BY hs.fecha_registro DESC
                LIMIT 1
            ) hist ON TRUE
            ORDER BY sd.fecha_actualizacion DESC, sd.id_senal_detectada DESC
            LIMIT :limite
        """), {"limite": limite})

        senales = []
        for row in result:
            senales.append({
                "id_senal_detectada": row[0],
                "titulo": row[1],
                "categoria": row[2],
                "color": row[3],
                "score_riesgo": float(row[4]),
                "fecha_deteccion": row[5].isoformat(),
                "categoria_analisis": row[6],
                "usuario": row[7],
                "fecha_evento": row[8].isoformat() if row[8] else None
            })

        return senales

    async def consultar_senales(
        self,
        id_senal_detectada: Optional[str],
        categoria: Optional[str],
        fecha_desde: Optional[str],
        fecha_hasta: Optional[str],
        score_min: Optional[float],
        score_max: Optional[float],
        limit: int,
        offset: int
    ) -> dict:
        where_conditions = []
        params = {}

        if id_senal_detectada:
            senal_ids = [int(x.strip()) for x in id_senal_detectada.split(',') if x.strip().isdigit()]
            if senal_ids:
                placeholders = ','.join([f':senal_{i}' for i in range(len(senal_ids))])
                where_conditions.append(f"sd.id_senal_detectada IN ({placeholders})")
                for i, senal_id in enumerate(senal_ids):
                    params[f'senal_{i}'] = senal_id

        if categoria:
            cat_ids = [int(x.strip()) for x in categoria.split(',') if x.strip().isdigit()]
            if cat_ids:
                placeholders = ','.join([f':cat_{i}' for i in range(len(cat_ids))])
                where_conditions.append(f"sd.id_categoria_senal IN ({placeholders})")
                for i, cat_id in enumerate(cat_ids):
                    params[f'cat_{i}'] = cat_id

        if fecha_desde:
            where_conditions.append("DATE(sd.fecha_deteccion) >= :fecha_desde")
            params['fecha_desde'] = fecha_desde

        if fecha_hasta:
            where_conditions.append("DATE(sd.fecha_deteccion) <= :fecha_hasta")
            params['fecha_hasta'] = fecha_hasta

        if score_min is not None:
            where_conditions.append("sd.score_riesgo >= :score_min")
            params['score_min'] = score_min

        if score_max is not None:
            where_conditions.append("sd.score_riesgo <= :score_max")
            params['score_max'] = score_max

        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        result = await self.db.execute(text(f"""
            SELECT 
                sd.id_senal_detectada,
                CONCAT('Señal #', sd.id_senal_detectada) as titulo,
                cs.nombre_categoria_senal,
                COALESCE(
                    cs.color_categoria,
                    CASE 
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%ruido%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%ruido%' THEN '#808080'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%problemas menores%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%problemas menores%' OR LOWER(cs.nombre_categoria_senal) LIKE '%problema menor%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%problema menor%' THEN '#00FF00'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%paracrisis%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%paracrisis%' THEN '#FFA500' 
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%crisis%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%crisis%' THEN '#FF0000'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%rojo%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%rojo%' THEN '#FF0000'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%amarillo%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%amarillo%' THEN '#FFFF00'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%verde%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%verde%' THEN '#00FF00'
                        ELSE '#CCCCCC'
                    END
                ) as color,
                sd.score_riesgo,
                sd.fecha_deteccion,
                cas.nombre_categoria_analisis,
                COALESCE(hist.usuario_nombre, 'prueba') as usuario,
                hist.fecha_registro as fecha_evento
            FROM sds.senal_detectada sd
            JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales
            JOIN sds.categoria_analisis_senal cas ON sd.id_categoria_analisis_senal = cas.id_categoria_analisis_senal
            LEFT JOIN LATERAL (
                SELECT 
                    COALESCE(u.nombre_usuario, 'prueba') as usuario_nombre,
                    hs.fecha_registro
                FROM sds.historial_senal hs
                LEFT JOIN usuarios u ON u.id = hs.usuario_id
                WHERE hs.id_senal_detectada = sd.id_senal_detectada
                ORDER BY hs.fecha_registro DESC
                LIMIT 1
            ) hist ON TRUE
            {where_clause}
            ORDER BY sd.score_riesgo DESC, sd.fecha_deteccion DESC
            LIMIT :limit OFFSET :offset
        """), {**params, 'limit': limit, 'offset': offset})

        senales = []
        for row in result:
            senales.append({
                "id_senal_detectada": row[0],
                "titulo": row[1],
                "categoria": row[2],
                "color": row[3],
                "score_riesgo": float(row[4]),
                "fecha_deteccion": row[5].isoformat(),
                "categoria_analisis": row[6],
                "usuario": row[7],
                "fecha_evento": row[8].isoformat() if row[8] else None
            })

        count_result = await self.db.execute(text(f"""
            SELECT COUNT(*)
            FROM sds.senal_detectada sd
            JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales
            JOIN sds.categoria_analisis_senal cas ON sd.id_categoria_analisis_senal = cas.id_categoria_analisis_senal
            {where_clause}
        """), params)
        total = count_result.scalar()

        return {
            "total": total,
            "senales": senales,
            "filtros_aplicados": {
                "id_senal_detectada": id_senal_detectada,
                "categoria": categoria,
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
                "score_min": score_min,
                "score_max": score_max
            },
            "paginacion": {
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        }

    async def obtener_tendencias(
        self,
        tipo: str,
        granularity: str,
        fecha_desde: Optional[str],
        fecha_hasta: Optional[str]
    ) -> dict:
        if granularity not in {"day", "hour", "month"}:
            raise ValueError("granularity debe ser day, hour o month")

        if tipo == "categoria_senal":
            return await self._obtener_tendencia_por_categoria(
                tabla_categoria="categoria_senal",
                sd_id_col="id_categoria_senal",
                cat_id_col="id_categoria_senales",
                nombre_col="nombre_categoria_senal",
                granularity=granularity,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta
            )
        if tipo == "categoria_analisis":
            return await self._obtener_tendencia_por_categoria(
                tabla_categoria="categoria_analisis_senal",
                sd_id_col="id_categoria_analisis_senal",
                cat_id_col="id_categoria_analisis_senal",
                nombre_col="nombre_categoria_analisis",
                granularity=granularity,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta
            )

        raise ValueError("tipo debe ser categoria_senal o categoria_analisis")

    async def _obtener_tendencia_por_categoria(
        self,
        tabla_categoria: str,
        sd_id_col: str,
        cat_id_col: str,
        nombre_col: str,
        granularity: str,
        fecha_desde: Optional[str],
        fecha_hasta: Optional[str]
    ) -> dict:
        where_conditions = []
        params = {}
        if fecha_desde:
            where_conditions.append("DATE(sd.fecha_deteccion) >= :fecha_desde")
            params["fecha_desde"] = fecha_desde
        if fecha_hasta:
            where_conditions.append("DATE(sd.fecha_deteccion) <= :fecha_hasta")
            params["fecha_hasta"] = fecha_hasta

        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        result = await self.db.execute(text(f"""
            SELECT
                date_trunc('{granularity}', sd.fecha_deteccion) AS bucket,
                c.{cat_id_col} AS id_categoria,
                c.{nombre_col} AS nombre_categoria,
                COUNT(*) AS total
            FROM sds.senal_detectada sd
            JOIN sds.{tabla_categoria} c
                ON sd.{sd_id_col} = c.{cat_id_col}
            {where_clause}
            GROUP BY bucket, c.{cat_id_col}, c.{nombre_col}
            ORDER BY bucket ASC, c.{cat_id_col} ASC
        """), params)

        rows = result.fetchall()
        labels = []
        label_index = {}
        series_map = {}

        def format_bucket(value):
            if granularity == "month":
                return value.strftime("%Y-%m")
            if granularity == "hour":
                return value.strftime("%Y-%m-%dT%H:00:00")
            return value.date().isoformat()

        for row in rows:
            bucket = format_bucket(row[0])
            if bucket not in label_index:
                label_index[bucket] = len(labels)
                labels.append(bucket)

            cat_id = row[1]
            if cat_id not in series_map:
                series_map[cat_id] = {
                    "id": cat_id,
                    "label": row[2],
                    "data": [0] * len(labels)
                }
            else:
                if len(series_map[cat_id]["data"]) < len(labels):
                    series_map[cat_id]["data"].extend([0] * (len(labels) - len(series_map[cat_id]["data"])))

            series_map[cat_id]["data"][label_index[bucket]] = int(row[3])

        datasets = list(series_map.values())

        return {
            "granularity": granularity,
            "labels": labels,
            "datasets": datasets
        }

    async def obtener_detalle_senal(self, id_senal: int) -> Optional[dict]:
        result = await self.db.execute(text("""
            SELECT 
                sd.id_senal_detectada,
                sd.fecha_deteccion,
                sd.fecha_actualizacion,
                sd.score_riesgo,
                cas.id_categoria_analisis_senal,
                cas.nombre_categoria_analisis,
                cas.descripcion_categoria_analisis,
                cs.id_categoria_senales,
                cs.nombre_categoria_senal,
                cs.descripcion_categoria_senal,
                cs.nivel
            FROM sds.senal_detectada sd
            JOIN sds.categoria_analisis_senal cas ON sd.id_categoria_analisis_senal = cas.id_categoria_analisis_senal
            JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales
            WHERE sd.id_senal_detectada = :id_senal
        """), {"id_senal": id_senal})

        senal_row = result.fetchone()
        if not senal_row:
            return None

        obs_result = await self.db.execute(text("""
            SELECT 
                ros.codigo_categoria_observacion,
                ros.resultado_observacion_categoria,
                co.nombre_categoria_observacion
            FROM sds.resultado_observacion_senal ros
            LEFT JOIN sds.categoria_observacion co ON ros.id_categoria_observacion = co.id_categoria_observacion
            WHERE ros.id_senal_detectada = :id_senal
            ORDER BY ros.codigo_categoria_observacion
        """), {"id_senal": id_senal})

        resultados_observacion = []
        for obs_row in obs_result:
            resultados_observacion.append({
                "codigo_categoria_observacion": obs_row[0],
                "resultado_observacion_categoria": float(obs_row[1]),
                "nombre_categoria_observacion": obs_row[2]
            })

        return {
            "id_senal_detectada": senal_row[0],
            "fecha_deteccion": senal_row[1].isoformat(),
            "fecha_actualizacion": senal_row[2].isoformat(),
            "score_riesgo": float(senal_row[3]),
            "categoria_analisis": {
                "id_categoria_analisis_senal": senal_row[4],
                "nombre_categoria_analisis": senal_row[5],
                "descripcion_categoria_analisis": senal_row[6]
            },
            "categoria_senal": {
                "id_categoria_senal": senal_row[7],
                "nombre_categoria_senal": senal_row[8],
                "descripcion_categoria_senal": senal_row[9],
                "nivel": senal_row[10]
            },
            "resultados_observacion": resultados_observacion
        }

    async def obtener_resumen_senal(self, id_senal: int) -> Optional[dict]:
        result = await self.db.execute(text("""
            SELECT 
                sd.id_senal_detectada,
                sd.fecha_actualizacion,
                sd.score_riesgo,
                cs.nombre_categoria_senal,
                cs.descripcion_categoria_senal,
                COALESCE(
                    cs.color_categoria,
                    CASE 
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%ruido%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%ruido%' THEN '#808080'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%problemas menores%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%problemas menores%' OR LOWER(cs.nombre_categoria_senal) LIKE '%problema menor%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%problema menor%' THEN '#00FF00'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%paracrisis%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%paracrisis%' THEN '#FFA500' 
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%crisis%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%crisis%' THEN '#FF0000'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%rojo%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%rojo%' THEN '#FF0000'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%amarillo%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%amarillo%' THEN '#FFFF00'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%verde%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%verde%' THEN '#00FF00'
                        ELSE '#CCCCCC'
                    END
                ) as color
            FROM sds.senal_detectada sd
            JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales
            WHERE sd.id_senal_detectada = :id_senal
        """), {"id_senal": id_senal})

        senal_row = result.fetchone()
        if not senal_row:
            return None

        audit_row = None
        try:
            audit_result = await self.db.execute(text("""
                SELECT u.nombre_usuario, hs.fecha_registro
                FROM sds.historial_senal hs
                LEFT JOIN usuarios u ON u.id = hs.usuario_id
                WHERE hs.id_senal_detectada = :id_senal
                ORDER BY hs.fecha_registro DESC
                LIMIT 1
            """), {"id_senal": id_senal})
            audit_row = audit_result.fetchone()
        except Exception as e:
            if "UndefinedTableError" not in str(e) and "historial_senal" not in str(e):
                raise

        usuario = audit_row[0] if audit_row and audit_row[0] else "prueba"
        fecha_evento = audit_row[1] if audit_row else senal_row[1]

        return {
            "id_senal_detectada": senal_row[0],
            "usuario": usuario,
            "fecha_evento": fecha_evento.isoformat() if fecha_evento else None,
            "categoria_senal": senal_row[3],
            "color": senal_row[5],
            "descripcion": senal_row[4],
            "score_riesgo": float(senal_row[2]) if senal_row[2] is not None else None
        }

    async def actualizar_senal(
        self,
        id_senal: int,
        payload,
        usuario_id: Optional[int],
        usuario_nombre: Optional[str],
        usuario_email: Optional[str],
        email_revisor: Optional[str],
        ip_address: Optional[str]
    ) -> Optional[dict]:
        current_row = await self.db.execute(
            text("""
                SELECT id_categoria_senal, id_categoria_analisis_senal, score_riesgo, fecha_deteccion
                FROM sds.senal_detectada
                WHERE id_senal_detectada = :id_senal
            """),
            {"id_senal": id_senal}
        )
        antes = current_row.fetchone()
        if not antes:
            return None
        categoria_previa = antes[0]

        updates = []
        params = {"id_senal": id_senal}

        if payload.id_categoria_senal is not None:
            updates.append("id_categoria_senal = :id_categoria_senal")
            params["id_categoria_senal"] = payload.id_categoria_senal

        if payload.id_categoria_analisis_senal is not None:
            updates.append("id_categoria_analisis_senal = :id_categoria_analisis_senal")
            params["id_categoria_analisis_senal"] = payload.id_categoria_analisis_senal

        if payload.score_riesgo is not None:
            updates.append("score_riesgo = :score_riesgo")
            params["score_riesgo"] = payload.score_riesgo

        if payload.fecha_deteccion is not None:
            updates.append("fecha_deteccion = :fecha_deteccion")
            params["fecha_deteccion"] = payload.fecha_deteccion

        updates.append("fecha_actualizacion = NOW()")

        result = await self.db.execute(
            text(f"""
                UPDATE sds.senal_detectada
                SET {", ".join(updates)}
                WHERE id_senal_detectada = :id_senal
                RETURNING id_senal_detectada, id_categoria_senal, id_categoria_analisis_senal, score_riesgo, fecha_deteccion, fecha_actualizacion
            """),
            params
        )
        row = result.fetchone()
        if not row:
            return None

        cambio_tipo_categoria = (
            payload.id_categoria_senal is not None
            and row[1] != categoria_previa
        )
        fecha_actualizacion_iso = row[5].isoformat() if row[5] else None

        datos_adicionales = {
            "usuario_nombre": usuario_nombre,
            "antes": {
                "id_categoria_senal": antes[0],
                "id_categoria_analisis_senal": antes[1],
                "score_riesgo": float(antes[2]) if antes[2] is not None else None,
                "fecha_deteccion": antes[3].isoformat() if antes[3] else None
            },
            "despues": {
                "id_categoria_senal": row[1],
                "id_categoria_analisis_senal": row[2],
                "score_riesgo": float(row[3]) if row[3] is not None else None,
                "fecha_deteccion": row[4].isoformat() if row[4] else None
            },
            "confirmo_revision": payload.confirmo_revision,
            "cambio_tipo_categoria": cambio_tipo_categoria
        }

        audit_result = await self.db.execute(
            text("""
                INSERT INTO sds.historial_senal (
                    id_senal_detectada, usuario_id, accion, descripcion,
                    estado_anterior, estado_nuevo, datos_adicionales, fecha_registro, ip_address
                ) VALUES (
                    :id_senal, :usuario_id, :accion, :descripcion,
                    :estado_anterior, :estado_nuevo, :datos_adicionales, NOW(), :ip_address
                )
                RETURNING id, fecha_registro
            """),
            {
                "id_senal": id_senal,
                "usuario_id": usuario_id,
                "accion": "actualizacion_senal",
                "descripcion": "Actualización de señal (categoría/análisis/score/fecha)",
                "estado_anterior": None,
                "estado_nuevo": None,
                "datos_adicionales": json.dumps(datos_adicionales),
                "ip_address": ip_address
            }
        )
        audit_row = audit_result.fetchone()

        await self.db.commit()

        if cambio_tipo_categoria:
            await self._enviar_notificaciones_revision(
                id_senal=id_senal,
                categoria_previa=categoria_previa,
                categoria_nueva=row[1],
                usuario_nombre=usuario_nombre,
                usuario_email=usuario_email,
                email_revisor=email_revisor,
                confirmo_revision=payload.confirmo_revision,
                fecha_actualizacion=fecha_actualizacion_iso
            )

        return {
            "id_senal_detectada": row[0],
            "id_categoria_senal": row[1],
            "id_categoria_analisis_senal": row[2],
            "score_riesgo": float(row[3]) if row[3] is not None else None,
            "fecha_deteccion": row[4].isoformat() if row[4] else None,
            "fecha_actualizacion": row[5].isoformat() if row[5] else None,
            "auditoria": {
                "id": audit_row[0] if audit_row else None,
                "usuario": usuario_nombre,
                "fecha_registro": audit_row[1].isoformat() if audit_row and audit_row[1] else None
            }
        }

    async def _obtener_nombre_categoria_senal(self, id_categoria: Optional[int]) -> Optional[str]:
        if id_categoria is None:
            return None
        result = await self.db.execute(
            select(CategoriaSenal.nombre_categoria_senal).where(
                CategoriaSenal.id_categoria_senales == id_categoria
            )
        )
        return result.scalar_one_or_none()

    async def _enviar_notificaciones_revision(
        self,
        id_senal: int,
        categoria_previa: Optional[int],
        categoria_nueva: Optional[int],
        usuario_nombre: Optional[str],
        usuario_email: Optional[str],
        email_revisor: Optional[str],
        confirmo_revision: Optional[bool],
        fecha_actualizacion: Optional[str]
    ):
        nombre_previa = await self._obtener_nombre_categoria_senal(categoria_previa)
        nombre_nueva = await self._obtener_nombre_categoria_senal(categoria_nueva)

        destinatarios = []
        if settings.coordinador_email:
            destinatarios.append(("coordinador", settings.coordinador_email))
        if usuario_email:
            destinatarios.append(("editor", usuario_email))
        if email_revisor:
            destinatarios.append(("revisor", email_revisor))

        if not destinatarios:
            logger.warning(
                "No se enviará ninguna notificación de la señal %s porque no hay correos configurados",
                id_senal
            )
            return

        enviados = set()
        for etiqueta, to_email in destinatarios:
            if not to_email:
                continue
            direccion = to_email.strip().lower()
            if not direccion or direccion in enviados:
                continue
            enviados.add(direccion)

            enviado = self._enviar_email_revision(
                to_email=to_email,
                senal_id=id_senal,
                categoria_previa=nombre_previa,
                categoria_nueva=nombre_nueva,
                usuario=usuario_nombre,
                confirmo_revision=confirmo_revision,
                fecha_actualizacion=fecha_actualizacion,
                contexto=etiqueta
            )

            if not enviado:
                logger.warning(
                    "No fue posible notificar a %s sobre la actualización de la señal %s",
                    to_email,
                    id_senal
                )

    def _enviar_email_revision(
        self,
        to_email: str,
        senal_id: int,
        categoria_previa: Optional[str],
        categoria_nueva: Optional[str],
        usuario: Optional[str],
        confirmo_revision: Optional[bool],
        fecha_actualizacion: Optional[str],
        contexto: str
    ) -> bool:
        """Envía el correo de revisión a un destinatario específico."""
        logger.info(
            "Enviando notificación de revisión (%s) de la señal %s a %s",
            contexto,
            senal_id,
            to_email
        )
        return email_service.send_signal_revision_notification(
            to_email=to_email,
            senal_id=senal_id,
            categoria_previa=categoria_previa,
            categoria_nueva=categoria_nueva,
            usuario=usuario,
            confirmo_revision=confirmo_revision,
            fecha_actualizacion=fecha_actualizacion
        )

    async def actualizar_categoria_senal(
        self,
        id_categoria_senal: int,
        payload,
        usuario_id: int,
        usuario_nombre: str,
        ip_address: Optional[str],
        user_agent: str
    ) -> Optional[dict]:
        updates = []
        params = {"id_categoria_senal": id_categoria_senal}
        if payload.color_categoria is not None:
            updates.append("color_categoria = :color_nuevo")
            params["color_nuevo"] = payload.color_categoria
        if payload.descripcion_categoria_senal is not None:
            updates.append("descripcion_categoria_senal = :descripcion")
            params["descripcion"] = payload.descripcion_categoria_senal
        updates.append("ultimo_usuario_id = :ultimo_usuario_id")
        updates.append("ultimo_usuario_nombre = :ultimo_usuario_nombre")
        updates.append("ultima_actualizacion = NOW()")
        params["ultimo_usuario_id"] = usuario_id
        params["ultimo_usuario_nombre"] = usuario_nombre

        result = await self.db.execute(
            text(f"""
                UPDATE sds.categoria_senal
                SET {", ".join(updates)}
                WHERE id_categoria_senales = :id_categoria_senal
                RETURNING id_categoria_senales, color_categoria, descripcion_categoria_senal, ultimo_usuario_id, ultimo_usuario_nombre, ultima_actualizacion
            """),
            params
        )
        row = result.fetchone()
        if not row:
            return None

        evento = EventoAuditoria(
            usuario_id=usuario_id,
            tipo_evento="actualizacion_categoria_senal",
            recurso="categoria_senal",
            accion="actualizar_categoria",
            resultado="exito",
            ip_address=ip_address,
            user_agent=user_agent,
            detalles={
                "id_categoria_senal": id_categoria_senal,
                "color_nuevo": payload.color_categoria,
                "descripcion_nueva": payload.descripcion_categoria_senal,
                "usuario_nombre": usuario_nombre
            },
            fecha_evento=datetime.utcnow()
        )
        self.db.add(evento)
        await self.db.commit()

        return {
            "id_categoria_senal": row[0],
            "color_categoria": row[1],
            "descripcion_categoria_senal": row[2],
            "ultimo_usuario_id": row[3],
            "ultimo_usuario_nombre": row[4],
            "ultima_actualizacion": row[5].isoformat() if row[5] else None,
            "usuario": usuario_nombre,
            "fecha_evento": evento.fecha_evento.isoformat()
        }

    async def obtener_analisis_completo(self, id_senal: int) -> Optional[dict]:
        result = await self.db.execute(text("""
            SELECT 
                sd.id_senal_detectada,
                sd.fecha_deteccion,
                sd.score_riesgo,
                cs.nombre_categoria_senal,
                COALESCE(
                    cs.color_categoria,
                    CASE 
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%ruido%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%ruido%' THEN '#808080'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%problemas menores%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%problemas menores%' OR LOWER(cs.nombre_categoria_senal) LIKE '%problema menor%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%problema menor%' THEN '#00FF00'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%paracrisis%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%paracrisis%' THEN '#FFA500' 
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%crisis%' OR LOWER(cs.descripcion_categoria_senal) LIKE '%crisis%' THEN '#FF0000'
                        ELSE '#CCCCCC'
                    END
                ) as color,
                cas.nombre_categoria_analisis
            FROM sds.senal_detectada sd
            JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales
            JOIN sds.categoria_analisis_senal cas ON sd.id_categoria_analisis_senal = cas.id_categoria_analisis_senal
            WHERE sd.id_senal_detectada = :id_senal
        """), {"id_senal": id_senal})

        senal_data = result.fetchone()
        if not senal_data:
            return None

        return {
            "senal_base": {
                "id_senal_detectada": senal_data[0],
                "fecha_deteccion": senal_data[1].isoformat(),
                "score_riesgo": float(senal_data[2]),
                "categoria_senal": senal_data[3],
                "color": senal_data[4],
                "categoria_analisis": senal_data[5]
            },
            "observaciones_multidimensionales": [],
            "total_observaciones": 0,
            "score_total": float(senal_data[2])
        }
