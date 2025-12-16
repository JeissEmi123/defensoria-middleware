import requests

BASE_URL = "http://localhost:8000"

# 1. Crear usuario (primer usuario, sin token)
resp = requests.post(f"{BASE_URL}/usuarios/usuarios", json={
    "nombre_usuario": "admin",
    "email": "admin@localhost.com",
    "contrasena": "admin12345678"
})
print("Crear usuario:", resp.status_code, resp.text)

# 2. Login
resp = requests.post(f"{BASE_URL}/auth/login", json={
    "nombre_usuario": "admin",
    "contrasena": "admin12345678"
})
print("Login:", resp.status_code, resp.text)

token = None
if resp.ok:
    token = resp.json().get("access_token")

# 3. Validar token
if token:
    resp = requests.get(f"{BASE_URL}/auth/validate", headers={"Authorization": f"Bearer {token}"})
    print("Validar token:", resp.status_code, resp.text)
else:
    print("No se obtuvo token, no se puede validar.")

# 4. Acceder a endpoint protegido (usuarios)
if token:
    resp = requests.get(f"{BASE_URL}/usuarios/usuarios", headers={"Authorization": f"Bearer {token}"})
    print("Listar usuarios:", resp.status_code, resp.text)
else:
    print("No se obtuvo token, no se puede listar usuarios.")
