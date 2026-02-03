#!/usr/bin/env python3
"""
Script para probar específicamente los endpoints que pueden causar error 500
al guardar comentarios en el módulo de detección de señales
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database.session import get_db_session
from app.services.senal_service_v2 import SenalServiceV2
from app.schemas.senales_v2 import SenalDetectadaUpdate
from sqlalchemy import text

async def test_actualizar_senal():
    """Probar el endpoint de actualización de señal que podría estar fallando"""
    print("🧪 Probando actualización de señal...")
    
    try:
        async for db in get_db_session():
            service = SenalServiceV2(db)
            
            # Obtener una señal existente para probar
            result = await db.execute(text("""
                SELECT id_senal_detectada, id_categoria_senal, score_riesgo 
                FROM sds.senal_detectada 
                LIMIT 1
            """))
            senal = result.fetchone()
            
            if not senal:
                print("❌ No hay señales para probar")
                return False
            
            id_senal = senal[0]
            print(f"📍 Probando con señal ID: {id_senal}")
            
            # Test 1: Actualización básica sin comentario
            try:
                payload = SenalDetectadaUpdate(
                    score_riesgo=85.5,
                    confirmo_revision=False
                )
                
                resultado = await service.actualizar_senal(
                    id_senal=id_senal,
                    payload=payload,
                    usuario_id=1,
                    usuario_nombre="test_user",
                    usuario_email="test@test.com",
                    email_revisor=None,
                    ip_address="127.0.0.1"
                )
                
                if resultado:
                    print("✅ Actualización básica: OK")
                else:
                    print("❌ Actualización básica: FALLÓ")
                    return False
                    
            except Exception as e:
                print(f"❌ Error en actualización básica: {str(e)}")
                return False
            
            # Test 2: Actualización con comentario/descripción
            try:
                payload = SenalDetectadaUpdate(
                    score_riesgo=90.0,
                    descripcion_cambio="Comentario de prueba para verificar funcionalidad",
                    confirmo_revision=False
                )
                
                resultado = await service.actualizar_senal(
                    id_senal=id_senal,
                    payload=payload,
                    usuario_id=1,
                    usuario_nombre="test_user",
                    usuario_email="test@test.com",
                    email_revisor=None,
                    ip_address="127.0.0.1"
                )
                
                if resultado:
                    print("✅ Actualización con comentario: OK")
                else:
                    print("❌ Actualización con comentario: FALLÓ")
                    return False
                    
            except Exception as e:
                print(f"❌ Error en actualización con comentario: {str(e)}")
                return False
            
            # Test 3: Cambio de categoría (requiere confirmación)
            try:
                payload = SenalDetectadaUpdate(
                    id_categoria_senal=2,  # Cambiar a paracrisis
                    descripcion_cambio="Cambio de categoría con comentario",
                    confirmo_revision=True
                )
                
                resultado = await service.actualizar_senal(
                    id_senal=id_senal,
                    payload=payload,
                    usuario_id=1,
                    usuario_nombre="test_user",
                    usuario_email="test@test.com",
                    email_revisor="revisor@test.com",
                    ip_address="127.0.0.1"
                )
                
                if resultado:
                    print("✅ Cambio de categoría con comentario: OK")
                else:
                    print("❌ Cambio de categoría con comentario: FALLÓ")
                    return False
                    
            except Exception as e:
                print(f"❌ Error en cambio de categoría: {str(e)}")
                return False
            
            break
            
        return True
        
    except Exception as e:
        print(f"❌ Error general en test de actualización: {str(e)}")
        return False

async def test_historial_senal():
    """Probar el registro de historial que podría estar causando problemas"""
    print("\n🧪 Probando registro de historial...")
    
    try:
        async for db in get_db_session():
            service = SenalServiceV2(db)
            
            # Verificar si la tabla historial_senal existe
            result = await db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'sds' AND table_name = 'historial_senal'
            """))
            
            if not result.scalar():
                print("⚠️  Tabla historial_senal no existe - esto podría causar errores")
                return False
            
            # Obtener una señal para probar
            result = await db.execute(text("""
                SELECT id_senal_detectada 
                FROM sds.senal_detectada 
                LIMIT 1
            """))
            senal = result.fetchone()
            
            if not senal:
                print("❌ No hay señales para probar historial")
                return False
            
            id_senal = senal[0]
            
            # Test de registro de historial
            try:
                historial_entry = await service.registrar_historial_senal(
                    id_senal_detectada=id_senal,
                    accion="TEST_COMENTARIO",
                    descripcion="Comentario de prueba desde diagnóstico",
                    estado_anterior="activo",
                    estado_nuevo="activo",
                    datos_adicionales={
                        "comentario": "Este es un comentario de prueba",
                        "usuario": "test_user",
                        "timestamp": datetime.now().isoformat()
                    },
                    usuario_id=1,
                    ip_address="127.0.0.1"
                )
                
                await db.commit()
                print("✅ Registro de historial: OK")
                return True
                
            except Exception as e:
                print(f"❌ Error registrando historial: {str(e)}")
                await db.rollback()
                return False
            
            break
            
    except Exception as e:
        print(f"❌ Error general en test de historial: {str(e)}")
        return False

async def test_validaciones_payload():
    """Probar validaciones que podrían causar errores 500"""
    print("\n🧪 Probando validaciones de payload...")
    
    try:
        async for db in get_db_session():
            service = SenalServiceV2(db)
            
            # Obtener una señal para probar
            result = await db.execute(text("""
                SELECT id_senal_detectada 
                FROM sds.senal_detectada 
                LIMIT 1
            """))
            senal = result.fetchone()
            
            if not senal:
                print("❌ No hay señales para probar validaciones")
                return False
            
            id_senal = senal[0]
            
            # Test 1: Payload vacío (debería fallar)
            try:
                payload = SenalDetectadaUpdate()
                
                resultado = await service.actualizar_senal(
                    id_senal=id_senal,
                    payload=payload,
                    usuario_id=1,
                    usuario_nombre="test_user",
                    usuario_email="test@test.com",
                    email_revisor=None,
                    ip_address="127.0.0.1"
                )
                
                print("⚠️  Payload vacío debería fallar pero no lo hizo")
                
            except Exception as e:
                print("✅ Validación de payload vacío: OK (falló como esperado)")
            
            # Test 2: Cambio de categoría sin confirmación (debería fallar)
            try:
                payload = SenalDetectadaUpdate(
                    id_categoria_senal=3,
                    confirmo_revision=False  # Sin confirmación
                )
                
                resultado = await service.actualizar_senal(
                    id_senal=id_senal,
                    payload=payload,
                    usuario_id=1,
                    usuario_nombre="test_user",
                    usuario_email="test@test.com",
                    email_revisor=None,
                    ip_address="127.0.0.1"
                )
                
                print("⚠️  Cambio sin confirmación debería fallar pero no lo hizo")
                
            except Exception as e:
                print("✅ Validación de confirmación requerida: OK (falló como esperado)")
            
            # Test 3: Comentario muy largo
            try:
                comentario_largo = "x" * 10000  # Comentario de 10k caracteres
                
                payload = SenalDetectadaUpdate(
                    score_riesgo=75.0,
                    descripcion_cambio=comentario_largo,
                    confirmo_revision=False
                )
                
                resultado = await service.actualizar_senal(
                    id_senal=id_senal,
                    payload=payload,
                    usuario_id=1,
                    usuario_nombre="test_user",
                    usuario_email="test@test.com",
                    email_revisor=None,
                    ip_address="127.0.0.1"
                )
                
                if resultado:
                    print("✅ Comentario largo: OK")
                else:
                    print("❌ Comentario largo: FALLÓ")
                
            except Exception as e:
                print(f"⚠️  Error con comentario largo: {str(e)}")
            
            break
            
        return True
        
    except Exception as e:
        print(f"❌ Error general en test de validaciones: {str(e)}")
        return False

async def verificar_configuracion_email():
    """Verificar configuración de email que podría causar errores"""
    print("\n🧪 Verificando configuración de email...")
    
    try:
        from app.config import settings
        
        print(f"Email service: {getattr(settings, 'email_service', 'No configurado')}")
        print(f"Coordinador email: {getattr(settings, 'coordinador_email', 'No configurado')}")
        print(f"Gmail OAuth: {getattr(settings, 'gmail_use_oauth', False)}")
        
        # Verificar si el servicio de email está disponible
        try:
            from app.services.email_service import email_service
            print("✅ Servicio de email: Importado correctamente")
        except Exception as e:
            print(f"⚠️  Error importando servicio de email: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando configuración de email: {str(e)}")
        return False

async def main():
    """Función principal de pruebas"""
    print("🔍 Probando endpoints específicos que pueden causar error 500...")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    resultados = []
    
    # Ejecutar todas las pruebas
    resultados.append(await test_actualizar_senal())
    resultados.append(await test_historial_senal())
    resultados.append(await test_validaciones_payload())
    resultados.append(await verificar_configuracion_email())
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    
    exitosos = sum(resultados)
    total = len(resultados)
    
    print(f"✅ Pruebas exitosas: {exitosos}/{total}")
    
    if exitosos == total:
        print("🎉 Todas las pruebas pasaron - El módulo debería funcionar correctamente")
        print("\n💡 Si sigues viendo error 500:")
        print("   1. Verifica los logs de la aplicación en tiempo real")
        print("   2. Revisa la configuración de CORS y autenticación")
        print("   3. Verifica que el usuario tenga permisos adecuados")
        print("   4. Comprueba la configuración de email si se envían notificaciones")
    else:
        print("⚠️  Algunas pruebas fallaron - Revisar los errores arriba")
    
    return 0 if exitosos == total else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)