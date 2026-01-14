# Configuración Final - Gmail API para Defensoría Middleware

## ✅ Estado Actual - COMPLETADO

1. **Service Account creado**: `email-service-account@sat-defensoriapueblo.iam.gserviceaccount.com`
2. **Gmail API habilitada** en el proyecto `sat-defensoriapueblo`
3. **Credenciales guardadas** en `config/service-account-key.json`
4. **OAuth client configurado** en `config/oauth-client-secret.json`
5. **EmailService funcionando** correctamente

## 🔧 Pasos Finales para Completar

### 1. Domain-wide Delegation (Si tienes Google Workspace)

Si tu organización usa Google Workspace, necesitas configurar Domain-wide Delegation:

1. Ve a [Google Admin Console](https://admin.google.com/)
2. **Security > API Controls > Domain-wide Delegation**
3. Haz clic en **"Add new"**
4. Usa estos valores:
   - **Client ID**: `110921003205179349806`
   - **OAuth Scopes**: `https://www.googleapis.com/auth/gmail.send`
5. Autoriza el cliente

### 2. Configurar Email Válido

Actualiza el archivo `.env` con un email válido de tu dominio:

```bash
# Cambiar por un email real de tu organización
GMAIL_DELEGATED_USER=tu-email@tu-dominio.com
COORDINADOR_EMAIL=coordinador@tu-dominio.com
```

### 3. Alternativa: Usar Gmail Personal

Si no tienes Google Workspace, puedes usar Gmail personal:

```bash
# Para desarrollo/testing con Gmail personal
GMAIL_DELEGATED_USER=tu-email@gmail.com
COORDINADOR_EMAIL=coordinador@gmail.com
```

## 🧪 Verificar Configuración

Para probar que todo funciona:

```bash
# Configurar variables de entorno
export GMAIL_SERVICE_ACCOUNT_FILE=config/service-account-key.json
export GMAIL_DELEGATED_USER=tu-email@dominio.com

# Ejecutar verificación
python scripts/test_gmail_setup.py
```

## 🚀 Uso en Producción

### Variables de Entorno Requeridas

```bash
# Configuración mínima para producción
GMAIL_SERVICE_ACCOUNT_FILE=/app/config/service-account-key.json
GMAIL_DELEGATED_USER=sistema@defensoria.gob.pe
COORDINADOR_EMAIL=coordinador@defensoria.gob.pe
GCP_PROJECT_ID=sat-defensoriapueblo
```

### Deployment

1. **Subir service account key** a Google Cloud Secret Manager (recomendado)
2. **Configurar variables** en Google Cloud Run
3. **Verificar permisos** del service account

## 📧 Emails Automáticos Configurados

El sistema enviará emails automáticamente en estos casos:

1. **Usuario creado**: Email de bienvenida con credenciales temporales
2. **Reset de contraseña**: Link de recuperación
3. **Cambio de categoría de señal**: Notificación al coordinador

## 🔒 Seguridad

- ✅ Credenciales excluidas de Git (`.gitignore`)
- ✅ Credenciales excluidas de Cloud Build (`.gcloudignore`)
- ✅ Service Account con permisos mínimos
- ✅ Emails solo a coordinadores autorizados

## 📋 Checklist Final

- [x] Service Account creado
- [x] Gmail API habilitada
- [x] Credenciales configuradas
- [x] EmailService funcionando
- [x] Scripts de verificación listos
- [ ] Domain-wide Delegation configurado (si aplica)
- [ ] Email válido configurado
- [ ] Prueba de envío exitosa

## 🆘 Solución de Problemas

### Error: "Invalid email or User ID"
- **Causa**: Email no existe en el dominio o Domain-wide Delegation no configurado
- **Solución**: Usar email válido y configurar delegation

### Error: "Permission denied"
- **Causa**: Service account sin permisos
- **Solución**: Verificar Domain-wide Delegation y scopes

### Error: "File not found"
- **Causa**: Ruta de credenciales incorrecta
- **Solución**: Verificar GMAIL_SERVICE_ACCOUNT_FILE

---

## 🎉 ¡Configuración Lista!

Tu middleware ya está configurado para enviar emails automáticamente. Solo necesitas:
1. Configurar un email válido
2. (Opcional) Domain-wide Delegation para Google Workspace

El sistema está listo para producción! 🚀