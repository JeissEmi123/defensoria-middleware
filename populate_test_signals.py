#!/usr/bin/env python3
"""
Script para insertar datos de prueba en las tablas de señales en producción.
Esto ayuda a llenar el frontend cuando no hay datos reales aún.

Uso:
    python populate_test_signals.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.config import settings

# Datos de prueba
CATEGORIAS_SENAL = [
    {
        "id": 1,
        "nombre": "Ruido",
        "color": "#808080",
        "nivel": 1,
        "descripcion": "Información no relevante"
    },
    {
        "id": 2,
        "nombre": "Problemas Menores",
        "color": "#00FF00",
        "nivel": 2,
        "descripcion": "Problemas que requieren atención"
    },
    {
        "id": 3,
        "nombre": "Paracrisis",
        "color": "#FFA500",
        "nivel": 3,
        "descripcion": "Situaciones que pueden escalar"
    },
    {
        "id": 4,
        "nombre": "Crisis",
        "color": "#FF0000",
        "nivel": 4,
        "descripcion": "Situaciones críticas que requieren acción inmediata"
    },
]

CATEGORIAS_ANALISIS = [
    {"id": 1, "nombre": "Violencia de Género"},
    {"id": 2, "nombre": "Violencia contra Menores"},
    {"id": 3, "nombre": "Derechos Laborales"},
    {"id": 4, "nombre": "Acceso a Educación"},
    {"id": 5, "nombre": "Seguridad Social"},
]

SENALES_PRUEBA = [
    {
        "id": 1,
        "categoria_senal": 4,
        "categoria_analisis": 1,
        "score": 95.5,
        "dias_atras": 0,
        "horas_atras": 2
    },
    {
        "id": 2,
        "categoria_senal": 3,
        "categoria_analisis": 2,
        "score": 78.0,
        "dias_atras": 0,
        "horas_atras": 4
    },
    {
        "id": 3,
        "categoria_senal": 2,
        "categoria_analisis": 3,
        "score": 65.5,
        "dias_atras": 1,
        "horas_atras": 0
    },
    {
        "id": 4,
        "categoria_senal": 2,
        "categoria_analisis": 4,
        "score": 72.0,
        "dias_atras": 1,
        "horas_atras": 3
    },
    {
        "id": 5,
        "categoria_senal": 1,
        "categoria_analisis": 5,
        "score": 45.0,
        "dias_atras": 2,
        "horas_atras": 1
    },
    {
        "id": 6,
        "categoria_senal": 4,
        "categoria_analisis": 1,
        "score": 88.5,
        "dias_atras": 2,
        "horas_atras": 6
    },
    {
        "id": 7,
        "categoria_senal": 3,
        "categoria_analisis": 2,
        "score": 75.0,
        "dias_atras": 3,
        "horas_atras": 0
    },
    {
        "id": 8,
        "categoria_senal": 2,
        "categoria_analisis": 3,
        "score": 60.0,
        "dias_atras": 3,
        "horas_atras": 5
    },
]

async def populate_db():
    """Insertar datos de prueba en la base de datos"""
    
    # Construir URL de conexión
    db_url = f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    
    print("=" * 70)
    print("📊 INSERTANDO DATOS DE PRUEBA EN SEÑALES")
    print("=" * 70)
    
    print(f"\nConectando a: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # 1. Insertar categorías de señal
            print("\n1️⃣  Insertando categorías de señal...")
            for cat in CATEGORIAS_SENAL:
                await session.execute(text("""
                    INSERT INTO sds.categoria_senal 
                    (id_categoria_senales, nombre_categoria_senal, color, nivel, descripcion_categoria_senal)
                    VALUES (:id, :nombre, :color, :nivel, :descripcion)
                    ON CONFLICT (id_categoria_senales) DO NOTHING
                """), {
                    "id": cat["id"],
                    "nombre": cat["nombre"],
                    "color": cat["color"],
                    "nivel": cat["nivel"],
                    "descripcion": cat["descripcion"]
                })
                print(f"   ✅ {cat['nombre']} (ID: {cat['id']})")
            
            # 2. Insertar categorías de análisis
            print("\n2️⃣  Insertando categorías de análisis...")
            for cat in CATEGORIAS_ANALISIS:
                await session.execute(text("""
                    INSERT INTO sds.categoria_analisis_senal 
                    (id_categoria_analisis_senal, nombre_categoria_analisis)
                    VALUES (:id, :nombre)
                    ON CONFLICT (id_categoria_analisis_senal) DO NOTHING
                """), {
                    "id": cat["id"],
                    "nombre": cat["nombre"]
                })
                print(f"   ✅ {cat['nombre']} (ID: {cat['id']})")
            
            # 3. Insertar señales de prueba
            print("\n3️⃣  Insertando señales de prueba...")
            for senal in SENALES_PRUEBA:
                fecha = datetime.now() - timedelta(
                    days=senal["dias_atras"],
                    hours=senal["horas_atras"]
                )
                
                await session.execute(text("""
                    INSERT INTO sds.senal_detectada 
                    (id_senal_detectada, id_categoria_senal, id_categoria_analisis, 
                     fecha_deteccion, score_riesgo, estado)
                    VALUES (:id, :cat_senal, :cat_analisis, :fecha, :score, 'DETECTADA')
                    ON CONFLICT (id_senal_detectada) DO NOTHING
                """), {
                    "id": senal["id"],
                    "cat_senal": senal["categoria_senal"],
                    "cat_analisis": senal["categoria_analisis"],
                    "fecha": fecha,
                    "score": senal["score"]
                })
                cat_nombre = next((c["nombre"] for c in CATEGORIAS_SENAL if c["id"] == senal["categoria_senal"]), "Unknown")
                print(f"   ✅ Señal #{senal['id']} - {cat_nombre} (Score: {senal['score']})")
            
            # Commit de la transacción
            await session.commit()
            print("\n✅ Todos los datos fueron insertados correctamente")
            
            # 4. Verificar los datos
            print("\n4️⃣  Verificando datos insertados...")
            
            # Contar registros
            result = await session.execute(text("SELECT COUNT(*) FROM sds.senal_detectada"))
            count = result.scalar()
            print(f"   📊 Total de señales en BD: {count}")
            
            # Probar la query del endpoint
            print("\n5️⃣  Probando la query del endpoint...")
            query = text("""
                SELECT 
                    sd.id_senal_detectada,
                    CONCAT('Señal #', sd.id_senal_detectada) as titulo,
                    cs.nombre_categoria_senal,
                    cs.color,
                    sd.score_riesgo,
                    sd.fecha_deteccion,
                    cas.nombre_categoria_analisis
                FROM sds.senal_detectada sd
                JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales
                JOIN sds.categoria_analisis_senal cas ON sd.id_categoria_analisis = cas.id_categoria_analisis_senal
                ORDER BY sd.score_riesgo DESC
                LIMIT 5
            """)
            
            result = await session.execute(query)
            rows = result.fetchall()
            
            if rows:
                print(f"   ✅ Query del endpoint retorna {len(rows)} registros:")
                for row in rows:
                    print(f"      - {row[1]}: {row[2]} ({row[6]}) - Score: {row[4]}")
            else:
                print(f"   ⚠️  La query del endpoint no retorna resultados")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error insertando datos: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await engine.dispose()

async def main():
    """Función principal"""
    try:
        success = await populate_db()
        
        print("\n" + "=" * 70)
        if success:
            print("✅ DATOS INSERTADOS EXITOSAMENTE")
            print("\nAhora puedes probar el endpoint:")
            print("  python test_senales_prod_simple.py")
        else:
            print("❌ ERROR AL INSERTAR DATOS")
        print("=" * 70)
        
        return success
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Inserción interrumpida por el usuario")
        sys.exit(1)
