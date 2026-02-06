# Defensoria Middleware

Este repositorio contiene la API REST para la gestión de señales (SDS), parámetros y catálogos asociados. Incluye autenticación JWT, RBAC y recuperación de contraseña. El uso recomendado es local con Docker y despliegue en Cloud Run.

## Inicio rápido (local con Docker)
```bash
./bootstrap.sh
./dev-up.sh
```

La API queda en `http://localhost:9000` y el health check en `http://localhost:9000/health`.

## Documentación clave
- `DOCUMENTACION_TECNICA.md` (arquitectura, configuración, ejecución, CI/CD, operación)
- `LOCAL_SETUP.md` (instalación local para máquina limpia)
- `DOCUMENTACION_FUNCIONAL.md` (flujos funcionales y alcance)
- `API_DOCUMENTATION.md` (resumen de endpoints y uso de `/docs`)
- `DEPLOY_QUICK.md` (despliegue rápido)
- `DEPLOYMENT_GUIDE.md` (despliegue detallado)
- `TROUBLESHOOTING.md` (diagnóstico y resolución)
- `docs/` (configuración de email y credenciales)

## Documentación interactiva de API
- Swagger UI: `http://localhost:9000/docs`
- ReDoc: `http://localhost:9000/redoc`

## Arquitectura (muy breve)
- FastAPI + SQLAlchemy + Alembic
- PostgreSQL
- Docker para desarrollo local
- Cloud Run para producción

## Operación básica
- Health check: `GET /health`
- Logs locales: `docker-compose logs -f app`
- Logs en producción: `gcloud run services logs read <servicio> --region=us-central1 --limit=50`

## CI/CD
- Workflow: `.github/workflows/deploy.yml`
- Configuración de GitHub Actions: `.github/README.md`
