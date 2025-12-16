# ====================================
# Script de Verificación Pre-Despliegue
# ====================================

param(
    [string]$ProjectId = ""
)

# Colores
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Warning { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "✗ $args" -ForegroundColor Red }
function Write-Info { Write-Host "ℹ $args" -ForegroundColor Cyan }

$errores = 0
$advertencias = 0

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Verificación Pre-Despliegue GCP" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# 1. Verificar gcloud instalado
Write-Info "`n[1/8] Verificando Google Cloud SDK..."
try {
    $version = gcloud version 2>&1 | Select-String "Google Cloud SDK" | Out-String
    Write-Success "gcloud CLI instalado"
    Write-Host "  $($version.Trim())" -ForegroundColor Gray
} catch {
    Write-Error "gcloud CLI no encontrado"
    Write-Warning "  Instalar desde: https://cloud.google.com/sdk/docs/install"
    $errores++
}

# 2. Verificar autenticación
Write-Info "`n[2/8] Verificando autenticación..."
try {
    $account = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
    if ($account) {
        Write-Success "Autenticado como: $account"
    } else {
        Write-Error "No hay cuenta activa"
        Write-Warning "  Ejecutar: gcloud auth login"
        $errores++
    }
} catch {
    Write-Error "Error verificando autenticación"
    $errores++
}

# 3. Verificar proyecto
Write-Info "`n[3/8] Verificando proyecto..."
if ([string]::IsNullOrEmpty($ProjectId)) {
    $ProjectId = gcloud config get-value project 2>&1
}

if ([string]::IsNullOrEmpty($ProjectId) -or $ProjectId -eq "(unset)") {
    Write-Error "No hay proyecto configurado"
    Write-Warning "  Ejecutar: gcloud config set project TU_PROJECT_ID"
    $errores++
} else {
    Write-Success "Proyecto configurado: $ProjectId"
    
    # Verificar que el proyecto existe
    $projectExists = gcloud projects describe $ProjectId 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Proyecto existe y es accesible"
    } else {
        Write-Error "No se puede acceder al proyecto"
        $errores++
    }
}

# 4. Verificar facturación
Write-Info "`n[4/8] Verificando facturación..."
if (-not [string]::IsNullOrEmpty($ProjectId) -and $ProjectId -ne "(unset)") {
    $billing = gcloud beta billing projects describe $ProjectId --format="value(billingEnabled)" 2>&1
    if ($billing -eq "True") {
        Write-Success "Facturación habilitada"
    } else {
        Write-Error "Facturación no habilitada"
        Write-Warning "  Habilitar en: https://console.cloud.google.com/billing"
        $errores++
    }
}

# 5. Verificar archivos necesarios
Write-Info "`n[5/8] Verificando archivos del proyecto..."
$archivosRequeridos = @(
    "Dockerfile",
    "requirements.txt",
    "app/main.py",
    "alembic.ini",
    "deploy.ps1",
    "run-migrations.ps1"
)

foreach ($archivo in $archivosRequeridos) {
    if (Test-Path $archivo) {
        Write-Success "$archivo existe"
    } else {
        Write-Error "$archivo no encontrado"
        $errores++
    }
}

# 6. Verificar Dockerfile
Write-Info "`n[6/8] Verificando Dockerfile..."
if (Test-Path "Dockerfile") {
    $dockerContent = Get-Content "Dockerfile" -Raw
    if ($dockerContent -match "FROM python") {
        Write-Success "Dockerfile válido"
    } else {
        Write-Warning "Dockerfile puede tener problemas"
        $advertencias++
    }
}

# 7. Verificar requirements.txt
Write-Info "`n[7/8] Verificando dependencias..."
if (Test-Path "requirements.txt") {
    $requirements = Get-Content "requirements.txt"
    $dependenciasClaves = @("fastapi", "sqlalchemy", "alembic", "psycopg2-binary")
    $faltantes = @()
    
    foreach ($dep in $dependenciasClaves) {
        if ($requirements -match $dep) {
            Write-Success "$dep encontrado"
        } else {
            Write-Warning "$dep no encontrado en requirements.txt"
            $faltantes += $dep
            $advertencias++
        }
    }
}

# 8. Verificar región configurada
Write-Info "`n[8/8] Verificando configuración regional..."
$region = gcloud config get-value compute/region 2>&1
if ([string]::IsNullOrEmpty($region) -or $region -eq "(unset)") {
    Write-Warning "Región no configurada (se usará us-central1 por defecto)"
    $advertencias++
} else {
    Write-Success "Región configurada: $region"
}

# Resumen
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Resumen de Verificación" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

if ($errores -eq 0 -and $advertencias -eq 0) {
    Write-Success "`n¡Todo listo para desplegar!"
    Write-Info "`nEjecutar: .\deploy.ps1 -ProjectId `"$ProjectId`""
    exit 0
} elseif ($errores -eq 0) {
    Write-Warning "`nHay $advertencias advertencia(s), pero puedes continuar"
    Write-Info "`nEjecutar: .\deploy.ps1 -ProjectId `"$ProjectId`""
    exit 0
} else {
    Write-Error "`nSe encontraron $errores error(es) y $advertencias advertencia(s)"
    Write-Warning "`nCorrige los errores antes de desplegar"
    exit 1
}
