import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


async def crear_indices_compuestos():
    logger.info("creando_indices_compuestos")
    engine = create_async_engine(settings.database_url, echo=True)
    
    indices = [
        # Índice compuesto para búsquedas de sesiones activas por usuario
        
        # Índice compuesto para auditoría por usuario y fecha
        
        # Índice compuesto para auditoría por tipo y resultado
        
        # Índice para búsquedas de usuarios activos
        
        # Índice para roles activos
        
        # Índice GIN para búsqueda en JSON de metadatos
        
        # Índice GIN para búsqueda en JSON de detalles de auditoría
    ]
    
    async with engine.begin() as conn:
        for idx, sql in enumerate(indices, 1):
            try:
                logger.info(f"creando_indice_{idx}")
                await conn.execute(text(sql))
                logger.info(f"indice_{idx}_creado")
            except Exception as e:
                logger.warning(f"error_indice_{idx}", error=str(e))
    
    await engine.dispose()
    logger.info("indices_compuestos_creados")


async def analizar_tablas():
    logger.info("analizando_tablas")
    engine = create_async_engine(settings.database_url, echo=False)
    
    tablas = [
        'usuarios', 'roles', 'permisos',
        'usuarios_roles', 'roles_permisos',
        'sesiones', 'eventos_auditoria', 'configuracion_sistema'
    ]
    
    async with engine.begin() as conn:
        for tabla in tablas:
            logger.info(f"analizando_{tabla}")
            await conn.execute(text(f"ANALYZE {tabla}"))
    
    await engine.dispose()
    logger.info("analisis_completado")


async def vacuum_tablas():
    logger.info("vacuum_tablas")
    # Nota: VACUUM no puede ejecutarse dentro de una transacción
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        isolation_level="AUTOCOMMIT"
    )
    
    tablas_vacuum = [
        'sesiones',  # Alta rotación de datos
        'eventos_auditoria'  # Crece constantemente
    ]
    
    async with engine.connect() as conn:
        for tabla in tablas_vacuum:
            try:
                logger.info(f"vacuum_{tabla}")
                await conn.execute(text(f"VACUUM ANALYZE {tabla}"))
                logger.info(f"vacuum_{tabla}_completado")
            except Exception as e:
                logger.error(f"error_vacuum_{tabla}", error=str(e))
    
    await engine.dispose()
    logger.info("vacuum_completado")


async def estadisticas_uso():
    logger.info("generando_estadisticas")
    engine = create_async_engine(settings.database_url, echo=False)
    
    queries = {
        "tamaño_tablas": """
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS tamaño,
                pg_total_relation_size(schemaname||'.'||tablename) AS bytes
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY bytes DESC
        
        "indices_no_usados": """
            SELECT 
                schemaname,
                tablename,
                indexname,
                pg_size_pretty(pg_relation_size(indexrelid)) AS tamaño
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            AND idx_scan = 0
            AND indexrelid NOT IN (
                SELECT conindid FROM pg_constraint WHERE contype IN ('p', 'u')
            )
    }
    
    async with engine.connect() as conn:
        for nombre, query in queries.items():
            logger.info(f"ejecutando_{nombre}")
            result = await conn.execute(text(query))
            rows = result.fetchall()
            
            print(f"\n{'='*80}")
            print(f" {nombre.replace('_', ' ').upper()}")
            print('='*80)
            
            for row in rows:
                print(" | ".join(str(col) for col in row))
            
            print('='*80)
    
    await engine.dispose()


async def sugerencias_optimizacion():
    logger.info("analizando_optimizaciones")
    engine = create_async_engine(settings.database_url, echo=False)
    
    print("\n" + "="*80)
    print(" SUGERENCIAS DE OPTIMIZACIÓN")
    print("="*80 + "\n")
    
    async with engine.connect() as conn:
        # 1. Tablas sin índices en foreign keys
        result = await conn.execute(text("""
            SELECT 
                tc.table_name,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            AND NOT EXISTS (
                SELECT 1
                FROM pg_indexes
                WHERE schemaname = 'public'
                AND tablename = tc.table_name
                AND indexdef LIKE '%' || kcu.column_name || '%'
            )
        
        print(" Configuración actual de PostgreSQL:")
        for row in result.fetchall():
            print(f"   {row[0]}: {row[1]} {row[2] or ''}")
        print()
        
        # 3. Conexiones activas
        result = await conn.execute(text("""
            SELECT 
                state,
                COUNT(*) as count
            FROM pg_stat_activity
            WHERE datname = current_database()
            GROUP BY state
