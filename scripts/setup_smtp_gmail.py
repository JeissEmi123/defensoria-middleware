#!/usr/bin/env python3
"""
Script para configurar SMTP con Gmail personal (usando App Passwords).
La opción más simple para enviar emails desde dominio genérico.
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def configure_gmail_smtp():
    """Configurar Gmail SMTP con App Password."""
    print("📧 Configuración SMTP Gmail - Defensoría Middleware")
    print("=" * 60)
    print()
    print("🔑 Para usar SMTP con Gmail necesitas un 'App Password'")
    print()
    print("📋 Pasos para obtener App Password:")
    print("1. Ve a https://myaccount.google.com/")
    print("2. Security > 2-Step Verification (debe estar habilitado)")
    print("3. App passwords > Select app: Mail")
    print("4. Generate > Copia la contraseña de 16 caracteres")
    print()
    
    # Solicitar datos
    gmail_user = input("✉️ Tu email Gmail: ").strip()
    if not gmail_user.endswith("@gmail.com"):
        gmail_user += "@gmail.com"
    
    app_password = input("🔑 App Password (16 caracteres): ").strip()
    coordinator_email = input("👥 Email del coordinador: ").strip()
    
    # Generar configuración
    config = f"""
# === CONFIGURACIÓN SMTP GMAIL ===
EMAIL_SERVICE=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME={gmail_user}
SMTP_PASSWORD={app_password}
SMTP_USE_TLS=true
EMAIL_FROM={gmail_user}
COORDINADOR_EMAIL={coordinator_email}

# Deshabilitar Gmail API
GMAIL_USE_OAUTH=false
# GMAIL_SERVICE_ACCOUNT_FILE=
# GMAIL_DELEGATED_USER=
"""
    
    print("\n📝 Configuración generada:")
    print(config)
    
    # Preguntar si guardar
    save = input("\n💾 ¿Agregar al .env? (y/n): ").lower().strip()
    if save in ['y', 'yes', 'sí', 'si']:
        with open('.env', 'a') as f:
            f.write("\n" + config)
        print("✅ Configuración agregada a .env")
    
    return gmail_user, app_password, coordinator_email


def test_smtp_config():
    """Probar configuración SMTP."""
    print("\n🧪 Probando configuración SMTP...")
    
    try:
        # Configurar variables de entorno temporalmente
        from app.services.unified_email_service import unified_email_service
        
        # Probar envío
        coordinator_email = os.getenv("COORDINADOR_EMAIL")
        if not coordinator_email:
            print("❌ COORDINADOR_EMAIL no configurado")
            return False
        
        result = unified_email_service.send_signal_revision_notification(
            to_email=coordinator_email,
            senal_id=999,
            categoria_previa="RUIDO",
            categoria_nueva="CRISIS",
            usuario="Sistema de Pruebas SMTP",
            confirmo_revision=True,
            fecha_actualizacion="2026-01-13 10:30:00",
            detalles="Email de prueba SMTP - Defensoría Middleware"
        )
        
        if result:
            print(f"✅ Email de prueba enviado a {coordinator_email}")
            return True
        else:
            print("❌ Error enviando email de prueba")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Configurar SMTP Gmail."""
    # Configurar
    gmail_user, app_password, coordinator = configure_gmail_smtp()
    
    # Test opcional
    if gmail_user and app_password:
        test = input("\n🚀 ¿Probar envío de email? (y/n): ").lower().strip()
        if test in ['y', 'yes', 'sí', 'si']:
            # Configurar variables temporalmente para el test
            os.environ["EMAIL_SERVICE"] = "smtp"
            os.environ["SMTP_HOST"] = "smtp.gmail.com"
            os.environ["SMTP_PORT"] = "587"
            os.environ["SMTP_USERNAME"] = gmail_user
            os.environ["SMTP_PASSWORD"] = app_password
            os.environ["SMTP_USE_TLS"] = "true"
            os.environ["EMAIL_FROM"] = gmail_user
            os.environ["COORDINADOR_EMAIL"] = coordinator
            
            if test_smtp_config():
                print("\n🎉 ¡SMTP configurado exitosamente!")
                print("✉️ Tu aplicación puede enviar emails desde Gmail")
            else:
                print("\n⚠️ Configuración guardada pero falló el test")
                print("Verifica tu App Password y configuración")
    
    print("\n📚 Documentación completa: docs/OPCIONES_EMAIL.md")


if __name__ == "__main__":
    main()