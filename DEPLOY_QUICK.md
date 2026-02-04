# 🚀 Guía Rápida de Despliegue

## Opción 1: GitHub Actions (Recomendado)

### Configuración Inicial (Una sola vez)
```bash
# 1. Ejecutar script de configuración
./setup-github-actions.sh

# 2. Copiar el JSON que aparece en pantalla
# 3. Ir a GitHub → Settings → Secrets → New secret
# 4. Nombre: GCP_SA_KEY
# 5. Pegar el JSON copiado
# 6. Eliminar el archivo local
rm github-actions-key.json
```

### Desplegar
```bash
git add .
git commit -m "feat: descripción del cambio"
git push origin main
```

El despliegue se ejecutará automáticamente. Verifica en:
- GitHub → Actions → Deploy to Cloud Run

---

## Opción 2: Despliegue Manual (Actual)

```bash
# Desplegar directamente
gcloud builds submit --config=cloudbuild-deploy.yaml

# O usar el script
./deploy-rapido.sh
```

---

## URLs del Servicio

- **Producción:** https://defensoria-middleware-prod-jrwf7omlvq-uc.a.run.app
- **Health Check:** https://defensoria-middleware-prod-jrwf7omlvq-uc.a.run.app/health
- **Docs API:** https://defensoria-middleware-prod-jrwf7omlvq-uc.a.run.app/docs

---

## Verificar Despliegue

```bash
# Ver última revisión
gcloud run services describe defensoria-middleware-prod --region=us-central1

# Probar health check
curl https://defensoria-middleware-prod-jrwf7omlvq-uc.a.run.app/health

# Ver logs
gcloud run services logs read defensoria-middleware-prod --region=us-central1 --limit=50
```

---

## Rollback (Si algo sale mal)

```bash
# Listar revisiones
gcloud run revisions list --service=defensoria-middleware-prod --region=us-central1

# Hacer rollback
gcloud run services update-traffic defensoria-middleware-prod \
  --to-revisions=NOMBRE_REVISION_ANTERIOR=100 \
  --region=us-central1
```
