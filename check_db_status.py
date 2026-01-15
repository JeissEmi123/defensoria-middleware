#!/usr/bin/env python3
"""
Script para verificar categorías de observación existentes
"""
import asyncio
import asyncpg
from app.config import settings

async def check_categoria_observacion():
    """Verificar qué categorías de observación existen"""
    try:
        # Extraer la URL de base de datos desde settings
        database_url = settings.database_url
        
        # Ajustar la URL para asyncpg
        if database_url.startswith('postgresql+asyncpg://'):
            database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        # Conectar a la base de datos
        conn = await asyncpg.connect(database_url)
        
        print("🔗 Conectado a la base de datos")
        
        # Verificar estructura de categoria_observacion
        structure_query = '''
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_schema = 'sds' AND table_name = 'categoria_observacion'
        ORDER BY ordinal_position;
        '''
        
        structure_result = await conn.fetch(structure_query)
        print(f'\n📋 Estructura de tabla categoria_observacion:')
        print('=' * 60)
        if structure_result:
            for row in structure_result:
                print(f'{row["column_name"]:<30} | {row["data_type"]:<15} | Nullable: {row["is_nullable"]}')
        else:
            print('❌ Tabla categoria_observacion no encontrada')
        
        # Verificar datos en categoria_observacion (usando estructura real)
        try:
            data_query = '''
            SELECT * FROM sds.categoria_observacion LIMIT 10;
            '''
            
            data_result = await conn.fetch(data_query)
            print(f'\n📊 Datos en categoria_observacion (primeros 10):')
            print('=' * 80)
            for row in data_result:
                print(dict(row))
        except Exception as e:
            print(f'❌ Error al obtener datos: {e}')
        
        # Verificar permisos en esquema SDS
        schema_query = '''
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name = 'sds';
        '''
        
        schema_result = await conn.fetch(schema_query)
        if schema_result:
            print(f'\n✅ Esquema SDS existe')
        else:
            print(f'\n❌ Esquema SDS no existe')
        
        # Verificar permisos actuales
        perms_query = '''
        SELECT table_schema, table_name, privilege_type
        FROM information_schema.role_table_grants 
        WHERE grantee = current_user AND table_schema = 'sds'
        ORDER BY table_name, privilege_type;
        '''
        
        perms_result = await conn.fetch(perms_query)
        print(f'\n🔒 Permisos del usuario actual en esquema SDS:')
        print('=' * 60)
        if perms_result:
            for row in perms_result:
                print(f'{row["table_name"]:<25} | {row["privilege_type"]}')
        else:
            print('❌ No hay permisos específicos encontrados')
        
        await conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_categoria_observacion())