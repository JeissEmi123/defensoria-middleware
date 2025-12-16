# Guía de PostgreSQL - Producción

##  Índice
1. [Docker Setup](#docker-setup)
2. [Configuración Óptima](#configuración-óptima)
3. [Migraciones con Alembic](#migraciones-con-alembic)
4. [Backups y Recuperación](#backups-y-recuperación)
5. [Optimización](#optimización)
6. [Monitoring y Health Checks](#monitoring-y-health-checks)
7. [Connection Pooling](#connection-pooling)
8. [Troubleshooting](#troubleshooting)

---

## Docker Setup

### Iniciar Servicios

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver logs solo de PostgreSQL
docker-compose logs -f db

# Ver estado de contenedores
docker-compose ps
```

### Administración de PostgreSQL en Docker

#### Conectar a PostgreSQL

```bash
# Desde el host (requiere psql instalado)
psql -h localhost -p 5432 -U defensoria -d defensoria_db

# Desde dentro del contenedor
docker exec -it defensoria_db psql -U defensoria -d defensoria_db

# Ejecutar query SQL directamente
docker exec -it defensoria_db psql -U defensoria -d defensoria_db -c "SELECT COUNT(*) FROM usuarios;"
```

#### Ejecutar Scripts SQL

```bash
# Desde archivo local
docker exec -i defensoria_db psql -U defensoria -d defensoria_db < script.sql

# Desde contenedor
docker cp script.sql defensoria_db:/tmp/script.sql
docker exec -it defensoria_db psql -U defensoria -d defensoria_db -f /tmp/script.sql
```

#### Backups con Docker

```bash
# Backup completo
docker exec defensoria_db pg_dump -U defensoria defensoria_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup comprimido
docker exec defensoria_db pg_dump -U defensoria defensoria_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup en formato custom (recomendado)
docker exec defensoria_db pg_dump -U defensoria -F c defensoria_db > backup.dump

# Restaurar desde backup
docker exec -i defensoria_db psql -U defensoria -d defensoria_db < backup.sql

# Restaurar desde .dump
docker exec -i defensoria_db pg_restore -U defensoria -d defensoria_db < backup.dump
```

### Comandos Útiles Docker

```bash
# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (¡CUIDADO! Elimina datos)
docker-compose down -v

# Reiniciar solo PostgreSQL
docker-compose restart db

# Ver logs en tiempo real
docker-compose logs -f db

# Ver uso de recursos
docker stats defensoria_db

# Inspeccionar contenedor
docker inspect defensoria_db

# Ejecutar comando bash en contenedor
docker exec -it defensoria_db bash
```

### Configuración Personalizada de PostgreSQL

Si necesitas ajustar configuración de PostgreSQL en Docker:

```bash
# 1. Crear archivo de configuración personalizado
# config/postgresql.conf

# 2. Modificar docker-compose.yml
services:
  db:
    image: postgres:15-alpine
    volumes:
      - ./config/postgresql.conf:/etc/postgresql/postgresql.conf
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
```

### Variables de Entorno

Actualizar credenciales en `.env`:

```bash
# .env
DB_PASSWORD=tu_password_seguro_aqui
POSTGRES_DB=defensoria_db
POSTGRES_USER=defensoria_user
```

Y en `docker-compose.yml`:

```yaml
environment:
  POSTGRES_DB: ${POSTGRES_DB:-defensoria_db}
  POSTGRES_USER: ${POSTGRES_USER:-defensoria}
  POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
```

### Migración de Datos

#### Migrar desde PostgreSQL local a Docker

```bash
# 1. Backup desde PostgreSQL local
pg_dump -U usuario_local -d bd_local > migracion.sql

# 2. Copiar al contenedor
docker cp migracion.sql defensoria_db:/tmp/

# 3. Restaurar en Docker
docker exec -it defensoria_db psql -U defensoria -d defensoria_db -f /tmp/migracion.sql
```

#### Migrar entre contenedores Docker

```bash
# Backup del contenedor origen
docker exec contenedor_origen pg_dump -U usuario bd_origen > datos.sql

# Restaurar en contenedor destino
docker exec -i defensoria_db psql -U defensoria -d defensoria_db < datos.sql
```

### Monitoreo y Logs

```bash
# Ver logs de PostgreSQL
docker-compose logs -f db

# Ver solo errores
docker-compose logs db | grep ERROR

# Logs desde fecha específica
docker-compose logs --since 2025-11-21T10:00:00 db

# Últimas 100 líneas
docker-compose logs --tail=100 db

# Ver conexiones activas
docker exec -it defensoria_db psql -U defensoria -d defensoria_db -c \
  "SELECT pid, usename, application_name, client_addr, state FROM pg_stat_activity;"
```

### Troubleshooting Docker

#### PostgreSQL no inicia

```bash
# Ver logs detallados
docker-compose logs db

# Problemas comunes:
# 1. Puerto 5432 ocupado
netstat -ano | findstr :5432  # Windows
lsof -i :5432                 # Linux/Mac

# 2. Permisos de volumen
docker-compose down -v
docker-compose up -d

# 3. Corrupción de datos
docker-compose down
docker volume rm defensoria-middleware_postgres_data
docker-compose up -d
```

#### Conexión rechazada desde la aplicación

```bash
# 1. Verificar que PostgreSQL esté listo
docker-compose ps

# 2. Verificar network
docker network inspect defensoria-middleware_default

# 3. Verificar DATABASE_URL
# Debe ser: postgresql://usuario:password@db:5432/defensoria_db
# NO usar 'localhost' dentro de Docker
```

#### Lentitud de PostgreSQL en Docker

```bash
# 1. Aumentar recursos de Docker Desktop
# Settings > Resources > Memory (mínimo 4GB)

# 2. Verificar uso de recursos
docker stats defensoria_db

# 3. Optimizar configuración
# Ver sección "Configuración Óptima" abajo
```

### Scripts de Utilidad para Docker

#### Script de Backup Automático (PowerShell)

```powershell
# backup-docker-db.ps1
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "backups/backup_$timestamp.sql.gz"

Write-Host "Creando backup en $backupFile..."
docker exec defensoria_db pg_dump -U defensoria defensoria_db | gzip > $backupFile

if ($LASTEXITCODE -eq 0) {
    Write-Host " Backup completado"
} else {
    Write-Host " Error en backup"
    exit 1
}
```

#### Script de Limpieza (PowerShell)

```powershell
# cleanup-docker-db.ps1
Write-Host "Limpiando sesiones expiradas..."
docker exec defensoria_db psql -U defensoria -d defensoria_db -c `
  "DELETE FROM sesiones WHERE fecha_expiracion < NOW() - INTERVAL '30 days';"

Write-Host "Limpiando eventos de auditoría antiguos..."
docker exec defensoria_db psql -U defensoria -d defensoria_db -c `
  "DELETE FROM eventos_auditoria WHERE fecha_evento < NOW() - INTERVAL '90 days';"

Write-Host "Ejecutando VACUUM..."
docker exec defensoria_db psql -U defensoria -d defensoria_db -c "VACUUM ANALYZE;"

Write-Host " Limpieza completada"
```

### Inicialización Automática

Para ejecutar scripts al crear el contenedor por primera vez:

```bash
# 1. Crear directorio init-scripts/
mkdir init-scripts

# 2. Agregar scripts .sql o .sh
# init-scripts/01-extensions.sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

# 3. Docker ejecutará automáticamente al crear contenedor
```

---

## Configuración Óptima

### postgresql.conf Recomendado

```ini
# MEMORIA
shared_buffers = 256MB              # 25% de RAM total (máximo 8GB)
effective_cache_size = 768MB        # 75% de RAM total
maintenance_work_mem = 64MB         # Para VACUUM, CREATE INDEX
work_mem = 16MB                     # Por query, cuidado con el total

# WAL (Write-Ahead Logging)
wal_buffers = 16MB
min_wal_size = 1GB
max_wal_size = 4GB
checkpoint_completion_target = 0.9

# QUERY PLANNER
random_page_cost = 1.1              # Para SSD (default: 4.0)
effective_io_concurrency = 200      # Para SSD (default: 1)

# CONEXIONES
max_connections = 100               # Usar PgBouncer para más conexiones

# LOGGING
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000   # Log queries > 1s
log_line_prefix = '%m [%p] %u@%d '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on

# PERFORMANCE
shared_preload_libraries = 'pg_stat_statements'
```

### Habilitar pg_stat_statements

```sql
-- Como superusuario de PostgreSQL
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Ver queries más lentas
SELECT 
    calls,
    mean_exec_time,
    query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## Migraciones con Alembic

### Inicialización

```bash
# Ya está configurado, pero para referencia:
alembic init alembic
```

### Crear Migración

```bash
# Automática (detecta cambios en modelos)
alembic revision --autogenerate -m "Descripción del cambio"

# Manual
alembic revision -m "Descripción del cambio"
```

### Aplicar Migraciones

```bash
# Aplicar todas las pendientes
alembic upgrade head

# Aplicar una específica
alembic upgrade +1

# Ver estado actual
alembic current

# Ver historial
alembic history

# Rollback
alembic downgrade -1
```

### Migración Inicial

```bash
# Ya existe: alembic/versions/001_initial_rbac.py
# Para aplicarla:
alembic upgrade head
```

---

## Backups y Recuperación

### Backup Manual

```bash
# Backup completo comprimido
python scripts/backup_db.py

# O usar pg_dump directamente:
pg_dump -h localhost -U defensoria_user -d defensoria_db \
    -F c -f backup.dump

# Backup SQL plain text
pg_dump -h localhost -U defensoria_user -d defensoria_db \
    -F p -f backup.sql
```

### Backup Automático (Cron)

```bash
# Editar crontab
crontab -e

# Agregar: Backup diario a las 2 AM
0 2 * * * cd /path/to/defensoria-middleware && python scripts/backup_db.py --auto

# Backup cada 6 horas
0 */6 * * * cd /path/to/defensoria-middleware && python scripts/backup_db.py --auto
```

### Restauración

```bash
# Con script
python scripts/backup_db.py
# Seleccionar opción 2

# O con pg_restore
pg_restore -h localhost -U defensoria_user -d defensoria_db \
    --clean --if-exists backup.dump

# O con psql (para .sql)
psql -h localhost -U defensoria_user -d defensoria_db < backup.sql
```

### Backup a Cloud Storage (GCP)

```bash
# Configurar gsutil (una vez)
gcloud auth application-default login

# Backup y subir a GCS
python scripts/backup_db.py --auto
gsutil cp backups/backup_*.sql.gz gs://defensoria-backups/
```

---

## Optimización

### Ejecutar Optimización

```bash
# Script completo
python scripts/optimize_db.py

# Incluye:
# - Crear índices compuestos
# - ANALYZE en todas las tablas
# - Estadísticas de uso
# - Sugerencias de mejoras
```

### Índices Importantes

```sql
-- Índice compuesto para sesiones activas
CREATE INDEX CONCURRENTLY ix_sesiones_usuario_activa 
ON sesiones(usuario_id, activa, fecha_expiracion) 
WHERE activa = true AND revocada = false;

-- Índice para auditoría
CREATE INDEX CONCURRENTLY ix_eventos_auditoria_usuario_fecha 
ON eventos_auditoria(usuario_id, fecha_evento DESC);

-- Índice GIN para búsqueda en JSON
CREATE INDEX CONCURRENTLY ix_usuarios_metadatos_gin 
ON usuarios USING GIN (metadatos);
```

### VACUUM Regular

```bash
# VACUUM manual
psql -c "VACUUM ANALYZE;" defensoria_db

# VACUUM específico
psql -c "VACUUM ANALYZE sesiones;" defensoria_db
```

### Configurar Autovacuum

```sql
-- Ver configuración actual
SELECT name, setting FROM pg_settings WHERE name LIKE 'autovacuum%';

-- Ajustar para tabla específica
ALTER TABLE eventos_auditoria SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);
```

---

## Monitoring y Health Checks

### Health Check Manual

```bash
python scripts/health_check_db.py
```

### Health Check Automático

```bash
# Agregar a cron: cada 15 minutos
*/15 * * * * cd /path/to/defensoria-middleware && python scripts/health_check_db.py >> /var/log/db_health.log 2>&1
```

### Métricas Clave a Monitorear

1. **Cache Hit Ratio** (debe ser > 95%)
```sql
SELECT 
    ROUND(100.0 * sum(heap_blks_hit) / 
          NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0), 2) 
    AS cache_hit_ratio
FROM pg_statio_user_tables;
```

2. **Conexiones Activas**
```sql
SELECT state, COUNT(*) 
FROM pg_stat_activity 
WHERE datname = 'defensoria_db'
GROUP BY state;
```

3. **Queries Lentas**
```sql
SELECT 
    pid,
    now() - query_start as duration,
    query
FROM pg_stat_activity
WHERE state != 'idle'
AND query_start < now() - interval '5 seconds'
ORDER BY duration DESC;
```

4. **Tamaño de Tablas**
```sql
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

5. **Locks Activos**
```sql
SELECT 
    mode,
    COUNT(*)
FROM pg_locks
WHERE database = (SELECT oid FROM pg_database WHERE datname = 'defensoria_db')
GROUP BY mode;
```

### Integración con Prometheus

```yaml
# docker-compose.yml - Agregar postgres_exporter
postgres_exporter:
  image: prometheuscommunity/postgres-exporter
  environment:
    DATA_SOURCE_NAME: "postgresql://user:pass@postgres:5432/defensoria_db?sslmode=disable"
  ports:
    - "9187:9187"
```

---

## Connection Pooling

### PgBouncer

#### Instalación

```bash
# Ubuntu/Debian
sudo apt-get install pgbouncer

# Configuración ya incluida en:
# config/pgbouncer.ini
```

#### Configurar

```bash
# Copiar configuración
sudo cp config/pgbouncer.ini /etc/pgbouncer/pgbouncer.ini

# Crear userlist.txt
echo '"defensoria_user" "md5hash_de_password"' | sudo tee /etc/pgbouncer/userlist.txt

# Generar hash MD5:
# echo -n "passwordusername" | md5sum
# Resultado: md5<hash>
```

#### Iniciar

```bash
# Iniciar servicio
sudo systemctl start pgbouncer
sudo systemctl enable pgbouncer

# Ver logs
sudo tail -f /var/log/postgresql/pgbouncer.log

# Conectar a admin
psql -h 127.0.0.1 -p 6432 -U postgres pgbouncer
# Dentro de admin:
SHOW POOLS;
SHOW CLIENTS;
SHOW SERVERS;
```

#### Usar en la Aplicación

```bash
# .env - Cambiar puerto a PgBouncer
DATABASE_URL=postgresql+asyncpg://defensoria_user:password@localhost:6432/defensoria_db
```

### Configuración de SQLAlchemy

```python
# Ya configurado en app/database/session.py
# Opciones importantes:

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,              # Conexiones en pool
    max_overflow=10,           # Conexiones extra permitidas
    pool_timeout=30,           # Timeout esperando conexión
    pool_recycle=3600,         # Reciclar conexión cada hora
    pool_pre_ping=True,        # Verificar conexión antes de usar
    echo=False                 # No loggear SQL (performance)
)
```

---

## Troubleshooting

### Conexiones Agotadas

```sql
-- Ver conexiones por usuario
SELECT 
    usename,
    COUNT(*) as connections
FROM pg_stat_activity
GROUP BY usename;

-- Matar conexión idle
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < current_timestamp - interval '1 hour';
```

### Query Lenta Bloqueando

```sql
-- Identificar query bloqueante
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- Matar query bloqueante (cuidado!)
SELECT pg_cancel_backend(pid);  -- Cancelar suavemente
SELECT pg_terminate_backend(pid);  -- Forzar terminación
```

### Espacio en Disco Lleno

```bash
# Ver tablas más grandes
psql -c "SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;" defensoria_db

# Limpiar sesiones expiradas
psql -c "DELETE FROM sesiones WHERE fecha_expiracion < NOW() - INTERVAL '7 days';" defensoria_db

# Archivar auditoría antigua
psql -c "DELETE FROM eventos_auditoria WHERE fecha_evento < NOW() - INTERVAL '90 days';" defensoria_db

# VACUUM FULL (requiere downtime)
psql -c "VACUUM FULL eventos_auditoria;" defensoria_db
```

### Replicación Rota

```sql
-- Ver estado de replicación
SELECT * FROM pg_stat_replication;

-- Ver lag de replicación
SELECT 
    client_addr,
    state,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn)) as pending
FROM pg_stat_replication;
```

### Performance Degradado

```bash
# 1. Ejecutar ANALYZE
python scripts/optimize_db.py

# 2. Verificar cache hit ratio
python scripts/health_check_db.py

# 3. Revisar queries lentas
psql -c "SELECT mean_exec_time, calls, query FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;" defensoria_db

# 4. Verificar configuración
psql -c "SHOW ALL;" defensoria_db | grep -E "(shared_buffers|effective_cache_size|work_mem)"
```

---

## Checklist de Producción

### Antes de Deploy

- [ ] Variables de entorno configuradas (`DATABASE_URL`, etc.)
- [ ] Migraciones aplicadas (`alembic upgrade head`)
- [ ] Índices creados (`python scripts/optimize_db.py`)
- [ ] Usuario admin creado (`python scripts/init_db.py`)
- [ ] Backup inicial tomado
- [ ] Health check pasando
- [ ] PgBouncer configurado (opcional pero recomendado)
- [ ] Monitoring configurado
- [ ] Logs configurados

### Mantenimiento Regular

- [ ] **Diario**: Backup automático
- [ ] **Semanal**: Health check manual
- [ ] **Mensual**: Optimización (VACUUM, ANALYZE)
- [ ] **Trimestral**: Revisión de espacio y archivado de auditoría

---

## Comandos Rápidos

### Docker (Recomendado)

```powershell
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f db

# Backup (Windows)
.\scripts\backup-docker-db.ps1

# Limpieza (Windows)
.\scripts\cleanup-docker-db.ps1

# Conectar a BD
docker exec -it defensoria_db psql -U defensoria -d defensoria_db

# Migraciones (desde contenedor app)
docker exec -it defensoria_middleware alembic upgrade head

# Inicializar BD (desde contenedor app)
docker exec -it defensoria_middleware python scripts/init_db.py

# Health check (desde contenedor app)
docker exec -it defensoria_middleware python scripts/health_check_db.py

# Ver estadísticas
docker exec defensoria_db psql -U defensoria -d defensoria_db -c "SELECT * FROM pg_stat_activity;"

# Reiniciar PostgreSQL
docker-compose restart db

# Detener servicios
docker-compose down
```

### PostgreSQL Local (Sin Docker)

```bash
# Backup
python scripts/backup_db.py

# Optimización
python scripts/optimize_db.py

# Health check
python scripts/health_check_db.py

# Migraciones
alembic upgrade head

# Inicializar
python scripts/init_db.py

# Ver logs PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log  # Linux
type "C:\Program Files\PostgreSQL\15\data\log\*.log"  # Windows

# Conectar a BD
psql -h localhost -U defensoria_user -d defensoria_db
```

### Tareas Programadas (Windows Task Scheduler)

```powershell
# Crear tarea de backup diario (2 AM)
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\defensoria-middleware\scripts\backup-docker-db.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "Defensoria DB Backup" `
    -Action $action -Trigger $trigger -Description "Backup diario PostgreSQL"

# Crear tarea de limpieza semanal (domingos 3 AM)
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\defensoria-middleware\scripts\cleanup-docker-db.ps1"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3am
Register-ScheduledTask -TaskName "Defensoria DB Cleanup" `
    -Action $action -Trigger $trigger -Description "Limpieza semanal PostgreSQL"
```

### Troubleshooting Rápido (Docker)

```powershell
# Ver recursos del contenedor
docker stats defensoria_db

# Ver conexiones activas
docker exec defensoria_db psql -U defensoria -d defensoria_db -c `
    "SELECT COUNT(*) FROM pg_stat_activity;"

# Matar conexiones idle
docker exec defensoria_db psql -U defensoria -d defensoria_db -c `
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < NOW() - INTERVAL '1 hour';"

# Ver tamaño de tablas
docker exec defensoria_db psql -U defensoria -d defensoria_db -c `
    "SELECT tablename, pg_size_pretty(pg_total_relation_size('public.'||tablename)) FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size('public.'||tablename) DESC;"

# Reiniciar contenedor si hay problemas
docker-compose restart db
```

---

## Notas Importantes

- **Docker**: Esta guía asume PostgreSQL corriendo en Docker (recomendado para desarrollo y producción)
- **Windows**: Los scripts PowerShell (.ps1) están optimizados para Windows
- **Linux/Mac**: Adaptar comandos usando bash y cron en lugar de PowerShell y Task Scheduler
- **Producción**: Considerar usar servicios administrados (AWS RDS, Azure Database, GCP Cloud SQL)

---

**Última actualización**: 21 de noviembre de 2025  
**Versión**: PostgreSQL 15 en Docker
