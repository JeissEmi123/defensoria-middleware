# Defensoria Middleware

API REST construida con FastAPI para la Defensoria del Pueblo. Incluye autenticacion, gestion de usuarios y endpoints operativos. Se ejecuta localmente con Docker y se despliega en Cloud Run mediante GitHub Actions y Cloud Build.

## Inicio rapido
```bash
./bootstrap.sh
./dev-up.sh
```

La API queda en `http://localhost:9000` y el health check en `http://localhost:9000/health`.

## Documentacion principal
- `DOCUMENTACION_TECNICA.md`: arquitectura, requisitos, ejecucion local, CI/CD, seguridad y rollback.
- `LOCAL_SETUP.md`: guia detallada para entorno local.
- `DEPLOY_QUICK.md`: flujo rapido de despliegue.
- `.github/README.md`: configuracion de CI/CD (GitHub Actions, secretos, WIF/OIDC).

## Arquitectura (resumen)
- FastAPI como framework principal.
- PostgreSQL como base de datos.
- Alembic para migraciones.
- Docker para entorno local.
- Cloud Run para produccion.

## Operacion (runbook basico)
- Health check: `GET /health`.
- Logs en local: `docker-compose logs -f app`.
- Logs en produccion: `gcloud run services logs read defensoria-middleware-prod --region=us-central1 --limit=50`.
- Rollback: ver `DOCUMENTACION_TECNICA.md`.

## Soporte
Revisa `TROUBLESHOOTING.md` para diagnostico y soluciones comunes.

## CI/CD (Produccion)
- Workflow: `.github/workflows/deploy.yml`.
- Se dispara con `push` a `master`/`main` o manualmente con `workflow_dispatch`.
- Auth recomendado (sin llaves): `./setup-github-wif.sh --gh --project-number 411798681660`.
- Auth alternativa: secret `GCP_SA_KEY` (ver `.github/README.md`).
