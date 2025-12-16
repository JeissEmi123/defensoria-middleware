# ===============================================
# Script de Limpieza de Base de Datos (Docker Windows)
# ===============================================
# Limpia sesiones expiradas, eventos antiguos, y ejecuta VACUUM
# Uso: .\cleanup-docker-db.ps1

$ErrorActionPreference = "Stop"

# Configuración
$CONTAINER_NAME = "defensoria_db"
$DB_USER = "defensoria"
$DB_NAME = "defensoria_db"
$SESIONES_RETENTION_DAYS = 30
$AUDITORIA_RETENTION_DAYS = 90

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Limpieza Base de Datos - Defensoría" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que el contenedor está corriendo
$containerRunning = docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}"
if ($containerRunning -ne $CONTAINER_NAME) {
    Write-Host " Error: Contenedor $CONTAINER_NAME no está corriendo" -ForegroundColor Red
    exit 1
}

Write-Host " Contenedor $CONTAINER_NAME está corriendo" -ForegroundColor Green
Write-Host ""

# Función para ejecutar SQL
function Invoke-DockerSQL {
    param(
        [string]$Query,
        [string]$Description
    )
    
    Write-Host "$Description..." -ForegroundColor Yellow
    
    $result = docker exec $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c $Query 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        # Extraer número de filas afectadas
        if ($result -match "DELETE (\d+)") {
            $count = $matches[1]
            Write-Host "   $count fila(s) eliminadas" -ForegroundColor Green
        } else {
            Write-Host "   Completado" -ForegroundColor Green
        }
    } else {
        Write-Host "   Error: $result" -ForegroundColor Red
    }
}

# 1. Limpiar sesiones expiradas inválidas
Invoke-DockerSQL `
    "DELETE FROM sesiones WHERE valida = false AND fecha_expiracion < NOW() - INTERVAL '$SESIONES_RETENTION_DAYS days';" `
    "Limpiando sesiones inválidas (>$SESIONES_RETENTION_DAYS días)"

# 2. Marcar sesiones expiradas como inválidas
Write-Host "Marcando sesiones expiradas como inválidas..." -ForegroundColor Yellow
$updateQuery = @"
UPDATE sesiones 
SET valida = false, 
    fecha_invalidacion = NOW(), 
    razon_invalidacion = 'expirada_automaticamente' 
WHERE valida = true 
AND fecha_expiracion < NOW();
"@
docker exec $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c $updateQuery | Out-Null
Write-Host "   Completado" -ForegroundColor Green

# 3. Limpiar tokens de reset expirados
Invoke-DockerSQL `
    "UPDATE usuarios SET reset_token = NULL, reset_token_expira = NULL WHERE reset_token_expira < NOW() - INTERVAL '7 days';" `
    "Limpiando tokens de reset expirados (>7 días)"

# 4. Limpiar eventos de auditoría antiguos
Invoke-DockerSQL `
    "DELETE FROM eventos_auditoria WHERE fecha_evento < NOW() - INTERVAL '$AUDITORIA_RETENTION_DAYS days';" `
    "Limpiando eventos de auditoría (>$AUDITORIA_RETENTION_DAYS días)"

# 5. Obtener estadísticas antes de VACUUM
Write-Host ""
Write-Host "Obteniendo estadísticas de tablas..." -ForegroundColor Yellow
$statsQuery = @"
SELECT 
    schemaname || '.' || tablename as tabla,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as tamaño
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 5;
"@
$stats = docker exec $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -t -c $statsQuery
Write-Host $stats -ForegroundColor DarkGray

# 6. Ejecutar VACUUM ANALYZE
Write-Host ""
Write-Host "Ejecutando VACUUM ANALYZE..." -ForegroundColor Yellow
docker exec $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "VACUUM ANALYZE;" | Out-Null
Write-Host "   VACUUM completado" -ForegroundColor Green

# Resumen final
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Limpieza completada exitosamente" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Mostrar estadísticas de sesiones
Write-Host " Estadísticas de Sesiones:" -ForegroundColor White
$sesionesQuery = @"
SELECT 
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE valida = true) as activas,
    COUNT(*) FILTER (WHERE valida = false) as inactivas
FROM sesiones;
"@
$sesionesStats = docker exec $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -t -c $sesionesQuery
Write-Host $sesionesStats -ForegroundColor White

Write-Host ""
Write-Host " Estadísticas de Auditoría:" -ForegroundColor White
$auditoriaQuery = @"
SELECT 
    COUNT(*) as total_eventos,
    COUNT(*) FILTER (WHERE fecha_evento > NOW() - INTERVAL '7 days') as ultimos_7_dias,
    pg_size_pretty(pg_total_relation_size('eventos_auditoria')) as tamaño_tabla
FROM eventos_auditoria;
"@
$auditoriaStats = docker exec $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -t -c $auditoriaQuery
Write-Host $auditoriaStats -ForegroundColor White

Write-Host ""
exit 0
