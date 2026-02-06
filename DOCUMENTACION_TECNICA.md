# Documentación Técnica - Defensoría Middleware

## Metadatos
- Versión: 2.1
- Fecha: 2026-02-06
- Responsable: Equipo de Ingeniería

## Para quién es este documento
Este documento está pensado para arquitectos, líderes técnicos y devs que necesitan entender cómo está armado el servicio, cómo se configura y cómo se opera en local y en producción.

## Panorama rápido
- API REST construida con FastAPI.
- Autenticación JWT, RBAC y recuperación de contraseña.
- PostgreSQL como base de datos.
- Alembic para migraciones.
- Docker para desarrollo local.
- Cloud Build + Cloud Run para producción.

## Decisiones de arquitectura (resumen)
- FastAPI por rendimiento y ergonomía en APIs asíncronas.
- PostgreSQL por consistencia y consultas relacionales.
- Alembic para controlar el ciclo de vida del esquema.
- Docker para reproducibilidad en entornos locales.
- Cloud Run para operación serverless con despliegue simple.

## Mapa rápido del repositorio
- `app/main.py`: inicialización de FastAPI y registro de routers.
- `app/api/`: endpoints por dominio funcional.
- `app/services/`: lógica de negocio.
- `app/database/`: modelos, repositorios y sesión de base de datos.
- `alembic/`: migraciones y scripts.
- `Dockerfile` y `docker-compose.yml`: entorno local.
- `.github/workflows/deploy.yml`: CI/CD.

## Flujo de una solicitud
1. Cliente invoca un endpoint HTTP.
2. FastAPI enruta al router correspondiente.
3. Servicios validan reglas y ejecutan la lógica de negocio.
4. Repositorios acceden a PostgreSQL.
5. Se retorna la respuesta JSON.

## Ejecución local

### Opción recomendada (Docker)
1. Verifica dependencias básicas con `./bootstrap.sh`.
2. Levanta el stack con `./dev-up.sh`.

Notas:
- `dev-up.sh` usa el archivo `.env.docker`.
- El servidor queda en `http://localhost:9000`.
- El `run.sh` ejecuta migraciones al iniciar el contenedor.

### Opción manual (sin Docker)
Requisitos:
- Python 3.11+
- PostgreSQL 15+

Pasos:
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
# Ajustar DATABASE_URL y credenciales locales en .env
alembic upgrade head
./run.sh
```

Notas:
- `run.sh` inicia Uvicorn en el puerto 9000.
- Si ejecutas `python -m app.main`, el puerto por defecto es 8000.

## Configuración
La configuración se gestiona vía variables de entorno.

Archivos relevantes:
- `.env.docker`: valores locales para Docker.
- `.env.example`: plantilla base para ejecución manual.
- `.env.production`: referencia para producción.

Variables mínimas para arrancar:
- `DATABASE_URL`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_PORT`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `JWT_REFRESH_SECRET_KEY`
- `ADMIN_DEFAULT_PASSWORD`

Formatos importantes:
- `ALLOWED_ORIGINS`: lista JSON, por ejemplo `["https://app.defensoria.gob.pe"]`.
- `ALLOWED_HOSTS`: lista JSON o string único.

## Base de datos y migraciones
- PostgreSQL 15+.
- Migraciones gestionadas con Alembic:
```bash
alembic upgrade head
```

Para crear migraciones:
```bash
alembic revision --autogenerate -m "descripcion"
```

## Seguridad
- JWT con expiración configurable.
- Rate limiting por endpoint.
- Política de contraseñas y bloqueo por intentos fallidos.
- Headers de seguridad en producción (configurable).

## Observabilidad
- Logs en stdout (Docker) y/o archivos si se configuran.
- Health check en `/health`.

## CI/CD

### GitHub Actions
- Workflow: `.github/workflows/deploy.yml`.
- Autenticación recomendada: Workload Identity Federation (WIF/OIDC).
- Alternativa: secret `GCP_SA_KEY`.

### Cloud Build / Cloud Run
- Configuración principal: `cloudbuild-deploy.yaml`.
- Servicio Cloud Run definido en `service.yaml`.

## Despliegue

### Automático (recomendado)
- `push` a `main`/`master` dispara el workflow.

### Manual
```bash
gcloud builds submit --config=cloudbuild-deploy.yaml
```

## Operación
- Logs locales: `docker-compose logs -f app`
- Logs en producción: `gcloud run services logs read <servicio> --region=us-central1 --limit=50`
- Revisiones: `gcloud run revisions list --service <servicio> --region=us-central1`

## Rollback
```bash
gcloud run services update-traffic <servicio> \
  --to-revisions=<revision>=100 \
  --region=us-central1
```

## Referencias
- `LOCAL_SETUP.md`
- `DEPLOY_QUICK.md`
- `DEPLOYMENT_GUIDE.md`
- `TROUBLESHOOTING.md`
