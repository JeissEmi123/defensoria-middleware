#!/usr/bin/env python3
"""
Script para probar directamente el endpoint home/dashboard localmente
usando las mismas configuraciones que Cloud Run
"""
import asyncio
import asyncpg
import sys
import os
from datetime import datetime


async def test_production_endpoint():
    """Simular exactamente lo que hace el endpoint en producción"""
    
    print("🧪 PROBANDO ENDPOINT home/dashboard CON CONFIGURACIÓN DE PRODUCCIÓN")
    print("=" * 70)
    
    # Usar las mismas credenciales que Cloud Run
    database_url = "postgresql+asyncpg://app_user:AppUser2026!@127.0.0.1:5433/defensoria_db"
    
    try:
        # Conectar usando las credenciales de producción
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5433,  # Proxy local
            database='defensoria_db',
            user='app_user',
            password='AppUser2026!'
        )
        
        print("✅ Conexión exitosa con credenciales de producción")
        
        # 1. Consulta de alertas críticas (exactamente como en el código)
        print("\n1️⃣ Probando consulta de alertas críticas...")
        
        sql_alertas = '''
            SELECT 
                sd.id_senal_detectada,
                sd.fecha_deteccion,
                sd.score_riesgo,
                cs.nombre_categoria_senal,
                cs.nivel,
                cs.descripcion_categoria_senal
            FROM sds.senal_detectada sd
            JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales
            WHERE sd.score_riesgo >= 80
            ORDER BY sd.fecha_deteccion DESC
            LIMIT 5
        '''
        
        alertas = await conn.fetch(sql_alertas)
        print(f"   ✅ Obtenidas {len(alertas)} alertas críticas")
        
        # 2. Consulta de estadísticas básicas
        print("\n2️⃣ Probando consulta de estadísticas...")
        
        sql_stats = '''
            SELECT 
                COUNT(*) as total_senales,
                AVG(sd.score_riesgo) as score_promedio,
                COUNT(CASE WHEN sd.fecha_deteccion >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as recientes
            FROM sds.senal_detectada sd
        '''
        
        stats = await conn.fetchrow(sql_stats)
        print(f"   ✅ Total señales: {stats[0]}")
        score_promedio = float(stats[1]) if stats[1] else 0
        print(f"   ✅ Score promedio: {score_promedio:.2f}")
        print(f"   ✅ Recientes (7 días): {stats[2]}")
        
        # 3. Simular el payload completo del endpoint
        print("\n3️⃣ Generando payload del endpoint...")
        
        payload = {
            "alertas_criticas": [
                {
                    "id_senal_detectada": row[0],
                    "fecha_deteccion": row[1].isoformat() if row[1] else None,
                    "score_riesgo": float(row[2]) if row[2] else 0,
                    "categoria_senal": {
                        "nombre_categoria_senal": row[3],
                        "nivel": row[4],
                        "descripcion_categoria_senal": row[5]
                    }
                }
                for row in alertas
            ],
            "estadisticas": {
                "total_senales": stats[0],
                "score_promedio": float(stats[1]) if stats[1] else 0,
                "senales_recientes": stats[2],
                "fecha_actualizacion": datetime.now().isoformat()
            }
        }
        
        print(f"   ✅ Payload generado con {len(payload['alertas_criticas'])} alertas")
        print(f"   ✅ Estadísticas incluidas: {len(payload['estadisticas'])} métricas")
        
        # 4. Mostrar estructura del payload
        print("\n4️⃣ Estructura del payload (muestra):")
        if payload['alertas_criticas']:
            primera_alerta = payload['alertas_criticas'][0]
            print(f"   Alerta ejemplo: ID={primera_alerta['id_senal_detectada']}, Score={primera_alerta['score_riesgo']}")
        
        print(f"   Estadísticas: Total={payload['estadisticas']['total_senales']}, Promedio={payload['estadisticas']['score_promedio']}")
        
        await conn.close()
        
        print("\n🎉 ENDPOINT SIMULADO EXITOSAMENTE")
        print("=" * 70)
        print("✅ Las consultas SQL funcionan correctamente")
        print("✅ Los permisos están aplicados")
        print("✅ El payload se genera sin errores")
        print("\n🤔 Si el endpoint en producción sigue fallando, el problema puede ser:")
        print("   1. La conexión unix socket en Cloud Run")
        print("   2. Cache de conexiones de BD")
        print("   3. Timeout de conexión")
        print("   4. Variables de entorno incorrectas")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN SIMULACIÓN: {str(e)}")
        
        if "permission denied" in str(e).lower():
            print("🔧 Los permisos NO están aplicados correctamente")
            print("   Vuelva a ejecutar los comandos SQL en Google Cloud Console")
            
        elif "authentication failed" in str(e).lower():
            print("🔧 Error de autenticación")
            print("   Verifique que el proxy SQL esté ejecutándose")
            
        else:
            print("🔧 Error inesperado:")
            import traceback
            print(f"   {traceback.format_exc()}")
            
        return False


if __name__ == "__main__":
    success = asyncio.run(test_production_endpoint())
    if success:
        print("\n✨ La lógica del endpoint funciona localmente")
        print("   El problema está en la infraestructura de Cloud Run")
    else:
        print("\n🔧 Hay problemas con la lógica o permisos de BD")
        sys.exit(1)