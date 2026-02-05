# GitHub Actions CI/CD Pipeline

## Configuración Inicial

### 1. Crear Service Account en GCP (opción rápida)

```bash
# Crear service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions" \
  --project=sat-defensoriapueblo

# Asignar permisos necesarios
gcloud projects add-iam-policy-binding sat-defensoriapueblo \
  --member="serviceAccount:github-actions@sat-defensoriapueblo.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding sat-defensoriapueblo \
  --member="serviceAccount:github-actions@sat-defensoriapueblo.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding sat-defensoriapueblo \
  --member="serviceAccount:github-actions@sat-defensoriapueblo.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding sat-defensoriapueblo \
  --member="serviceAccount:github-actions@sat-defensoriapueblo.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Crear y descargar la clave
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@sat-defensoriapueblo.iam.gserviceaccount.com
```

### 2. Configurar Secret en GitHub

1. Ve a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions
3. Click en "New repository secret"
4. Nombre: `GCP_SA_KEY`
5. Valor: Pega el contenido completo del archivo `github-actions-key.json`
6. Click en "Add secret"

Alternativa (si usas GitHub CLI):
```bash
./setup-github-actions.sh --gh
```

### 2.1 (Opcional) Configurar variables de entorno de Cloud Run por Secret

Si quieres que el pipeline actualice variables de entorno en cada despliegue, crea el secret:
- Nombre: `CLOUD_RUN_ENV_VARS`
- Valor recomendado: lista con delimitador custom para soportar comas dentro de valores (ej. JSON):

```text
^|^APP_ENV=production|EMAIL_SERVICE=none|LOG_LEVEL=INFO|DEBUG=false|ALLOWED_ORIGINS=["*"]
```

Nota: si `CLOUD_RUN_ENV_VARS` no existe, el workflow **no cambia** variables de entorno (usa las que ya estén configuradas en el servicio).

### 3. (Recomendado) Workload Identity Federation (sin llaves)

El workflow soporta OIDC/WIF si defines estos secrets:
- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`

Esto evita usar `GCP_SA_KEY` (llaves de larga duración).

Script de configuración (GCP + secrets en GitHub):
```bash
./setup-github-wif.sh --gh --repo JeissEmi123/defensoria-middleware --project-number 411798681660
```

### 3. Activar el Pipeline

El pipeline se ejecutará automáticamente cuando:
- Hagas push a la rama `main` o `master`
- Ejecutes manualmente desde la pestaña "Actions" en GitHub

## Uso

### Despliegue Automático
```bash
git add .
git commit -m "Deploy: descripción de cambios"
git push origin main
```

### Despliegue Manual
1. Ve a la pestaña "Actions" en GitHub
2. Selecciona "Deploy to Cloud Run"
3. Click en "Run workflow"
4. Selecciona la rama y click en "Run workflow"

## Verificación

Después del despliegue, verifica:
-  Build exitoso en Cloud Build
-  Servicio actualizado en Cloud Run
-  Health check respondiendo correctamente

## Troubleshooting

### Error de permisos
```bash
# Verificar permisos del service account
gcloud projects get-iam-policy sat-defensoriapueblo \
  --flatten="bindings[].members" \
  --filter="bindings.members:github-actions@sat-defensoriapueblo.iam.gserviceaccount.com"
```

### Ver logs del workflow
1. Ve a la pestaña "Actions" en GitHub
2. Click en el workflow fallido
3. Revisa los logs de cada step

## Comandos Útiles

```bash
# Ver últimos despliegues
gcloud run revisions list --service=defensoria-middleware-prod --region=us-central1

# Ver logs del servicio
gcloud run services logs read defensoria-middleware-prod --region=us-central1

# Rollback a versión anterior
gcloud run services update-traffic defensoria-middleware-prod \
  --to-revisions=REVISION_NAME=100 \
  --region=us-central1
```
