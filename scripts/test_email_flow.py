#!/usr/bin/env python3
"""
Script para probar el endpoint de cambio de categoría de señal
Simula una llamada real al API para verificar el flujo completo
"""
import os
import sys
import json
import asyncio
import aiohttp
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings

class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.token = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def login(self, username="admin", password="Admin123456!"):
        """Autenticarse y obtener token"""
        print(f"🔐 Autenticándose como {username}...")
        
        login_data = {
            "username": username,
            "password": password
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get("access_token")
                    print("✅ Autenticación exitosa")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Error de autenticación ({response.status}): {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Error conectando al API: {e}")
            return False
    
    async def get_categorias(self):
        """Obtener categorías disponibles"""
        print("📋 Obteniendo categorías de señales...")
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/senales/catalogos/categorias-senal",
                headers=headers
            ) as response:
                if response.status == 200:
                    categorias = await response.json()
                    print(f"✅ {len(categorias)} categorías encontradas:")
                    for cat in categorias:
                        print(f"   - ID {cat.get('id_categoria_senal')}: {cat.get('nombre_categoria_senal')}")
                    return categorias
                else:
                    error_text = await response.text()
                    print(f"❌ Error obteniendo categorías ({response.status}): {error_text}")
                    return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    async def get_senales(self, limit=5):
        """Obtener señales para probar"""
        print(f"🔍 Obteniendo últimas {limit} señales...")
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/senales?limit={limit}",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    senales = data.get('items', [])
                    print(f"✅ {len(senales)} señales encontradas")
                    
                    for senal in senales:
                        print(f"   - ID {senal.get('id_senal_detectada')}: "
                              f"Categoría {senal.get('id_categoria_senal', 'N/A')} "
                              f"({senal.get('estado', 'N/A')})")
                    
                    return senales
                else:
                    error_text = await response.text()
                    print(f"❌ Error obteniendo señales ({response.status}): {error_text}")
                    return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    async def crear_senal_prueba(self):
        """Crear una señal de prueba para testing"""
        print("➕ Creando señal de prueba...")
        
        senal_data = {
            "id_categoria_senal": 1,  # RUIDO
            "id_categoria_analisis": 1,
            "score_riesgo": 45.0,
            "categorias_observacion": {"test": True},
            "plataformas_digitales": ["Twitter"],
            "contenido_detectado": "Contenido de prueba para validar el sistema de emails",
            "metadatos": {"test_script": True},
            "url_origen": "https://test.example.com",
            "estado": "DETECTADA"
        }
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/senales",
                json=senal_data,
                headers=headers
            ) as response:
                if response.status == 201:
                    senal = await response.json()
                    senal_id = senal.get('id_senal_detectada')
                    print(f"✅ Señal de prueba creada con ID: {senal_id}")
                    return senal_id
                else:
                    error_text = await response.text()
                    print(f"❌ Error creando señal ({response.status}): {error_text}")
                    return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    async def test_cambio_categoria(self, senal_id, nueva_categoria_id=3, confirmo_revision=True):
        """Probar cambio de categoría con confirmación"""
        print(f"🔄 Probando cambio de categoría para señal {senal_id}...")
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        params = {
            "nueva_categoria_id": nueva_categoria_id,
            "confirmo_revision": confirmo_revision,
            "comentario": "Test automático del sistema de notificaciones por email"
        }
        
        try:
            async with self.session.put(
                f"{self.base_url}/api/v1/senales/{senal_id}/categoria",
                params=params,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Cambio de categoría exitoso")
                    print(f"   Nueva categoría: {data.get('id_categoria_senal')}")
                    
                    if confirmo_revision:
                        print("📧 Si la configuración es correcta, se debería enviar email al coordinador")
                        print(f"   Destinatario: {settings.coordinador_email or 'NO CONFIGURADO'}")
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Error en cambio de categoría ({response.status}): {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def test_flujo_completo(self):
        """Probar flujo completo: crear señal, cambiar categoría, verificar email"""
        print("\n🧪 PROBANDO FLUJO COMPLETO DE NOTIFICACIÓN")
        print("=" * 50)
        
        # 1. Autenticarse
        if not await self.login():
            return False
        
        # 2. Obtener categorías (para verificar que el API funciona)
        categorias = await self.get_categorias()
        if not categorias:
            print("❌ No se pueden obtener categorías - API podría no estar funcionando")
            return False
        
        # 3. Crear señal de prueba
        senal_id = await self.crear_senal_prueba()
        if not senal_id:
            print("❌ No se pudo crear señal de prueba")
            return False
        
        # 4. Cambiar categoría con confirmación (debería disparar email)
        success = await self.test_cambio_categoria(senal_id, nueva_categoria_id=3)
        
        if success:
            print("\n✅ FLUJO COMPLETO EXITOSO")
            print("📧 Revisa el email del coordinador para confirmar la notificación")
        else:
            print("\n❌ FLUJO FALLÓ")
        
        return success

async def check_api_health():
    """Verificar que el API esté funcionando"""
    print("❤️  Verificando estado del API...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    print("✅ API está funcionando")
                    return True
                else:
                    print(f"⚠️  API responde pero con status {response.status}")
                    return False
    except aiohttp.ClientConnectorError:
        print("❌ No se puede conectar al API en http://localhost:8000")
        print("   Verifica que el servidor esté corriendo con: docker-compose up")
        return False
    except Exception as e:
        print(f"❌ Error verificando API: {e}")
        return False

async def main():
    """Función principal"""
    print("🧪 TESTER DE API - SISTEMA DE NOTIFICACIONES")
    print("=" * 60)
    
    # Verificar configuración básica
    if not settings.coordinador_email:
        print("⚠️  COORDINADOR_EMAIL no está configurado")
        print("   El test funcionará pero no se enviarán emails")
    else:
        print(f"📧 Email del coordinador: {settings.coordinador_email}")
    
    # Verificar que el API esté corriendo
    if not await check_api_health():
        return False
    
    # Ejecutar test completo
    async with APITester() as tester:
        success = await tester.test_flujo_completo()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TODOS LOS TESTS PASARON")
        print("🎉 El sistema está funcionando correctamente")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("🔧 Revisa los logs y la configuración")
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrumpido por el usuario")
        sys.exit(1)