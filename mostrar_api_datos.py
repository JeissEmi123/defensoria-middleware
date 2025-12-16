#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mostrar datos completos del API con formato JSON
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
    'http://localhost:8000/api/v1/senales?skip=0&limit=3&orden=fecha_desc',
    headers=headers
)

data = response.json()

print("=" * 100)
print("RESPUESTA COMPLETA DEL API - /api/v1/senales")
print("=" * 100)
print(f"\nContent-Type: {response.headers.get('Content-Type')}")
print(f"Total señales: {data['total']}")
print(f"Mostrando: {len(data['senales'])} señales\n")

print("=" * 100)
print("JSON COMPLETO (primeras 3 señales):")
print("=" * 100)
print(json.dumps(data, indent=2, ensure_ascii=False))

print("\n" + "=" * 100)
print("RESUMEN DE CAMPOS POR SEÑAL:")
print("=" * 100)

for i, senal in enumerate(data['senales'], 1):
    print(f"\n{'='*50}")
    print(f"SEÑAL #{i} - ID: {senal['id_senal_detectada']}")
    print(f"{'='*50}")
    print(f"📅 Fecha: {senal['fecha_deteccion']}")
    print(f"📱 Plataformas: {', '.join(senal['plataformas_digitales']) if senal['plataformas_digitales'] else 'N/A'}")
    print(f"📍 Ubicación: {senal['metadatos'].get('ubicacion', 'N/A') if senal['metadatos'] else 'N/A'}")
    print(f"📊 Score Riesgo: {senal['score_riesgo']}")
    print(f"🏷️  Estado: {senal['estado']}")
    print(f"🔖 Categoría Señal ID: {senal['id_categoria_senal']}")
    print(f"📝 Contenido: {senal['contenido_detectado'][:100]}...")
    
    if senal['metadatos']:
        print(f"\n🔍 Metadatos completos:")
        for key, value in senal['metadatos'].items():
            print(f"   - {key}: {value}")
