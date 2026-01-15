#!/usr/bin/env python3
"""
Script para autorizar Gmail OAuth para el proyecto Defensoría
Este script debe ejecutarse ANTES de usar el contenedor Docker para obtener el token.
"""

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

def autorizar_gmail_oauth():
    """
    Autoriza Gmail OAuth y guarda el token para usar en Docker
    """
    creds = None
    config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
    client_secret_file = os.path.join(config_dir, 'client_secret.json')
    token_file = os.path.join(config_dir, 'gmail-token.pickle')
    
    print(f"🔍 Buscando archivo client_secret en: {client_secret_file}")
    
    if not os.path.exists(client_secret_file):
        print(f"❌ Error: No se encontró el archivo {client_secret_file}")
        print("   Asegúrate de haber copiado el client_secret.json al directorio config/")
        return False
    
    # Si ya existe un token, intentar usarlo
    if os.path.exists(token_file):
        print(f"📄 Token existente encontrado: {token_file}")
        try:
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
                print("✅ Token cargado exitosamente")
        except Exception as e:
            print(f"⚠️  Error cargando token existente: {e}")
            creds = None
    
    # Si no hay credenciales válidas, autorizar
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refrescando token expirado...")
            try:
                creds.refresh(Request())
                print("✅ Token refrescado exitosamente")
            except Exception as e:
                print(f"❌ Error refrescando token: {e}")
                creds = None
        
        if not creds:
            print("🚀 Iniciando flujo de autorización OAuth...")
            print("   Se abrirá tu navegador web para autorizar la aplicación")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret_file, SCOPES)
                creds = flow.run_local_server(port=0)
                print("✅ Autorización OAuth completada exitosamente")
            except Exception as e:
                print(f"❌ Error en el flujo OAuth: {e}")
                return False
    
    # Guardar credenciales
    try:
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
        print(f"💾 Token guardado en: {token_file}")
        
        # Verificar que el archivo se puede leer
        with open(token_file, 'rb') as token:
            test_creds = pickle.load(token)
            if test_creds.valid:
                print("✅ Verificación del token: OK")
            else:
                print("⚠️  Advertencia: El token guardado no es válido")
                
    except Exception as e:
        print(f"❌ Error guardando token: {e}")
        return False
    
    print("\n🎉 ¡Configuración OAuth completada!")
    print("   Ahora puedes usar Docker Compose para probar el envío de correos")
    print(f"   Email que se usará: {creds.token.get('email', 'No detectado')}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("📧 CONFIGURACIÓN OAUTH GMAIL - DEFENSORÍA")
    print("=" * 60)
    
    if autorizar_gmail_oauth():
        print("\n✅ Proceso completado exitosamente")
    else:
        print("\n❌ Proceso falló - revisa los mensajes de error")
        exit(1)
