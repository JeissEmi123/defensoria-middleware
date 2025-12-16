# Script para verificar prerequisitos de GCP
Write-Host "=== Verificando Prerequisitos para GCP ===" -ForegroundColor Cyan

# 1. Verificar gcloud CLI
Write-Host "`n1. Verificando gcloud CLI..." -ForegroundColor Yellow
try {
    $gcloudVersion = gcloud version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ gcloud CLI instalado" -ForegroundColor Green
        gcloud version | Select-String "Google Cloud SDK"
    } else {
        Write-Host "   ✗ gcloud CLI NO instalado" -ForegroundColor Red
        Write-Host "   Instalar desde: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ✗ gcloud CLI NO instalado" -ForegroundColor Red
    Write-Host "   Instalar desde: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
}

# 2. Verificar autenticación
Write-Host "`n2. Verificando autenticación..." -ForegroundColor Yellow
try {
    $account = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
    if ($account) {
        Write-Host "   ✓ Autenticado como: $account" -ForegroundColor Green
    } else {
        Write-Host "   ✗ No autenticado" -ForegroundColor Red
        Write-Host "   Ejecutar: gcloud auth login" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ✗ No autenticado" -ForegroundColor Red
}

# 3. Verificar proyecto configurado
Write-Host "`n3. Verificando proyecto..." -ForegroundColor Yellow
try {
    $project = gcloud config get-value project 2>&1
    if ($project -and $project -ne "(unset)") {
        Write-Host "   ✓ Proyecto configurado: $project" -ForegroundColor Green
    } else {
        Write-Host "   ✗ No hay proyecto configurado" -ForegroundColor Red
        Write-Host "   Ejecutar: gcloud config set project TU_PROJECT_ID" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ✗ No hay proyecto configurado" -ForegroundColor Red
}

# 4. Verificar Docker
Write-Host "`n4. Verificando Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Docker instalado: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Docker NO instalado" -ForegroundColor Red
    }
} catch {
    Write-Host "   ✗ Docker NO instalado" -ForegroundColor Red
}

# 5. Verificar Dockerfile
Write-Host "`n5. Verificando Dockerfile..." -ForegroundColor Yellow
if (Test-Path "Dockerfile") {
    Write-Host "   ✓ Dockerfile existe" -ForegroundColor Green
} else {
    Write-Host "   ✗ Dockerfile NO encontrado" -ForegroundColor Red
}

# Resumen
Write-Host "`n=== Resumen ===" -ForegroundColor Cyan
Write-Host "Si todos los checks están en verde (✓), estás listo para desplegar." -ForegroundColor White
Write-Host "Si hay checks en rojo (✗), sigue las instrucciones para corregirlos." -ForegroundColor White
