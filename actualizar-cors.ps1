# Script para actualizar CORS y redesplegar backend
# Ejecutar desde: PowerShell en c:\defensoria-middleware

Write-Host "🔄 Actualizando Backend con nueva configuración CORS..." -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "sat-defensoriapueblo"
$SERVICE_NAME = "defensoria-middleware"
$REGION = "us-central1"

# Paso 1: Build imagen Docker
Write-Host "📦 Construyendo imagen Docker..." -ForegroundColor Yellow
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al construir imagen Docker" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Imagen construida exitosamente" -ForegroundColor Green
Write-Host ""

# Paso 2: Push a Container Registry
Write-Host "☁️ Subiendo imagen a Google Container Registry..." -ForegroundColor Yellow
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al subir imagen" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Imagen subida exitosamente" -ForegroundColor Green
Write-Host ""

# Paso 3: Deploy a Cloud Run
Write-Host "🚀 Desplegando a Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest `
    --region $REGION `
    --platform managed

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al desplegar en Cloud Run" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Backend actualizado exitosamente" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URLs configuradas en CORS:" -ForegroundColor Cyan
Write-Host "   - https://defensoria-frontend-411798681660.us-central1.run.app" -ForegroundColor White
Write-Host "   - http://localhost:3000 (desarrollo)" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Prueba el login desde tu frontend:" -ForegroundColor Yellow
Write-Host "   URL: https://defensoria-frontend-411798681660.us-central1.run.app" -ForegroundColor White
Write-Host "   Usuario: admin" -ForegroundColor White
Write-Host "   Password: Admin123!" -ForegroundColor White
Write-Host ""
