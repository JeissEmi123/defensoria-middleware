#!/bin/bash

# Script para verificar y probar el deploy de producción

echo "🔍 Verificando configuración actual..."

# 1. Verificar triggers existentes
echo -e "\n📋 Triggers configurados:"
gcloud builds triggers list

# 2. Verificar servicios en Cloud Run
echo -e "\n🚀 Servicios en Cloud Run:"
gcloud run services list --region=us-central1

# 3. Verificar permisos del service account
echo -e "\n🔐 Permisos del Service Account:"
gcloud projects get-iam-policy sat-defensoriapueblo \
  --flatten="bindings[].members" \
  --filter="bindings.members:411798681660@cloudbuild.gserviceaccount.com" \
  --format="table(bindings.role)"

# 4. Comando para probar el build manualmente (opcional)
echo -e "\n🧪 Para probar el build manualmente:"
echo "gcloud builds submit --config cloudbuild-prod.yaml ."

# 5. Comandos para verificar después del deploy
echo -e "\n✅ Para verificar después del deploy:"
echo "gcloud builds list --limit=5"
echo "gcloud run services describe defensoria-middleware-prod --region=us-central1"
echo "curl https://defensoria-middleware-prod-[hash]-uc.a.run.app/health"

echo -e "\n🎯 Todo listo para el CI/CD!"