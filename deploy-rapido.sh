#!/bin/bash
set -e

echo " Despliegue Rápido - Defensoria Backend"
echo "=========================================="

PROJECT_ID="sat-defensoriapueblo"
SERVICE_NAME="defensoria-middleware-prod"
REGION="us-central1"

# Configurar proyecto
gcloud config set project $PROJECT_ID

# Desplegar
echo " Construyendo y desplegando..."    
gcloud builds submit --config=cloudbuild-deploy.yaml

# Obtener URL
echo ""
echo " Despliegue completado!"
URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo " URL: $URL"

# Verificar health
echo ""
echo " Verificando servicio..."
sleep 5
curl -s "$URL/health" | jq .

echo ""
echo "✅ Todo listo!"
