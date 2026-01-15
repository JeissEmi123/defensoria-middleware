import requests
import sys
import json

# Configuración
BASE_URL = "http://localhost:8000"

def get_admin_token():
    """Obtener token de admin mediante login"""
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "nombre_usuario": "admin",
            "contrasena": "Admin123456!"
        }, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            return data.get("access_token")
        else:
            print(f"❌ Error obteniendo token admin - Status: {resp.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en login admin: {e}")
        return None

def test_user_flow():
    """Test de operaciones con usuarios usando token dinámico"""
    print("=== TEST USER FLOW ===")
    print(f"Conectando a: {BASE_URL}")
    
    # 1. Obtener token de admin
    print("\n--- 1. Obteniendo token de admin ---")
    token = get_admin_token()
    
    if not token:
        print("❌ No se pudo obtener token de admin")
        return False
    
    print("✅ Token de admin obtenido")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # 2. Crear usuario adicional
    print("\n--- 2. Creando usuario adicional ---")
    usuario_data = {
        "nombre_usuario": "usuario2",
        "email": "usuario2@demo.com",
        "contrasena": "StrongP@ssw0rd123!"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/usuarios/create", 
                           json=usuario_data, headers=headers, timeout=10)
        
        if resp.status_code in [200, 201]:
            print(f"✅ Usuario creado exitosamente - Status: {resp.status_code}")
        elif resp.status_code == 400 and "ya existe" in resp.text:
            print(f"⚠️ Usuario ya existe - Status: {resp.status_code}")
        else:
            print(f"❌ Error creando usuario - Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en petición de crear usuario: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error decodificando respuesta JSON: {e}")
        return False

    # 3. Listar usuarios
    print("\n--- 3. Listando usuarios ---")
    try:
        resp = requests.get(f"{BASE_URL}/usuarios/list", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            users = resp.json()
            print(f"✅ Usuarios listados exitosamente - {len(users)} usuarios encontrados")
            
            # Mostrar información básica de usuarios
            for i, user in enumerate(users, 1):
                username = user.get('nombre_usuario', 'N/A')
                email = user.get('email', 'N/A')
                print(f"  {i}. {username} ({email})")
        else:
            print(f"❌ Error listando usuarios - Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en petición de listar usuarios: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error decodificando respuesta JSON: {e}")
        return False

    # 4. Test login con el nuevo usuario
    print("\n--- 4. Probando login con nuevo usuario ---")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "nombre_usuario": "usuario2",
            "contrasena": "StrongP@ssw0rd123!"
        }, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            new_token = data.get("access_token")
            if new_token:
                print(f"✅ Login con nuevo usuario exitoso")
            else:
                print(f"❌ Login exitoso pero sin token")
        else:
            print(f"❌ Error en login nuevo usuario - Status: {resp.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en login nuevo usuario: {e}")
        return False

    print("\n=== USER FLOW COMPLETADO ===")
    return True

if __name__ == "__main__":
    success = test_user_flow()
    sys.exit(0 if success else 1)
