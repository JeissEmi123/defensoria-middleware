#!/usr/bin/env python3
"""
Script para validar la configuración de Gmail API y GCP
Ejecuta varias pruebas para verificar que todo esté configurado correctamente
"""
import os
import sys
import json
import asyncio
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings
from app.services.email_service import email_service

class ColoredOutput:
    """Clase para output coloreado en terminal"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @classmethod
    def print_success(cls, message):
        print(f"{cls.GREEN}✅ {message}{cls.END}")
    
    @classmethod
    def print_error(cls, message):
        print(f"{cls.RED}❌ {message}{cls.END}")
    
    @classmethod
    def print_warning(cls, message):
        print(f"{cls.YELLOW}⚠️  {message}{cls.END}")
    
    @classmethod
    def print_info(cls, message):
        print(f"{cls.BLUE}ℹ️  {message}{cls.END}")
    
    @classmethod
    def print_header(cls, message):
        print(f"\n{cls.BOLD}{cls.CYAN}🔍 {message}{cls.END}")

def validate_environment_variables():
    """Validar variables de entorno necesarias"""
    ColoredOutput.print_header("Validando Variables de Entorno")
    
    required_vars = {
        'GMAIL_SERVICE_ACCOUNT_FILE': 'Ruta al archivo de credenciales de Service Account',
        'GMAIL_DELEGATED_USER': 'Usuario delegado para enviar emails',
        'EMAIL_FROM': 'Email remitente',
        'COORDINADOR_EMAIL': 'Email del coordinador'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = getattr(settings, var.lower(), None)
        if value:
            ColoredOutput.print_success(f"{var}: {value}")
        else:
            ColoredOutput.print_error(f"{var}: NO CONFIGURADO - {description}")
            missing_vars.append(var)
    
    if missing_vars:
        ColoredOutput.print_warning(f"Variables faltantes: {', '.join(missing_vars)}")
        return False
    return True

def validate_service_account_file():
    """Validar que el archivo de service account exista y sea válido"""
    ColoredOutput.print_header("Validando Service Account File")
    
    if not settings.gmail_service_account_file:
        ColoredOutput.print_error("GMAIL_SERVICE_ACCOUNT_FILE no está configurado")
        return False
    
    file_path = Path(settings.gmail_service_account_file)
    
    # Verificar si el archivo existe
    if not file_path.exists():
        ColoredOutput.print_error(f"Archivo no encontrado: {file_path}")
        return False
    
    ColoredOutput.print_success(f"Archivo existe: {file_path}")
    
    # Verificar si es un JSON válido
    try:
        with open(file_path, 'r') as f:
            credentials = json.load(f)
        
        required_keys = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_keys = [key for key in required_keys if key not in credentials]
        
        if missing_keys:
            ColoredOutput.print_error(f"Claves faltantes en el JSON: {missing_keys}")
            return False
        
        ColoredOutput.print_success(f"JSON válido con project_id: {credentials.get('project_id')}")
        ColoredOutput.print_success(f"Client email: {credentials.get('client_email')}")
        
        if credentials.get('type') != 'service_account':
            ColoredOutput.print_warning(f"Tipo de credencial: {credentials.get('type')} (esperado: service_account)")
            
        return True
        
    except json.JSONDecodeError as e:
        ColoredOutput.print_error(f"JSON inválido: {e}")
        return False
    except Exception as e:
        ColoredOutput.print_error(f"Error leyendo archivo: {e}")
        return False

def validate_gmail_service():
    """Validar la inicialización del servicio de Gmail"""
    ColoredOutput.print_header("Validando Gmail Service")
    
    if email_service.gmail_service is None:
        ColoredOutput.print_error("Gmail service no está inicializado")
        ColoredOutput.print_info("Posibles causas:")
        ColoredOutput.print_info("- GMAIL_SERVICE_ACCOUNT_FILE no existe")
        ColoredOutput.print_info("- GMAIL_DELEGATED_USER no configurado")
        ColoredOutput.print_info("- Credenciales inválidas")
        ColoredOutput.print_info("- No hay domain-wide delegation configurado")
        return False
    
    ColoredOutput.print_success("Gmail service inicializado correctamente")
    return True

def test_gmail_api_connection():
    """Probar conexión a Gmail API"""
    ColoredOutput.print_header("Probando Conexión a Gmail API")
    
    if not email_service.gmail_service:
        ColoredOutput.print_error("No se puede probar - Gmail service no inicializado")
        return False
    
    try:
        # Intentar obtener el perfil del usuario
        profile = email_service.gmail_service.users().getProfile(userId='me').execute()
        ColoredOutput.print_success(f"Conexión exitosa - Email: {profile.get('emailAddress')}")
        ColoredOutput.print_success(f"Total de mensajes: {profile.get('messagesTotal', 'N/A')}")
        return True
    except Exception as e:
        ColoredOutput.print_error(f"Error conectando a Gmail API: {e}")
        ColoredOutput.print_info("Posibles soluciones:")
        ColoredOutput.print_info("- Verificar domain-wide delegation en Google Admin Console")
        ColoredOutput.print_info("- Verificar que los scopes incluyan 'https://www.googleapis.com/auth/gmail.send'")
        ColoredOutput.print_info("- Verificar que el usuario delegado exista y tenga permisos")
        return False

def test_send_email():
    """Probar envío de email de prueba"""
    ColoredOutput.print_header("Probando Envío de Email")
    
    if not settings.coordinador_email:
        ColoredOutput.print_error("COORDINADOR_EMAIL no configurado - no se puede probar envío")
        return False
    
    try:
        result = email_service.send_signal_revision_notification(
            to_email=settings.coordinador_email,
            senal_id=999999,
            categoria_previa="RUIDO",
            categoria_nueva="CRISIS",
            usuario="Script de Validación",
            confirmo_revision=True,
            fecha_actualizacion="2026-01-13 15:30:00",
            detalles="Este es un email de prueba para validar la configuración del sistema."
        )
        
        if result:
            ColoredOutput.print_success(f"Email de prueba enviado exitosamente a {settings.coordinador_email}")
            ColoredOutput.print_info("Revisa la bandeja de entrada del coordinador")
            return True
        else:
            ColoredOutput.print_error("Falló el envío del email de prueba")
            return False
            
    except Exception as e:
        ColoredOutput.print_error(f"Error enviando email: {e}")
        return False

def print_summary(results):
    """Imprimir resumen de resultados"""
    ColoredOutput.print_header("Resumen de Validación")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    if passed_tests == total_tests:
        ColoredOutput.print_success(f"Todas las validaciones pasaron ({passed_tests}/{total_tests})")
        ColoredOutput.print_success("✨ Tu sistema está listo para enviar emails automáticos!")
    else:
        failed_tests = total_tests - passed_tests
        ColoredOutput.print_warning(f"Algunas validaciones fallaron ({failed_tests}/{total_tests})")
        
        failed_items = [test for test, passed in results.items() if not passed]
        ColoredOutput.print_info("Tests fallidos:")
        for item in failed_items:
            ColoredOutput.print_error(f"  - {item}")
    
    print()

def main():
    """Función principal"""
    print(f"{ColoredOutput.BOLD}{ColoredOutput.MAGENTA}")
    print("=" * 60)
    print("    VALIDADOR DE CONFIGURACIÓN GCP/GMAIL")
    print("    Defensoría del Pueblo - Sistema de Señales")
    print("=" * 60)
    print(ColoredOutput.END)
    
    results = {}
    
    # Ejecutar validaciones
    results["Variables de Entorno"] = validate_environment_variables()
    results["Service Account File"] = validate_service_account_file()
    results["Gmail Service Initialization"] = validate_gmail_service()
    results["Gmail API Connection"] = test_gmail_api_connection()
    
    # Solo probar envío si todo lo anterior funciona
    if all(results.values()):
        results["Email Test"] = test_send_email()
    else:
        ColoredOutput.print_warning("Saltando test de envío - hay problemas de configuración")
    
    print_summary(results)
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)