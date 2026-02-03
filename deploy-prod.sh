#!/bin/bash
set -e

echo "🚀 Desplegando Defensoria Middleware a Cloud Run (Producción)"
echo "============================================================"

PROJECT_ID="sat-defensoriapueblo"
SERVICE_NAME="defensoria-middleware-prod"
REGION="us-central1"

# Verificar que estamos en el proyecto correcto
echo "📋 Verificando proyecto GCP..."
gcloud config set project $PROJECT_ID

# Trigger Cloud Build
echo "🔨 Iniciando Cloud Build..."
gcloud builds submit --config=cloudbuild-prod.yaml --project=$PROJECT_ID

echo "✅ Despliegue completado!"
echo "🌐 URL: https://${SERVICE_NAME}-411798681660.${REGION}.run.app"
