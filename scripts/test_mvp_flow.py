import requests
import sys
import json

BASE_URL = "http://localhost:8000"

def test_mvp_flow():
    """Test completo del flujo MVP: registro, login, validación y acceso"""
    print("=== TEST MVP FLOW ===")
    print(f"Conectando a: {BASE_URL}")
    
    # 1. Verificar conectividad
    try:
        resp = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"✅ Conectividad OK - Status: {resp.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conectividad: {e}")
        return False
    
    # 2. Crear usuario (primer usuario, sin token)
    print("\n--- 1. Verificando/Creando usuario admin ---")
    try:
        resp = requests.post(f"{BASE_URL}/usuarios/create", json={
            "nombre_usuario": "admin",
            "email": "admin@localhost.com", 
            "contrasena": "Admin123456!"
        }, timeout=10)
        
        if resp.status_code in [200, 201]:
            print(f"✅ Usuario creado - Status: {resp.status_code}")
        elif resp.status_code == 403 and "No autorizado" in resp.text:
            print(f"⚠️ Usuario admin ya configurado - Status: {resp.status_code}")
        elif resp.status_code == 400 and "ya existe" in resp.text:
            print(f"⚠️ Usuario ya existe - Status: {resp.status_code}")
        else:
            print(f"❌ Error creando usuario - Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en petición de crear usuario: {e}")
        return False

    # 3. Login
    print("\n--- 2. Realizando login ---")
    token = None
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "nombre_usuario": "admin",
            "contrasena": "Admin123456!"
        }, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token")
            if token:
                print(f"✅ Login exitoso - Token obtenido")
            else:
                print(f"❌ Login exitoso pero sin token en respuesta")
                print(f"Response: {resp.text}")
        else:
            print(f"❌ Error en login - Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en petición de login: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error decodificando respuesta JSON: {e}")
        return False

    if not token:
        print("❌ No se pudo obtener token, abortando tests siguientes")
        return False

    # 4. Validar token
    print("\n--- 3. Validando token ---")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            print(f"✅ Token válido - Status: {resp.status_code}")
        else:
            print(f"❌ Token inválido - Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en validación de token: {e}")
        return False

    # 5. Acceder a endpoint protegido (usuarios)
    print("\n--- 4. Accediendo a endpoint protegido ---")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/usuarios/list", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            users = resp.json()
            print(f"✅ Acceso a usuarios exitoso - {len(users)} usuarios encontrados")
        else:
            print(f"❌ Error accediendo a usuarios - Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en petición de usuarios: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error decodificando respuesta JSON: {e}")
        return False

    print("\n=== MVP FLOW COMPLETADO ===")
    return True

if __name__ == "__main__":
    success = test_mvp_flow()
    sys.exit(0 if success else 1)
