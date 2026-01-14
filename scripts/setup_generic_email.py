#!/usr/bin/env python3
"""
Script para reconfigurar el sistema con la cuenta genérica defensoria.middleware@gmail.com
"""
import os
import subprocess
from pathlib import Path

def reconfigure_for_generic_account():
    """Reconfigurar sistema para cuenta genérica."""
    print("🔧 Configurando cuenta genérica: defensoria.middleware@gmail.com")
    print("=" * 70)
    print()
    
    # Paso 1: Actualizar .env
    print("📝 Actualizando configuración...")
    
    # Leer .env actual
    env_file = ".env"
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Actualizar EMAIL_FROM y COORDINADOR_EMAIL
    new_content = content.replace(
        "EMAIL_FROM=jcamargom@agatadata.com",
        "EMAIL_FROM=defensoria.middleware@gmail.com"
    )
    
    # Escribir .env actualizado
    with open(env_file, 'w') as f:
        f.write(new_content)
    
    print("✅ Archivo .env actualizado")
    
    # Paso 2: Eliminar token anterior
    print("🗑️ Eliminando token anterior...")
    token_file = "config/gmail-token.pickle"
    if os.path.exists(token_file):
        os.remove(token_file)
        print("✅ Token anterior eliminado")
    else:
        print("ℹ️ No hay token anterior que eliminar")
    
    # Paso 3: Instrucciones para el usuario
    print()
    print("🎯 PRÓXIMOS PASOS:")
    print("1. ✅ Crea la cuenta: defensoria.middleware@gmail.com")
    print("2. ✅ Habilita 2FA en la nueva cuenta")
    print("3. ✅ Ejecuta: python scripts/setup_oauth_gmail.py")
    print("4. ✅ Autoriza desde la nueva cuenta Gmail")
    print()
    print("📧 Los emails se enviarán desde: defensoria.middleware@gmail.com")
    print("📨 Las notificaciones irán a: jcamargom@agatadata.com")
    
    return True

def show_current_config():
    """Mostrar configuración actual."""
    print("📊 Configuración actual:")
    configs = [
        ("EMAIL_FROM", "Cuenta que envía"),
        ("COORDINADOR_EMAIL", "Cuenta que recibe notificaciones"),
        ("GMAIL_USE_OAUTH", "Método de autenticación"),
        ("GMAIL_TOKEN_FILE", "Archivo de token")
    ]
    
    for key, desc in configs:
        value = os.getenv(key, "❌ No configurado")
        print(f"   {desc}: {value}")

if __name__ == "__main__":
    print("🏛️ Configurador de Cuenta Genérica - Defensoría Middleware")
    print("=" * 70)
    print()
    
    # Mostrar configuración actual
    show_current_config()
    print()
    
    # Confirmar cambio
    confirm = input("¿Cambiar a defensoria.middleware@gmail.com? (y/n): ").lower().strip()
    
    if confirm in ['y', 'yes', 'sí', 'si']:
        reconfigure_for_generic_account()
        print()
        print("🎉 Configuración actualizada!")
        print("📋 Recuerda crear la cuenta Gmail y ejecutar el setup OAuth")
    else:
        print("❌ Configuración no modificada")