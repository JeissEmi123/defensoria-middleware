#  Guía de Solución de Problemas

## Defensoría del Pueblo - Middleware API

Esta guía te ayudará a resolver los problemas más comunes que pueden surgir durante el desarrollo, despliegue y operación del middleware.

---

##  Diagnóstico Rápido

### Comandos de Verificación Básica

```bash
# Verificar estado de contenedores
docker-compose ps

# Verificar logs de la aplicación
docker-compose logs app

# Verificar health check
curl http://localhost:9000/health

# Verificar conectividad a base de datos
docker-compose exec app python -c "from app.database.session import engine; print('DB OK')"

# Verificar migraciones
docker-compose exec app alembic current
```

---

##  Problemas Comunes y Soluciones

### 1. Error de Conexión a Base de Datos

#### Síntomas:
- Error 500 en endpoints
- Mensaje: "could not connect to server"
- Logs: "connection refused"

#### Soluciones:

**Verificar estado de PostgreSQL:**
```bash
# Verificar contenedor de DB
docker-compose ps db

# Verificar logs de PostgreSQL
docker-compose logs db

# Reiniciar base de datos
docker-compose restart db
```

**Verificar configuración:**
```bash
# Verificar variables de entorno
grep DATABASE_URL .env

# Verificar conectividad desde el contenedor
docker-compose exec app ping db
```

**Solución completa:**
```bash
# 1. Parar servicios
docker-compose down

# 2. Limpiar volúmenes (¡CUIDADO! Esto borra datos)
docker-compose down -v

# 3. Reiniciar servicios
docker-compose up -d

# 4. Verificar logs
docker-compose logs -f
```

### 2. Error 500 en Endpoints de Entidades

#### Síntomas:
- Error: "column entidades.id_entidad does not exist"
- Endpoints `/api/v2/parametros/crud/entidades` fallan

#### Solución:
Este error ya está solucionado en el código actual. Si persiste:

```bash
# Verificar que el fix esté aplicado
grep -n "id_entidades" app/database/models_sds.py

# Debería mostrar:
# id_entidad = Column('id_entidades', SmallInteger, primary_key=True)

# Si no está, aplicar el fix:
docker-compose exec app python scripts/verify_fix.py
```

### 3. Problemas de Migraciones

#### Síntomas:
- Error: "Target database is not up to date"
- Tablas faltantes
- Errores de esquema

#### Soluciones:

**Verificar estado actual:**
```bash
# Ver migración actual
docker-compose exec app alembic current

# Ver historial
docker-compose exec app alembic history

# Ver migraciones pendientes
docker-compose exec app alembic show head
```

**Aplicar migraciones:**
```bash
# Aplicar todas las migraciones
docker-compose exec app alembic upgrade head

# Aplicar migración específica
docker-compose exec app alembic upgrade <revision_id>
```

**Resetear migraciones (¡CUIDADO!):**
```bash
# Solo en desarrollo - borra todos los datos
docker-compose exec app python scripts/reset_sds_auto.py
```

### 4. Problemas de Autenticación

#### Síntomas:
- Error 401 "Invalid credentials"
- Tokens expirados
- Usuario no encontrado

#### Soluciones:

**Verificar usuario administrador:**
```bash
# Crear usuario admin si no existe
docker-compose exec app python scripts/manage_users.py create-admin

# Listar usuarios existentes
docker-compose exec app python scripts/manage_users.py list-users

# Cambiar contraseña
docker-compose exec app python scripts/manage_users.py change-password admin
```

**Verificar configuración JWT:**
```bash
# Verificar claves de seguridad
grep JWT_SECRET_KEY .env

# Regenerar claves si es necesario
openssl rand -hex 32
```

### 5. Problemas de CORS

#### Síntomas:
- Error en navegador: "CORS policy"
- Requests bloqueados desde frontend

#### Soluciones:

**Verificar configuración CORS:**
```bash
# Verificar dominios permitidos
grep ALLOWED_ORIGINS .env

# Para desarrollo local, usar:
ALLOWED_ORIGINS=["*"]

# Para producción, especificar dominios:
ALLOWED_ORIGINS=["https://defensoria.gob.pe"]
```

**Reiniciar aplicación:**
```bash
docker-compose restart app
```

### 6. Problemas de Performance

#### Síntomas:
- Respuestas lentas
- Timeouts
- Alta utilización de CPU/memoria

#### Soluciones:

**Verificar recursos:**
```bash
# Ver uso de recursos
docker stats

# Ver logs de performance
docker-compose logs app | grep "slow"
```

**Optimizar base de datos:**
```bash
# Ejecutar script de optimización
docker-compose exec app python scripts/optimize_db.py

# Verificar índices
docker-compose exec db psql -U defensoria_user -d defensoria_db -c "\di"
```

### 7. Problemas de Email

#### Síntomas:
- Notificaciones no se envían
- Error de autenticación SMTP
- Configuración Gmail fallida

#### Soluciones:

**Verificar configuración:**
```bash
# Test de configuración de email
docker-compose exec app python scripts/test_email_flow.py

# Verificar credenciales Gmail
ls -la config/service-account-key.json
```

**Configurar Gmail API:**
```bash
# Ejecutar configuración de Gmail
docker-compose exec app python scripts/setup_oauth_gmail.py
```

### 8. Problemas de Contenedores

#### Síntomas:
- Contenedores no inician
- Errores de build
- Puertos ocupados

#### Soluciones:

**Limpiar Docker:**
```bash
# Limpiar contenedores parados
docker container prune

# Limpiar imágenes no utilizadas
docker image prune

# Limpiar todo (¡CUIDADO!)
docker system prune -a
```

**Verificar puertos:**
```bash
# Ver puertos en uso
lsof -i :9000
netstat -tulpn | grep 9000

# Cambiar puerto si es necesario
APP_PORT=9001 docker-compose up -d
```

---

##  Herramientas de Diagnóstico

### Scripts de Validación

```bash
# Validación completa del sistema
docker-compose exec app python scripts/validate_all.py

# Verificar configuración
docker-compose exec app python scripts/validate_config.py

# Test de integración
docker-compose exec app python scripts/test_integration.py

# Verificar estado de la base de datos
docker-compose exec app python scripts/health_check_db.py
```

### Logs Detallados

```bash
# Logs de aplicación con timestamp
docker-compose logs -f --timestamps app

# Logs de base de datos
docker-compose logs -f db

# Logs del sistema (si usa systemd)
sudo journalctl -u defensoria-middleware.service -f
```

### Monitoreo en Tiempo Real

```bash
# Monitorear recursos
watch docker stats

# Monitorear logs de errores
docker-compose logs -f app | grep ERROR

# Monitorear conexiones de base de datos
docker-compose exec db psql -U defensoria_user -d defensoria_db -c "SELECT * FROM pg_stat_activity;"
```

---

## 🚑 Procedimientos de Emergencia

### Restaurar desde Backup

```bash
# 1. Parar aplicación
docker-compose stop app

# 2. Restaurar base de datos
gunzip -c backups/defensoria_db_YYYYMMDD_HHMMSS.sql.gz | \
docker-compose exec -T db psql -U defensoria_user -d defensoria_db

# 3. Reiniciar servicios
docker-compose up -d
```

### Rollback de Despliegue

```bash
# 1. Parar servicios actuales
docker-compose down

# 2. Restaurar código anterior
git checkout <previous_commit>

# 3. Restaurar base de datos
# (usar backup anterior)

# 4. Reiniciar servicios
docker-compose up -d
```

### Reinicio Completo

```bash
# 1. Backup de emergencia
docker-compose exec -T db pg_dump -U defensoria_user defensoria_db > emergency_backup.sql

# 2. Parar todo
docker-compose down

# 3. Limpiar volúmenes (¡CUIDADO!)
docker-compose down -v

# 4. Reiniciar desde cero
docker-compose up -d

# 5. Restaurar datos
cat emergency_backup.sql | docker-compose exec -T db psql -U defensoria_user -d defensoria_db
```

---

##  Monitoreo Preventivo

### Health Checks Automáticos

```bash
# Crear script de monitoreo
cat > scripts/monitor.sh << 'EOF'
#!/bin/bash
HEALTH_URL="http://localhost:9000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "$(date): API is healthy"
else
    echo "$(date): API is unhealthy (HTTP $RESPONSE)"
    # Enviar alerta o reiniciar servicio
    systemctl restart defensoria-middleware.service
fi
EOF

chmod +x scripts/monitor.sh

# Agregar a crontab (cada 5 minutos)
echo "*/5 * * * * /path/to/scripts/monitor.sh >> /var/log/defensoria-health.log 2>&1" | crontab -
```

### Alertas por Email

```bash
# Script de alerta
cat > scripts/alert.sh << 'EOF'
#!/bin/bash
if ! curl -f http://localhost:9000/health &>/dev/null; then
    echo "API is down at $(date)" | mail -s "Defensoria API Alert" admin@defensoria.gob.pe
fi
EOF
```

---

##  Escalación de Problemas

### Nivel 1: Auto-resolución
- Reiniciar servicios
- Verificar logs básicos
- Aplicar soluciones comunes

### Nivel 2: Intervención Manual
- Análisis detallado de logs
- Verificación de configuración
- Restauración desde backup

### Nivel 3: Soporte Técnico
- **Email**: soporte@defensoria.gob.pe
- **Teléfono**: +51-XXX-XXXX
- **Incluir**: Logs, configuración, pasos reproducir error

### Información para Soporte

Cuando contactes soporte, incluye:

```bash
# Información del sistema
uname -a
docker --version
docker-compose --version

# Estado de contenedores
docker-compose ps

# Logs recientes
docker-compose logs --tail=100 app

# Configuración (sin contraseñas)
grep -v PASSWORD .env | grep -v SECRET
```

---

##  Recursos Adicionales

### Documentación
- [README.md](README.md) - Información general
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Guía de despliegue
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Documentación de API

### Logs Importantes
- `logs/app.log` - Logs de aplicación
- `logs/deploy.log` - Logs de despliegue
- `logs/backup.log` - Logs de backup

### Scripts Útiles
- `scripts/validate_all.py` - Validación completa
- `scripts/health_check_db.py` - Verificar base de datos
- `scripts/manage_users.py` - Gestión de usuarios
- `scripts/backup_db.py` - Backup manual

---

**Documento**: Guía de Solución de Problemas  
**Versión**: 1.0.0  
**Fecha**: Enero 2024  
**Estado**:  Completa y Actualizada