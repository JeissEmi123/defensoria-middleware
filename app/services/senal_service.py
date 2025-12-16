"""
Servicio de gestión de señales detectadas
Lógica de negocio para el módulo de detección de señales
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, desc, asc, text
from sqlalchemy.orm import selectinload

from app.database.models import (
    SenalDetectada,
    CategoriaSenal,
    CategoriaAnalisisSenal,
    HistorialSenal,
    Usuario
)
from app.schemas.senales import (
    SenalDetectadaCreate,
    SenalDetectadaUpdate,
    SenalDetectadaResponse,
    SenalDetectadaDetalle,
    SenalDetectadaFiltros,
    EstadisticasSenales,
    AsignacionMasiva,
    CambioEstadoMasivo,
    HistorialSenalCreate
)


class SenalService:
    """Servicio para gestión de señales detectadas"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def listar_senales(
        self,
        skip: int = 0,
        limit: int = 100,
        orden: str = "fecha_desc",
        filtros: Optional[SenalDetectadaFiltros] = None
    ) -> Tuple[List[SenalDetectada], int]:
        """
        Listar señales con paginación, ordenamiento y filtros
        
        Args:
            skip: Offset para paginación
            limit: Límite de resultados
            orden: Criterio de ordenamiento (fecha_desc, fecha_asc, score_desc, score_asc)
            filtros: Filtros opcionales
            
        Returns:
            Tupla (lista_senales, total_count)
        """
        # Construir query base
        query = select(SenalDetectada).options(
            selectinload(SenalDetectada.categoria_senal),
            selectinload(SenalDetectada.categoria_analisis),
            selectinload(SenalDetectada.usuario_asignado)
        )
        
        # Aplicar filtros
        if filtros:
            if filtros.estado:
                query = query.where(SenalDetectada.estado == filtros.estado)
            
            if filtros.id_categoria_senal:
                query = query.where(SenalDetectada.id_categoria_senal == filtros.id_categoria_senal)
            
            if filtros.id_categoria_analisis:
                query = query.where(SenalDetectada.id_categoria_analisis == filtros.id_categoria_analisis)
            
            if filtros.score_riesgo_min is not None:
                query = query.where(SenalDetectada.score_riesgo >= filtros.score_riesgo_min)
            
            if filtros.score_riesgo_max is not None:
                query = query.where(SenalDetectada.score_riesgo <= filtros.score_riesgo_max)
            
            if filtros.fecha_desde:
                # Convertir a naive datetime (sin timezone) si es necesario
                fecha_desde_naive = filtros.fecha_desde.replace(tzinfo=None) if filtros.fecha_desde.tzinfo else filtros.fecha_desde
                query = query.where(SenalDetectada.fecha_deteccion >= fecha_desde_naive)
            
            if filtros.fecha_hasta:
                # Convertir a naive datetime (sin timezone) si es necesario
                fecha_hasta_naive = filtros.fecha_hasta.replace(tzinfo=None) if filtros.fecha_hasta.tzinfo else filtros.fecha_hasta
                query = query.where(SenalDetectada.fecha_deteccion <= fecha_hasta_naive)
            
            if filtros.plataforma:
                # Búsqueda en array JSON
                query = query.where(
                    SenalDetectada.plataformas_digitales.contains([filtros.plataforma])
                )
            
            if filtros.usuario_asignado_id:
                query = query.where(SenalDetectada.usuario_asignado_id == filtros.usuario_asignado_id)
        
        # Contar total antes de paginación
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0
        
        # Aplicar ordenamiento
        if orden == "fecha_desc":
            query = query.order_by(desc(SenalDetectada.fecha_deteccion))
        elif orden == "fecha_asc":
            query = query.order_by(asc(SenalDetectada.fecha_deteccion))
        elif orden == "score_desc":
            query = query.order_by(desc(SenalDetectada.score_riesgo), desc(SenalDetectada.fecha_deteccion))
        elif orden == "score_asc":
            query = query.order_by(asc(SenalDetectada.score_riesgo), desc(SenalDetectada.fecha_deteccion))
        else:
            # Por defecto: fecha descendente
            query = query.order_by(desc(SenalDetectada.fecha_deteccion))
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        # Ejecutar query
        result = await self.db.execute(query)
        senales = result.scalars().all()
        
        return list(senales), total
    
    async def buscar_senales(
        self,
        busqueda: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[SenalDetectada], int]:
        """
        Búsqueda full-text en señales
        
        Args:
            busqueda: Término de búsqueda
            skip: Offset para paginación
            limit: Límite de resultados
            
        Returns:
            Tupla (lista_senales, total_count)
        """
        # Búsqueda en múltiples campos
        search_pattern = f"%{busqueda}%"
        
        query = select(SenalDetectada).options(
            selectinload(SenalDetectada.categoria_senal),
            selectinload(SenalDetectada.categoria_analisis)
        ).where(
            or_(
                SenalDetectada.contenido_detectado.ilike(search_pattern),
                SenalDetectada.url_origen.ilike(search_pattern),
                SenalDetectada.notas_resolucion.ilike(search_pattern)
            )
        )
        
        # Contar total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0
        
        # Ordenar por relevancia (score + fecha)
        query = query.order_by(
            desc(SenalDetectada.score_riesgo),
            desc(SenalDetectada.fecha_deteccion)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        senales = result.scalars().all()
        
        return list(senales), total
    
    async def obtener_senal(self, id_senal: int) -> Optional[SenalDetectada]:
        """
        Obtener señal por ID con todas sus relaciones
        
        Args:
            id_senal: ID de la señal
            
        Returns:
            Señal encontrada o None
        """
        query = select(SenalDetectada).options(
            selectinload(SenalDetectada.categoria_senal),
            selectinload(SenalDetectada.categoria_analisis),
            selectinload(SenalDetectada.usuario_asignado),
            selectinload(SenalDetectada.historial)
        ).where(SenalDetectada.id_senal_detectada == id_senal)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def crear_senal(
        self,
        senal_data: SenalDetectadaCreate,
        usuario_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> SenalDetectada:
        """
        Crear nueva señal detectada
        
        Args:
            senal_data: Datos de la señal
            usuario_id: ID del usuario creador
            ip_address: IP del cliente
            
        Returns:
            Señal creada
        """
        # Crear señal
        senal = SenalDetectada(**senal_data.model_dump())
        self.db.add(senal)
        await self.db.flush()  # Para obtener el ID
        
        # Registrar en historial
        historial = HistorialSenal(
            id_senal_detectada=senal.id_senal_detectada,
            usuario_id=usuario_id,
            accion="CREACION",
            descripcion="Señal detectada y registrada en el sistema",
            estado_nuevo=senal.estado,
            datos_adicionales={"origen": "manual" if usuario_id else "automatico"},
            ip_address=ip_address
        )
        self.db.add(historial)
        
        await self.db.commit()
        await self.db.refresh(senal)
        
        return senal
    
    async def actualizar_senal(
        self,
        id_senal: int,
        senal_data: SenalDetectadaUpdate,
        usuario_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> Optional[SenalDetectada]:
        """
        Actualizar señal existente
        
        Args:
            id_senal: ID de la señal
            senal_data: Datos a actualizar
            usuario_id: ID del usuario que actualiza
            ip_address: IP del cliente
            
        Returns:
            Señal actualizada o None
        """
        senal = await self.obtener_senal(id_senal)
        if not senal:
            return None
        
        # Guardar valores anteriores para historial
        estado_anterior = senal.estado
        cambios = {}
        
        # Actualizar campos
        update_data = senal_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None and getattr(senal, field) != value:
                cambios[field] = {
                    "anterior": str(getattr(senal, field)),
                    "nuevo": str(value)
                }
                setattr(senal, field, value)
        
        # Si hay cambios, registrar en historial
        if cambios:
            descripcion = f"Campos actualizados: {', '.join(cambios.keys())}"
            historial = HistorialSenal(
                id_senal_detectada=id_senal,
                usuario_id=usuario_id,
                accion="ACTUALIZACION",
                descripcion=descripcion,
                estado_anterior=estado_anterior if "estado" in cambios else None,
                estado_nuevo=senal.estado if "estado" in cambios else None,
                datos_adicionales={"cambios": cambios},
                ip_address=ip_address
            )
            self.db.add(historial)
        
        await self.db.commit()
        await self.db.refresh(senal)
        
        return senal
    
    async def cambiar_categoria(
        self,
        id_senal: int,
        nueva_categoria_id: int,
        comentario: Optional[str] = None,
        confirmo_revision: bool = False,
        usuario_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> Optional[SenalDetectada]:
        """
        Cambiar categoría de señal con registro en historial
        
        Args:
            id_senal: ID de la señal
            nueva_categoria_id: ID de la nueva categoría
            comentario: Comentario opcional del cambio
            confirmo_revision: Confirmación de revisión
            usuario_id: ID del usuario que cambia
            ip_address: IP del cliente
            
        Returns:
            Señal actualizada o None
        """
        if not confirmo_revision:
            raise ValueError("Debe confirmar la revisión antes de cambiar la categoría")
        
        senal = await self.obtener_senal(id_senal)
        if not senal:
            return None
        
        # Obtener categorías para nombres
        categoria_anterior = await self.db.get(CategoriaSenal, senal.id_categoria_senal)
        categoria_nueva = await self.db.get(CategoriaSenal, nueva_categoria_id)
        
        if not categoria_nueva:
            raise ValueError(f"Categoría {nueva_categoria_id} no encontrada")
        
        # Guardar valor anterior
        id_categoria_anterior = senal.id_categoria_senal
        nombre_anterior = categoria_anterior.nombre_categoria_senal if categoria_anterior else "N/A"
        
        # Actualizar categoría
        senal.id_categoria_senal = nueva_categoria_id
        
        # Registrar en historial
        historial = HistorialSenal(
            id_senal_detectada=id_senal,
            usuario_id=usuario_id,
            accion="CAMBIO_CATEGORIA",
            descripcion=comentario or f"Categoría cambiada de {nombre_anterior} a {categoria_nueva.nombre_categoria_senal}",
            estado_anterior=nombre_anterior,
            estado_nuevo=categoria_nueva.nombre_categoria_senal,
            datos_adicionales={
                "categoria_anterior_id": id_categoria_anterior,
                "categoria_nueva_id": nueva_categoria_id,
                "confirmo_revision": confirmo_revision
            },
            ip_address=ip_address
        )
        self.db.add(historial)
        
        await self.db.commit()
        await self.db.refresh(senal)
        
        # Si cambió a CRISIS, aquí se podría enviar notificación
        # TODO: Implementar servicio de notificaciones
        if categoria_nueva.nombre_categoria_senal == "CRISIS":
            # Enviar email al coordinador
            pass
        
        return senal
    
    async def obtener_alertas_criticas(
        self,
        limite: int = 5
    ) -> List[SenalDetectada]:
        """
        Obtener top alertas críticas del día
        
        Args:
            limite: Número máximo de alertas a retornar
            
        Returns:
            Lista de señales críticas
        """
        hoy = datetime.now().date()
        inicio_dia = datetime.combine(hoy, datetime.min.time())
        
        query = select(SenalDetectada).options(
            selectinload(SenalDetectada.categoria_senal),
            selectinload(SenalDetectada.categoria_analisis)
        ).join(
            CategoriaSenal,
            SenalDetectada.id_categoria_senal == CategoriaSenal.id_categoria_senal
        ).where(
            and_(
                SenalDetectada.fecha_deteccion >= inicio_dia,
                or_(
                    CategoriaSenal.nombre_categoria_senal == "CRISIS",
                    CategoriaSenal.nombre_categoria_senal == "PARACRISIS"
                )
            )
        ).order_by(
            desc(SenalDetectada.score_riesgo),
            desc(SenalDetectada.fecha_deteccion)
        ).limit(limite)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def obtener_indicadores(self) -> Dict[str, Any]:
        """
        Obtener indicadores del sistema
        
        Returns:
            Diccionario con indicadores
        """
        # Total de señales activas (no resueltas ni rechazadas)
        query_activas = select(func.count(SenalDetectada.id_senal_detectada)).where(
            SenalDetectada.estado.in_(["DETECTADA", "EN_REVISION", "VALIDADA"])
        )
        total_activas = await self.db.scalar(query_activas) or 0
        
        # Señales en revisión
        query_revision = select(func.count(SenalDetectada.id_senal_detectada)).where(
            SenalDetectada.estado == "EN_REVISION"
        )
        en_revision = await self.db.scalar(query_revision) or 0
        
        # Por categoría (señales activas)
        query_por_categoria = select(
            CategoriaSenal.nombre_categoria_senal,
            func.count(SenalDetectada.id_senal_detectada)
        ).join(
            SenalDetectada,
            SenalDetectada.id_categoria_senal == CategoriaSenal.id_categoria_senal
        ).where(
            SenalDetectada.estado.in_(["DETECTADA", "EN_REVISION", "VALIDADA"])
        ).group_by(CategoriaSenal.nombre_categoria_senal)
        
        result = await self.db.execute(query_por_categoria)
        por_categoria = {row[0]: row[1] for row in result}
        
        return {
            "total_activas": total_activas,
            "en_revision": en_revision,
            "por_categoria": por_categoria,
            "fecha_calculo": datetime.now().isoformat()
        }
    
    async def obtener_estadisticas(
        self,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None
    ) -> EstadisticasSenales:
        """
        Obtener estadísticas completas del sistema
        
        Args:
            fecha_desde: Fecha inicio del rango
            fecha_hasta: Fecha fin del rango
            
        Returns:
            Estadísticas detalladas
        """
        # Query base con filtro de fechas
        base_query = select(SenalDetectada)
        if fecha_desde:
            base_query = base_query.where(SenalDetectada.fecha_deteccion >= fecha_desde)
        if fecha_hasta:
            base_query = base_query.where(SenalDetectada.fecha_deteccion <= fecha_hasta)
        
        # Total de señales
        total = await self.db.scalar(
            select(func.count()).select_from(base_query.subquery())
        ) or 0
        
        # Por estado
        query_estado = select(
            SenalDetectada.estado,
            func.count(SenalDetectada.id_senal_detectada)
        ).group_by(SenalDetectada.estado)
        
        if fecha_desde or fecha_hasta:
            if fecha_desde:
                query_estado = query_estado.where(SenalDetectada.fecha_deteccion >= fecha_desde)
            if fecha_hasta:
                query_estado = query_estado.where(SenalDetectada.fecha_deteccion <= fecha_hasta)
        
        result = await self.db.execute(query_estado)
        por_estado = {row[0]: row[1] for row in result}
        
        # Por categoría de señal
        query_cat_senal = select(
            CategoriaSenal.nombre_categoria_senal,
            func.count(SenalDetectada.id_senal_detectada)
        ).join(
            SenalDetectada,
            SenalDetectada.id_categoria_senal == CategoriaSenal.id_categoria_senal
        ).group_by(CategoriaSenal.nombre_categoria_senal)
        
        if fecha_desde or fecha_hasta:
            if fecha_desde:
                query_cat_senal = query_cat_senal.where(SenalDetectada.fecha_deteccion >= fecha_desde)
            if fecha_hasta:
                query_cat_senal = query_cat_senal.where(SenalDetectada.fecha_deteccion <= fecha_hasta)
        
        result = await self.db.execute(query_cat_senal)
        por_categoria_senal = {row[0]: row[1] for row in result}
        
        # Por categoría de análisis
        query_cat_analisis = select(
            CategoriaAnalisisSenal.nombre_categoria_analisis,
            func.count(SenalDetectada.id_senal_detectada)
        ).join(
            SenalDetectada,
            SenalDetectada.id_categoria_analisis == CategoriaAnalisisSenal.id
        ).group_by(CategoriaAnalisisSenal.nombre_categoria_analisis)
        
        if fecha_desde or fecha_hasta:
            if fecha_desde:
                query_cat_analisis = query_cat_analisis.where(SenalDetectada.fecha_deteccion >= fecha_desde)
            if fecha_hasta:
                query_cat_analisis = query_cat_analisis.where(SenalDetectada.fecha_deteccion <= fecha_hasta)
        
        result = await self.db.execute(query_cat_analisis)
        por_categoria_analisis = {row[0]: row[1] for row in result}
        
        # Score promedio
        score_avg = await self.db.scalar(
            select(func.avg(SenalDetectada.score_riesgo)).select_from(base_query.subquery())
        )
        
        # Señales última semana
        hace_semana = datetime.now() - timedelta(days=7)
        senales_semana = await self.db.scalar(
            select(func.count(SenalDetectada.id_senal_detectada)).where(
                SenalDetectada.fecha_deteccion >= hace_semana
            )
        ) or 0
        
        # Señales último mes
        hace_mes = datetime.now() - timedelta(days=30)
        senales_mes = await self.db.scalar(
            select(func.count(SenalDetectada.id_senal_detectada)).where(
                SenalDetectada.fecha_deteccion >= hace_mes
            )
        ) or 0
        
        return EstadisticasSenales(
            total_senales=total,
            por_estado=por_estado,
            por_categoria_senal=por_categoria_senal,
            por_categoria_analisis=por_categoria_analisis,
            score_promedio=float(score_avg) if score_avg else None,
            senales_ultima_semana=senales_semana,
            senales_ultimo_mes=senales_mes
        )
    
    async def asignar_masivo(
        self,
        asignacion: AsignacionMasiva,
        usuario_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> int:
        """
        Asignar múltiples señales a un usuario
        
        Args:
            asignacion: Datos de asignación masiva
            usuario_id: ID del usuario que realiza la asignación
            ip_address: IP del cliente
            
        Returns:
            Número de señales asignadas
        """
        # Verificar que el usuario asignado existe
        usuario_asignado = await self.db.get(Usuario, asignacion.usuario_asignado_id)
        if not usuario_asignado:
            raise ValueError(f"Usuario {asignacion.usuario_asignado_id} no encontrado")
        
        count = 0
        for id_senal in asignacion.ids_senales:
            senal = await self.obtener_senal(id_senal)
            if senal:
                usuario_anterior_id = senal.usuario_asignado_id
                senal.usuario_asignado_id = asignacion.usuario_asignado_id
                
                # Registrar en historial
                historial = HistorialSenal(
                    id_senal_detectada=id_senal,
                    usuario_id=usuario_id,
                    accion="ASIGNACION",
                    descripcion=asignacion.notas or f"Señal asignada a {usuario_asignado.nombre_usuario}",
                    datos_adicionales={
                        "usuario_anterior_id": usuario_anterior_id,
                        "usuario_nuevo_id": asignacion.usuario_asignado_id
                    },
                    ip_address=ip_address
                )
                self.db.add(historial)
                count += 1
        
        await self.db.commit()
        return count
    
    async def cambiar_estado_masivo(
        self,
        cambio: CambioEstadoMasivo,
        usuario_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> int:
        """
        Cambiar estado de múltiples señales
        
        Args:
            cambio: Datos del cambio masivo
            usuario_id: ID del usuario que realiza el cambio
            ip_address: IP del cliente
            
        Returns:
            Número de señales actualizadas
        """
        count = 0
        for id_senal in cambio.ids_senales:
            senal = await self.obtener_senal(id_senal)
            if senal:
                estado_anterior = senal.estado
                senal.estado = cambio.nuevo_estado
                
                if cambio.nuevo_estado == "RESUELTA":
                    senal.fecha_resolucion = datetime.now()
                    if cambio.notas:
                        senal.notas_resolucion = cambio.notas
                
                # Registrar en historial
                historial = HistorialSenal(
                    id_senal_detectada=id_senal,
                    usuario_id=usuario_id,
                    accion="CAMBIO_ESTADO",
                    descripcion=cambio.notas or f"Estado cambiado a {cambio.nuevo_estado}",
                    estado_anterior=estado_anterior,
                    estado_nuevo=cambio.nuevo_estado,
                    ip_address=ip_address
                )
                self.db.add(historial)
                count += 1
        
        await self.db.commit()
        return count
