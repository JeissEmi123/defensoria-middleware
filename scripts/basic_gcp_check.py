#!/usr/bin/env python3
"""
Script simple para validar conectividad GCP sin dependencias del proyecto
"""
import os
import json
import socket
import subprocess
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests no disponible - algunos tests serán omitidos")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_warning(msg):
    print(f"⚠️  {msg}")

def print_info(msg):
    print(f"ℹ️  {msg}")

def check_basic_connectivity():
    """Verificar conectividad básica a Google"""
    print("🔍 VERIFICANDO CONECTIVIDAD BÁSICA")
    print("=" * 40)
    
    # DNS Resolution
    print("\n📡 Resolución DNS:")
    google_hosts = ["google.com", "accounts.google.com", "gmail.googleapis.com"]
    
    for host in google_hosts:
        try:
            ip = socket.gethostbyname(host)
            print_success(f"{host} -> {ip}")
        except Exception as e:
            print_error(f"{host} -> {e}")
    
    # HTTP Connectivity (si requests está disponible)
    if REQUESTS_AVAILABLE:
        print("\n🌐 Conectividad HTTP:")
        test_urls = [
            "https://www.google.com",
            "https://accounts.google.com", 
            "https://www.googleapis.com"
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print_success(f"{url} - OK")
                else:
                    print_warning(f"{url} - Status: {response.status_code}")
            except Exception as e:
                print_error(f"{url} - {e}")

def check_environment_file():
    """Verificar archivo .env"""
    print("\n🔍 VERIFICANDO ARCHIVO .ENV")
    print("=" * 40)
    
    env_file = Path(".env")
    if not env_file.exists():
        print_error(".env no encontrado")
        return
    
    print_success(".env encontrado")
    
    # Leer variables relevantes
    gmail_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                
                if 'GMAIL' in key or 'EMAIL' in key or 'COORDINADOR' in key:
                    gmail_vars[key] = value
    
    print("\n📧 Variables de Email:")
    required_vars = [
        'GMAIL_SERVICE_ACCOUNT_FILE',
        'GMAIL_DELEGATED_USER', 
        'EMAIL_FROM',
        'COORDINADOR_EMAIL'
    ]
    
    for var in required_vars:
        if var in gmail_vars and gmail_vars[var]:
            if 'EMAIL' in var:
                print_success(f"{var}: {gmail_vars[var]}")
            else:
                print_success(f"{var}: {gmail_vars[var]}")
        else:
            print_error(f"{var}: NO CONFIGURADO")

def check_service_account():
    """Verificar service account file"""
    print("\n🔍 VERIFICANDO SERVICE ACCOUNT")
    print("=" * 40)
    
    # Buscar archivo de service account en .env
    sa_file = None
    env_file = Path(".env")
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if 'GMAIL_SERVICE_ACCOUNT_FILE' in line and '=' in line:
                    _, path = line.split('=', 1)
                    sa_file = path.strip().strip('"\'')
                    break
    
    if not sa_file:
        print_error("GMAIL_SERVICE_ACCOUNT_FILE no configurado en .env")
        return
    
    sa_path = Path(sa_file)
    if not sa_path.exists():
        print_error(f"Archivo no encontrado: {sa_path}")
        print_info("Crea el service account siguiendo la documentación")
        return
    
    print_success(f"Archivo encontrado: {sa_path}")
    
    # Verificar contenido JSON
    try:
        with open(sa_path, 'r') as f:
            sa_data = json.load(f)
        
        required_keys = ['type', 'project_id', 'private_key', 'client_email']
        missing = [k for k in required_keys if k not in sa_data]
        
        if missing:
            print_error(f"Claves faltantes: {missing}")
        else:
            print_success("JSON válido con todas las claves requeridas")
            print_info(f"Project ID: {sa_data.get('project_id')}")
            print_info(f"Client Email: {sa_data.get('client_email')}")
            
            if sa_data.get('type') != 'service_account':
                print_warning(f"Tipo: {sa_data.get('type')} (esperado: service_account)")
            else:
                print_success("Tipo: service_account")
                
    except json.JSONDecodeError as e:
        print_error(f"JSON inválido: {e}")
    except Exception as e:
        print_error(f"Error leyendo archivo: {e}")

def check_gcloud_cli():
    """Verificar Google Cloud CLI"""
    print("\n🔍 VERIFICANDO GOOGLE CLOUD CLI")
    print("=" * 40)
    
    try:
        result = subprocess.run(['gcloud', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print_success(f"gcloud instalado: {version}")
        else:
            print_error("gcloud no funciona correctamente")
    except FileNotFoundError:
        print_warning("gcloud CLI no instalado")
        print_info("Instala con: curl https://sdk.cloud.google.com | bash")
    except Exception as e:
        print_error(f"Error verificando gcloud: {e}")
    
    # Verificar autenticación
    try:
        result = subprocess.run(['gcloud', 'auth', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            if "ACTIVE" in result.stdout:
                print_success("Usuario autenticado en gcloud")
            else:
                print_warning("No hay usuario autenticado")
                print_info("Ejecuta: gcloud auth login")
        else:
            print_warning("No se puede verificar autenticación")
    except Exception:
        print_warning("No se puede verificar autenticación gcloud")

def print_next_steps():
    """Imprimir próximos pasos"""
    print("\n🚀 PRÓXIMOS PASOS")
    print("=" * 40)
    
    print("\n1. Si no tienes Service Account:")
    print("   - Ve a Google Cloud Console")
    print("   - Crea un proyecto o selecciona existente")
    print("   - Habilita Gmail API")
    print("   - Crea Service Account con permisos de Gmail")
    print("   - Descarga el archivo JSON")
    
    print("\n2. Configurar variables de entorno (.env):")
    print("   GMAIL_SERVICE_ACCOUNT_FILE=/ruta/al/archivo.json")
    print("   GMAIL_DELEGATED_USER=admin@tu-dominio.com")
    print("   EMAIL_FROM=noreply@tu-dominio.com")
    print("   COORDINADOR_EMAIL=coordinador@tu-dominio.com")
    
    print("\n3. Si tienes Google Workspace:")
    print("   - Configura Domain-wide Delegation")
    print("   - Scope: https://www.googleapis.com/auth/gmail.send")
    
    print("\n4. Para probar la configuración completa:")
    print("   python3 scripts/validate_all.py")
    
    print("\n📚 Documentación completa:")
    print("   docs/CONFIGURACION_EMAIL.md")

def main():
    print("🔍 DIAGNÓSTICO BÁSICO GCP/GMAIL")
    print("Defensoría del Pueblo")
    print("=" * 50)
    
    check_basic_connectivity()
    check_environment_file()
    check_service_account()
    check_gcloud_cli()
    print_next_steps()
    
    print("\n✅ Diagnóstico básico completado")

if __name__ == "__main__":
    main()