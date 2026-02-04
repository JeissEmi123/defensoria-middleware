#!/bin/bash
set -e

echo " Configurando GitHub Actions para CI/CD"
echo "=========================================="

PROJECT_ID="sat-defensoriapueblo"
SA_NAME="github-actions"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Crear service account
echo " Creando service account..."
if gcloud iam service-accounts describe $SA_EMAIL --project=$PROJECT_ID &>/dev/null; then
  echo "Service account ya existe"
else
  gcloud iam service-accounts create $SA_NAME \
    --display-name="GitHub Actions" \
    --project=$PROJECT_ID
  echo " Service account creado"
  sleep 5
fi

# Asignar roles
echo " Asignando permisos..."
for role in "roles/run.admin" "roles/cloudbuild.builds.editor" "roles/iam.serviceAccountUser" "roles/storage.admin"; do
  echo "  Asignando $role..."
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="$role" \
    --condition=None \
    --quiet 2>/dev/null || echo "  Ya tiene el rol"
done

# Crear clave
echo " Generando clave..."
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=$SA_EMAIL

echo ""
echo " Configuración completada!"
echo ""
echo " Próximos pasos:"
echo "1. Ve a GitHub → Settings → Secrets and variables → Actions"
echo "2. Crea un nuevo secret llamado: GCP_SA_KEY"
echo "3. Copia y pega el contenido de: github-actions-key.json"
echo ""
echo " Contenido del secret (cópialo ahora):"
echo "=========================================="
cat github-actions-key.json
echo ""
echo "=========================================="
echo ""
echo "  IMPORTANTE: Elimina el archivo después de copiarlo:"
echo "   rm github-actions-key.json"
