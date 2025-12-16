#  Guía Docker - Defensoría Middleware

Documentación completa para ejecutar el sistema de autenticación en Docker.

---

##  Requisitos Previos

- **Docker Desktop**: 4.x o superior
- **Docker Compose**: 2.x o superior
- **PowerShell**: 5.1 o superior (Windows)
- **RAM**: Mínimo 4GB disponible para Docker
- **Disco**: Mínimo 10GB libres

### Verificar Instalación

```powershell
docker --version
docker-compose --version
```

---

##  Inicio Rápido

### 1. Configurar Variables de Entorno

```powershell
# Copiar archivo de ejemplo
Copy-Item .env.example .env

# Editar .env y actualizar:
# - DB_PASSWORD (contraseña de PostgreSQL)
# - SECRET_KEY (para JWT)
# - CORS_ORIGINS (dominios permitidos)
```

### 2. Iniciar Servicios

```powershell
# Iniciar todos los contenedores
docker-compose up -d

# Ver logs
docker-compose logs -f

# Verificar estado
docker-compose ps
```

Deberías ver:

```
NAME                   STATUS       PORTS
defensoria_db          Up           0.0.0.0:5432->5432/tcp
defensoria_middleware  Up           0.0.0.0:8000->8000/tcp
```

### 3. Inicializar Base de Datos

```powershell
# Ejecutar migraciones
docker exec -it defensoria_middleware alembic upgrade head

# Crear usuario admin y roles
docker exec -it defensoria_middleware python scripts/init_db.py
```

### 4. Verificar Funcionamiento

```powershell
# Health check
curl http://localhost:8000/health

# Documentación API
Start-Process "http://localhost:8000/docs"
```

---

##  Servicios Incluidos

### Servicio: `db` (PostgreSQL)

- **Imagen**: `postgres:15-alpine`
- **Puerto**: `5432`
- **Usuario**: `defensoria` (configurable)
- **Base de datos**: `defensoria_db`
- **Volumen**: `postgres_data` (persistente)

### Servicio: `app` (FastAPI)

- **Build**: Dockerfile local
- **Puerto**: `8000`
- **Comando**: `sh run.sh`
- **Depende de**: `db`
- **Volúmenes**: Código montado para desarrollo

---

##  Comandos Útiles

### Administración de Contenedores

```powershell
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Reiniciar un servicio
docker-compose restart db
docker-compose restart app

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f db
docker-compose logs -f app

# Ver estado y recursos
docker-compose ps
docker stats

# Reconstruir imagen de la app
docker-compose build app
docker-compose up -d --build app
```

### Base de Datos

#### Conexión

```powershell
# Conectar con psql
docker exec -it defensoria_db psql -U defensoria -d defensoria_db

# Desde el host (requiere psql instalado)
psql -h localhost -p 5432 -U defensoria -d defensoria_db
```

#### Backups

```powershell
# Backup automático (usa script PowerShell)
.\scripts\backup-docker-db.ps1

# Backup manual
docker exec defensoria_db pg_dump -U defensoria defensoria_db > backup.sql

# Backup comprimido
docker exec defensoria_db pg_dump -U defensoria defensoria_db | gzip > backup.sql.gz

# Restaurar
docker exec -i defensoria_db psql -U defensoria -d defensoria_db < backup.sql
```

#### Limpieza

```powershell
# Limpieza automática (script PowerShell)
.\scripts\cleanup-docker-db.ps1

# Limpieza manual de sesiones expiradas
docker exec defensoria_db psql -U defensoria -d defensoria_db -c `
    "DELETE FROM sesiones WHERE fecha_expiracion < NOW() - INTERVAL '30 days';"

# VACUUM
docker exec defensoria_db psql -U defensoria -d defensoria_db -c "VACUUM ANALYZE;"
```

#### Consultas Útiles

```powershell
# Ver usuarios
docker exec defensoria_db psql -U defensoria -d defensoria_db -c "SELECT id, nombre_usuario, email, activo FROM usuarios;"

# Ver sesiones activas
docker exec defensoria_db psql -U defensoria -d defensoria_db -c "SELECT COUNT(*) FROM sesiones WHERE valida = true;"

# Ver conexiones activas
docker exec defensoria_db psql -U defensoria -d defensoria_db -c "SELECT * FROM pg_stat_activity;"
```

### Aplicación

```powershell
# Ver logs de la aplicación
docker-compose logs -f app

# Ejecutar migraciones
docker exec -it defensoria_middleware alembic upgrade head

# Crear migración nueva
docker exec -it defensoria_middleware alembic revision --autogenerate -m "descripcion"

# Inicializar BD
docker exec -it defensoria_middleware python scripts/init_db.py

# Health check
docker exec -it defensoria_middleware python scripts/health_check_db.py

# Shell dentro del contenedor
docker exec -it defensoria_middleware sh

# Reiniciar aplicación
docker-compose restart app
```

---

##  Desarrollo

### Hot Reload

El código está montado como volumen, los cambios se reflejan automáticamente:

```yaml
volumes:
  - .:/app  # Monta código actual
```

Para forzar rebuild:

```powershell
docker-compose down
docker-compose build app
docker-compose up -d
```

### Ejecutar Tests

```powershell
# Dentro del contenedor
docker exec -it defensoria_middleware pytest

# Con coverage
docker exec -it defensoria_middleware pytest --cov=app tests/
```

### Ver Variables de Entorno

```powershell
# Ver env de la aplicación
docker exec defensoria_middleware env | grep DATABASE

# Inspeccionar contenedor
docker inspect defensoria_middleware
```

---

##  Monitoreo

### Logs

```powershell
# Logs agregados
docker-compose logs -f

# Solo últimas 100 líneas
docker-compose logs --tail=100

# Desde fecha específica
docker-compose logs --since 2025-11-21T10:00:00

# Solo errores (PowerShell)
docker-compose logs | Select-String "ERROR"
```

### Recursos

```powershell
# Uso de CPU y memoria
docker stats

# Información detallada de un contenedor
docker inspect defensoria_db

# Ver volúmenes
docker volume ls
docker volume inspect defensoria-middleware_postgres_data
```

### Health Checks

```powershell
# PostgreSQL health
docker exec defensoria_db pg_isready -U defensoria

# API health
curl http://localhost:8000/health

# Script completo
docker exec defensoria_middleware python scripts/health_check_db.py
```

---

##  Producción

### Cambiar a Modo Producción

```powershell
# 1. Actualizar .env
DEBUG=false
ENVIRONMENT=production

# 2. Usar contraseñas seguras
DB_PASSWORD=<password-fuerte-aqui>
SECRET_KEY=<generar-con-openssl-rand-hex-32>

# 3. Configurar workers
# En docker-compose.yml
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 4. Rebuildar
docker-compose down
docker-compose up -d --build
```

### Backups Automáticos

```powershell
# Crear tarea programada de Windows
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\defensoria-middleware\scripts\backup-docker-db.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "Defensoria DB Backup" `
    -Action $action -Trigger $trigger
```

### Limpieza Automática

```powershell
# Tarea semanal de limpieza
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\defensoria-middleware\scripts\cleanup-docker-db.ps1"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3am
Register-ScheduledTask -TaskName "Defensoria DB Cleanup" `
    -Action $action -Trigger $trigger
```

---

##  Troubleshooting

### PostgreSQL no inicia

```powershell
# Ver logs detallados
docker-compose logs db

# Problema: Puerto 5432 ocupado
netstat -ano | findstr :5432
# Matar proceso o cambiar puerto en docker-compose.yml

# Problema: Corrupción de datos
docker-compose down -v  #  Elimina datos
docker-compose up -d
```

### Aplicación no conecta a BD

```powershell
# 1. Verificar que BD está lista
docker-compose ps

# 2. Verificar DATABASE_URL en .env
# DEBE SER: postgresql://defensoria:password@db:5432/defensoria_db
# NO usar 'localhost', usar 'db' (nombre del servicio)

# 3. Ver logs de la app
docker-compose logs app
```

### Lentitud

```powershell
# 1. Aumentar recursos de Docker Desktop
# Settings > Resources > Memory: 4GB mínimo

# 2. Ver uso de recursos
docker stats

# 3. Verificar configuración de PostgreSQL
docker exec defensoria_db psql -U defensoria -d defensoria_db -c "SHOW shared_buffers;"
```

### Reset Completo

```powershell
#  ELIMINA TODOS LOS DATOS
docker-compose down -v
docker-compose up -d
docker exec -it defensoria_middleware alembic upgrade head
docker exec -it defensoria_middleware python scripts/init_db.py
```

---

##  Recursos Adicionales

- **Documentación API**: http://localhost:8000/docs
- **Guía PostgreSQL**: [docs/POSTGRESQL_GUIDE.md](docs/POSTGRESQL_GUIDE.md)
- **Guía de Autenticación**: [docs/AUTH_COMPLETE_GUIDE.md](docs/AUTH_COMPLETE_GUIDE.md)
- **Docker Compose Docs**: https://docs.docker.com/compose/

---

##  Checklist de Deploy

### Desarrollo
- [ ] `.env` configurado con valores de desarrollo
- [ ] `docker-compose up -d` funcionando
- [ ] Migraciones aplicadas
- [ ] Usuario admin creado
- [ ] Health check pasando
- [ ] Logs sin errores

### Producción
- [ ] `.env` con contraseñas seguras
- [ ] `DEBUG=false` y `ENVIRONMENT=production`
- [ ] Workers configurados (4+)
- [ ] Backups automáticos configurados
- [ ] Limpieza automática configurada
- [ ] Monitoring configurado
- [ ] SSL/HTTPS configurado (nginx)
- [ ] Firewall configurado

---

**Última actualización**: 21 de noviembre de 2025  
**Versión Docker**: 24.x  
**Versión Docker Compose**: 2.x
