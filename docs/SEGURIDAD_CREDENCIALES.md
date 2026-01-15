# 🔒 Guía de Manejo Seguro de Credenciales

## ❌ Problemas de Seguridad Anteriores

- ✅ **RESUELTO**: `service-account-key.json` se copiaba al contenedor
- ✅ **RESUELTO**: Credenciales hardcodeadas en el código
- ✅ **RESUELTO**: No había `.dockerignore` para excluir archivos sensibles

## ✅ Configuración Actual Segura

### 1. Archivos Sensibles Excluidos

El `.dockerignore` ahora excluye:
```
config/service-account-key.json
config/client_secret.json
config/gmail_token.json
config/oauth-client-secret.json
.env
```

### 2. Secretos en Google Secret Manager

Los secretos se almacenan en Google Secret Manager:
- `service-account-key`: Credenciales del Service Account
- `oauth-client-secret`: Credenciales OAuth de Gmail
- `gmail-token-pickle`: Token de autenticación de Gmail

### 3. Acceso Seguro en Producción

Cloud Run monta los secretos como archivos:
```yaml
--update-secrets
/app/config/service-account-key.json=service-account-key:latest
```

## 🛡️ Buenas Prácticas Implementadas

### Variables de Entorno
```env
# ✅ Solo referencias a rutas, no credenciales
GMAIL_SERVICE_ACCOUNT_FILE=/app/config/service-account-key.json
GMAIL_OAUTH_CLIENT_SECRET_FILE=/app/config/oauth-client-secret.json
GMAIL_TOKEN_FILE=/app/config/gmail-token.pickle
```

### Permisos IAM
```bash
# Service Account con permisos mínimos
gcloud projects add-iam-policy-binding sat-defensoriapueblo \
  --member="serviceAccount:411798681660-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## 📋 Checklist de Seguridad

- [x] ✅ Archivos sensibles en `.dockerignore`
- [x] ✅ Secretos almacenados en Secret Manager
- [x] ✅ Montaje seguro de secretos en Cloud Run
- [x] ✅ Permisos IAM configurados correctamente
- [x] ✅ Variables de entorno solo con rutas, no credenciales

## 🚀 Despliegue Seguro

### Desarrollo Local
```bash
# Los archivos locales se usan directamente
export GMAIL_SERVICE_ACCOUNT_FILE=./config/service-account-key.json
```

### Producción (Cloud Run)
```bash
# Los secretos se montan desde Secret Manager
gcloud run deploy defensoria-middleware-prod \
  --update-secrets /app/config/service-account-key.json=service-account-key:latest
```

## 🔄 Actualizar Secretos

### Crear/Actualizar un Secreto
```bash
# Crear nuevo secreto
gcloud secrets create service-account-key \
  --data-file=./config/service-account-key.json

# Actualizar secreto existente
gcloud secrets versions add service-account-key \
  --data-file=./config/service-account-key.json
```

### Verificar Secretos
```bash
# Listar secretos
gcloud secrets list

# Ver versiones
gcloud secrets versions list service-account-key
```

## ⚠️ NUNCA Hacer

- ❌ No commitear archivos de credenciales en Git
- ❌ No hardcodear credenciales en el código
- ❌ No incluir credenciales en variables de entorno en `cloudbuild.yaml`
- ❌ No logear o imprimir credenciales
- ❌ No usar credenciales de producción en desarrollo

## 🔐 Rotación de Credenciales

### Service Account Key
1. Generar nueva key en Google Cloud Console
2. Actualizar secret en Secret Manager
3. Redesplegar la aplicación
4. Eliminar la key anterior

### OAuth Tokens
1. Revocar tokens existentes
2. Regenerar tokens
3. Actualizar secretos
4. Redesplegar

---

**🎯 Resultado**: Las credenciales están completamente seguras y no se exponen en el contenedor Docker ni en el repositorio de código.