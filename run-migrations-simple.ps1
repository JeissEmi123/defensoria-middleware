# ====================================
# Script de Migraciones Simplificado
# ====================================

param(
    [string]$ProjectId = "sat-defensoriapueblo",
    [string]$Region = "us-central1"
)

# Agregar gcloud al PATH
$env:PATH += ";C:\Users\jeiss\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"

$SERVICE_NAME = "defensoria-middleware"

Write-Host "`n=====================================" -ForegroundColor Green
Write-Host "Ejecutando Migraciones de BD" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Configurar proyecto
gcloud config set project $ProjectId

# Obtener URL del servicio
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $Region --format="value(status.url)"

if (-not $SERVICE_URL) {
    Write-Host "Error: No se pudo obtener la URL del servicio" -ForegroundColor Red
    exit 1
}

Write-Host "`nServicio: $SERVICE_URL" -ForegroundColor Cyan

# Ejecutar migraciones via Cloud Run Jobs
Write-Host "`nEjecutando migraciones..." -ForegroundColor Cyan

# Crear job temporal para migraciones
$JOB_NAME = "defensoria-migrations-$(Get-Date -Format 'yyyyMMddHHmmss')"

gcloud run jobs create $JOB_NAME `
    --image "$Region-docker.pkg.dev/$ProjectId/defensoria-repo/middleware:latest" `
    --region $Region `
    --set-env-vars "RUN_MIGRATIONS=true" `
    --set-secrets "SECRET_KEY=SECRET_KEY:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest,POSTGRES_PASSWORD=POSTGRES_PASSWORD:latest" `
    --command "python" `
    --args "-m,alembic,upgrade,head"

# Ejecutar job
Write-Host "Ejecutando job de migraciones..." -ForegroundColor Yellow
gcloud run jobs execute $JOB_NAME --region $Region --wait

# Eliminar job
Write-Host "Limpiando..." -ForegroundColor Cyan
gcloud run jobs delete $JOB_NAME --region $Region --quiet

Write-Host "`n=====================================" -ForegroundColor Green
Write-Host "MIGRACIONES COMPLETADAS" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "`nVerificar: curl $SERVICE_URL/health" -ForegroundColor Cyan
