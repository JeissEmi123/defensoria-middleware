#!/bin/bash
"""
Script interactivo para configurar Gmail API paso a paso
"""

echo "🚀 CONFIGURADOR GMAIL API - DEFENSORÍA DEL PUEBLO"
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar que gcloud esté instalado
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud CLI no está instalado"
        echo "Instala con: curl https://sdk.cloud.google.com | bash"
        exit 1
    fi
    print_success "Google Cloud CLI encontrado"
}

# Verificar autenticación
check_auth() {
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_warning "No hay usuario autenticado"
        echo "🔐 Autenticándose en Google Cloud..."
        gcloud auth login
    else
        print_success "Usuario autenticado"
    fi
}

# Configurar proyecto
setup_project() {
    echo ""
    echo "📋 CONFIGURACIÓN DEL PROYECTO"
    echo "=============================="
    
    current_project=$(gcloud config get-value project 2>/dev/null)
    
    if [[ -z "$current_project" || "$current_project" == "(unset)" ]]; then
        echo "🔍 Listando proyectos disponibles..."
        gcloud projects list
        echo ""
        read -p "🤔 Ingresa el ID del proyecto a usar: " PROJECT_ID
        gcloud config set project $PROJECT_ID
    else
        print_info "Proyecto actual: $current_project"
        read -p "¿Usar este proyecto? (s/N): " use_current
        if [[ $use_current =~ ^[Ss]$ ]]; then
            PROJECT_ID=$current_project
        else
            gcloud projects list
            read -p "Ingresa el ID del nuevo proyecto: " PROJECT_ID
            gcloud config set project $PROJECT_ID
        fi
    fi
    
    print_success "Proyecto configurado: $PROJECT_ID"
}

# Habilitar APIs
enable_apis() {
    echo ""
    echo "🔧 HABILITANDO APIs NECESARIAS"
    echo "=============================="
    
    print_info "Habilitando Gmail API..."
    gcloud services enable gmail.googleapis.com
    
    print_info "Habilitando Cloud Resource Manager API..."
    gcloud services enable cloudresourcemanager.googleapis.com
    
    print_success "APIs habilitadas"
}

# Crear service account
create_service_account() {
    echo ""
    echo "🔑 CREANDO SERVICE ACCOUNT"
    echo "=========================="
    
    SA_NAME="defensoria-gmail"
    SA_DISPLAY_NAME="Defensoria Gmail Service"
    
    # Verificar si ya existe
    if gcloud iam service-accounts describe "${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" &>/dev/null; then
        print_info "Service Account ya existe: ${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    else
        print_info "Creando Service Account..."
        gcloud iam service-accounts create $SA_NAME \
            --display-name="$SA_DISPLAY_NAME" \
            --description="Service Account para envío de emails via Gmail API"
        print_success "Service Account creado"
    fi
    
    # Crear archivo de credenciales
    CREDENTIALS_FILE="$PWD/config/gmail-service-account.json"
    mkdir -p "$PWD/config"
    
    print_info "Generando archivo de credenciales..."
    gcloud iam service-accounts keys create "$CREDENTIALS_FILE" \
        --iam-account="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    
    print_success "Credenciales guardadas en: $CREDENTIALS_FILE"
    
    # Guardar información para la configuración
    SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
}

# Configurar .env
configure_env() {
    echo ""
    echo "📝 CONFIGURANDO VARIABLES DE ENTORNO"
    echo "===================================="
    
    # Obtener información del usuario
    read -p "📧 Email del administrador delegado (ej: admin@defensoria.gob.pe): " DELEGATED_USER
    read -p "📧 Email remitente (ej: noreply@defensoria.gob.pe): " EMAIL_FROM
    read -p "📧 Email del coordinador (ej: coordinador@defensoria.gob.pe): " COORDINADOR_EMAIL
    
    # Backup del .env actual
    if [[ -f .env ]]; then
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
        print_info "Backup del .env creado"
    fi
    
    # Actualizar variables en .env
    print_info "Actualizando variables de entorno..."
    
    # Eliminar líneas existentes
    if [[ -f .env ]]; then
        sed -i.bak '/^GMAIL_SERVICE_ACCOUNT_FILE=/d' .env
        sed -i.bak '/^GMAIL_DELEGATED_USER=/d' .env
        sed -i.bak '/^EMAIL_FROM=/d' .env
        sed -i.bak '/^COORDINADOR_EMAIL=/d' .env
    fi
    
    # Agregar nuevas configuraciones
    echo "" >> .env
    echo "# Gmail API Configuration - $(date)" >> .env
    echo "GMAIL_SERVICE_ACCOUNT_FILE=$CREDENTIALS_FILE" >> .env
    echo "GMAIL_DELEGATED_USER=$DELEGATED_USER" >> .env
    echo "EMAIL_FROM=$EMAIL_FROM" >> .env
    echo "COORDINADOR_EMAIL=$COORDINADOR_EMAIL" >> .env
    
    print_success "Variables de entorno configuradas"
}

# Mostrar configuración de Domain-wide Delegation
show_delegation_config() {
    echo ""
    echo "🔐 CONFIGURACIÓN DOMAIN-WIDE DELEGATION"
    echo "======================================="
    
    print_warning "PASO MANUAL REQUERIDO:"
    echo ""
    print_info "1. Ve a Google Admin Console: https://admin.google.com/"
    print_info "2. Navega a: Security > API Controls > Domain-wide Delegation"
    print_info "3. Clic en 'ADD NEW'"
    print_info "4. Ingresa los siguientes datos:"
    echo ""
    echo "   Client ID: $(gcloud iam service-accounts describe $SA_EMAIL --format='value(oauth2ClientId)')"
    echo "   OAuth Scopes: https://www.googleapis.com/auth/gmail.send"
    echo ""
    print_info "5. Clic en 'AUTHORIZE'"
    echo ""
    print_warning "⚠️  Sin este paso, el envío de emails NO funcionará"
}

# Ejecutar test
run_tests() {
    echo ""
    echo "🧪 EJECUTANDO TESTS DE VALIDACIÓN"
    echo "================================="
    
    print_info "Ejecutando diagnóstico básico..."
    python3 scripts/basic_gcp_check.py
    
    echo ""
    read -p "¿Ejecutar test completo de configuración? (s/N): " run_full_test
    if [[ $run_full_test =~ ^[Ss]$ ]]; then
        python3 scripts/validate_all.py
    fi
}

# Mostrar resumen final
show_summary() {
    echo ""
    echo "🎉 CONFIGURACIÓN COMPLETADA"
    echo "==========================="
    
    print_success "Service Account: $SA_EMAIL"
    print_success "Credenciales: $CREDENTIALS_FILE"
    print_success "Variables configuradas en .env"
    
    echo ""
    print_warning "PENDIENTES:"
    echo "1. Configurar Domain-wide Delegation en Google Admin Console"
    echo "2. Reiniciar la aplicación para cargar nuevas variables"
    echo "3. Probar envío de emails"
    
    echo ""
    print_info "Comandos útiles:"
    echo "  python3 scripts/basic_gcp_check.py        # Diagnóstico básico"
    echo "  python3 scripts/validate_all.py           # Test completo"
    echo "  docker-compose restart                    # Reiniciar aplicación"
    
    echo ""
    print_info "Documentación: docs/CONFIGURACION_EMAIL.md"
}

# Función principal
main() {
    echo "🚀 Iniciando configuración automática..."
    echo ""
    
    check_gcloud
    check_auth
    setup_project
    enable_apis
    create_service_account
    configure_env
    show_delegation_config
    run_tests
    show_summary
    
    echo ""
    print_success "¡Configuración completada!"
    print_info "Revisa los pasos manuales pendientes arriba"
}

# Ejecutar si es llamado directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi