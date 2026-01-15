#!/usr/bin/env python3
"""
Script para ejecutar SQL y crear las tablas faltantes de SDS
"""
import asyncio
import asyncpg
from app.config import settings

async def execute_sql_file():
    """Ejecutar el archivo SQL para crear tablas"""
    try:
        # Leer el archivo SQL
        with open('create_simple_tables.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Extraer la URL de base de datos desde settings
        database_url = settings.database_url
        
        # Ajustar la URL para asyncpg (cambiar postgresql+asyncpg por postgresql)
        if database_url.startswith('postgresql+asyncpg://'):
            database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        # Conectar a la base de datos
        conn = await asyncpg.connect(database_url)
        
        print("🔗 Conectado a la base de datos")
        
        # Ejecutar el script SQL
        print("📋 Ejecutando script SQL...")
        await conn.execute(sql_content)
        
        print("✅ Script SQL ejecutado exitosamente")
        
        # Verificar las tablas creadas
        query = '''
        SELECT table_name, 
               (SELECT COUNT(*) FROM information_schema.columns 
                WHERE table_schema = 'sds' AND table_name = t.table_name) as column_count
        FROM information_schema.tables t
        WHERE table_schema = 'sds' 
        ORDER BY table_name;
        '''
        
        result = await conn.fetch(query)
        print(f'\n📊 Tablas en esquema SDS:')
        print('=' * 50)
        for row in result:
            print(f'✅ {row["table_name"]:<30} ({row["column_count"]} columnas)')
        
        # Verificar datos insertados en las nuevas tablas
        tables_to_check = ['figuras_publicas', 'influencers', 'medios_digitales', 'entidades']
        print(f'\n📈 Conteo de registros insertados:')
        print('=' * 50)
        
        for table in tables_to_check:
            try:
                count_result = await conn.fetchval(f'SELECT COUNT(*) FROM sds.{table}')
                print(f'✅ {table:<25} - {count_result} registros')
            except Exception as e:
                print(f'❌ {table:<25} - Error: {str(e)[:50]}...')
        
        await conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    asyncio.run(execute_sql_file())