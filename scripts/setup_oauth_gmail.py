#!/usr/bin/env python3
"""
Script para configurar OAuth con Gmail personal.
Genera token de acceso para enviar emails desde Gmail personal.
"""
import os
import json
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scope para enviar emails y leer perfil
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]
TOKEN_FILE = 'config/gmail-token.pickle'
CREDENTIALS_FILE = 'config/oauth-client-secret.json'


def setup_oauth_flow():
    """Configura el flujo OAuth para Gmail personal."""
    print("🔧 Configurando OAuth para Gmail Personal")
    print("=" * 50)
    
    # Verificar que existe el archivo de credenciales OAuth
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ No se encontró {CREDENTIALS_FILE}")
        print("Descarga el archivo desde Google Cloud Console:")
        print("1. Ve a APIs & Services > Credentials")
        print("2. Descarga el OAuth 2.0 client")
        print("3. Guarda como config/oauth-client-secret.json")
        return False
    
    creds = None
    
    # Cargar token existente si existe
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # Si no hay credenciales válidas, ejecutar flujo OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refrescando token existente...")
            creds.refresh(Request())
        else:
            print("🌐 Iniciando flujo OAuth...")
            print("Se abrirá tu navegador para autorizar la aplicación")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guardar credenciales para próxima ejecución
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        print(f"✅ Token guardado en {TOKEN_FILE}")
    
    # Probar conexión
    try:
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Conectado como: {profile.get('emailAddress')}")
        return True
    except Exception as e:
        print(f"❌ Error conectando: {e}")
        return False


def update_env_for_oauth():
    """Actualiza .env para usar OAuth en lugar de Service Account."""
    env_updates = {
        'GMAIL_USE_OAUTH': 'true',
        'GMAIL_TOKEN_FILE': 'config/gmail-token.pickle',
        'GMAIL_OAUTH_CLIENT_SECRET_FILE': 'config/oauth-client-secret.json',
        # Comentar configuración de Service Account
        '# GMAIL_SERVICE_ACCOUNT_FILE': 'config/service-account-key.json',
        '# GMAIL_DELEGATED_USER': 'coordinador@defensoria.gob.pe'
    }
    
    print("\n📝 Actualizando configuración...")
    for key, value in env_updates.items():
        print(f"   {key}={value}")


def test_send_email():
    """Probar envío de email con OAuth."""
    if not os.path.exists(TOKEN_FILE):
        print("❌ Token no encontrado. Ejecuta setup_oauth_flow() primero.")
        return False
    
    try:
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
        
        service = build('gmail', 'v1', credentials=creds)
        
        # Email de prueba simple
        from email.mime.text import MIMEText
        import base64
        
        profile = service.users().getProfile(userId='me').execute()
        my_email = profile.get('emailAddress')
        
        message = MIMEText('Email de prueba desde Defensoría Middleware via OAuth')
        message['to'] = my_email  # Enviar a sí mismo
        message['subject'] = 'Prueba OAuth - Defensoría'
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print(f"✅ Email de prueba enviado. ID: {result['id']}")
        return True
        
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Configurador OAuth Gmail - Defensoría Middleware")
    print("=" * 60)
    
    # Paso 1: Configurar OAuth
    if setup_oauth_flow():
        print("\n✅ OAuth configurado correctamente!")
        
        # Paso 2: Mostrar configuración
        update_env_for_oauth()
        
        # Paso 3: Probar envío
        print("\n🧪 ¿Probar envío de email? (y/n): ", end="")
        try:
            if input().lower().strip() in ['y', 'yes', 'sí', 'si']:
                test_send_email()
        except KeyboardInterrupt:
            print("\nCancelado")
        
        print("\n🎉 ¡OAuth configurado! Ahora puedes enviar emails desde Gmail personal")
        print("📝 Recuerda actualizar tu .env con la configuración mostrada arriba")
    else:
        print("\n❌ Error en configuración OAuth")