#!/usr/bin/env python3
"""
Test simple del endpoint /api/v2/senales/consultar en producción
"""

import requests
import json
import sys
import os

BASE_URL_PROD = os.getenv(
    "BASE_URL_PROD",
    "https://defensoria-middleware-prod-411798681660.us-central1.run.app",
)
PROD_USERNAME = os.getenv("PROD_USERNAME", "admin")
PROD_PASSWORD = os.getenv("PROD_PASSWORD")

def main():
    print("=" * 70)
    print("🔧 TEST ENDPOINT SENALES - PRODUCCIÓN")
    print("=" * 70)

    if not PROD_PASSWORD:
        print("\n❌ Falta PROD_PASSWORD. Define PROD_PASSWORD (y opcionalmente PROD_USERNAME) y reintenta.")
        return False
    
    # 1. Login
    print("\n1️⃣  Obteniendo token de autenticación...")
    try:
        resp = requests.post(
            f"{BASE_URL_PROD}/auth/login",
            json={"username": PROD_USERNAME, "password": PROD_PASSWORD},
            timeout=30
        )
        
        if resp.status_code != 200:
            print(f"   ❌ Error de login: {resp.status_code}")
            print(f"   {resp.text}")
            return False
            
        data = resp.json()
        token = data.get("access_token")
        if not token:
            print(f"   ❌ No se obtuvo token en respuesta")
            print(f"   {json.dumps(data, indent=2)}")
            return False
            
        print(f"   ✅ Token obtenido: {token[:50]}...")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # 2. Test endpoint sin filtros
    print("\n2️⃣  Probando /api/v2/senales/consultar sin filtros...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    try:
        url = f"{BASE_URL_PROD}/api/v2/senales/consultar?limite=10&desplazamiento=0"
        print(f"   GET {url}")
        
        resp = requests.get(url, headers=headers, timeout=30)
        
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"   ❌ Error: {resp.text[:500]}")
            return False
        
        data = resp.json()
        
        # Analizar respuesta
        total = data.get("total", 0)
        senales = data.get("senales", [])
        
        print(f"\n   📊 RESULTADOS:")
        print(f"      Total de registros en BD: {total}")
        print(f"      Señales retornadas en esta página: {len(senales)}")
        
        if senales:
            print(f"\n      ✅ ¡El endpoint está retornando datos!")
            print(f"\n      Primeros 3 registros:")
            for i, senal in enumerate(senales[:3], 1):
                print(f"\n         {i}. {senal.get('titulo', 'Sin título')}")
                print(f"            Categoría: {senal.get('categoria')}")
                print(f"            Score: {senal.get('score_riesgo')}")
                print(f"            Fecha: {senal.get('fecha_deteccion')}")
                print(f"            Color: {senal.get('color')}")
            
            # Full response
            print(f"\n   📋 RESPUESTA COMPLETA:")
            print(json.dumps(data, indent=2, default=str))
            
            return True
        else:
            print(f"\n   ⚠️  El endpoint responde correctamente pero NO HAY DATOS")
            print(f"      Respuesta: {json.dumps(data, indent=2, default=str)}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ ENDPOINT FUNCIONANDO CORRECTAMENTE")
    else:
        print("❌ PROBLEMA CON EL ENDPOINT")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
