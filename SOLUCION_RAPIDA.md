# 🚨 SOLUCIÓN RÁPIDA - Error de Despliegue en Cloud Run

## Problema
El despliegue en Cloud Run estaba fallando porque **el contenedor no iniciaba** debido a un error de validación de Pydantic causado por variables de entorno SMTP no definidas en `app/config.py`.

## Solución Aplicada (3 pasos)

### ✅ 1. Actualizado `app/config.py`
- Agregadas variables SMTP faltantes
- Agregado `extra = "ignore"` en Config

### ✅ 2. Actualizado `cloudbuild-prod.yaml`  
- Removidos secretos hardcodeados del repo
- El deploy no define variables sensibles (se gestionan en Cloud Run / Secrets)
- Removidas variables SMTP problemáticas (mantener `EMAIL_SERVICE=none` si aplica)

### ✅ 3. Creado `.env.cloudrun`
- Plantilla de configuración para Cloud Run **sin secretos**

## 🚀 Para Desplegar AHORA

```bash
# Opción 1: Script automático
./deploy-prod.sh

# Opción 2: Manual
gcloud builds submit --config=cloudbuild-prod.yaml --project=sat-defensoriapueblo
```

## 🔍 Verificar que Funciona

```bash
# 1. Health check
curl https://defensoria-middleware-prod-411798681660.us-central1.run.app/health

# 2. Ver logs
gcloud run services logs tail defensoria-middleware-prod --region=us-central1 --project=sat-defensoriapueblo

# 3. Verificar servicio
gcloud run services describe defensoria-middleware-prod --region=us-central1 --project=sat-defensoriapueblo
```

## 📋 Cambios Realizados

| Archivo | Cambio |
|---------|--------|
| `app/config.py` | ✅ Agregadas variables SMTP + `extra="ignore"` |
| `cloudbuild-prod.yaml` | ✅ Deploy sin secretos versionados |
| `.env.cloudrun` | ✅ Plantilla sin secretos |
| `deploy-prod.sh` | ✅ Script de despliegue automático |
| `SOLUCION_DEPLOY_CLOUDRUN.md` | ✅ Documentación completa |

## ⚠️ Importante

- **NO agregar variables SMTP** si no se van a usar
- **Usar `EMAIL_SERVICE=none`** para deshabilitar emails
- **Mantener `extra="ignore"`** en Pydantic Config
- **Verificar logs** después de cada despliegue

## 🎯 Resultado Esperado

Después del despliegue, deberías poder acceder a:
- ✅ https://defensoria-middleware-prod-411798681660.us-central1.run.app/health
- ✅ https://defensoria-middleware-prod-411798681660.us-central1.run.app/docs
- ✅ https://defensoria-middleware-prod-411798681660.us-central1.run.app/api/v2/senales/admin/inicializar-modelo-v2-completo

---

**Próximo paso:** Ejecutar `./deploy-prod.sh` para desplegar
