#!/usr/bin/env python3
"""
Script para probar los endpoints de parámetros SDS
"""
import asyncio
import aiohttp
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

async def get_auth_token() -> str:
    """Obtener token de autenticación"""
    async with aiohttp.ClientSession() as session:
        login_data = {
            "username": "admin",
            "password": "Admin123456!"
        }
        async with session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                return data["access_token"]
            else:
                error = await response.text()
                raise Exception(f"Error al obtener token: {error}")

async def test_endpoint(session: aiohttp.ClientSession, token: str, method: str, endpoint: str, data: Dict[Any, Any] = None) -> Dict[str, Any]:
    """Probar un endpoint específico"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            async with session.get(f"{BASE_URL}{endpoint}", headers=headers) as response:
                return {
                    "status": response.status,
                    "data": await response.json() if response.status != 204 else None
                }
        elif method == "POST":
            async with session.post(f"{BASE_URL}{endpoint}", headers=headers, json=data) as response:
                return {
                    "status": response.status,
                    "data": await response.json() if response.status != 204 else None
                }
        elif method == "PUT":
            async with session.put(f"{BASE_URL}{endpoint}", headers=headers, json=data) as response:
                return {
                    "status": response.status,
                    "data": await response.json() if response.status != 204 else None
                }
        elif method == "DELETE":
            async with session.delete(f"{BASE_URL}{endpoint}", headers=headers) as response:
                return {
                    "status": response.status,
                    "data": await response.json() if response.status != 204 else None
                }
    except Exception as e:
        return {
            "status": "ERROR",
            "data": {"error": str(e)}
        }

async def main():
    """Función principal para ejecutar las pruebas"""
    print("🚀 Iniciando pruebas de endpoints SDS...")
    
    # Obtener token
    try:
        token = await get_auth_token()
        print("✅ Token de autenticación obtenido")
    except Exception as e:
        print(f"❌ Error al obtener token: {e}")
        return
    
    # Endpoints para probar
    endpoints_tests = [
        ("GET", "/api/v2/parametros/categorias-analisis", None),
        ("GET", "/api/v2/parametros/conductas-vulneratorias", None),
        ("GET", "/api/v2/parametros/palabras-clave", None),
        ("GET", "/api/v2/parametros/emoticonos", None),
        ("GET", "/api/v2/parametros/frases-clave", None),
        ("GET", "/api/v2/parametros/categorias-senal", None),
        ("GET", "/api/v2/parametros/figuras-publicas", None),
        ("GET", "/api/v2/parametros/influencers", None),
        ("GET", "/api/v2/parametros/medios-digitales", None),
        ("GET", "/api/v2/parametros/entidades", None),
    ]
    
    async with aiohttp.ClientSession() as session:
        print("\n📊 Resultados de las pruebas GET:")
        print("=" * 50)
        
        for method, endpoint, data in endpoints_tests:
            result = await test_endpoint(session, token, method, endpoint, data)
            endpoint_name = endpoint.split("/")[-1]
            
            if result["status"] == 200:
                if isinstance(result["data"], list):
                    count = len(result["data"])
                    print(f"✅ {endpoint_name:<25} - {count} registros encontrados")
                else:
                    print(f"✅ {endpoint_name:<25} - Respuesta exitosa")
            else:
                if result["data"] and "error" in result["data"]:
                    error_msg = result["data"]["message"][:80] + "..." if len(result["data"]["message"]) > 80 else result["data"]["message"]
                    print(f"❌ {endpoint_name:<25} - Error: {error_msg}")
                else:
                    print(f"❌ {endpoint_name:<25} - Status: {result['status']}")
        
        # Probar CRUD en categorías de análisis (que sabemos que funciona)
        print(f"\n🔄 Probando operaciones CRUD en categorías de análisis...")
        print("=" * 50)
        
        # POST - Crear
        create_data = {
            "nombre_categoria_analisis": "Categoría de Prueba Script",
            "descripcion_categoria_analisis": "Categoría creada desde script de prueba"
        }
        
        create_result = await test_endpoint(session, token, "POST", "/api/v2/parametros/categorias-analisis", create_data)
        
        if create_result["status"] == 201:
            created_id = create_result["data"]["id_categoria_analisis_senal"]
            print(f"✅ CREATE - Categoría creada con ID: {created_id}")
            
            # PUT - Actualizar
            update_data = {
                "nombre_categoria_analisis": "Categoría de Prueba Script Actualizada",
                "descripcion_categoria_analisis": "Descripción actualizada desde script"
            }
            
            update_result = await test_endpoint(session, token, "PUT", f"/api/v2/parametros/categorias-analisis/{created_id}", update_data)
            
            if update_result["status"] == 200:
                print(f"✅ UPDATE - Categoría {created_id} actualizada")
                
                # GET específico
                get_result = await test_endpoint(session, token, "GET", f"/api/v2/parametros/categorias-analisis/{created_id}")
                if get_result["status"] == 200:
                    print(f"✅ GET ID - Categoría {created_id} obtenida correctamente")
                
                # DELETE
                delete_result = await test_endpoint(session, token, "DELETE", f"/api/v2/parametros/categorias-analisis/{created_id}")
                print(f"🗑️  DELETE - Status: {delete_result['status']} (puede fallar por dependencias)")
                
            else:
                print(f"❌ UPDATE - Error: {update_result['status']}")
        else:
            print(f"❌ CREATE - Error: {create_result['status']}")
        
        # Probar validación de unicidad
        print(f"\n🔒 Probando validaciones...")
        print("=" * 50)
        
        duplicate_result = await test_endpoint(session, token, "POST", "/api/v2/parametros/categorias-analisis", {
            "nombre_categoria_analisis": "Reclutamiento, uso y utilización de niñas, niños y adolescentes",
            "descripcion_categoria_analisis": "Intento de duplicar nombre existente"
        })
        
        if duplicate_result["status"] == 400:
            print("✅ VALIDACIÓN - Unicidad de nombre funcionando correctamente")
        else:
            print(f"❌ VALIDACIÓN - Unicidad no funcionó como se esperaba: {duplicate_result['status']}")

if __name__ == "__main__":
    asyncio.run(main())