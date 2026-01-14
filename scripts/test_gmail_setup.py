#!/usr/bin/env python3
"""
Script para verificar la configuración de Gmail API.
"""
import os
import sys
import json
import logging
from pathlib import Path

# Agregar el directorio raíz al path para importar modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.services.email_service import EmailService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_config():
    """Verificar configuración básica."""
    print("=== Verificando Configuración ===")
    
    print(f"Proyecto GCP: {settings.gcp_project_id}")
    print(f"Service Account File: {settings.gmail_service_account_file}")
    print(f"Delegated User: {settings.gmail_delegated_user}")
    print(f"Coordinador Email: {settings.coordinador_email}")
    
    # Verificar archivos
    if settings.gmail_service_account_file:
        if os.path.exists(settings.gmail_service_account_file):
            print(f"✅ Service Account file encontrado: {settings.gmail_service_account_file}")
        else:
            print(f"❌ Service Account file NO encontrado: {settings.gmail_service_account_file}")
            return False
    else:
        print("❌ GMAIL_SERVICE_ACCOUNT_FILE no configurado")
        return False
    
    if settings.gmail_oauth_client_secret_file:
        if os.path.exists(settings.gmail_oauth_client_secret_file):
            print(f"✅ OAuth Client Secret file encontrado: {settings.gmail_oauth_client_secret_file}")
        else:
            print(f"⚠️ OAuth Client Secret file NO encontrado: {settings.gmail_oauth_client_secret_file}")
    
    return True


def validate_service_account():
    """Validar que el service account JSON sea válido."""
    print("\n=== Validando Service Account ===")
    
    try:
        with open(settings.gmail_service_account_file, 'r') as f:
            sa_data = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 
                          'client_email', 'client_id', 'auth_uri', 'token_uri']
        
        for field in required_fields:
            if field in sa_data:
                if field == 'private_key':
                    print(f"✅ {field}: [PRESENTE]")
                else:
                    print(f"✅ {field}: {sa_data[field]}")
            else:
                print(f"❌ Campo requerido faltante: {field}")
                return False
        
        # Verificar que sea type service_account
        if sa_data.get('type') != 'service_account':
            print(f"❌ Tipo incorrecto: {sa_data.get('type')} (debe ser 'service_account')")
            return False
        
        print(f"✅ Service Account válido para proyecto: {sa_data.get('project_id')}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False


def test_email_service_init():
    """Probar inicialización del servicio de email."""
    print("\n=== Probando EmailService ===")
    
    try:
        email_service = EmailService()
        
        if email_service.gmail_service:
            print("✅ EmailService inicializado correctamente")
            print(f"✅ Gmail service activo: {type(email_service.gmail_service)}")
            return True
        else:
            print("❌ EmailService no se pudo inicializar")
            return False
            
    except Exception as e:
        print(f"❌ Error inicializando EmailService: {e}")
        return False


def test_send_email():
    """Probar envío de email de prueba."""
    if not settings.coordinador_email:
        print("\n❌ No se puede probar envío: COORDINADOR_EMAIL no configurado")
        return False
    
    print(f"\n=== Probando Envío de Email a {settings.coordinador_email} ===")
    
    try:
        email_service = EmailService()
        
        # Enviar email de prueba
        result = email_service.send_signal_revision_notification(
            to_email=settings.coordinador_email,
            senal_id=999,
            categoria_previa="RUIDO",
            categoria_nueva="CRISIS",
            usuario="Sistema de Pruebas",
            confirmo_revision=True,
            fecha_actualizacion="2026-01-13 10:30:00",
            detalles="Email de prueba de configuración"
        )
        
        if result:
            print("✅ Email de prueba enviado exitosamente")
            return True
        else:
            print("❌ Error al enviar email de prueba")
            return False
            
    except Exception as e:
        print(f"❌ Excepción al enviar email: {e}")
        return False


def main():
    """Ejecutar todas las verificaciones."""
    print("🔧 Verificador de Configuración Gmail API - Defensoría Middleware")
    print("=" * 60)
    
    checks = [
        ("Configuración", check_config),
        ("Service Account", validate_service_account),
        ("EmailService", test_email_service_init),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
            else:
                print(f"❌ {name} falló")
        except Exception as e:
            print(f"❌ {name} falló con excepción: {e}")
    
    print(f"\n=== Resumen ===")
    print(f"✅ Verificaciones pasadas: {passed}/{total}")
    
    # Test opcional de envío
    if passed == total:
        print("\n🚀 Configuración básica correcta. ¿Probar envío de email? (y/n): ", end="")
        try:
            response = input().lower().strip()
            if response in ['y', 'yes', 'sí', 'si']:
                test_send_email()
        except KeyboardInterrupt:
            print("\nPrueba cancelada")
    
    if passed == total:
        print("\n🎉 ¡Configuración completada exitosamente!")
        print("El sistema está listo para enviar emails automáticos.")
    else:
        print(f"\n⚠️ Faltan {total - passed} configuraciones por completar.")


if __name__ == "__main__":
    main()