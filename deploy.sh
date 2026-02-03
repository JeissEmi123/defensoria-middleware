#!/bin/bash

# ============================================
# SCRIPT DE DESPLIEGUE AUTOMATIZADO
# Defensoría del Pueblo - Middleware API
# ============================================

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
PROJECT_NAME="defensoria-middleware"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deploy.log"

# Funciones de utilidad
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN} $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}  $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED} $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

# Verificar prerrequisitos
check_prerequisites() {
    log "Verificando prerrequisitos..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        error "Docker no está instalado"
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose no está instalado"
    fi
    
    # Verificar archivo de configuración
    if [ ! -f "$ENV_FILE" ]; then
        error "Archivo de configuración $ENV_FILE no encontrado"
    fi
    
    # Verificar que las claves de seguridad han sido cambiadas
    if grep -q "CAMBIAR" "$ENV_FILE"; then
        error "Hay configuraciones que deben ser cambiadas en $ENV_FILE"
    fi
    
    success "Prerrequisitos verificados"
}

# Crear directorios necesarios
create_directories() {
    log "Creando directorios necesarios..."
    
    mkdir -p logs
    mkdir -p backups
    mkdir -p config
    mkdir -p /opt/defensoria-data/{postgres,redis,prometheus,grafana}
    
    # Configurar permisos
    sudo chown -R $USER:$USER /opt/defensoria-data
    chmod -R 755 /opt/defensoria-data
    
    success "Directorios creados"
}

# Backup de la base de datos actual (si existe)
backup_database() {
    log "Creando backup de seguridad..."
    
    if docker ps | grep -q "defensoria_db"; then
        BACKUP_FILE="$BACKUP_DIR/pre_deploy_$(date +%Y%m%d_%H%M%S).sql"
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_FILE"
        gzip "$BACKUP_FILE"
        success "Backup creado: ${BACKUP_FILE}.gz"
    else
        warning "No hay base de datos existente para hacer backup"
    fi
}

# Construir imágenes
build_images() {
    log "Construyendo imágenes Docker..."
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    success "Imágenes construidas"
}

# Desplegar servicios
deploy_services() {
    log "Desplegando servicios..."
    
    # Copiar archivo de configuración
    cp "$ENV_FILE" .env
    
    # Iniciar servicios
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    success "Servicios desplegados"
}

# Esperar a que los servicios estén listos
wait_for_services() {
    log "Esperando a que los servicios estén listos..."
    
    # Esperar PostgreSQL
    log "Esperando PostgreSQL..."
    timeout=60
    while ! docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T db pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" &>/dev/null; do
        sleep 2
        timeout=$((timeout - 2))
        if [ $timeout -le 0 ]; then
            error "Timeout esperando PostgreSQL"
        fi
    done
    success "PostgreSQL listo"
    
    # Esperar aplicación
    log "Esperando aplicación..."
    timeout=120
    while ! curl -f http://localhost:9000/health &>/dev/null; do
        sleep 5
        timeout=$((timeout - 5))
        if [ $timeout -le 0 ]; then
            error "Timeout esperando aplicación"
        fi
    done
    success "Aplicación lista"
}

# Ejecutar migraciones
run_migrations() {
    log "Ejecutando migraciones de base de datos..."
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec app alembic upgrade head
    
    success "Migraciones ejecutadas"
}

# Crear usuario administrador
create_admin_user() {
    log "Verificando usuario administrador..."
    
    # Verificar si ya existe un usuario admin
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T app python -c "
from app.database.session import get_db
from app.database.models import Usuario
from sqlalchemy.orm import Session

db = next(get_db())
admin_exists = db.query(Usuario).filter(Usuario.username == 'admin').first()
exit(0 if admin_exists else 1)
" 2>/dev/null; then
        warning "Usuario administrador ya existe"
    else
        log "Creando usuario administrador..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" exec app python scripts/manage_users.py create-admin
        success "Usuario administrador creado"
    fi
}

# Verificar despliegue
verify_deployment() {
    log "Verificando despliegue..."
    
    # Verificar health check
    if curl -f http://localhost:9000/health &>/dev/null; then
        success "Health check OK"
    else
        error "Health check falló"
    fi
    
    # Verificar endpoints principales
    if curl -f http://localhost:9000/docs &>/dev/null; then
        success "Documentación API accesible"
    else
        warning "Documentación API no accesible"
    fi
    
    # Verificar logs
    if docker-compose -f "$DOCKER_COMPOSE_FILE" logs app | grep -q "Application startup complete"; then
        success "Aplicación iniciada correctamente"
    else
        warning "Verificar logs de la aplicación"
    fi
}

# Configurar servicios del sistema
setup_system_services() {
    log "Configurando servicios del sistema..."
    
    # Crear servicio systemd
    sudo tee /etc/systemd/system/defensoria-middleware.service > /dev/null << EOF
[Unit]
Description=Defensoria Middleware API
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$(pwd)
ExecStart=/usr/local/bin/docker-compose -f $DOCKER_COMPOSE_FILE up -d
ExecStop=/usr/local/bin/docker-compose -f $DOCKER_COMPOSE_FILE down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
    
    # Habilitar servicio
    sudo systemctl daemon-reload
    sudo systemctl enable defensoria-middleware.service
    
    success "Servicio systemd configurado"
}

# Configurar backup automático
setup_backup() {
    log "Configurando backup automático..."
    
    # Crear script de backup
    cat > scripts/backup_prod.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="defensoria_db"
DB_USER="defensoria_user"

# Crear backup
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/defensoria_db_$DATE.sql
gzip $BACKUP_DIR/defensoria_db_$DATE.sql

# Limpiar backups antiguos (mantener 30 días)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "$(date): Backup completado: defensoria_db_$DATE.sql.gz"
EOF
    
    chmod +x scripts/backup_prod.sh
    
    # Agregar a crontab
    (crontab -l 2>/dev/null; echo "0 2 * * * $(pwd)/scripts/backup_prod.sh >> $(pwd)/logs/backup.log 2>&1") | crontab -
    
    success "Backup automático configurado"
}

# Mostrar información post-despliegue
show_deployment_info() {
    echo ""
    echo "============================================"
    echo " DESPLIEGUE COMPLETADO EXITOSAMENTE"
    echo "==========================================="
    echo ""
    echo " Información del Despliegue:"
    echo "  • Aplicación: http://localhost:9000"
    echo "  • Health Check: http://localhost:9000/health"
    echo "  • Documentación: http://localhost:9000/docs"
    echo "  • Base de Datos: localhost:5432"
    echo ""
    echo " Comandos Útiles:"
    echo "  • Ver logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
    echo "  • Reiniciar: docker-compose -f $DOCKER_COMPOSE_FILE restart"
    echo "  • Parar: docker-compose -f $DOCKER_COMPOSE_FILE down"
    echo "  • Estado: docker-compose -f $DOCKER_COMPOSE_FILE ps"
    echo ""
    echo " Próximos Pasos:"
    echo "  1. Cambiar contraseña del usuario admin"
    echo "  2. Configurar SSL/TLS si es necesario"
    echo "  3. Configurar monitoreo"
    echo "  4. Verificar backups automáticos"
    echo ""
    echo "============================================"
}

# Función principal
main() {
    echo "============================================"
    echo " INICIANDO DESPLIEGUE DE PRODUCCIÓN"
    echo "============================================"
    echo ""
    
    # Verificar si se ejecuta como root
    if [ "$EUID" -eq 0 ]; then
        error "No ejecutar este script como root"
    fi
    
    # Crear archivo de log
    mkdir -p logs
    touch "$LOG_FILE"
    
    log "Iniciando despliegue de $PROJECT_NAME"
    
    # Ejecutar pasos del despliegue
    check_prerequisites
    create_directories
    backup_database
    build_images
    deploy_services
    wait_for_services
    run_migrations
    create_admin_user
    verify_deployment
    setup_system_services
    setup_backup
    
    success "Despliegue completado exitosamente"
    show_deployment_info
}

# Manejo de señales
trap 'error "Despliegue interrumpido"' INT TERM

# Verificar argumentos
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "backup")
        backup_database
        ;;
    "verify")
        verify_deployment
        ;;
    "logs")
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f
        ;;
    "status")
        docker-compose -f "$DOCKER_COMPOSE_FILE" ps
        ;;
    "stop")
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        ;;
    "restart")
        docker-compose -f "$DOCKER_COMPOSE_FILE" restart
        ;;
    "help")
        echo "Uso: $0 [comando]"
        echo ""
        echo "Comandos disponibles:"
        echo "  deploy   - Desplegar aplicación (por defecto)"
        echo "  backup   - Crear backup de base de datos"
        echo "  verify   - Verificar estado del despliegue"
        echo "  logs     - Ver logs en tiempo real"
        echo "  status   - Ver estado de contenedores"
        echo "  stop     - Parar todos los servicios"
        echo "  restart  - Reiniciar servicios"
        echo "  help     - Mostrar esta ayuda"
        ;;
    *)
        error "Comando desconocido: $1. Usar '$0 help' para ver comandos disponibles."
        ;;
esac