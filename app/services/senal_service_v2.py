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
    ResultadoObservacionSenal,
    HistorialSenal
)
from app.schemas.senales_v2 import FiltrosSenales
from app.database.models import EventoAuditoria
from app.config import settings
from app.services.email_service import email_service
from app.core.json_utils import serialize_decimal, safe_json_dumps

logger = logging.getLogger(__name__)

class SenalServiceV2:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_table_columns(self, schema: str, table: str) -> set:
        result = await self.db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = :schema AND table_name = :table
        """), {"schema": schema, "table": table})
        return {row[0] for row in result.fetchall()}

    async def _table_exists(self, schema: str, table: str) -> bool:
        result = await self.db.execute(text("""
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = :schema AND table_name = :table
            LIMIT 1
        """), {"schema": schema, "table": table})
        return result.scalar() is not None

    def _pick_column(self, columns: set, candidates: List[str], fallback: Optional[str] = None) -> Optional[str]:
        for col in candidates:
            if col in columns:
                return col
        return fallback if fallback is not None else candidates[0]

    async def _build_senal_query_parts(self) -> dict:
        sd_columns = await self._get_table_columns("sds", "senal_detectada")
        cs_columns = await self._get_table_columns("sds", "categoria_senal")

        sd_cat_analisis_col = self._pick_column(
            sd_columns,
            ["id_categoria_analisis", "id_categoria_analisis_senal"]
        )
        cs_id_col = self._pick_column(
            cs_columns,
            ["id_categoria_senales", "id_categoria_senal"]
        )
        cs_desc_col = self._pick_column(
            cs_columns,
            ["descripcion_categoria_senal", "descripcion"],
            fallback=None
        )
        cs_color_col = None
        if "color" in cs_columns:
            cs_color_col = "color"
        elif "color_categoria" in cs_columns:
            cs_color_col = "color_categoria"

        desc_expr = f"cs.{cs_desc_col}" if cs_desc_col else "NULL"
        color_expr = f"cs.{cs_color_col}" if cs_color_col else "NULL"

        nombre_lower = "LOWER(COALESCE(cs.nombre_categoria_senal, ''))"
        desc_lower = f"LOWER(COALESCE({desc_expr}, ''))"

        case_expr = f"""
                    CASE 
                        WHEN {nombre_lower} LIKE '%ruido%' OR {desc_lower} LIKE '%ruido%' THEN '#808080'
                        WHEN {nombre_lower} LIKE '%problemas menores%' OR {desc_lower} LIKE '%problemas menores%' OR {nombre_lower} LIKE '%problema menor%' OR {desc_lower} LIKE '%problema menor%' THEN '#00FF00'
                        WHEN {nombre_lower} LIKE '%paracrisis%' OR {desc_lower} LIKE '%paracrisis%' THEN '#FFA500' 
                        WHEN {nombre_lower} LIKE '%crisis%' OR {desc_lower} LIKE '%crisis%' THEN '#FF0000'
                        WHEN {nombre_lower} LIKE '%rojo%' OR {desc_lower} LIKE '%rojo%' THEN '#FF0000'
                        WHEN {nombre_lower} LIKE '%amarillo%' OR {desc_lower} LIKE '%amarillo%' THEN '#FFFF00'
                        WHEN {nombre_lower} LIKE '%verde%' OR {desc_lower} LIKE '%verde%' THEN '#00FF00'
                        ELSE '#CCCCCC'
                    END
                """

        color_select = f"COALESCE({color_expr}, {case_expr}) as color"

        has_historial = await self._table_exists("sds", "historial_senal")
        has_usuarios = await self._table_exists("public", "usuarios")

        if has_historial:
            user_join = "LEFT JOIN usuarios u ON u.id = hs.usuario_id" if has_usuarios else ""
            user_select = "COALESCE(u.nombre_usuario, 'prueba')" if has_usuarios else "'prueba'"
            historial_join = f"""
            LEFT JOIN LATERAL (
                SELECT 
                    {user_select} as usuario_nombre,
                    hs.fecha_registro
                FROM sds.historial_senal hs
                {user_join}
                WHERE hs.id_senal_detectada = sd.id_senal_detectada
                ORDER BY hs.fecha_registro DESC
                LIMIT 1
            ) hist ON TRUE
            """
            usuario_select = "COALESCE(hist.usuario_nombre, 'prueba') as usuario"
            fecha_select = "hist.fecha_registro as fecha_evento"
        else:
            historial_join = ""
            usuario_select = "'prueba' as usuario"
            fecha_select = "NULL::timestamp as fecha_evento"

        return {
            "sd_cat_analisis_col": sd_cat_analisis_col,
            "cs_id_col": cs_id_col,
            "desc_expr": desc_expr,
            "color_select": color_select,
            "historial_join": historial_join,
            "usuario_select": usuario_select,
            "fecha_select": fecha_select,
            "has_historial": has_historial,
            "has_usuarios": has_usuarios
        }
    
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
                conditions.append(SenalDetectada.id_categoria_analisis == filtros.id_categoria_analisis_senal)
            if filtros.id_categoria_senal:
                conditions.append(SenalDetectada.id_categoria_senal == filtros.id_categoria_senal)
            if filtros.estado:
                conditions.append(SenalDetectada.estado == filtros.estado)
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
                conditions.append(SenalDetectada.id_categoria_analisis == filtros.id_categoria_analisis_senal)
            if filtros.id_categoria_senal:
                conditions.append(SenalDetectada.id_categoria_senal == filtros.id_categoria_senal)
            if filtros.estado:
                conditions.append(SenalDetectada.estado == filtros.estado)
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
    
    async def obtener_alertas_criticas(self, limite: int = 5) -> List[dict]:
        """Obtener top alertas críticas del día (HU-DF008)"""
        hoy = date.today()
        parts = await self._build_senal_query_parts()

        result = await self.db.execute(text(f"""
            SELECT
                sd.id_senal_detectada,
                sd.fecha_deteccion,
                sd.score_riesgo,
                cas.id_categoria_analisis_senal,
                cas.nombre_categoria_analisis,
                cas.descripcion_categoria_analisis,
                cs.{parts["cs_id_col"]} AS id_categoria_senal,
                cs.nombre_categoria_senal,
                {parts["desc_expr"]} AS descripcion_categoria_senal,
                cs.nivel,
                {parts["color_select"]}
            FROM sds.senal_detectada sd
            JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.{parts["cs_id_col"]}
            JOIN sds.categoria_analisis_senal cas ON sd.{parts["sd_cat_analisis_col"]} = cas.id_categoria_analisis_senal
            WHERE DATE(sd.fecha_deteccion) = :hoy
              AND sd.id_categoria_senal IN (2, 3)
            ORDER BY sd.score_riesgo DESC, sd.fecha_deteccion DESC
            LIMIT :limite
        """), {"hoy": hoy, "limite": limite})

        alertas = []
        for row in result.fetchall():
            alertas.append({
                "id_senal_detectada": row[0],
                "fecha_deteccion": row[1],
                "score_riesgo": serialize_decimal(row[2]),
                "categoria_analisis": {
                    "id_categoria_analisis_senal": row[3],
                    "nombre_categoria_analisis": row[4],
                    "descripcion_categoria_analisis": row[5],
                },
                "categoria_senal": {
                    "id_categoria_senales": row[6],
                    "nombre_categoria_senal": row[7],
                    "descripcion_categoria_senal": row[8],
                    "nivel": row[9],
                    "color_categoria": row[10],
                    "ultimo_usuario_id": None,
                    "ultimo_usuario_nombre": None,
                    "ultima_actualizacion": None,
                },
            })

        return alertas
    
    async def obtener_estadisticas_home(self) -> dict:
        """Obtener estadísticas para el home (HU-DF008)"""
        hoy = date.today()

        total_hoy_result = await self.db.execute(text("""
            SELECT COUNT(*)
            FROM sds.senal_detectada sd
            WHERE DATE(sd.fecha_deteccion) = :hoy
        """), {"hoy": hoy})
        total_hoy = total_hoy_result.scalar()

        crisis_result = await self.db.execute(text("""
            SELECT COUNT(*)
            FROM sds.senal_detectada sd
            WHERE DATE(sd.fecha_deteccion) = :hoy
              AND sd.id_categoria_senal = 3
        """), {"hoy": hoy})
        total_crisis = crisis_result.scalar()

        paracrisis_result = await self.db.execute(text("""
            SELECT COUNT(*)
            FROM sds.senal_detectada sd
            WHERE DATE(sd.fecha_deteccion) = :hoy
              AND sd.id_categoria_senal = 2
        """), {"hoy": hoy})
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
        query = (
            select(CategoriaSenal)
            .where(CategoriaSenal.id_parent_categoria_senales != 0)
            .order_by(
                CategoriaSenal.id_parent_categoria_senales,
                CategoriaSenal.nivel,
                CategoriaSenal.nombre_categoria_senal
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def obtener_senales_recientes(self, limite: int) -> List[dict]:
        parts = await self._build_senal_query_parts()
        sd_cat_analisis_col = parts["sd_cat_analisis_col"]
        color_select = parts["color_select"]

        query = text(f"""
            SELECT 
                sd.id_senal_detectada,
                CONCAT('Señal #', sd.id_senal_detectada) as titulo,
                cs.nombre_categoria_senal,
                {color_select},
                sd.score_riesgo,
                sd.fecha_deteccion,
                cas.nombre_categoria_analisis,
                'Sistema' as usuario,
                sd.fecha_deteccion as fecha_evento
            FROM sds.senal_detectada sd
            JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales
            JOIN sds.categoria_analisis_senal cas ON sd.{sd_cat_analisis_col} = cas.id_categoria_analisis_senal
            ORDER BY sd.fecha_actualizacion DESC, sd.id_senal_detectada DESC
            LIMIT :limite
        """)

        result = await self.db.execute(query, {"limite": limite})

        senales = []
        for row in result:
            senales.append({
                "id_senal_detectada": row[0],
                "titulo": row[1],
                "categoria": row[2],
                "color": row[3],
                "score_riesgo": serialize_decimal(row[4]),
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
        estado: Optional[str],
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

        if estado:
            where_conditions.append("sd.estado = :estado")
            params["estado"] = estado

        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        parts = await self._build_senal_query_parts()
        
        # Forzar uso de columnas correctas (fix temporal para inconsistencia en esquema)
        cs_id_col = "id_categoria_senales"  # La tabla categoria_senal usa id_categoria_senales
        sd_cat_analisis_col = parts.get("sd_cat_analisis_col", "id_categoria_analisis")
        
        query = text(f"""
            SELECT 
                sd.id_senal_detectada,
                CONCAT('Señal #', sd.id_senal_detectada) as titulo,
                cs.nombre_categoria_senal,
                COALESCE(
                    cs.color,
                    CASE 
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%ruido%' THEN '#808080'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%problemas menores%' OR LOWER(cs.nombre_categoria_senal) LIKE '%problema menor%' THEN '#00FF00'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%paracrisis%' THEN '#FFA500' 
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%crisis%' THEN '#FF0000'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%rojo%' THEN '#FF0000'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%amarillo%' THEN '#FFFF00'
                        WHEN LOWER(cs.nombre_categoria_senal) LIKE '%verde%' THEN '#00FF00'
                        ELSE '#CCCCCC'
                    END
                ) as color,
                sd.score_riesgo,
                sd.fecha_deteccion,
                sd.estado,
                cas.nombre_categoria_analisis,
                'Sistema' as usuario,
                sd.fecha_deteccion as fecha_evento
            FROM sds.senal_detectada sd
            JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.{cs_id_col}
            JOIN sds.categoria_analisis_senal cas ON sd.{sd_cat_analisis_col} = cas.id_categoria_analisis_senal
            {where_clause}
            ORDER BY sd.score_riesgo DESC, sd.fecha_deteccion DESC
            LIMIT :limit OFFSET :offset
        """)

        result = await self.db.execute(query, {**params, 'limit': limit, 'offset': offset})

        senales = []
        for row in result:
            senales.append({
                "id_senal_detectada": row[0],
                "titulo": row[1],
                "categoria": row[2],
                "color": row[3],
                "score_riesgo": serialize_decimal(row[4]),
                "fecha_deteccion": row[5].isoformat(),
                "estado": row[6],
                "categoria_analisis": row[7],
                "usuario": row[8],
                "fecha_evento": row[9].isoformat() if row[9] else None
            })

        count_result = await self.db.execute(text(f"""
            SELECT COUNT(*)
            FROM sds.senal_detectada sd
            JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.{parts["cs_id_col"]}
            JOIN sds.categoria_analisis_senal cas ON sd.{parts["sd_cat_analisis_col"]} = cas.id_categoria_analisis_senal
            {where_clause}
        """), params)
        total = count_result.scalar()

        return {
            "total": total,
            "senales": senales,
            "filtros_aplicados": {
                "id_senal_detectada": id_senal_detectada,
                "categoria": categoria,
                "estado": estado,
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

        parts = await self._build_senal_query_parts()

        if tipo == "categoria_senal":
            return await self._obtener_tendencia_por_categoria(
                tabla_categoria="categoria_senal",
                sd_id_col="id_categoria_senal",
                cat_id_col=parts["cs_id_col"],
                nombre_col="nombre_categoria_senal",
                granularity=granularity,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta
            )
        if tipo == "categoria_analisis":
            return await self._obtener_tendencia_por_categoria(
                tabla_categoria="categoria_analisis_senal",
                sd_id_col=parts["sd_cat_analisis_col"],
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
        # Fix directo para JOIN con columnas correctas
        result = await self.db.execute(text("""
            SELECT 
                sd.id_senal_detectada,
                sd.fecha_deteccion,
                sd.fecha_actualizacion,
                sd.score_riesgo,
                sd.estado,
                cas.id_categoria_analisis_senal,
                cas.nombre_categoria_analisis,
                cas.descripcion_categoria_analisis,
                cs.id_categoria_senales,
                cs.nombre_categoria_senal,
                cs.descripcion_categoria_senal as descripcion,
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
            "score_riesgo": serialize_decimal(senal_row[3]),
            "estado": senal_row[4],
            "categoria_analisis": {
                "id_categoria_analisis_senal": senal_row[5],
                "nombre_categoria_analisis": senal_row[6],
                "descripcion_categoria_analisis": senal_row[7]
            },
            "categoria_senal": {
                "id_categoria_senal": senal_row[8],
                "nombre_categoria_senal": senal_row[9],
                "descripcion_categoria_senal": senal_row[10],
                "nivel": senal_row[11]
            },
            "resultados_observacion": [
                {
                    "codigo_categoria_observacion": obs_row[0],
                    "resultado_observacion_categoria": serialize_decimal(obs_row[1]),
                    "nombre_categoria_observacion": obs_row[2]
                }
                for obs_row in obs_result
            ]
        }

    async def obtener_resumen_senal(self, id_senal: int) -> Optional[dict]:
        parts = await self._build_senal_query_parts()
        result = await self.db.execute(text(f"""
            SELECT 
                sd.id_senal_detectada,
                sd.fecha_actualizacion,
                sd.score_riesgo,
                cs.nombre_categoria_senal,
                {parts["desc_expr"]} as descripcion,
                {parts["color_select"]}
            FROM sds.senal_detectada sd
            JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.{parts["cs_id_col"]}
            WHERE sd.id_senal_detectada = :id_senal
        """), {"id_senal": id_senal})

        senal_row = result.fetchone()
        if not senal_row:
            return None

        audit_row = None
        if parts["has_historial"]:
            user_join = "LEFT JOIN usuarios u ON u.id = hs.usuario_id" if parts["has_usuarios"] else ""
            user_select = "COALESCE(u.nombre_usuario, 'prueba')" if parts["has_usuarios"] else "'prueba'"
            try:
                audit_result = await self.db.execute(text(f"""
                    SELECT {user_select} as usuario_nombre, hs.fecha_registro
                    FROM sds.historial_senal hs
                    {user_join}
                    WHERE hs.id_senal_detectada = :id_senal
                    ORDER BY hs.fecha_registro DESC
                    LIMIT 1
                """), {"id_senal": id_senal})
                audit_row = audit_result.fetchone()
            except Exception as e:
                await self.db.rollback()
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
            "score_riesgo": serialize_decimal(senal_row[2])
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
        parts = await self._build_senal_query_parts()
        sd_cat_analisis_col = parts["sd_cat_analisis_col"]

        # Verificar qué columnas existen en la tabla
        sd_columns = await self._get_table_columns("sds", "senal_detectada")
        has_estado = "estado" in sd_columns
        has_fecha_actualizacion = "fecha_actualizacion" in sd_columns

        # Construir la consulta SELECT considerando columnas disponibles
        select_columns = [
            "id_categoria_senal", 
            sd_cat_analisis_col, 
            "score_riesgo", 
            "fecha_deteccion"
        ]
        if has_estado:
            select_columns.append("estado")

        current_row = await self.db.execute(
            text(f"""
                SELECT {", ".join(select_columns)}
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
            updates.append(f"{sd_cat_analisis_col} = :id_categoria_analisis")
            params["id_categoria_analisis"] = payload.id_categoria_analisis_senal

        if payload.score_riesgo is not None:
            updates.append("score_riesgo = :score_riesgo")
            params["score_riesgo"] = payload.score_riesgo

        if payload.fecha_deteccion is not None:
            updates.append("fecha_deteccion = :fecha_deteccion")
            params["fecha_deteccion"] = payload.fecha_deteccion

        if payload.estado is not None and has_estado:
            updates.append("estado = :estado")
            params["estado"] = payload.estado

        if has_fecha_actualizacion:
            updates.append("fecha_actualizacion = NOW()")

        # Construir la consulta RETURNING considerando columnas disponibles  
        returning_columns = [
            "id_senal_detectada",
            "id_categoria_senal", 
            sd_cat_analisis_col,
            "score_riesgo", 
            "fecha_deteccion"
        ]
        if has_estado:
            returning_columns.append("estado")
        if has_fecha_actualizacion:
            returning_columns.append("fecha_actualizacion")

        result = await self.db.execute(
            text(f"""
                UPDATE sds.senal_detectada
                SET {", ".join(updates)}
                WHERE id_senal_detectada = :id_senal
                RETURNING {", ".join(returning_columns)}
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
        
        # Manejar índices de columnas dinámicamente
        fecha_actualizacion_iso = None
        if has_fecha_actualizacion and len(row) > len(returning_columns) - 1:
            fecha_actualizacion_idx = len(returning_columns) - 1
            if row[fecha_actualizacion_idx]:
                fecha_actualizacion_iso = row[fecha_actualizacion_idx].isoformat()

        # Construir datos antes/después considerando columnas disponibles
        estado_antes = antes[4] if has_estado and len(antes) > 4 else None
        estado_despues = None
        if has_estado:
            estado_idx = returning_columns.index("estado")
            estado_despues = row[estado_idx] if len(row) > estado_idx else None

        datos_adicionales = {
            "usuario_nombre": usuario_nombre,
            "antes": {
                "id_categoria_senal": antes[0],
                "id_categoria_analisis_senal": antes[1],
                "score_riesgo": serialize_decimal(antes[2]),
                "fecha_deteccion": antes[3].isoformat() if antes[3] else None,
                "estado": estado_antes
            },
            "despues": {
                "id_categoria_senal": row[1],
                "id_categoria_analisis_senal": row[2],
                "score_riesgo": serialize_decimal(row[3]),
                "fecha_deteccion": row[4].isoformat() if row[4] else None,
                "estado": estado_despues
            },
            "confirmo_revision": payload.confirmo_revision,
            "cambio_tipo_categoria": cambio_tipo_categoria
        }

        descripcion_cambio = payload.descripcion_cambio.strip() if payload.descripcion_cambio else None
        if descripcion_cambio:
            datos_adicionales["descripcion_cambio"] = descripcion_cambio

        descripcion_evento = descripcion_cambio or "Actualización de señal (categoría/análisis/score/fecha)"

        audit_row = None
        if parts["has_historial"]:
            cambios_reales = (
                antes[0] != row[1]
                or antes[1] != row[2]
                or antes[2] != row[3]
                or antes[3] != row[4]
                or estado_antes != estado_despues
            )
            skip_historial = not cambios_reales and not descripcion_cambio
            if not skip_historial:
                last_event = await self.db.execute(
                    text("""
                        SELECT accion, descripcion, usuario_id
                        FROM sds.historial_senal
                        WHERE id_senal_detectada = :id_senal
                          AND fecha_registro >= NOW() - INTERVAL '5 seconds'
                        ORDER BY fecha_registro DESC
                        LIMIT 1
                    """),
                    {"id_senal": id_senal}
                )
                last_row = last_event.fetchone()
                if last_row and last_row[0] == "Actualizacion_estado_señal" and last_row[1] == descripcion_evento and last_row[2] == usuario_id:
                    skip_historial = True
            if not skip_historial:
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
                        "accion": "Actualizacion_estado_señal",
                        "descripcion": descripcion_evento,
                        "estado_anterior": str(estado_antes) if estado_antes is not None else None,
                        "estado_nuevo": str(estado_despues) if estado_despues is not None else None,
                        "datos_adicionales": safe_json_dumps(datos_adicionales),
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

        # Construir respuesta con índices dinámicos
        response = {
            "id_senal_detectada": row[0],
            "id_categoria_senal": row[1],
            "id_categoria_analisis_senal": row[2],
            "score_riesgo": serialize_decimal(row[3]),
            "fecha_deteccion": row[4].isoformat() if row[4] else None,
        }
        
        # Agregar estado si está disponible
        if has_estado:
            estado_idx = returning_columns.index("estado")
            response["estado"] = row[estado_idx] if len(row) > estado_idx else None

        # Agregar fecha_actualizacion si está disponible  
        if has_fecha_actualizacion:
            fecha_idx = returning_columns.index("fecha_actualizacion")
            response["fecha_actualizacion"] = row[fecha_idx].isoformat() if len(row) > fecha_idx and row[fecha_idx] else None

        response["auditoria"] = {
            "id": audit_row[0] if audit_row else None,
            "usuario": usuario_nombre,
            "fecha_registro": audit_row[1].isoformat() if audit_row and audit_row[1] else None
        }

        return serialize_decimal(response)

    async def listar_historial_senal(
        self,
        usuario_id: Optional[int] = None,
        id_senal: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        if not await self._table_exists("sds", "historial_senal"):
            return []

        has_usuarios = await self._table_exists("public", "usuarios")
        join_usuarios = "LEFT JOIN public.usuarios u ON u.id = hs.usuario_id" if has_usuarios else ""
        usuario_select = "u.nombre_usuario as usuario_nombre" if has_usuarios else "NULL as usuario_nombre"

        conditions = []
        params = {"limit": limit, "offset": skip}
        if usuario_id is not None:
            conditions.append("hs.usuario_id = :usuario_id")
            params["usuario_id"] = usuario_id
        if id_senal is not None:
            conditions.append("hs.id_senal_detectada = :id_senal")
            params["id_senal"] = id_senal

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        result = await self.db.execute(
            text(f"""
                SELECT
                    hs.id,
                    hs.id_senal_detectada,
                    hs.usuario_id,
                    {usuario_select},
                    hs.accion,
                    hs.descripcion,
                    hs.estado_anterior,
                    hs.estado_nuevo,
                    hs.fecha_registro,
                    hs.ip_address,
                    hs.datos_adicionales
                FROM sds.historial_senal hs
                {join_usuarios}
                {where_clause}
                ORDER BY hs.fecha_registro DESC
                LIMIT :limit OFFSET :offset
            """),
            params
        )
        rows = result.fetchall()

        historial = []
        for row in rows:
            datos = row[10]
            if isinstance(datos, str):
                try:
                    datos = json.loads(datos)
                except json.JSONDecodeError:
                    datos = None

            descripcion_cambio = None
            cambio_tipo_categoria = None
            confirmo_revision = None
            categoria_antes = None
            categoria_despues = None
            if isinstance(datos, dict):
                descripcion_cambio = datos.get("descripcion_cambio")
                cambio_tipo_categoria = datos.get("cambio_tipo_categoria")
                confirmo_revision = datos.get("confirmo_revision")
                antes = datos.get("antes") or {}
                despues = datos.get("despues") or {}
                categoria_antes = antes.get("id_categoria_senal")
                categoria_despues = despues.get("id_categoria_senal")

            historial.append({
                "id": row[0],
                "id_senal_detectada": row[1],
                "usuario_id": row[2],
                "usuario_nombre": row[3],
                "accion": row[4],
                "descripcion": row[5],
                "estado_anterior": row[6],
                "estado_nuevo": row[7],
                "fecha_registro": row[8],
                "ip_address": row[9],
                "descripcion_cambio": descripcion_cambio,
                "cambio_tipo_categoria": cambio_tipo_categoria,
                "confirmo_revision": confirmo_revision,
                "categoria_senal_antes": categoria_antes,
                "categoria_senal_despues": categoria_despues,
                "datos_adicionales": datos
            })

        return historial

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
        cs_columns = await self._get_table_columns("sds", "categoria_senal")
        color_col = None
        if "color" in cs_columns:
            color_col = "color"
        elif "color_categoria" in cs_columns:
            color_col = "color_categoria"

        desc_col = None
        if "descripcion_categoria_senal" in cs_columns:
            desc_col = "descripcion_categoria_senal"
        elif "descripcion" in cs_columns:
            desc_col = "descripcion"

        has_fecha_actualizacion = "fecha_actualizacion" in cs_columns

        updates = []
        params = {"id_categoria_senal": id_categoria_senal}
        if payload.color_categoria is not None:
            if color_col:
                updates.append(f"{color_col} = :color_nuevo")
                params["color_nuevo"] = payload.color_categoria
            else:
                logger.warning("No se encontro columna de color en sds.categoria_senal")
        if payload.descripcion_categoria_senal is not None:
            if desc_col:
                updates.append(f"{desc_col} = :descripcion_categoria_senal")
                params["descripcion_categoria_senal"] = payload.descripcion_categoria_senal
            else:
                logger.warning("No se encontro columna de descripcion en sds.categoria_senal")

        if updates and has_fecha_actualizacion:
            updates.append("fecha_actualizacion = NOW()")
        if not updates:
            return None

        color_return = f"{color_col} as color" if color_col else "NULL as color"
        desc_return = f"{desc_col} as descripcion_categoria_senal" if desc_col else "NULL as descripcion_categoria_senal"
        fecha_return = "fecha_actualizacion" if has_fecha_actualizacion else "NULL as fecha_actualizacion"

        # Solo incluir fecha_actualizacion en el RETURNING si la columna existe
        returning_cols = [f"id_categoria_senales, {color_return}, {desc_return}"]
        if has_fecha_actualizacion:
            returning_cols.append("fecha_actualizacion")
        else:
            returning_cols.append("NULL as fecha_actualizacion")

        result = await self.db.execute(
            text(f"""
                UPDATE sds.categoria_senal
                SET {", ".join(updates)}
                WHERE id_categoria_senales = :id_categoria_senal
                RETURNING {", ".join(returning_cols)}
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
            "ultima_actualizacion": row[3].isoformat() if row[3] else None,
            "usuario": usuario_nombre,
            "fecha_evento": evento.fecha_evento.isoformat()
        }

    async def obtener_analisis_completo(self, id_senal: int) -> Optional[dict]:
        parts = await self._build_senal_query_parts()
        result = await self.db.execute(text(f"""
            SELECT 
                sd.id_senal_detectada,
                sd.fecha_deteccion,
                sd.score_riesgo,
                cs.nombre_categoria_senal,
                {parts["color_select"]},
                cas.nombre_categoria_analisis
            FROM sds.senal_detectada sd
            JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.{parts["cs_id_col"]}
            JOIN sds.categoria_analisis_senal cas ON sd.{parts["sd_cat_analisis_col"]} = cas.id_categoria_analisis_senal
            WHERE sd.id_senal_detectada = :id_senal
        """), {"id_senal": id_senal})

        senal_data = result.fetchone()
        if not senal_data:
            return None

        return {
            "senal_base": {
                "id_senal_detectada": senal_data[0],
                "fecha_deteccion": senal_data[1].isoformat(),
                "score_riesgo": serialize_decimal(senal_data[2]),
                "categoria_senal": senal_data[3],
                "color": senal_data[4],
                "categoria_analisis": senal_data[5]
            },
            "observaciones_multidimensionales": [],
            "total_observaciones": 0,
            "score_total": serialize_decimal(senal_data[2])
        }

    async def registrar_historial_senal(
        self,
        id_senal_detectada: int,
        accion: str,
        descripcion: Optional[str] = None,
        estado_anterior: Optional[str] = None,
        estado_nuevo: Optional[str] = None,
        datos_adicionales: Optional[dict] = None,
        usuario_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> HistorialSenal:
        """
        Registra un nuevo evento en el historial de una señal usando SQLAlchemy ORM.
        
        Args:
            id_senal_detectada: ID de la señal
            accion: Tipo de acción (CREACION, ACTUALIZACION, CAMBIO_ESTADO, etc.)
            descripcion: Descripción del evento
            estado_anterior: Estado previo (opcional)
            estado_nuevo: Estado nuevo (opcional)
            datos_adicionales: Datos JSON adicionales (opcional)
            usuario_id: ID del usuario que realiza la acción (opcional)
            ip_address: Dirección IP del cliente (opcional)
            
        Returns:
            HistorialSenal: Registro del historial creado
        """
        historial_entry = HistorialSenal(
            id_senal_detectada=id_senal_detectada,
            accion=accion,
            descripcion=descripcion,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            datos_adicionales=datos_adicionales,
            usuario_id=usuario_id,
            ip_address=ip_address,
            fecha_registro=datetime.now()
        )
        
        self.db.add(historial_entry)
        await self.db.flush()  # Para obtener el ID generado
        
        return historial_entry
