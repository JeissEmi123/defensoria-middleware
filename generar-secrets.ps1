# ====================================
# Generador de Secrets para GCP
# ====================================

function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }

Write-Host "`n====================================" -ForegroundColor Cyan
Write-Host "Generador de Secrets" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

Write-Info "`nEste script generará secrets seguros para tu despliegue."
Write-Info "Guarda estos valores en un lugar seguro (ej: password manager)`n"

# Función para generar secret aleatorio
function Generate-Secret {
    param([int]$Length = 32)
    
    # Intentar usar openssl si está disponible
    try {
        $secret = openssl rand -hex $Length 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $secret.Trim()
        }
    } catch {}
    
    # Fallback: generar con PowerShell
    $bytes = New-Object byte[] $Length
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes)
    $rng.Dispose()
    return [System.BitConverter]::ToString($bytes).Replace("-", "").ToLower()
}

# Generar secrets
Write-Info "Generando secrets..."
Start-Sleep -Milliseconds 500

$secrets = @{
    "SECRET_KEY" = Generate-Secret 32
    "JWT_SECRET_KEY" = Generate-Secret 32
    "JWT_REFRESH_SECRET_KEY" = Generate-Secret 32
}

# Mostrar secrets
Write-Host "`n====================================" -ForegroundColor Green
Write-Host "SECRETS GENERADOS" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

foreach ($key in $secrets.Keys) {
    Write-Host "`n$key" -ForegroundColor Yellow
    Write-Host $secrets[$key] -ForegroundColor White
}

# Generar contraseñas sugeridas
Write-Host "`n====================================" -ForegroundColor Green
Write-Host "CONTRASENAS SUGERIDAS" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

$adminPass = Generate-Secret 16
$dbPass = Generate-Secret 16

Write-Host "`nADMIN_DEFAULT_PASSWORD (sugerida)" -ForegroundColor Yellow
Write-Host $adminPass -ForegroundColor White

Write-Host "`nPOSTGRES_PASSWORD (sugerida)" -ForegroundColor Yellow
Write-Host $dbPass -ForegroundColor White

# Guardar en archivo temporal
$outputFile = "secrets-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"
$output = @"
====================================
SECRETS GENERADOS - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
====================================

IMPORTANTE: Guarda estos valores en un lugar seguro y elimina este archivo después.

SECRET_KEY=$($secrets["SECRET_KEY"])

JWT_SECRET_KEY=$($secrets["JWT_SECRET_KEY"])

JWT_REFRESH_SECRET_KEY=$($secrets["JWT_REFRESH_SECRET_KEY"])

ADMIN_DEFAULT_PASSWORD=$adminPass

POSTGRES_PASSWORD=$dbPass

====================================
NOTAS:
====================================
1. Estos secrets se usarán durante el despliegue
2. El script deploy.ps1 te pedirá estos valores
3. También se almacenarán en GCP Secret Manager
4. ELIMINA ESTE ARCHIVO después de usarlo

====================================
PRÓXIMO PASO:
====================================
.\deploy.ps1 -ProjectId "TU_PROJECT_ID"

"@

$output | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "`n====================================" -ForegroundColor Cyan
Write-Success "Secrets guardados en: $outputFile"
Write-Warning "`nIMPORTANTE: Elimina este archivo despues de usarlo"
Write-Info "`nProximo paso: .\deploy.ps1 -ProjectId `"TU_PROJECT_ID`""
Write-Host "====================================" -ForegroundColor Cyan
