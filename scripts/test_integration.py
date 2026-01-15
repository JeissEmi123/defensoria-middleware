import requests
import sys
import json

BASE_URL = "http://localhost:8000"

def get_admin_token():
    """Obtener token de admin mediante login"""
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "nombre_usuario": "admin", 
            "contrasena": "Admin123456!"
        }, timeout=10)
        
        if resp.status_code == 200:
            return resp.json().get("access_token")
        return None
    except:
        return None

def test_api_endpoints():
    """Test de endpoints adicionales de la API"""
    print("=== TEST API ENDPOINTS ===")
    
    # Obtener token
    token = get_admin_token()
    if not token:
        print("❌ No se pudo obtener token de admin")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Endpoints a testear
    endpoints = [
        ("GET", "/docs", "Documentación API"),
        ("GET", "/health", "Health Check"),
        ("GET", "/usuarios/list", "Lista de Usuarios"),
        ("GET", "/auth/me", "Validación de Token"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"\n--- Testeando: {description} ---")
        try:
            if method == "GET":
                resp = requests.get(f"{BASE_URL}{endpoint}", 
                                  headers=headers if endpoint != "/docs" and endpoint != "/health" else {}, 
                                  timeout=10)
            
            if resp.status_code in [200, 201]:
                print(f"✅ {description} - Status: {resp.status_code}")
            else:
                print(f"❌ {description} - Status: {resp.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en {description}: {e}")
    
    print("\n=== API ENDPOINTS TEST COMPLETADO ===")
    return True

def test_authentication_flow():
    """Test completo del flujo de autenticación"""
    print("\n=== TEST AUTHENTICATION FLOW ===")
    
    # 1. Login con credenciales incorrectas
    print("\n--- 1. Login con credenciales incorrectas ---")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "nombre_usuario": "admin",
            "contrasena": "wrongpassword"
        }, timeout=10)
        
        if resp.status_code == 401:
            print("✅ Credenciales incorrectas rechazadas correctamente")
        else:
            print(f"❌ Credenciales incorrectas no rechazadas - Status: {resp.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en test de credenciales incorrectas: {e}")
    
    # 2. Acceso sin token
    print("\n--- 2. Acceso sin token a endpoint protegido ---")
    try:
        resp = requests.get(f"{BASE_URL}/usuarios/list", timeout=10)
        
        if resp.status_code == 401:
            print("✅ Acceso sin token rechazado correctamente")
        else:
            print(f"❌ Acceso sin token no rechazado - Status: {resp.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en test de acceso sin token: {e}")
    
    # 3. Token inválido
    print("\n--- 3. Acceso con token inválido ---")
    try:
        headers = {"Authorization": "Bearer invalid_token_here"}
        resp = requests.get(f"{BASE_URL}/usuarios/list", headers=headers, timeout=10)
        
        if resp.status_code == 401:
            print("✅ Token inválido rechazado correctamente")
        else:
            print(f"❌ Token inválido no rechazado - Status: {resp.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en test de token inválido: {e}")
    
    print("\n=== AUTHENTICATION FLOW TEST COMPLETADO ===")
    return True

def test_integration_flow():
    """Test de integración completo"""
    print("\n=== TEST INTEGRATION COMPLETE ===")
    
    success = True
    
    # Ejecutar tests individuales
    success &= test_api_endpoints()
    success &= test_authentication_flow()
    
    return success

if __name__ == "__main__":
    success = test_integration_flow()
    sys.exit(0 if success else 1)