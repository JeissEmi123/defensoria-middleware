# ====================================
# Script de Despliegue Simplificado
# ====================================

param(
    [string]$ProjectId = "sat-defensoriapueblo",
    [string]$Region = "us-central1"
)

# Agregar gcloud al PATH
$env:PATH += ";C:\Users\jeiss\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"

# Variables
$SERVICE_NAME = "defensoria-middleware"
$DB_INSTANCE_NAME = "defensoria-db"
$DB_NAME = "defensoria_db"
$DB_USER = "app_user"
$REPO_NAME = "defensoria-repo"

Write-Host "`n=====================================" -ForegroundColor Green
Write-Host "Despliegue en GCP - $ProjectId" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Configurar proyecto
Write-Host "`n[1/7] Configurando proyecto..." -ForegroundColor Cyan
gcloud config set project $ProjectId

# Habilitar APIs
Write-Host "`n[2/7] Habilitando APIs..." -ForegroundColor Cyan
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Crear repositorio Artifact Registry
Write-Host "`n[3/7] Creando repositorio..." -ForegroundColor Cyan
$repoExists = gcloud artifacts repositories describe $REPO_NAME --location=$Region 2>&1
if ($LASTEXITCODE -ne 0) {
    gcloud artifacts repositories create $REPO_NAME `
        --repository-format=docker `
        --location=$Region `
        --description="Defensoria Middleware Repository"
    Write-Host "Repositorio creado" -ForegroundColor Green
} else {
    Write-Host "Repositorio ya existe" -ForegroundColor Green
}

# Verificar/Crear Cloud SQL
Write-Host "`n[4/7] Verificando Cloud SQL..." -ForegroundColor Cyan
$sqlExists = gcloud sql instances describe $DB_INSTANCE_NAME 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Cloud SQL no existe. Creando..." -ForegroundColor Yellow
    $rootPassword = Read-Host "Password para PostgreSQL root" -AsSecureString
    $rootPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($rootPassword))
    
    gcloud sql instances create $DB_INSTANCE_NAME `
        --database-version=POSTGRES_15 `
        --tier=db-f1-micro `
        --region=$Region `
        --root-password="$rootPasswordPlain" `
        --storage-type=SSD `
        --storage-size=10GB `
        --backup `
        --backup-start-time=03:00
    
    gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE_NAME
    
    $appPassword = Read-Host "Password para usuario app_user" -AsSecureString
    $appPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($appPassword))
    
    gcloud sql users create $DB_USER `
        --instance=$DB_INSTANCE_NAME `
        --password="$appPasswordPlain"
} else {
    Write-Host "Cloud SQL ya existe" -ForegroundColor Green
}

# Obtener connection name
$CONNECTION_NAME = gcloud sql instances describe $DB_INSTANCE_NAME --format="value(connectionName)"
Write-Host "Connection: $CONNECTION_NAME" -ForegroundColor Green

# Crear secrets
Write-Host "`n[5/7] Configurando secrets..." -ForegroundColor Cyan

# Leer secrets del archivo generado
$secretsFile = Get-ChildItem "secrets-*.txt" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($secretsFile) {
    Write-Host "Usando secrets de: $($secretsFile.Name)" -ForegroundColor Yellow
    $secretsContent = Get-Content $secretsFile.FullName -Raw
    
    # Extraer valores
    if ($secretsContent -match "SECRET_KEY=([a-f0-9]+)") { $SECRET_KEY = $matches[1] }
    if ($secretsContent -match "JWT_SECRET_KEY=([a-f0-9]+)") { $JWT_SECRET_KEY = $matches[1] }
    if ($secretsContent -match "JWT_REFRESH_SECRET_KEY=([a-f0-9]+)") { $JWT_REFRESH_SECRET_KEY = $matches[1] }
    if ($secretsContent -match "ADMIN_DEFAULT_PASSWORD=([a-f0-9]+)") { $ADMIN_PASSWORD = $matches[1] }
    if ($secretsContent -match "POSTGRES_PASSWORD=([a-f0-9]+)") { $POSTGRES_PASSWORD = $matches[1] }
    
    # Crear secrets en GCP
    $secrets = @{
        "SECRET_KEY" = $SECRET_KEY
        "JWT_SECRET_KEY" = $JWT_SECRET_KEY
        "JWT_REFRESH_SECRET_KEY" = $JWT_REFRESH_SECRET_KEY
        "ADMIN_DEFAULT_PASSWORD" = $ADMIN_PASSWORD
        "POSTGRES_PASSWORD" = $POSTGRES_PASSWORD
    }
    
    foreach ($key in $secrets.Keys) {
        $exists = gcloud secrets describe $key 2>&1
        if ($LASTEXITCODE -ne 0) {
            echo $secrets[$key] | gcloud secrets create $key --data-file=-
            Write-Host "Secret $key creado" -ForegroundColor Green
        } else {
            Write-Host "Secret $key ya existe" -ForegroundColor Green
        }
    }
} else {
    Write-Host "No se encontro archivo de secrets. Ejecuta: .\generar-secrets.ps1" -ForegroundColor Red
    exit 1
}

# Build imagen
Write-Host "`n[6/7] Construyendo imagen Docker..." -ForegroundColor Cyan
gcloud builds submit --tag "$Region-docker.pkg.dev/$ProjectId/$REPO_NAME/middleware:latest"

# Deploy a Cloud Run
Write-Host "`n[7/7] Desplegando en Cloud Run..." -ForegroundColor Cyan
$dbUrl = "postgresql+asyncpg://${DB_USER}:PLACEHOLDER@/${DB_NAME}?host=/cloudsql/${CONNECTION_NAME}"

gcloud run deploy $SERVICE_NAME `
    --image "$Region-docker.pkg.dev/$ProjectId/$REPO_NAME/middleware:latest" `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --add-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars "APP_NAME=Defensoria Middleware,APP_ENV=production,DEBUG=false,POSTGRES_USER=$DB_USER,POSTGRES_DB=$DB_NAME,POSTGRES_PORT=5432,GCP_PROJECT_ID=$ProjectId,DATABASE_URL=$dbUrl" `
    --set-secrets "SECRET_KEY=SECRET_KEY:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest,JWT_REFRESH_SECRET_KEY=JWT_REFRESH_SECRET_KEY:latest,ADMIN_DEFAULT_PASSWORD=ADMIN_DEFAULT_PASSWORD:latest,POSTGRES_PASSWORD=POSTGRES_PASSWORD:latest" `
    --memory 512Mi `
    --cpu 1 `
    --max-instances 10 `
    --min-instances 0 `
    --timeout 300

# Obtener URL
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $Region --format="value(status.url)"

Write-Host "`n=====================================" -ForegroundColor Green
Write-Host "DESPLIEGUE COMPLETADO" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host "`nProximos pasos:" -ForegroundColor Yellow
Write-Host "1. Ejecutar migraciones: .\run-migrations-simple.ps1" -ForegroundColor White
Write-Host "2. Verificar: curl $SERVICE_URL/health" -ForegroundColor White
Write-Host "3. Docs: $SERVICE_URL/docs" -ForegroundColor White
Write-Host "=====================================" -ForegroundColor Green
