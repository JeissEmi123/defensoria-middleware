#!/usr/bin/env python3
"""
Test completo de todas las funciones de email con OAuth de Google.
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_all_email_functions():
    """Probar todas las funciones de email."""
    print("📧 Test Completo del Sistema de Email - Defensoría Middleware")
    print("=" * 70)
    
    from app.services.email_service import EmailService
    
    email_service = EmailService()
    test_email = "jcamargom@agatadata.com"
    
    print(f"📬 Enviando emails de prueba a: {test_email}")
    print()
    
    # Test 1: Email de bienvenida
    print("1️⃣ Probando email de bienvenida...")
    result1 = email_service.send_welcome_email(
        to_email=test_email,
        username="usuario_prueba",
        temporary_password="TempPass123!",
        nombre_completo="Usuario de Prueba"
    )
    print(f"   Resultado: {'✅ Enviado' if result1 else '❌ Error'}")
    
    # Test 2: Email de reset de contraseña
    print("2️⃣ Probando email de reset de contraseña...")
    result2 = email_service.send_password_reset_email(
        to_email=test_email,
        username="usuario_prueba",
        reset_token="abc123def456"
    )
    print(f"   Resultado: {'✅ Enviado' if result2 else '❌ Error'}")
    
    # Test 3: Notificación de cambio de señal
    print("3️⃣ Probando notificación de cambio de señal...")
    result3 = email_service.send_signal_revision_notification(
        to_email=test_email,
        senal_id=12345,
        categoria_previa="RUIDO",
        categoria_nueva="CRISIS",
        usuario="Analista Prueba",
        confirmo_revision=True,
        fecha_actualizacion="2026-01-13 15:30:00",
        detalles="Email de prueba completa del sistema"
    )
    print(f"   Resultado: {'✅ Enviado' if result3 else '❌ Error'}")
    
    # Resumen
    total_tests = 3
    passed_tests = sum([result1, result2, result3])
    
    print()
    print("=" * 50)
    print(f"📊 Resumen: {passed_tests}/{total_tests} tests pasaron")
    
    if passed_tests == total_tests:
        print("🎉 ¡Todo el sistema de email funciona perfectamente!")
        print("📧 Tu middleware está listo para enviar emails automáticos")
    else:
        print("⚠️ Algunos tests fallaron, revisa la configuración")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    # Configurar variables de entorno desde .env
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        success = test_all_email_functions()
        if success:
            print("\n🚀 Sistema listo para producción!")
        else:
            print("\n🔧 Necesita ajustes en la configuración")
    except ImportError:
        print("❌ Instalando python-dotenv...")
        import subprocess
        subprocess.run(["/usr/local/bin/python3", "-m", "pip", "install", "python-dotenv"])
        print("✅ Reinstala: pip install python-dotenv")
    except Exception as e:
        print(f"❌ Error: {e}")