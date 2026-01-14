# ===============================================
# Script de Backup Automático para Docker (Windows)
# ===============================================
# Uso: .\backup-docker-db.ps1

$ErrorActionPreference = "Stop"

# Configuración
$CONTAINER_NAME = "defensoria_db"
$DB_USER = "defensoria"
$DB_NAME = "defensoria_db"
$BACKUP_DIR = "backups"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_FILE = "$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"
$RETENTION_DAYS = 30

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Backup PostgreSQL Docker - Defensoría" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que el directorio de backups existe
if (!(Test-Path -Path $BACKUP_DIR)) {
    Write-Host "Creando directorio $BACKUP_DIR..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
}

# Verificar que el contenedor está corriendo
$containerRunning = docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}"
if ($containerRunning -ne $CONTAINER_NAME) {
    Write-Host " Error: Contenedor $CONTAINER_NAME no está corriendo" -ForegroundColor Red
    exit 1
}

Write-Host " Contenedor $CONTAINER_NAME está corriendo" -ForegroundColor Green

# Crear backup
Write-Host ""
Write-Host "Creando backup en $BACKUP_FILE..." -ForegroundColor Yellow

docker exec $CONTAINER_NAME pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

if ($LASTEXITCODE -eq 0) {
    $fileSize = (Get-Item $BACKUP_FILE).Length / 1MB
    Write-Host " Backup completado exitosamente" -ForegroundColor Green
    Write-Host "  Archivo: $BACKUP_FILE" -ForegroundColor Green
    Write-Host "  Tamaño: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
} else {
    Write-Host " Error al crear backup" -ForegroundColor Red
    exit 1
}

# Limpiar backups antiguos
Write-Host ""
Write-Host "Limpiando backups antiguos (>$RETENTION_DAYS días)..." -ForegroundColor Yellow

$cutoffDate = (Get-Date).AddDays(-$RETENTION_DAYS)
$oldBackups = Get-ChildItem -Path $BACKUP_DIR -Filter "backup_*.sql.gz" | 
              Where-Object { $_.LastWriteTime -lt $cutoffDate }

if ($oldBackups) {
    foreach ($backup in $oldBackups) {
        Write-Host "  Eliminando: $($backup.Name)" -ForegroundColor DarkGray
        Remove-Item $backup.FullName
    }
    Write-Host " $($oldBackups.Count) backup(s) antiguos eliminados" -ForegroundColor Green
} else {
    Write-Host "  No hay backups antiguos para eliminar" -ForegroundColor DarkGray
}

# Resumen
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Backup completado" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total de backups: $((Get-ChildItem -Path $BACKUP_DIR -Filter 'backup_*.sql.gz').Count)" -ForegroundColor White

exit 0
