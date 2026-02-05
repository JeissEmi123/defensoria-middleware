# Documentacion Tecnica - Defensoria Middleware

## Metadatos
- Version: 1.0
- Fecha: 2026-02-04
- Responsable: Equipo de desarrollo

## Proposito y alcance
Este documento describe como descargar, ejecutar y operar localmente el middleware de la Defensoria. Incluye la descripcion del pipeline CI/CD y lineamientos de despliegue.

## Resumen del sistema
El proyecto es una API REST construida con FastAPI. Usa PostgreSQL como base de datos y Alembic para migraciones. En produccion se ejecuta en Cloud Run y se despliega con Cloud Build desde GitHub Actions.

## Repositorio
```bash
git clone https://github.com/JeissEmi123/defensoria-middleware.git
cd defensoria-middleware
```

## Requisitos
- Python 3.11+
- PostgreSQL 15+
- Git
- Docker y Docker Compose (opcional)
- Google Cloud SDK (solo para despliegue manual)

## Preparacion de equipo nuevo (sin herramientas)
1. Instalar Git y Docker.
2. Verificar con el script:
```bash
./bootstrap.sh
```
3. Si falta algo, el script sugiere comandos segun el sistema operativo.
4. Iniciar Docker Desktop (si aplica) antes de levantar la app.

## Arquitectura

### Componentes principales
- API FastAPI en `app/main.py` y routers en `app/api`.
- Modelos y capa de negocio en `app/`.
- Migraciones en `alembic/`.
- Contenedores en `Dockerfile` y `docker-compose.yml`.
- Pipeline en `.github/workflows/deploy.yml` y `cloudbuild-deploy.yaml`.

### Flujo de una solicitud
1. El cliente consume un endpoint HTTP.
2. FastAPI enruta la peticion al router correspondiente.
3. La capa de negocio valida y procesa la operacion.
4. Se consulta o actualiza PostgreSQL.
5. Se responde JSON al cliente.

## Ejecucion local

### Comando unico (equipo nuevo)
```bash
./dev-up.sh
```

Este comando levanta la base de datos y la API con Docker y deja el servicio listo en `http://localhost:9000`.

### Opcion A: Docker Compose
```bash
# Revisar y ajustar .env.docker si es necesario
docker-compose up -d --build
curl http://localhost:9000/health
```

Notas:
- La API queda en `http://localhost:9000`.
- Logs: `docker-compose logs -f app`.
- Detener: `docker-compose down`.

### Opcion B: Manual (sin Docker)
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
./run.sh
```

Requisitos adicionales:
- PostgreSQL local corriendo.
- `DATABASE_URL` en `.env` apuntando a la instancia local.

Verificacion:
```bash
curl http://localhost:9000/health
```

Documentacion API local:
- Swagger UI: `http://localhost:9000/docs`
- ReDoc: `http://localhost:9000/redoc`

## Configuracion

### Archivos de entorno
- `.env.example`: plantilla base.
- `.env.docker`: valores para Docker local.
- `.env.production`: referencia de produccion.

### Variables clave
- `DATABASE_URL`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `JWT_REFRESH_SECRET_KEY`
- `LOCAL_AUTH_ENABLED`
- `ALLOWED_ORIGINS`

## Migraciones
```bash
alembic upgrade head
```

Para crear una migracion:
```bash
alembic revision --autogenerate -m "descripcion"
```

## Pruebas
```bash
pytest
```

Pruebas puntuales:
```bash
python scripts/test_endpoints_sds.py
```

## CI/CD

### Pipeline GitHub Actions
Archivo: `.github/workflows/deploy.yml`

Triggers:
- `push` a la rama `master` o `main`.
- `workflow_dispatch` manual.

Secret requerido:
- `GCP_SA_KEY` (JSON de service account en GitHub Secrets) **o** Workload Identity Federation:
  - `GCP_WORKLOAD_IDENTITY_PROVIDER`
  - `GCP_SERVICE_ACCOUNT`

Secret opcional:
- `CLOUD_RUN_ENV_VARS` (lista de env vars para `gcloud run deploy --update-env-vars`, recomendado con delimitador custom: `^|^KEY=VAL|KEY2=VAL2`).

Configuracion del secret:
```bash
./setup-github-actions.sh
```

Configuracion WIF (recomendado, sin llaves):
```bash
./setup-github-wif.sh --gh --project-number 411798681660
```

Flujo del pipeline:
1. Checkout del codigo.
2. Autenticacion en Google Cloud.
3. Build de imagen con Cloud Build (`gcloud builds submit --tag ...`).
4. Deploy a Cloud Run con la imagen construida (`gcloud run deploy ...`).
5. Verificacion con reintentos (`curl /health`).

### Cloud Build
Archivo: `cloudbuild-deploy.yaml`

Acciones principales:
- Build de imagen Docker.
- Push a Container Registry.
- Deploy a Cloud Run `defensoria-middleware-prod` en `us-central1` (sin hardcodear secretos).

## Despliegue manual
```bash
gcloud builds submit --config=cloudbuild-deploy.yaml
```

O usar el script:
```bash
./deploy-rapido.sh
```

## Operacion y monitoreo (runbook basico)
- Health check: `GET /health`.
- Logs en local: `docker-compose logs -f app`.
- Logs en produccion: `gcloud run services logs read defensoria-middleware-prod --region=us-central1 --limit=50`.
- Ver ultima revision: `gcloud run services describe defensoria-middleware-prod --region=us-central1`.

## Rollback
```bash
gcloud run revisions list --service=defensoria-middleware-prod --region=us-central1
gcloud run services update-traffic defensoria-middleware-prod \
  --to-revisions=NOMBRE_REVISION_ANTERIOR=100 \
  --region=us-central1
```

## Seguridad y secretos
- No versionar credenciales en el repositorio.
- Usar GitHub Secrets para `GCP_SA_KEY`.
- Rotar secretos si se exponen o se comparten.
- Considerar Secret Manager para variables sensibles en produccion.

## Checklist de entrega
1. Codigo actualizado y con commit.
2. Migraciones revisadas y aplicadas en local.
3. Variables de entorno documentadas.
4. Pipeline CI/CD verificado.
5. Health check funcional en local y produccion.
6. URL de produccion confirmada.

## Referencias
- `LOCAL_SETUP.md`
- `DEPLOY_QUICK.md`
- `DEPLOYMENT_GUIDE.md`
- `TROUBLESHOOTING.md`
