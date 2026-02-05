# Solución al Error de Despliegue en Cloud Run

## 🔴 Problema Identificado

El despliegue en Cloud Run estaba fallando con el error:
```
The user-provided container failed to start and listen on the port defined provided by the PORT=8080 environment variable
```

### Causa Raíz

El error era causado por **variables de entorno SMTP no definidas en el modelo de configuración** (`app/config.py`):
- `EMAIL_SERVICE`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_USE_TLS`

Estas variables estaban en el archivo `.env` local pero no estaban declaradas en la clase `Settings`, causando un error de validación de Pydantic que impedía que la aplicación iniciara.

## ✅ Solución Aplicada

### 1. Actualización de `app/config.py`

Se agregaron los campos faltantes a la clase `Settings`:

```python
# Email Service Configuration
email_service: Optional[str] = None
smtp_host: Optional[str] = None
smtp_port: Optional[int] = None
smtp_username: Optional[str] = None
smtp_password: Optional[str] = None
smtp_use_tls: Optional[bool] = None
```

También se agregó `extra = "ignore"` en la clase Config para ignorar campos no definidos:

```python
class Config:
    env_file = ".env"
    case_sensitive = False
    extra = "ignore"  # Ignorar campos extra no definidos
```

### 2. Actualización de `cloudbuild-prod.yaml`

Se removieron secretos hardcodeados del repositorio. El despliegue ya no versiona valores sensibles: configura variables en Cloud Run (recomendado) o vía CI/CD (GitHub Actions secret `CLOUD_RUN_ENV_VARS`).

Ejemplo (plantilla, **no** pegar secretos reales en el repo):
```text
APP_ENV=production
DATABASE_URL=postgresql+asyncpg://<POSTGRES_USER>:<POSTGRES_PASSWORD>@/defensoria_db?host=/cloudsql/<PROJECT_ID>:us-central1:defensoria-db
POSTGRES_USER=<POSTGRES_USER>
POSTGRES_PASSWORD=<POSTGRES_PASSWORD>
POSTGRES_DB=<POSTGRES_DB>
POSTGRES_PORT=5432
EMAIL_SERVICE=none
EMAIL_FROM=<EMAIL_FROM>
COORDINADOR_EMAIL=<COORDINADOR_EMAIL>
GCP_PROJECT_ID=sat-defensoriapueblo
GMAIL_USE_OAUTH=false
LOG_LEVEL=INFO
DEBUG=false
```

### 3. Creación de `.env.cloudrun`

Se creó un archivo de configuración específico para Cloud Run sin las variables SMTP problemáticas.

## 🚀 Cómo Desplegar Ahora

### Opción 1: Script Automático

```bash
./deploy-prod.sh
```

### Opción 2: Manual

```bash
# 1. Configurar proyecto
gcloud config set project sat-defensoriapueblo

# 2. Desplegar
gcloud builds submit --config=cloudbuild-prod.yaml
```

## 🔍 Verificación del Despliegue

### 1. Verificar que el servicio está corriendo

```bash
gcloud run services describe defensoria-middleware-prod \
  --region=us-central1 \
  --project=sat-defensoriapueblo
```

### 2. Verificar logs en tiempo real

```bash
gcloud run services logs read defensoria-middleware-prod \
  --region=us-central1 \
  --project=sat-defensoriapueblo \
  --limit=50
```

### 3. Probar el endpoint de salud

```bash
curl https://defensoria-middleware-prod-411798681660.us-central1.run.app/health
```

### 4. Probar el endpoint de inicialización

```bash
curl https://defensoria-middleware-prod-411798681660.us-central1.run.app/api/v2/senales/admin/inicializar-modelo-v2-completo
```

## 📊 Monitoreo Post-Despliegue

### Ver logs de la aplicación

```bash
# Logs en tiempo real
gcloud run services logs tail defensoria-middleware-prod \
  --region=us-central1 \
  --project=sat-defensoriapueblo

# Últimos 100 logs
gcloud run services logs read defensoria-middleware-prod \
  --region=us-central1 \
  --project=sat-defensoriapueblo \
  --limit=100
```

### Ver métricas en Cloud Console

https://console.cloud.google.com/run/detail/us-central1/defensoria-middleware-prod/metrics?project=sat-defensoriapueblo

## 🛠️ Troubleshooting

### Si el despliegue sigue fallando:

1. **Verificar que la imagen se construyó correctamente:**
   ```bash
   gcloud builds list --limit=1 --project=sat-defensoriapueblo
   ```

2. **Verificar logs del último build:**
   ```bash
   BUILD_ID=$(gcloud builds list --limit=1 --format="value(id)" --project=sat-defensoriapueblo)
   gcloud builds log $BUILD_ID --project=sat-defensoriapueblo
   ```

3. **Verificar que Cloud SQL está accesible:**
   ```bash
   gcloud sql instances describe defensoria-db --project=sat-defensoriapueblo
   ```

4. **Verificar permisos de la cuenta de servicio:**
   ```bash
   gcloud run services get-iam-policy defensoria-middleware-prod \
     --region=us-central1 \
     --project=sat-defensoriapueblo
   ```

### Si hay errores de base de datos:

1. Verificar que el usuario `app_user` existe y tiene permisos
2. Verificar que la instancia Cloud SQL está corriendo
3. Verificar que la conexión Cloud SQL está configurada correctamente

### Si hay errores 500 en endpoints:

1. Revisar logs de la aplicación
2. Verificar que las migraciones se ejecutaron
3. Verificar que los datos de prueba están cargados

## 📝 Notas Importantes

- **No incluir variables SMTP** en las variables de entorno de Cloud Run si no se van a usar
- **Usar `EMAIL_SERVICE=none`** si no se requiere envío de emails
- **Mantener `extra = "ignore"`** en la configuración de Pydantic para evitar errores con variables no definidas
- **Verificar siempre los logs** después de cada despliegue

## 🔗 URLs Importantes

- **Servicio en producción:** https://defensoria-middleware-prod-411798681660.us-central1.run.app
- **Health check:** https://defensoria-middleware-prod-411798681660.us-central1.run.app/health
- **API Docs:** https://defensoria-middleware-prod-411798681660.us-central1.run.app/docs
- **Cloud Console:** https://console.cloud.google.com/run?project=sat-defensoriapueblo

## ✅ Checklist de Despliegue

- [ ] Código actualizado en repositorio
- [ ] Variables de entorno configuradas correctamente
- [ ] Build exitoso en Cloud Build
- [ ] Servicio desplegado en Cloud Run
- [ ] Health check responde correctamente
- [ ] Endpoints principales funcionando
- [ ] Logs sin errores críticos
- [ ] Base de datos accesible
- [ ] Migraciones aplicadas
