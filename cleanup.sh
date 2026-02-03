#!/bin/bash

# Script para limpiar archivos innecesarios del proyecto
# Defensoría del Pueblo - Middleware API

echo "🧹 LIMPIEZA DEL PROYECTO - Defensoría del Pueblo"
echo "================================================"

# Archivos y directorios a eliminar
FILES_TO_DELETE=(
    # Archivos de prueba y diagnóstico
    "test_*.py"
    "diagnose_*.py"
    "diagnostico_*.py"
    "diagnosticar_*.py"
    "verificar_*.py"
    "verify_*.py"
    "check_*.py"
    "populate_test_signals.py"
    
    # Archivos SQL de prueba y temporales
    "*.sql"
    "sds_model_v2.sql"
    "defensoria_sds.sql"
    "create_sds_tables.sql"
    "create_simple_tables.sql"
    
    # Archivos de configuración temporal
    ".env.backup"
    ".env.cloudrun"
    ".pgpass"
    
    # Archivos de logs temporales
    "*.log"
    "proxy.log"
    "proxy_prod.log"
    
    # Archivos de documentación temporal/obsoleta
    "DIAGNOSTICO_*.md"
    "SOLUCION_*.md"
    "MIGRACION_*.md"
    "PROPUESTA_*.md"
    "RESUMEN_OPTIMIZACION_*.md"
    "VERIFICACION_FIX_COMPLETA.md"
    "AGENTS.md"
    
    # Scripts de prueba y temporales
    "apply_gcp_changes.py"
    "fix_*.py"
    "fix_*.sql"
    "migration_*.sql"
    "gcp_*.sql"
    "*_gcp_*.sql"
    "connect_*.sh"
    "check_tables.sh"
    "test-*.sh"
    "run-tests-*.sh"
    "verify-*.sh"
    
    # Archivos de build y deploy temporales
    "cloudbuild*.yaml"
    "build-trigger-config.yaml"
    "deploy-backend.sh"
    
    # Directorios temporales
    "tmp/"
    "oauth_env/"
    "sds_env/"
    "__pycache__/"
    ".pytest_cache/"
    "backups/"
)

# Función para eliminar archivos
delete_files() {
    local pattern="$1"
    echo "🗑️  Eliminando: $pattern"
    
    if [[ "$pattern" == "*/" ]]; then
        # Es un directorio
        find . -type d -name "${pattern%/}" -exec rm -rf {} + 2>/dev/null || true
    else
        # Es un archivo
        find . -name "$pattern" -type f -delete 2>/dev/null || true
    fi
}

# Mostrar archivos que se van a eliminar
echo "📋 Archivos que se eliminarán:"
echo "=============================="

for pattern in "${FILES_TO_DELETE[@]}"; do
    if [[ "$pattern" == "*/" ]]; then
        find . -type d -name "${pattern%/}" 2>/dev/null | head -10
    else
        find . -name "$pattern" -type f 2>/dev/null | head -10
    fi
done

echo ""
read -p "¿Continuar con la eliminación? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Iniciando limpieza..."
    
    # Eliminar archivos
    for pattern in "${FILES_TO_DELETE[@]}"; do
        delete_files "$pattern"
    done
    
    # Limpiar directorios específicos
    echo "🗂️  Limpiando directorios específicos..."
    
    # Limpiar cache de Python
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # Limpiar archivos temporales de macOS
    find . -name ".DS_Store" -delete 2>/dev/null || true
    
    # Limpiar logs antiguos
    find . -name "*.log.*" -delete 2>/dev/null || true
    
    echo "✅ Limpieza completada!"
    echo ""
    echo "📊 Archivos restantes importantes:"
    echo "=================================="
    ls -la | grep -E "\.(py|md|yml|yaml|txt|json|conf|sh|ini)$" | head -20
    
else
    echo "❌ Limpieza cancelada"
fi