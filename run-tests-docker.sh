#!/bin/bash

# Script para ejecutar tests dentro del contenedor Docker
echo "=== Ejecutando tests en entorno Docker ==="

# Verificar que Docker esté disponible
if ! command -v docker &> /dev/null; then
    echo "Error: Docker no está instalado o no está en PATH"
    exit 1
fi

# Verificar que docker-compose esté disponible
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose no está instalado o no está en PATH"
    exit 1
fi

# Verificar que existe .env.docker
if [ ! -f ".env.docker" ]; then
    echo "Error: No existe el archivo .env.docker"
    echo "Por favor, crea el archivo .env.docker con las variables necesarias"
    exit 1
fi

echo "1. Levantando servicios con docker-compose..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "2. Esperando a que los servicios estén listos..."
sleep 10

# Verificar que el contenedor esté corriendo
if [ ! "$(docker ps -q -f name=defensoria_middleware)" ]; then
    echo "Error: El contenedor defensoria_middleware no está corriendo"
    echo "Logs del contenedor:"
    docker-compose logs app
    exit 1
fi

echo "3. Verificando conectividad del servicio..."
# Verificar que el servicio responda
max_retries=30
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    if docker exec defensoria_middleware python -c "import requests; requests.get('http://localhost:8000/docs', timeout=5)" > /dev/null 2>&1; then
        echo "✅ Servicio está respondiendo"
        break
    fi
    echo "Esperando que el servicio esté listo... ($((retry_count + 1))/$max_retries)"
    sleep 2
    retry_count=$((retry_count + 1))
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ Error: El servicio no responde después de $max_retries intentos"
    echo "Logs del contenedor:"
    docker-compose logs app
    exit 1
fi

echo "4. Ejecutando test MVP flow..."
docker exec defensoria_middleware python scripts/test_mvp_flow.py
test_mvp_exit=$?

echo ""
echo "5. Ejecutando test user flow..."
docker exec defensoria_middleware python scripts/test_user_flow.py
test_user_exit=$?

echo ""
echo "6. Ejecutando test de integración..."
docker exec defensoria_middleware python scripts/test_integration.py
test_integration_exit=$?

echo ""
echo "7. Ejecutando otros tests disponibles..."
# Ejecutar otros scripts de test si existen
test_others_exit=0
if docker exec defensoria_middleware ls scripts/test_*.py > /dev/null 2>&1; then
    for test_file in $(docker exec defensoria_middleware ls scripts/test_*.py 2>/dev/null | grep -v "test_mvp_flow.py\|test_user_flow.py\|test_integration.py"); do
        if [ ! -z "$test_file" ]; then
            echo "Ejecutando $test_file..."
            docker exec defensoria_middleware python "$test_file"
            if [ $? -ne 0 ]; then
                test_others_exit=1
            fi
            echo ""
        fi
    done
fi

echo "=== RESUMEN DE TESTS ==="
echo "MVP Flow: $([ $test_mvp_exit -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
echo "User Flow: $([ $test_user_exit -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"  
echo "Integration: $([ $test_integration_exit -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
echo "Otros tests: $([ $test_others_exit -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"

# Exit con código de error si algún test falló
overall_exit=$((test_mvp_exit + test_user_exit + test_integration_exit + test_others_exit))
if [ $overall_exit -ne 0 ]; then
    echo ""
    echo "❌ Algunos tests fallaron"
    exit 1
else
    echo ""
    echo "✅ Todos los tests pasaron exitosamente"
fi

echo "=== Tests completados ==="
echo ""
echo "Para ver logs de los servicios:"
echo "  docker-compose logs -f"
echo ""
echo "Para parar los servicios:"
echo "  docker-compose down"