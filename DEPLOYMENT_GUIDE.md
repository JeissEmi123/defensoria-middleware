# Guía de Despliegue en Producción

## Objetivo
Desplegar la API en Cloud Run usando GitHub Actions o Cloud Build. Incluye una alternativa self-hosted con Docker.

## Opción A: Cloud Run (recomendada)

### Requisitos
- Proyecto GCP con Cloud Run y Cloud Build habilitados.
- Autenticación desde GitHub Actions por WIF/OIDC o con `GCP_SA_KEY`.

### Flujo recomendado
1. Configura credenciales (ver `.github/README.md`).
2. Asegura variables de entorno en Cloud Run (o en el secret `CLOUD_RUN_ENV_VARS`).
3. Haz `push` a `main`/`master`.
4. Verifica el workflow en GitHub Actions.
5. Valida el servicio en Cloud Run.

### Variables de entorno mínimas
- `APP_ENV=production`
- `DEBUG=false`
- `DATABASE_URL`
- `SECRET_KEY`, `JWT_SECRET_KEY`, `JWT_REFRESH_SECRET_KEY`
- `ALLOWED_ORIGINS` (lista JSON)
- `ALLOWED_HOSTS` (lista JSON o string único)

Ejemplo:
```
ALLOWED_ORIGINS=["https://app.defensoria.gob.pe"]
ALLOWED_HOSTS=["app.defensoria.gob.pe","api.defensoria.gob.pe"]
```

### Verificación
```bash
gcloud run services describe <servicio> --region=us-central1
curl https://<tu-servicio>/health
```

## Opción B: Self-hosted (Docker)

### Requisitos
- Docker 20.10+
- Docker Compose 2.x
- PostgreSQL 15+ (local o administrado)

### Pasos
```bash
cp .env.example .env
# Edita .env con valores de producción

docker compose up -d --build

docker compose exec app alembic upgrade head
```

### Verificación
```bash
curl http://<host>:9000/health
```

## Rollback (Cloud Run)
```bash
gcloud run revisions list --service <servicio> --region=us-central1
gcloud run services update-traffic <servicio> \
  --to-revisions=<revision>=100 \
  --region=us-central1
```
