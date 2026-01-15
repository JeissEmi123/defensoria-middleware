#!/bin/bash

# Script para probar todos los endpoints de Categorías de Observación
# Uso: ./test_categorias_observacion.sh

BASE_URL="http://localhost:8000"

echo "🚀 Iniciando pruebas de Categorías de Observación"
echo "================================================="

# 1. Obtener token de autenticación
echo -e "\n🔐 1. Obteniendo token de autenticación..."
TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"nombre_usuario": "admin", "contrasena": "Admin123456!"}' | \
  jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Error: No se pudo obtener el token de autenticación"
    exit 1
fi

echo "✅ Token obtenido: ${TOKEN:0:20}..."

# 2. Listar todas las categorías
echo -e "\n📋 2. Listando todas las categorías..."
curl -s -X GET "$BASE_URL/api/v2/categorias-observacion" \
  -H "Authorization: Bearer $TOKEN" | jq

# 3. Obtener categoría por ID
echo -e "\n🔍 3. Obteniendo categoría por ID (ID=1)..."
curl -s -X GET "$BASE_URL/api/v2/categorias-observacion/1" \
  -H "Authorization: Bearer $TOKEN" | jq

# 4. Crear nueva categoría
echo -e "\n➕ 4. Creando nueva categoría..."
NUEVA_CATEGORIA=$(curl -s -X POST "$BASE_URL/api/v2/categorias-observacion" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_categoria_observacion": "PRUEBA_'$(date +%s)'",
    "nombre_categoria_observacion": "Categoría de Prueba Automática",
    "descripcion_categoria_observacion": "Creada por script de pruebas",
    "nivel": 1,
    "peso_categoria_observacion": 75.5
  }')

echo "$NUEVA_CATEGORIA" | jq

# Obtener ID de la nueva categoría
CATEGORIA_ID=$(echo "$NUEVA_CATEGORIA" | jq -r '.id_categoria_observacion')

if [ "$CATEGORIA_ID" != "null" ] && [ ! -z "$CATEGORIA_ID" ]; then
    echo "✅ Categoría creada con ID: $CATEGORIA_ID"
    
    # 5. Actualizar la categoría
    echo -e "\n📝 5. Actualizando categoría ID $CATEGORIA_ID..."
    curl -s -X PUT "$BASE_URL/api/v2/categorias-observacion/$CATEGORIA_ID" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "nombre_categoria_observacion": "Categoría de Prueba ACTUALIZADA",
        "descripcion_categoria_observacion": "Descripción actualizada por script",
        "peso_categoria_observacion": 85.0
      }' | jq
    
    # 6. Intentar eliminar la categoría
    echo -e "\n🗑️ 6. Intentando eliminar categoría ID $CATEGORIA_ID..."
    RESPONSE=$(curl -s -w "%{http_code}" -X DELETE "$BASE_URL/api/v2/categorias-observacion/$CATEGORIA_ID" \
      -H "Authorization: Bearer $TOKEN")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -c 4)
    
    if [ "$HTTP_CODE" == "204" ]; then
        echo "✅ Categoría eliminada exitosamente"
    else
        echo "⚠️ Error al eliminar (código $HTTP_CODE): Probablemente tiene dependencias en BD"
    fi
    
else
    echo "❌ No se pudo crear la categoría para pruebas"
fi

# 7. Probar validación de unicidad
echo -e "\n🔒 7. Probando validación de unicidad (esto debería fallar)..."
curl -s -X POST "$BASE_URL/api/v2/categorias-observacion" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_categoria_observacion": "ACOSO_DIGITAL",
    "nombre_categoria_observacion": "Debería fallar",
    "nivel": 1,
    "peso_categoria_observacion": 50.0
  }' | jq

# 8. Obtener árbol jerárquico
echo -e "\n🌳 8. Obteniendo estructura jerárquica..."
curl -s -X GET "$BASE_URL/api/v2/categorias-observacion/jerarquia/arbol" \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\n✅ Pruebas completadas!"
echo "================================================="