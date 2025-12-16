import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


class DatabaseHealthChecker:
    def __init__(self):
        self.engine = create_async_engine(
            settings.database_url,
            echo=False,
            pool_pre_ping=True
        )
        self.checks = []
        self.warnings = []
        self.errors = []
    
    async def check_conexion(self):
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                result.scalar()
            self.checks.append(("Conexión", "OK", ""))
            return True
        except Exception as e:
            self.errors.append(("Conexión", f"FALLO: {str(e)}"))
            return False
    
    async def check_version(self):
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
            # Extraer número de versión
            version_num = version.split()[1].split('.')[0]
            
            if int(version_num) >= 14:
                self.checks.append(("Versión PostgreSQL", version_num, ""))
            else:
                self.warnings.append(("Versión PostgreSQL", f"{version_num} (se recomienda >= 14)"))
            
            return True
        except Exception as e:
            self.errors.append(("Versión", str(e)))
            return False
    
    async def check_espacio_disco(self):
        try:
            async with self.engine.connect() as conn:
                # Tamaño total de la base de datos
                result = await conn.execute(text("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                tablespace = result.fetchone()
                self.checks.append(("Tamaño BD", db_size, ""))
                self.checks.append(("Tablespace", tablespace[1] if tablespace else "N/A", ""))
            
            return True
        except Exception as e:
            self.warnings.append(("Espacio Disco", str(e)))
            return False
    
    async def check_conexiones(self):
        try:
            async with self.engine.connect() as conn:
                # Conexiones activas
                result = await conn.execute(text("""
                    SELECT 
                        COUNT(*) FILTER (WHERE state = 'active') as active,
                        COUNT(*) FILTER (WHERE state = 'idle') as idle,
                        COUNT(*) as total
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                ratio = result.scalar() or 0
                if ratio >= 95:
                    self.checks.append(("Cache Hit Ratio", f"{ratio}%", ""))
                elif ratio >= 80:
                    self.warnings.append(("Cache Hit Ratio", f"{ratio}% (se recomienda > 95%)"))
                else:
                    self.errors.append(("Cache Hit Ratio", f"{ratio}% - ¡Muy bajo! Revisar shared_buffers"))
            
            return True
        except Exception as e:
            self.warnings.append(("Cache Hit Ratio", str(e)))
            return False
    
    async def check_locks(self):
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute(text("""
                    SELECT 
                        COUNT(*) FILTER (WHERE NOT granted) as waiting_locks,
                        COUNT(*) as total_locks
                    FROM pg_locks
                    WHERE database = (SELECT oid FROM pg_database WHERE datname = current_database())
                slow_queries = result.fetchall()
                if not slow_queries:
                    self.checks.append(("Queries Lentas", "Ninguna > 5s", ""))
                else:
                    self.warnings.append(
                        ("Queries Lentas", 
                         f"{len(slow_queries)} queries > 5s encontradas")
                    )
            
            return True
        except Exception as e:
            self.warnings.append(("Queries Lentas", str(e)))
            return False
    
    async def check_sesiones_expiradas(self):
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM sesiones 
                    WHERE fecha_expiracion < NOW() 
                    AND activa = true
                huerfanas = result.scalar()
                # 2. Usuarios con demasiadas sesiones activas
                result = await conn.execute(text("""
                    SELECT usuario_id, COUNT(*) as sesiones_count
                    FROM sesiones
                    WHERE activa = true AND revocada = false
                    GROUP BY usuario_id
                    HAVING COUNT(*) > 10
                muy_expiradas = result.scalar()

                # Reportar resultados
                issues = []
                if huerfanas > 0:
                    issues.append(f"{huerfanas} sesiones huÃ©rfanas")
                if len(usuarios_exceso) > 0:
                    issues.append(f"{len(usuarios_exceso)} usuarios con >10 sesiones")
                if muy_expiradas > 0:
                    issues.append(f"{muy_expiradas} sesiones expiradas hace >7 dÃ­as")

                if not issues:
                    self.checks.append(("Sesiones Adicionales", "Todo OK", "âœ…"))
                else:
                    self.warnings.append(("Sesiones Adicionales", ", ".join(issues)))

            return True
        except Exception as e:
            self.warnings.append(("Sesiones Adicionales", str(e)))
            return False

    async def check_eventos_auditoria(self):
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute(text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE fecha_evento > NOW() - INTERVAL '7 days') as ultimos_7_dias,
                        pg_size_pretty(pg_total_relation_size('eventos_auditoria')) as size
                    FROM eventos_auditoria
                unused = result.scalar()
                # Índices inválidos
                result = await conn.execute(text("""
                    SELECT COUNT(*)
                    FROM pg_index
                    WHERE NOT indisvalid
