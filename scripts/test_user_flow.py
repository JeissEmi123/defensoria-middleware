import requests

# Configuración
BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY0Mjk3NjkwLCJpYXQiOjE3NjQyOTU4OTAsInR5cGUiOiJhY2Nlc3MifQ.fBy5ouRxSaZ_OG9ZYPmzIZCze9VtxZTqYaGBaf6J1q4"

# Crear usuario adicional
usuario_data = {
    "nombre_usuario": "usuario2",
    "email": "usuario2@demo.com",
    "contrasena": "usuario212345678"
}
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}
resp = requests.post(f"{BASE_URL}/usuarios/usuarios", json=usuario_data, headers=headers)
print("Crear usuario:", resp.status_code, resp.json())

# Listar usuarios
resp = requests.get(f"{BASE_URL}/usuarios/usuarios", headers=headers)
print("Listar usuarios:", resp.status_code, resp.json())
