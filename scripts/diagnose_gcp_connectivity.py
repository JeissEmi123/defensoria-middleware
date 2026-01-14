#!/usr/bin/env python3
"""
Script para diagnosticar problemas de conectividad con Google Cloud
Realiza tests específicos de red, DNS, y autenticación
"""
import os
import sys
import subprocess
import json
import socket
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

try:
    import requests
except ImportError:
    print("❌ requests no está instalado. Instala con: pip install requests")
    sys.exit(1)

from app.config import settings

class NetworkDiagnostic:
    """Clase para diagnósticos de red y conectividad"""
    
    @staticmethod
    def check_internet_connectivity():
        """Verificar conectividad a internet"""
        print("🔍 Verificando conectividad a internet...")
        
        test_urls = [
            "https://www.google.com",
            "https://accounts.google.com", 
            "https://www.googleapis.com"
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {url} - Accesible")
                else:
                    print(f"⚠️  {url} - Estado: {response.status_code}")
            except Exception as e:
                print(f"❌ {url} - Error: {e}")
    
    @staticmethod
    def check_dns_resolution():
        """Verificar resolución DNS de Google APIs"""
        print("\n🔍 Verificando resolución DNS...")
        
        google_domains = [
            "accounts.google.com",
            "oauth2.googleapis.com",
            "gmail.googleapis.com",
            "www.googleapis.com"
        ]
        
        for domain in google_domains:
            try:
                ip = socket.gethostbyname(domain)
                print(f"✅ {domain} -> {ip}")
            except Exception as e:
                print(f"❌ {domain} - Error DNS: {e}")
    
    @staticmethod
    def test_gmail_api_endpoint():
        """Probar acceso directo a Gmail API"""
        print("\n🔍 Probando acceso a Gmail API...")
        
        try:
            # Test básico sin autenticación - debería retornar 401
            response = requests.get("https://gmail.googleapis.com/gmail/v1/users/me/profile", timeout=10)
            if response.status_code == 401:
                print("✅ Gmail API endpoint accesible (401 - sin autenticación, esperado)")
            else:
                print(f"⚠️  Gmail API endpoint respondió: {response.status_code}")
        except Exception as e:
            print(f"❌ Error accediendo Gmail API: {e}")
    
    @staticmethod
    def check_google_oauth_endpoint():
        """Verificar endpoint de OAuth de Google"""
        print("\n🔍 Verificando OAuth endpoint...")
        
        try:
            response = requests.get("https://accounts.google.com/.well-known/openid_configuration", timeout=10)
            if response.status_code == 200:
                print("✅ OAuth endpoint accesible")
                config = response.json()
                print(f"   - Issuer: {config.get('issuer')}")
                print(f"   - Token endpoint: {config.get('token_endpoint')}")
            else:
                print(f"❌ OAuth endpoint error: {response.status_code}")
        except Exception as e:
            print(f"❌ Error OAuth endpoint: {e}")

def check_gcp_cli_tools():
    """Verificar herramientas CLI de GCP"""
    print("\n🔍 Verificando herramientas CLI de GCP...")
    
    tools = {
        'gcloud': 'Google Cloud CLI',
        'gsutil': 'Google Cloud Storage CLI', 
        'docker': 'Docker (para containers)'
    }
    
    for tool, description in tools.items():
        try:
            result = subprocess.run([tool, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                print(f"✅ {tool} - {description}")
                print(f"   Versión: {version}")
            else:
                print(f"❌ {tool} - No funciona correctamente")
        except subprocess.TimeoutExpired:
            print(f"⚠️  {tool} - Timeout")
        except FileNotFoundError:
            print(f"❌ {tool} - No instalado")
        except Exception as e:
            print(f"❌ {tool} - Error: {e}")

def check_gcp_authentication():
    """Verificar autenticación con GCP usando gcloud"""
    print("\n🔍 Verificando autenticación GCP...")
    
    try:
        # Verificar si gcloud está autenticado
        result = subprocess.run(['gcloud', 'auth', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ gcloud CLI encontrado")
            if "ACTIVE" in result.stdout:
                print("✅ Usuario autenticado en gcloud")
                print("Cuentas activas:")
                for line in result.stdout.split('\n'):
                    if '*' in line or '@' in line:
                        print(f"   {line.strip()}")
            else:
                print("⚠️  No hay usuarios autenticados en gcloud")
                print("Ejecuta: gcloud auth login")
        else:
            print(f"❌ Error en gcloud auth: {result.stderr}")
    except Exception as e:
        print(f"❌ Error verificando gcloud auth: {e}")
    
    # Verificar proyecto activo
    try:
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            project = result.stdout.strip()
            print(f"✅ Proyecto GCP activo: {project}")
        else:
            print("⚠️  No hay proyecto GCP configurado")
            print("Ejecuta: gcloud config set project TU_PROJECT_ID")
    except Exception as e:
        print(f"❌ Error obteniendo proyecto: {e}")

def check_service_account_permissions():
    """Verificar permisos del service account"""
    print("\n🔍 Verificando Service Account...")
    
    if not settings.gmail_service_account_file:
        print("❌ GMAIL_SERVICE_ACCOUNT_FILE no configurado")
        return
    
    sa_file = Path(settings.gmail_service_account_file)
    if not sa_file.exists():
        print(f"❌ Archivo no encontrado: {sa_file}")
        return
    
    try:
        with open(sa_file, 'r') as f:
            sa_data = json.load(f)
        
        client_email = sa_data.get('client_email')
        project_id = sa_data.get('project_id')
        
        print(f"✅ Service Account: {client_email}")
        print(f"✅ Proyecto: {project_id}")
        
        # Verificar si podemos usar el service account con gcloud
        try:
            result = subprocess.run([
                'gcloud', 'auth', 'activate-service-account', client_email,
                '--key-file', str(sa_file), '--quiet'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Service Account activado correctamente")
            else:
                print(f"⚠️  Problema activando SA: {result.stderr}")
        except Exception as e:
            print(f"⚠️  No se pudo probar activación: {e}")
            
    except Exception as e:
        print(f"❌ Error leyendo service account: {e}")

def generate_setup_commands():
    """Generar comandos para resolver problemas comunes"""
    print("\n" + "="*60)
    print("🛠️  COMANDOS PARA RESOLVER PROBLEMAS COMUNES")
    print("="*60)
    
    print("\n1. Instalar/Actualizar Google Cloud CLI:")
    print("   curl https://sdk.cloud.google.com | bash")
    print("   exec -l $SHELL")
    print("   gcloud init")
    
    print("\n2. Autenticarse en GCP:")
    print("   gcloud auth login")
    print("   gcloud config set project TU_PROJECT_ID")
    
    print("\n3. Crear Service Account:")
    print("   gcloud iam service-accounts create defensoria-gmail \\")
    print("     --display-name='Defensoria Gmail Service'")
    print("   gcloud iam service-accounts keys create ~/defensoria-sa.json \\")
    print("     --iam-account=defensoria-gmail@TU_PROJECT_ID.iam.gserviceaccount.com")
    
    print("\n4. Habilitar APIs necesarias:")
    print("   gcloud services enable gmail.googleapis.com")
    print("   gcloud services enable cloudresourcemanager.googleapis.com")
    
    print("\n5. Configurar variables de entorno:")
    print("   export GMAIL_SERVICE_ACCOUNT_FILE=~/defensoria-sa.json")
    print("   export GMAIL_DELEGATED_USER=admin@tu-dominio.com")
    print("   export COORDINADOR_EMAIL=coordinador@tu-dominio.com")

def main():
    """Función principal de diagnóstico"""
    print("🏥 DIAGNÓSTICO DE CONECTIVIDAD GCP")
    print("="*50)
    
    NetworkDiagnostic.check_internet_connectivity()
    NetworkDiagnostic.check_dns_resolution()
    NetworkDiagnostic.test_gmail_api_endpoint()
    NetworkDiagnostic.check_google_oauth_endpoint()
    
    check_gcp_cli_tools()
    check_gcp_authentication()
    check_service_account_permissions()
    
    generate_setup_commands()
    
    print("\n✅ Diagnóstico completado.")
    print("📄 Si persisten problemas, revisa: docs/CONFIGURACION_EMAIL.md")

if __name__ == "__main__":
    main()