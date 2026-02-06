# Guía de Instalación Local

## Objetivo
Levantar la API en una máquina limpia, con la ruta rápida en Docker y una alternativa manual si necesitas depurar a bajo nivel.

## Requisitos
Para la opción recomendada:
- Git
- Docker Desktop o Docker Engine + Docker Compose

Para la opción manual:
- Python 3.11+
- PostgreSQL 15+
- Git

## Opción recomendada (Docker)
```bash
./bootstrap.sh
./dev-up.sh
```

Notas:
- `dev-up.sh` usa `.env.docker`.
- La API queda en `http://localhost:9000`.
- Health check: `http://localhost:9000/health`.
- Para reiniciar desde cero la base local: `docker compose down -v`.

## Opción manual (sin Docker)
1. Crea el entorno de Python y dependencias:
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. Prepara la base de datos local en PostgreSQL:
```bash
createuser defensoria --pwprompt
createdb defensoria_db -O defensoria
```

3. Configura variables y migra:
```bash
cp .env.example .env
# Edita .env y ajusta DATABASE_URL y credenciales
alembic upgrade head
```

4. Levanta la API:
```bash
./run.sh
```

## Variables de entorno
El archivo `.env.example` contiene la plantilla. Valores mínimos:
- `DATABASE_URL`
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`
- `SECRET_KEY`, `JWT_SECRET_KEY`, `JWT_REFRESH_SECRET_KEY`
- `ADMIN_DEFAULT_PASSWORD`

## Verificación
```bash
curl http://localhost:9000/health
```

## Documentación local
- Swagger UI: `http://localhost:9000/docs`
- ReDoc: `http://localhost:9000/redoc`

## Tests (opcional)
```bash
pytest
```
