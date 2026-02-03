#  Guía de Despliegue en Producción

## Defensoría del Pueblo - Middleware API

Esta guía proporciona instrucciones detalladas para desplegar el middleware de la Defensoría del Pueblo en un entorno de producción.

---

## Pre-requisitos

### Infraestructura Mínima
- **CPU**: 2 vCPUs mínimo, 4 vCPUs recomendado
- **RAM**: 4GB mínimo, 8GB recomendado
- **Almacenamiento**: 50GB SSD mínimo
- **Red**: Conexión estable a internet
- **OS**: Ubuntu 20.04 LTS o superior / CentOS 8 / RHEL 8

### Software Requerido
- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL 15+ (puede ser externo)
- Nginx (opcional, para proxy reverso)
- Certbot (para SSL/TLS)

---

##  Instalación Paso a Paso

### 1. Preparación del Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias básicas
sudo apt install -y curl wget git unzip

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reiniciar sesión para aplicar cambios de grupo
newgrp docker
```

### 2. Configuración del Proyecto

```bash
# Crear directorio de aplicación
sudo mkdir -p /opt/defensoria-middleware
sudo chown $USER:$USER /opt/defensoria-middleware
cd /opt/defensoria-middleware

# Clonar repositorio
git clone https://github.com/agata-dp/sds-dp.git .
cd apps/backend

# Crear archivo de configuración de producción
cp .env.example .env
```

### 3. Configuración de Variables de Entorno

Editar el archivo `.env` con las configuraciones de producción:

```bash
nano .env
```

**Configuración mínima requerida:**

```bash
# ============================================
# CONFIGURACIÓN DE PRODUCCIÓN
# ============================================

# Aplicación
APP_NAME=Defensoria Middleware
APP_VERSION=1.0.0
APP_ENV=production
DEBUG=False

# Seguridad (GENERAR NUEVAS CLAVES)
SECRET_KEY=GENERAR_CON_openssl_rand_hex_32
JWT_SECRET_KEY=GENERAR_CON_openssl_rand_hex_32
JWT_REFRESH_SECRET_KEY=GENERAR_CON_openssl_rand_hex_32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Base de Datos
DATABASE_URL=postgresql+asyncpg://defensoria_user:SECURE_PASSWORD@localhost:5432/defensoria_db
POSTGRES_USER=defensoria_user
POSTGRES_PASSWORD=SECURE_PASSWORD
POSTGRES_DB=defensoria_db
POSTGRES_PORT=5432
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_ECHO=False

# Seguridad Web
ALLOWED_ORIGINS=["https://defensoria.gob.pe","https://app.defensoria.gob.pe"]
ALLOWED_HOSTS=["defensoria.gob.pe","app.defensoria.gob.pe"]
ENABLE_SECURITY_HEADERS=True
ENABLE_HTTPS_REDIRECT=True
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=strict

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
AUTH_RATE_LIMIT_PER_MINUTE=5

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
ENABLE_AUDIT_LOG=True

# Email (Configurar según necesidades)
COORDINADOR_EMAIL=coordinador@defensoria.gob.pe
GMAIL_SERVICE_ACCOUNT_FILE=/opt/defensoria-middleware/config/service-account-key.json
GMAIL_DELEGATED_USER=coordinador@defensoria.gob.pe

# Usuario administrador por defecto
ADMIN_DEFAULT_PASSWORD=CAMBIAR_INMEDIATAMENTE
```

### 4. Generar Claves de Seguridad

```bash
# Generar claves seguras
echo "SECRET_KEY=$(openssl rand -hex 32)"
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
echo "JWT_REFRESH_SECRET_KEY=$(openssl rand -hex 32)"

# Reemplazar en el archivo .env con las claves generadas
```

### 5. Configuración de Base de Datos

#### Opción A: PostgreSQL en Docker (Recomendado para desarrollo)

```bash
# Usar docker-compose.yml incluido
docker-compose up -d db
```

#### Opción B: PostgreSQL Externo (Recomendado para producción)

```bash
# Conectar a PostgreSQL externo
sudo -u postgres psql

-- Crear usuario y base de datos
CREATE USER defensoria_user WITH PASSWORD 'SECURE_PASSWORD';
CREATE DATABASE defensoria_db OWNER defensoria_user;
GRANT ALL PRIVILEGES ON DATABASE defensoria_db TO defensoria_user;

-- Configurar permisos adicionales
\c defensoria_db
GRANT ALL ON SCHEMA public TO defensoria_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO defensoria_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO defensoria_user;

-- Crear esquema SDS
CREATE SCHEMA IF NOT EXISTS sds;
GRANT ALL ON SCHEMA sds TO defensoria_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sds TO defensoria_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA sds TO defensoria_user;

\q
```

### 6. Configuración de Archivos de Servicio

#### Crear archivo de configuración para Docker Compose en producción:

```bash
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    container_name: defensoria_middleware_prod
    restart: unless-stopped
    ports:
      - "9000:9000"
    env_file:
      - .env
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
    depends_on:
      - db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:15-alpine
    container_name: defensoria_db_prod
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
    driver: local
EOF
```

### 7. Configuración de Nginx (Proxy Reverso)

```bash
# Instalar Nginx
sudo apt install -y nginx

# Crear configuración del sitio
sudo tee /etc/nginx/sites-available/defensoria-api << 'EOF'
server {
    listen 80;
    server_name api.defensoria.gob.pe;
    
    # Redirigir HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.defensoria.gob.pe;
    
    # Configuración SSL
    ssl_certificate /etc/letsencrypt/live/api.defensoria.gob.pe/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.defensoria.gob.pe/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Headers de seguridad
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Configuración del proxy
    location / {
        proxy_pass http://127.0.0.1:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:9000/health;
        access_log off;
    }
}
EOF

# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/defensoria-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. Configuración de SSL/TLS con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d api.defensoria.gob.pe

# Configurar renovación automática
sudo crontab -e
# Agregar línea:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

---

##  Despliegue

### 1. Construir y Ejecutar Contenedores

```bash
# Construir imagen
docker-compose -f docker-compose.prod.yml build

# Iniciar servicios
docker-compose -f docker-compose.prod.yml up -d

# Verificar estado
docker-compose -f docker-compose.prod.yml ps
```

### 2. Ejecutar Migraciones de Base de Datos

```bash
# Ejecutar migraciones
docker-compose -f docker-compose.prod.yml exec app alembic upgrade head

# Verificar tablas creadas
docker-compose -f docker-compose.prod.yml exec db psql -U defensoria_user -d defensoria_db -c "\dt"
```

### 3. Crear Usuario Administrador

```bash
# Ejecutar script de inicialización
docker-compose -f docker-compose.prod.yml exec app python scripts/manage_users.py create-admin
```

### 4. Verificar Despliegue

```bash
# Verificar health check
curl https://api.defensoria.gob.pe/health

# Verificar documentación API
curl https://api.defensoria.gob.pe/docs

# Verificar logs
docker-compose -f docker-compose.prod.yml logs -f app
```

---

##  Configuración de Servicios del Sistema

### 1. Crear Servicio Systemd

```bash
sudo tee /etc/systemd/system/defensoria-middleware.service << 'EOF'
[Unit]
Description=Defensoria Middleware API
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/defensoria-middleware
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Habilitar servicio
sudo systemctl daemon-reload
sudo systemctl enable defensoria-middleware.service
sudo systemctl start defensoria-middleware.service
```

### 2. Configurar Logrotate

```bash
sudo tee /etc/logrotate.d/defensoria-middleware << 'EOF'
/opt/defensoria-middleware/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /opt/defensoria-middleware/docker-compose.prod.yml restart app
    endscript
}
EOF
```

---

##  Monitoreo y Mantenimiento

### 1. Scripts de Monitoreo

```bash
# Crear script de health check
cat > /opt/defensoria-middleware/scripts/health_check.sh << 'EOF'
#!/bin/bash

HEALTH_URL="https://api.defensoria.gob.pe/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "$(date): API is healthy"
    exit 0
else
    echo "$(date): API is unhealthy (HTTP $RESPONSE)"
    # Reiniciar servicio si es necesario
    systemctl restart defensoria-middleware.service
    exit 1
fi
EOF

chmod +x /opt/defensoria-middleware/scripts/health_check.sh

# Agregar a crontab para monitoreo cada 5 minutos
echo "*/5 * * * * /opt/defensoria-middleware/scripts/health_check.sh >> /var/log/defensoria-health.log 2>&1" | sudo crontab -
```

### 2. Backup Automático

```bash
# Crear script de backup
cat > /opt/defensoria-middleware/scripts/backup_prod.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/defensoria-middleware/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="defensoria_db"
DB_USER="defensoria_user"

# Crear backup de base de datos
docker-compose -f /opt/defensoria-middleware/docker-compose.prod.yml exec -T db pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/defensoria_db_$DATE.sql

# Comprimir backup
gzip $BACKUP_DIR/defensoria_db_$DATE.sql

# Eliminar backups antiguos (mantener últimos 30 días)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "$(date): Backup completed: defensoria_db_$DATE.sql.gz"
EOF

chmod +x /opt/defensoria-middleware/scripts/backup_prod.sh

# Programar backup diario a las 2:00 AM
echo "0 2 * * * /opt/defensoria-middleware/scripts/backup_prod.sh >> /var/log/defensoria-backup.log 2>&1" | sudo crontab -
```

---

##  Configuración de Seguridad Adicional

### 1. Firewall (UFW)

```bash
# Configurar firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### 2. Fail2Ban

```bash
# Instalar Fail2Ban
sudo apt install -y fail2ban

# Configurar para Nginx
sudo tee /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

sudo systemctl restart fail2ban
```

---

##  Lista de Verificación Post-Despliegue

###  Verificaciones Técnicas

- [ ] Contenedores ejecutándose correctamente
- [ ] Base de datos accesible y migraciones aplicadas
- [ ] Health check respondiendo 200 OK
- [ ] SSL/TLS configurado y funcionando
- [ ] Logs generándose correctamente
- [ ] Backup automático configurado
- [ ] Monitoreo activo

###  Verificaciones de Seguridad

- [ ] Claves de seguridad generadas y únicas
- [ ] CORS configurado para dominios específicos
- [ ] Headers de seguridad habilitados
- [ ] Rate limiting funcionando
- [ ] Firewall configurado
- [ ] Fail2Ban activo

###  Verificaciones Funcionales

- [ ] Autenticación funcionando
- [ ] Endpoints principales respondiendo
- [ ] Documentación API accesible
- [ ] Notificaciones email configuradas (si aplica)
- [ ] Usuario administrador creado

---

##  Solución de Problemas

### Problemas Comunes

1. **Error de conexión a base de datos**
   ```bash
   # Verificar estado de PostgreSQL
   docker-compose -f docker-compose.prod.yml logs db
   
   # Verificar conectividad
   docker-compose -f docker-compose.prod.yml exec app python -c "from app.database.session import engine; print('DB OK')"
   ```

2. **Error 500 en endpoints**
   ```bash
   # Revisar logs de aplicación
   docker-compose -f docker-compose.prod.yml logs app
   
   # Verificar migraciones
   docker-compose -f docker-compose.prod.yml exec app alembic current
   ```

3. **Problemas de SSL**
   ```bash
   # Verificar certificado
   sudo certbot certificates
   
   # Renovar si es necesario
   sudo certbot renew --dry-run
   ```

### Comandos Útiles

```bash
# Reiniciar servicios
sudo systemctl restart defensoria-middleware.service

# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f

# Acceder al contenedor
docker-compose -f docker-compose.prod.yml exec app bash

# Backup manual
docker-compose -f docker-compose.prod.yml exec db pg_dump -U defensoria_user defensoria_db > backup_manual.sql
```

---
