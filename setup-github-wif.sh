#!/bin/bash
set -euo pipefail

usage() {
  cat <<'EOF'
Configura Workload Identity Federation (OIDC/WIF) para GitHub Actions + setea secrets en GitHub.

Requisitos:
  - gcloud autenticado con un usuario/SA con permisos IAM (crear pools/providers + set IAM policy)
  - gh autenticado (para setear secrets) si usas --gh

Uso:
  ./setup-github-wif.sh [--project-id ID] [--project-number N] [--repo OWNER/REPO] [--gh]

Opciones:
  --project-id         GCP project ID (default: sat-defensoriapueblo)
  --project-number     GCP project number (recomendado si no puedes hacer `gcloud projects describe`)
  --repo               GitHub repo owner/name (default: detecta desde gh o git remote)
  --pool-id            Workload Identity Pool ID (default: github-actions-pool)
  --provider-id        Provider ID (default: github)
  --service-account    Service Account name (default: github-actions)
  --branches           Ramas permitidas (default: master,main)
  --gh                 Setea secrets en GitHub (GCP_WORKLOAD_IDENTITY_PROVIDER y GCP_SERVICE_ACCOUNT)

Ejemplo:
  ./setup-github-wif.sh --gh --repo JeissEmi123/defensoria-middleware --project-number 411798681660
EOF
}

PROJECT_ID="sat-defensoriapueblo"
PROJECT_NUMBER=""
REPO=""
POOL_ID="github-actions-pool"
PROVIDER_ID="github"
SERVICE_ACCOUNT_NAME="github-actions"
BRANCHES="master,main"
SET_GH_SECRETS=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-id)
      PROJECT_ID="$2"
      shift 2
      ;;
    --project-number)
      PROJECT_NUMBER="$2"
      shift 2
      ;;
    --repo)
      REPO="$2"
      shift 2
      ;;
    --pool-id)
      POOL_ID="$2"
      shift 2
      ;;
    --provider-id)
      PROVIDER_ID="$2"
      shift 2
      ;;
    --service-account)
      SERVICE_ACCOUNT_NAME="$2"
      shift 2
      ;;
    --branches)
      BRANCHES="$2"
      shift 2
      ;;
    --gh)
      SET_GH_SECRETS=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Argumento no reconocido: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "${REPO}" ]]; then
  if command -v gh >/dev/null 2>&1; then
    REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || true)"
  fi
  if [[ -z "${REPO}" ]]; then
    REPO="$(git remote get-url origin 2>/dev/null | sed -E 's#^https://github.com/##; s#^git@github.com:##; s#\\.git$##' || true)"
  fi
fi

if [[ -z "${REPO}" ]]; then
  echo "❌ No pude detectar el repo. Pasa --repo OWNER/REPO." >&2
  exit 1
fi

if [[ -z "${PROJECT_NUMBER}" ]]; then
  PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)' 2>/dev/null || true)"
fi

if [[ -z "${PROJECT_NUMBER}" ]]; then
  echo "❌ No pude obtener el project number para ${PROJECT_ID}." >&2
  echo "   Solución: vuelve a intentar con --project-number (ej. 411798681660)." >&2
  exit 1
fi

SA_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Proyecto: ${PROJECT_ID} (${PROJECT_NUMBER})"
echo "Repo: ${REPO}"
echo "Pool: ${POOL_ID}"
echo "Provider: ${PROVIDER_ID}"
echo "Service Account: ${SA_EMAIL}"
echo "Ramas permitidas: ${BRANCHES}"
echo ""

gcloud config set project "${PROJECT_ID}" >/dev/null

if ! gcloud iam workload-identity-pools list \
  --location="global" \
  --project="${PROJECT_ID}" \
  --format="value(name)" >/dev/null 2>&1; then
  cat <<EOF >&2

❌ Permisos insuficientes en GCP para configurar WIF en el proyecto "${PROJECT_ID}".

Ejecuta este script con una cuenta (usuario o service account) que tenga, como mínimo:
  - roles/iam.workloadIdentityPoolAdmin
  - roles/iam.serviceAccountAdmin
  - roles/resourcemanager.projectIamAdmin (o Owner)

Luego reintenta:
  ./setup-github-wif.sh --gh --repo ${REPO} --project-number ${PROJECT_NUMBER}
EOF
  exit 1
fi

echo "1) Creando/validando Workload Identity Pool..."
if gcloud iam workload-identity-pools describe "${POOL_ID}" \
  --location="global" \
  --project="${PROJECT_ID}" >/dev/null 2>&1; then
  echo "   - Pool ya existe"
else
  gcloud iam workload-identity-pools create "${POOL_ID}" \
    --location="global" \
    --project="${PROJECT_ID}" \
    --display-name="GitHub Actions"
  echo "   - Pool creado"
fi

echo "2) Creando/validando Provider OIDC..."
BRANCH_CONDITION=""
IFS=',' read -r -a BRANCH_ARRAY <<< "${BRANCHES}"
for b in "${BRANCH_ARRAY[@]}"; do
  b_trimmed="$(echo "$b" | xargs)"
  if [[ -n "${b_trimmed}" ]]; then
    ref_cond="assertion.ref == 'refs/heads/${b_trimmed}'"
    if [[ -z "${BRANCH_CONDITION}" ]]; then
      BRANCH_CONDITION="${ref_cond}"
    else
      BRANCH_CONDITION="${BRANCH_CONDITION} || ${ref_cond}"
    fi
  fi
done

ATTRIBUTE_CONDITION="assertion.repository == '${REPO}'"
if [[ -n "${BRANCH_CONDITION}" ]]; then
  ATTRIBUTE_CONDITION="${ATTRIBUTE_CONDITION} && (${BRANCH_CONDITION})"
fi

if gcloud iam workload-identity-pools providers describe "${PROVIDER_ID}" \
  --location="global" \
  --workload-identity-pool="${POOL_ID}" \
  --project="${PROJECT_ID}" >/dev/null 2>&1; then
  echo "   - Provider ya existe"
else
  gcloud iam workload-identity-pools providers create-oidc "${PROVIDER_ID}" \
    --location="global" \
    --workload-identity-pool="${POOL_ID}" \
    --project="${PROJECT_ID}" \
    --display-name="GitHub OIDC" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
    --attribute-condition="${ATTRIBUTE_CONDITION}"
  echo "   - Provider creado"
fi

echo "3) Creando/validando Service Account..."
if gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
  echo "   - Service account ya existe"
else
  gcloud iam service-accounts create "${SERVICE_ACCOUNT_NAME}" \
    --project="${PROJECT_ID}" \
    --display-name="GitHub Actions (WIF)"
  echo "   - Service account creado"
fi

echo "4) Asignando roles necesarios al Service Account..."
for role in roles/run.admin roles/cloudbuild.builds.editor roles/iam.serviceAccountUser roles/storage.admin; do
  echo "   - $role"
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${role}" \
    --condition=None \
    --quiet >/dev/null 2>&1 || true
done

echo "5) Habilitando impersonación via Workload Identity..."
PRINCIPAL="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${REPO}"
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="${PRINCIPAL}" \
  --quiet >/dev/null 2>&1 || true
echo "   - Binding aplicado"

WIF_PROVIDER_RESOURCE="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"
echo ""
echo "✅ WIF listo."
echo "   Provider: ${WIF_PROVIDER_RESOURCE}"
echo "   Service Account: ${SA_EMAIL}"
echo ""

if [[ "${SET_GH_SECRETS}" = true ]]; then
  if ! command -v gh >/dev/null 2>&1; then
    echo "❌ gh no está instalado. Instálalo o setea los secrets manualmente." >&2
    exit 1
  fi
  echo "6) Seteando secrets en GitHub (${REPO})..."
  echo -n "${WIF_PROVIDER_RESOURCE}" | gh secret set GCP_WORKLOAD_IDENTITY_PROVIDER --repo "${REPO}"
  echo -n "${SA_EMAIL}" | gh secret set GCP_SERVICE_ACCOUNT --repo "${REPO}"
  echo "   - Secrets configurados: GCP_WORKLOAD_IDENTITY_PROVIDER, GCP_SERVICE_ACCOUNT"
fi

echo ""
echo "Siguiente paso:"
echo "  - Haz push a master/main o ejecuta el workflow manualmente en GitHub Actions."
