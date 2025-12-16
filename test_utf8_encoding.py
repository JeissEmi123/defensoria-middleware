#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar que el API responde correctamente con UTF-8
"""
import requests
import json

# Login
login_response = requests.post(
    'http://localhost:8000/auth/login',
    json={'username': 'admin', 'password': 'Admin123456!'}
)
token = login_response.json()['access_token']

# Obtener señales
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
    'http://localhost:8000/api/v1/senales?skip=0&limit=2',
    headers=headers
)

print("=" * 80)
print("VERIFICACIÓN DE UTF-8 EN API RESPONSES")
print("=" * 80)

# Verificar Content-Type
content_type = response.headers.get('Content-Type', '')
print(f"\n✅ Content-Type: {content_type}")

if 'charset=utf-8' in content_type.lower():
    print("   ✓ Header incluye charset=utf-8")
else:
    print("   ✗ Header NO incluye charset=utf-8")

# Verificar encoding
print(f"\n✅ Response Encoding: {response.encoding}")

# Decodificar como UTF-8
data = response.json()

print(f"\n✅ Total señales: {data['total']}")
print(f"✅ Señales retornadas: {len(data['senales'])}")

# Mostrar primera señal con caracteres UTF-8
if data['senales']:
    senal = data['senales'][0]
    print("\n" + "=" * 80)
    print("PRIMERA SEÑAL - CARACTERES UTF-8:")
    print("=" * 80)
    print(f"ID: {senal['id_senal_detectada']}")
    print(f"Fecha: {senal['fecha_deteccion']}")
    print(f"Contenido: {senal['contenido_detectado']}")
    
    if senal.get('metadatos') and senal['metadatos'].get('ubicacion'):
        ubicacion = senal['metadatos']['ubicacion']
        print(f"Ubicación: {ubicacion}")
        
        # Verificar caracteres específicos
        caracteres_test = {
            'á': 'á' in ubicacion.lower() or 'á' in senal['contenido_detectado'].lower(),
            'é': 'é' in ubicacion.lower() or 'é' in senal['contenido_detectado'].lower(),
            'í': 'í' in ubicacion.lower() or 'í' in senal['contenido_detectado'].lower(),
            'ó': 'ó' in ubicacion.lower() or 'ó' in senal['contenido_detectado'].lower(),
            'ú': 'ú' in ubicacion.lower() or 'ú' in senal['contenido_detectado'].lower(),
            'ñ': 'ñ' in ubicacion.lower() or 'ñ' in senal['contenido_detectado'].lower(),
        }
        
        print("\n" + "=" * 80)
        print("CARACTERES ESPECIALES DETECTADOS:")
        print("=" * 80)
        for char, encontrado in caracteres_test.items():
            status = "✓" if encontrado else "✗"
            print(f"  {status} '{char}' encontrado: {encontrado}")

# Mostrar JSON pretty
print("\n" + "=" * 80)
print("JSON RAW (primeras 500 caracteres):")
print("=" * 80)
json_str = json.dumps(senal, ensure_ascii=False, indent=2)
print(json_str[:500])

print("\n" + "=" * 80)
print("✅ VERIFICACIÓN COMPLETA")
print("=" * 80)
