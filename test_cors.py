#!/usr/bin/env python3
"""Script para verificar configuración CORS"""
import sys
sys.path.insert(0, '.')

from app.config import get_settings

settings = get_settings()

print("=" * 60)
print("🔍 VERIFICACIÓN DE CONFIGURACIÓN CORS")
print("=" * 60)

print(f"\n📋 ALLOWED_ORIGINS (raw): {settings.allowed_origins}")
print(f"\n✅ ALLOWED_ORIGINS (parsed): {settings.get_allowed_origins}")
print(f"\n🔐 CORS Allow Credentials: {settings.cors_allow_credentials}")
print(f"\n📝 CORS Allow Methods: {settings.cors_allow_methods}")
print(f"\n📄 CORS Allow Headers: {settings.cors_allow_headers}")

print("\n" + "=" * 60)
print("✅ Verificación completada")
print("=" * 60)

# Verificar si 3001 está incluido
if "http://localhost:3001" in settings.get_allowed_origins:
    print("\n✅ Puerto 3001 está configurado correctamente")
else:
    print("\n❌ ADVERTENCIA: Puerto 3001 NO está en la lista")
