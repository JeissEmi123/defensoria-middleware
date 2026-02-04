# 🚨 SOLUCIÓN INMEDIATA - Error 500 en Producción

## Estado Actual
✅ **Código corregido localmente**  
❌ **Despliegue a producción fallando** (contenedor no inicia)

## Problema
El contenedor en Cloud Run no inicia por error de validación de Pydantic con variables de entorno.

## ✅ Solución Aplicada en Código

### 1. `app/config.py` - Variables agregadas ✅
```python
email_service: Optional[str] = None
smtp_host: Optional[str] = None  
smtp_port: Optional[int] = None
smtp_username: Optional[str] = None
smtp_password: Optional[str] = None
smtp_use_tls: Optional[bool] = None

class Config:
    extra = "ignore"  # ✅ Agregado
```

### 2. `app/api/senales_v2.py` - Serialización corregida ✅
```python
# Removido jsonable_encoder
# Ahora usa serialize_decimal del servicio
return resultado  # Ya viene serializado
```

### 3. `cloudbuild-prod.yaml` - Variables simplificadas ✅

## 🔧 PASOS PARA DESPLEGAR

### Opción 1: Despliegue Directo (Recomendado)

```bash
# 1. Asegurar que estás en el proyecto correcto
gcloud config set project sat-defensoriapueblo

# 2. Desplegar
gcloud builds submit \
  --config=cloudbuild-prod.yaml \
  --project=sat-defensoriapueblo \
  --substitutions=COMMIT_SHA=$(git rev-parse --short HEAD)
```

### Opción 2: Si sigue fallando - Despliegue Manual

```bash
# 1. Build de la imagen
docker build -t gcr.io/sat-defensoriapueblo/defensoria-middleware:latest .

# 2. Push a GCR
docker push gcr.io/sat-defensoriapueblo/defensoria-middleware:latest

# 3. Deploy directo a Cloud Run
gcloud run deploy defensoria-middleware-prod \
  --image gcr.io/sat-defensoriapueblo/defensoria-middleware:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="APP_ENV=production,DATABASE_URL=postgresql+asyncpg://app_user:AppUser2026!@/defensoria_db?host=/cloudsql/sat-defensoriapueblo:us-central1:defensoria-db,POSTGRES_USER=app_user,POSTGRES_PASSWORD=AppUser2026!,POSTGRES_DB=defensoria_db,POSTGRES_PORT=5432,EMAIL_SERVICE=none,EMAIL_FROM=jcamargom@agatadata.com,COORDINADOR_EMAIL=jcamargom@agatadata.com,GCP_PROJECT_ID=sat-defensoriapueblo,GMAIL_USE_OAUTH=false,LOG_LEVEL=INFO,DEBUG=false" \
  --add-cloudsql-instances=sat-defensoriapueblo:us-central1:defensoria-db \
  --min-instances=1 \
  --max-instances=10 \
  --cpu=1 \
  --memory=2Gi \
  --timeout=3600 \
  --concurrency=80
```

## 🔍 Verificar Logs de Cloud Run

```bash
# Ver logs en tiempo real
gcloud run services logs tail defensoria-middleware-prod \
  --region=us-central1 \
  --project=sat-defensoriapueblo

# Ver últimos 100 logs
gcloud run services logs read defensoria-middleware-prod \
  --region=us-central1 \
  --project=sat-defensoriapueblo \
  --limit=100
```

## 🧪 Probar Después del Despliegue

```bash
# 1. Health check
curl https://defensoria-middleware-prod-411798681660.us-central1.run.app/health

# 2. Probar el endpoint corregido
curl -X PATCH \
  "https://defensoria-middleware-prod-411798681660.us-central1.run.app/api/v2/senales/2001" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"id_categoria_senal":6,"descripcion_cambio":"pruebas","confirmo_revision":true}'
```

## ⚠️ Si el Contenedor No Inicia

El error más común es que Pydantic rechaza las variables de entorno. Verifica:

1. **Ver logs del contenedor:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=defensoria-middleware-prod" \
     --limit=50 \
     --project=sat-defensoriapueblo \
     --format=json
   ```

2. **Verificar que `extra="ignore"` está en config.py**

3. **Verificar que todas las variables SMTP están definidas en config.py**

## 📝 Cambios Realizados

| Archivo | Estado |
|---------|--------|
| `app/config.py` | ✅ Variables SMTP agregadas + `extra="ignore"` |
| `app/api/senales_v2.py` | ✅ Removido `jsonable_encoder` |
| `cloudbuild-prod.yaml` | ✅ Variables simplificadas |
| Git commit | ✅ f3ee8ad |

## 🎯 Resultado Esperado

Después del despliegue exitoso:
- ✅ Contenedor inicia correctamente
- ✅ Health check responde 200
- ✅ PATCH /api/v2/senales/{id} funciona sin error 500
- ✅ Los comentarios se guardan correctamente

---

**Próximo paso:** Ejecutar Opción 1 o Opción 2 de despliegue
