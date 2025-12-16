import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Defensoria Middleware API"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200

def test_login_endpoint_exists():
    response = client.post("/api/auth/login", data={
        "username": "test",
        "password": "test"
    })
    # Puede ser 401 (credenciales inválidas) o 500 (LDAP no configurado)
    # Lo importante es que el endpoint existe
    assert response.status_code in [401, 500]

def test_validate_endpoint_without_token():
    response = client.post("/api/auth/validate")
    assert response.status_code == 401

def test_user_endpoint_without_token():
    response = client.get("/api/auth/user")
    assert response.status_code == 401

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
