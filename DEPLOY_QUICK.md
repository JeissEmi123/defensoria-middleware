# Guía Rápida de Despliegue

Objetivo: publicar la API en Cloud Run sin perder tiempo en detalles. Para configuración completa, ver `DEPLOYMENT_GUIDE.md`.

## Opción 1: GitHub Actions (recomendada)

### Configuración inicial (una sola vez)
```bash
./setup-github-actions.sh
```

Alternativa sin llaves (WIF/OIDC):
```bash
./setup-github-wif.sh --gh --project-number <PROJECT_NUMBER>
```

### Desplegar
```bash
git add .
git commit -m "deploy: descripcion"
git push origin main
```

## Opción 2: Manual
```bash
gcloud builds submit --config=cloudbuild-deploy.yaml
```

## Verificación
```bash
gcloud run services describe <servicio> --region=us-central1
curl https://<tu-servicio>/health
```
