#  Guía de Instalación Local

## Defensoría del Pueblo - Middleware API

Esta guía te ayudará a configurar el entorno de desarrollo local para el middleware de la Defensoría del Pueblo.

---

##  Requisitos Previos

### Software Necesario
- **Python 3.11+** - [Descargar](https://python.org/downloads/)
- **PostgreSQL 15+** - [Descargar](https://postgresql.org/download/)
- **Git** - [Descargar](https://git-scm.com/downloads)
- **Docker** (Opcional) - [Descargar](https://docker.com/get-started)

### Equipo nuevo (sin herramientas)
```bash
./bootstrap.sh
```
Si falta algo, el script muestra comandos sugeridos segun el sistema operativo.

### Verificar Instalaciones
```bash
python --version    # Debe ser 3.11+
psql --version     # Debe ser 15+
git --version      # Cualquier versión reciente
docker --version   # Opcional
```

---

##  Instalación Rápida (Recomendada)

### Comando único (equipo nuevo)
```bash
./dev-up.sh
```

Este comando levanta la base de datos y la API con Docker y deja el servicio listo en http://localhost:9000

### Opción 1: Docker Compose (Más Fácil)

```bash
# 1. Clonar repositorio
git clone https://github.com/JeissEmi123/defensoria-middleware.git
cd defensoria-middleware

# 2. Configurar variables de entorno
cp .env.example .env.docker

# 3. Iniciar servicios
docker-compose up -d

# 4. Verificar instalación
curl http://localhost:9000/health
```

¡Listo! La API estará disponible en http://localhost:9000

---

##  Instalación Manual (Desarrollo)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/JeissEmi123/defensoria-middleware.git
cd defensoria-middleware
```

### 2. Crear Entorno Virtual

#### En Linux/macOS:
```bash
python -m venv venv
source venv/bin/activate
```

#### En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias principales
pip install -r requirements.txt

# Instalar dependencias de desarrollo (opcional)
pip install -r requirements-dev.txt
```

### 4. Configurar Base de Datos

#### Opción A: PostgreSQL Local

```bash
# Crear base de datos
createdb defensoria_db

# Crear usuario (opcional)
psql -c "CREATE USER defensoria_user WITH PASSWORD 'dev_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE defensoria_db TO defensoria_user;"
```

#### Opción B: PostgreSQL con Docker

```bash
# Iniciar solo PostgreSQL
docker run -d \
  --name defensoria_postgres \
  -e POSTGRES_DB=defensoria_db \
  -e POSTGRES_USER=defensoria_user \
  -e POSTGRES_PASSWORD=dev_password \
  -p 5432:5432 \
  postgres:15-alpine
```

### 5. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar configuración para desarrollo local
nano .env  # o usar tu editor preferido
```

**Configuración mínima para desarrollo:**

```bash
# Aplicación
APP_NAME=Defensoria Middleware
APP_VERSION=1.0.0
APP_ENV=development
DEBUG=True

# Seguridad (para desarrollo local)
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-key
JWT_REFRESH_SECRET_KEY=dev-jwt-refresh-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Base de Datos Local
DATABASE_URL=postgresql+asyncpg://defensoria_user:dev_password@localhost:5432/defensoria_db
POSTGRES_USER=defensoria_user
POSTGRES_PASSWORD=dev_password
POSTGRES_DB=defensoria_db
POSTGRES_PORT=5432

# CORS para desarrollo (permite todos los orígenes)
ALLOWED_ORIGINS=["*"]
ALLOWED_HOSTS=["*"]
CORS_ALLOW_CREDENTIALS=True

# Rate Limiting (más permisivo para desarrollo)
RATE_LIMIT_PER_MINUTE=1000
AUTH_RATE_LIMIT_PER_MINUTE=100

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=json
ENABLE_AUDIT_LOG=True

# Autenticación local habilitada
LOCAL_AUTH_ENABLED=True
LDAP_ENABLED=False

# Usuario administrador por defecto
ADMIN_DEFAULT_PASSWORD=admin123
```

### 6. Ejecutar Migraciones

```bash
# Ejecutar migraciones de Alembic
alembic upgrade head

# Verificar que las tablas se crearon
psql defensoria_db -c "\dt"
```

### 7. Inicializar Datos (Opcional)

```bash
# Crear usuario administrador
python scripts/manage_users.py create-admin

# Cargar datos de prueba (opcional)
python scripts/insertar_senales_prueba.py
```

### 8. Iniciar la Aplicación

```bash
# Opción 1: Con uvicorn directamente
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload

# Opción 2: Con el script incluido
chmod +x run.sh
./run.sh

# Opción 3: Con Python directamente
python -m app.main
```

---

## Verificar Instalación

### 1. Health Check
```bash
curl http://localhost:9000/health
# Respuesta esperada: {"status": "healthy"}
```

### 2. Documentación API
Abrir en el navegador:
- **Swagger UI**: http://localhost:9000/docs
- **ReDoc**: http://localhost:9000/redoc

### 3. Test de Autenticación
```bash
# Crear usuario de prueba (si no existe)
curl -X POST "http://localhost:9000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Usuario de Prueba"
  }'

# Iniciar sesión
curl -X POST "http://localhost:9000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

---

## Configuración del IDE

### Visual Studio Code

#### Extensiones Recomendadas:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.flake8",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-json"
  ]
}
```

#### Configuración del Workspace (.vscode/settings.json):
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".pytest_cache": true
  }
}
```

### PyCharm

1. Abrir el proyecto en PyCharm
2. Configurar intérprete: File → Settings → Project → Python Interpreter
3. Seleccionar el entorno virtual creado
4. Configurar run configuration para FastAPI

---

## Ejecutar Tests

### Tests Unitarios
```bash
# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=app --cov-report=html

# Ejecutar tests específicos
pytest tests/test_auth.py
```

### Tests de Integración
```bash
# Tests de endpoints
pytest tests/integration/

# Test específico de API
python scripts/test_integration.py
```

### Tests Manuales
```bash
# Verificar endpoints principales
python scripts/test_endpoints_sds.py

# Test de flujo completo
python scripts/test_mvp_flow.py
```

---

## Herramientas de Desarrollo

### 1. Formateo de Código
```bash
# Formatear con Black
black app/ tests/

# Ordenar imports con isort
isort app/ tests/

# Verificar estilo con flake8
flake8 app/ tests/
```

### 2. Análisis de Código
```bash
# Análisis estático con mypy
mypy app/

# Verificar seguridad con bandit
bandit -r app/
```

### 3. Base de Datos

#### Crear Nueva Migración
```bash
# Generar migración automática
alembic revision --autogenerate -m "Descripción del cambio"

# Crear migración manual
alembic revision -m "Descripción del cambio"
```

#### Gestión de Migraciones
```bash
# Ver historial de migraciones
alembic history

# Ver migración actual
alembic current

# Aplicar migración específica
alembic upgrade <revision_id>

# Revertir migración
alembic downgrade -1
```

---

##  Debugging

### 1. Logs de Desarrollo
```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Filtrar logs por nivel
grep "ERROR" logs/app.log
```

### 2. Debug con Python Debugger
```python
# Agregar breakpoint en el código
import pdb; pdb.set_trace()

# O usar el nuevo breakpoint() en Python 3.7+
breakpoint()
```

### 3. Debug con VS Code
1. Crear `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI Debug",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/app/main.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```

---

## Scripts Útiles

### Gestión de Base de Datos
```bash
# Backup de desarrollo
python scripts/backup_db.py

# Resetear base de datos
python scripts/reset_sds_auto.py

# Verificar estado de la DB
python scripts/health_check_db.py
```

### Gestión de Usuarios
```bash
# Crear usuario administrador
python scripts/manage_users.py create-admin

# Listar usuarios
python scripts/manage_users.py list-users

# Cambiar contraseña
python scripts/manage_users.py change-password <username>
```

### Validación del Sistema
```bash
# Validar configuración completa
python scripts/validate_all.py

# Verificar configuración de email
python scripts/test_email_flow.py

# Test de integración completo
python scripts/test_integration.py
```

---

## Solución de Problemas Comunes

### 1. Error de Conexión a PostgreSQL
```bash
# Verificar que PostgreSQL esté ejecutándose
sudo systemctl status postgresql  # Linux
brew services list | grep postgres  # macOS

# Verificar conexión
psql -h localhost -U defensoria_user -d defensoria_db
```

### 2. Error de Dependencias de Python
```bash
# Reinstalar dependencias
pip install --force-reinstall -r requirements.txt

# Limpiar cache de pip
pip cache purge
```

### 3. Error de Migraciones
```bash
# Verificar estado actual
alembic current

# Marcar como aplicada manualmente (si es necesario)
alembic stamp head

# Aplicar migraciones forzadamente
alembic upgrade head --sql  # Ver SQL sin ejecutar
```

### 4. Puerto en Uso
```bash
# Encontrar proceso usando el puerto
lsof -i :9000  # Linux/macOS
netstat -ano | findstr :9000  # Windows

# Cambiar puerto en la aplicación
uvicorn app.main:app --port 9001
```

---

## Recursos Adicionales

### Documentación
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://postgresql.org/docs/)

### Archivos de Configuración
- `.env` - Variables de entorno
- `alembic.ini` - Configuración de migraciones
- `requirements.txt` - Dependencias de Python
- `docker-compose.yml` - Configuración de Docker

### Scripts Importantes
- `run.sh` - Script de inicio
- `scripts/manage_users.py` - Gestión de usuarios
- `scripts/validate_all.py` - Validación del sistema
- `scripts/test_integration.py` - Tests de integración

---

## Ayuda y Soporte

### Contactos
- **Equipo de Desarrollo**: desarrollo@defensoria.gob.pe
- **Documentación Técnica**: docs@defensoria.gob.pe

### Issues Comunes
Si encuentras problemas, revisa:
1. Los logs de la aplicación
2. El estado de PostgreSQL
3. Las variables de entorno
4. Las migraciones de base de datos

### Contribuir
Para contribuir al proyecto:
1. Fork del repositorio
2. Crear rama de feature
3. Hacer commits con mensajes descriptivos
4. Crear Pull Request

---

**Documento**: Guía de Instalación Local  
**Versión**: 1.0.0  
**Estado**:  Listo para Desarrollo
