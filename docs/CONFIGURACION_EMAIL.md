# Configuración de Email para Defensoría Middleware

## Resumen

El sistema ya está **completamente configurado** para enviar correos automáticos cuando se confirma la revisión de una señal (HU04-01). Solo necesitas configurar las variables de entorno.

## ✅ Funcionalidades Implementadas

### 1. EmailService configurado con Gmail API
- Localización: [`app/services/email_service.py`](app/services/email_service.py)
- Método específico: `send_signal_revision_notification()`
- Usa Service Account de Google para autenticación

### 2. Integración automática en el flujo de señales
- Localización: [`app/services/senal_service_v2.py`](app/services/senal_service_v2.py) líneas 726-736
- Se ejecuta automáticamente cuando:
  - Se cambia el tipo de categoría de señal (RUIDO/PARACRISIS/CRISIS)
  - Se confirma la revisión (`confirmo_revision=true`)

### 3. Endpoint REST ya configurado
- **PUT** `/api/v1/senales/{id}/categoria`
- Requiere: `confirmo_revision=true` (obligatorio)
- Documentación: [`docs/API_SENALES_FRONTEND.md`](docs/API_SENALES_FRONTEND.md#put-senalesidcategoria)
 
### 4. Notificación al revisor
- El usuario que confirma el cambio también recibe ese correo con el mismo resumen si su cuenta tiene un `email` válido configurado.

## 🔧 Configuración Requerida

### Variables de Entorno (.env)

```bash
# === CONFIGURACIÓN GMAIL API (Service Account) ===
GMAIL_SERVICE_ACCOUNT_FILE=/ruta/a/service-account-key.json
GMAIL_DELEGATED_USER=admin@defensoria.gob.co
EMAIL_FROM=noreply@defensoria.gob.co

# === EMAIL DEL COORDINADOR ===
COORDINADOR_EMAIL=coordinador@defensoria.gob.co

# === OTRAS CONFIGURACIONES ===
APP_ENV=production
LOG_LEVEL=INFO
```

### Dependencias ya instaladas

```bash
# Ya están en requirements-email.txt
google-api-python-client==2.110.1
google-auth==2.25.1
google-auth-httplib2==0.1.0
```

## 📋 Pasos para Activar

### 1. Crear Service Account en Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita Gmail API
4. Crea un Service Account:
   - Ve a **IAM & Admin > Service Accounts**
   - Clic en **+ CREATE SERVICE ACCOUNT**
   - Nombre: `defensoria-gmail-service`
   - Descarga el archivo JSON de credenciales

### 2. Configurar Domain-wide Delegation (GSuite/Google Workspace)

Si tienes Google Workspace:
1. Ve a [Google Admin Console](https://admin.google.com/)
2. **Security > API Controls > Domain-wide Delegation**
3. Agrega el Client ID del service account
4. Scopes: `https://www.googleapis.com/auth/gmail.send`

### 3. Configurar variables de entorno

```bash
# Copiar el archivo de credenciales
cp /ruta/descarga/service-account-key.json /app/config/gmail-service-account.json

# Agregar al .env
echo "GMAIL_SERVICE_ACCOUNT_FILE=/app/config/gmail-service-account.json" >> .env
echo "GMAIL_DELEGATED_USER=tu-email@defensoria.gob.co" >> .env
echo "COORDINADOR_EMAIL=coordinador@defensoria.gob.co" >> .env
```

> **Nota:** para que el revisor reciba confirmaciones, su cuenta en el sistema debe tener un `email` válido registrado.
```

## 📧 Ejemplo de Email Automático

Cuando se confirma una revisión de señal, se envía automáticamente:

**Asunto:** `Cambio confirmado en tipo de señal #123`

**Contenido:**
- Señal ID
- Categoría anterior: RUIDO → CRISIS
- Usuario que revisó: Juan Pérez
- Confirmó revisión: Sí
- Fecha de actualización: 2026-01-13 10:30:00
- Comentarios adicionales (opcional)

## 🔄 Configuración OAuth (Alternativa)

Si necesitas usar OAuth en lugar de Service Account:

```bash
# Variables para OAuth 2.0
CLIENT_ID="TU_CLIENT_ID.apps.googleusercontent.com"
REDIRECT_URI="https://TU_DOMINIO.com/oauth/callback"
SCOPE="openid%20email%20profile"

# URL de autorización
echo "https://accounts.google.com/o/oauth2/v2/auth?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=code&scope=${SCOPE}&access_type=offline&prompt=consent"
```

**Nota:** El método OAuth es más complejo para aplicaciones server-to-server. Se recomienda usar Service Account.

## 🧪 Testing

### Probar configuración manualmente

```python
from app.services.email_service import email_service
from app.config import settings

# Verificar configuración
print(f"Service Account File: {settings.gmail_service_account_file}")
print(f"Delegated User: {settings.gmail_delegated_user}")  
print(f"Coordinador Email: {settings.coordinador_email}")

# Probar envío
resultado = email_service.send_signal_revision_notification(
    to_email="test@example.com",
    senal_id=999,
    categoria_previa="RUIDO",
    categoria_nueva="CRISIS", 
    usuario="Test User",
    confirmo_revision=True,
    fecha_actualizacion="2026-01-13 10:30:00"
)

print(f"Email enviado: {resultado}")
```

### Probar endpoint completo

```bash
curl -X PUT "http://localhost:8000/api/v1/senales/123/categoria" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d "nueva_categoria_id=3&confirmo_revision=true&comentario=Escalando a crisis"
```

## 🚨 Solución de Problemas

### Email no se envía

1. **Verificar logs:**
   ```bash
   docker logs defensoria-middleware | grep -i email
   ```

2. **Verificar variables de entorno:**
   ```bash
   echo $GMAIL_SERVICE_ACCOUNT_FILE
   echo $COORDINADOR_EMAIL
   ```

3. **Verificar permisos del service account**

4. **Verificar que el archivo JSON existe y es válido**

### Errores comunes

- `GMAIL_SERVICE_ACCOUNT_FILE no configurado` → Configurar variable de entorno
- `GMAIL_DELEGATED_USER no configurado` → Configurar usuario con permisos  
- `Error HTTP 403` → Verificar domain-wide delegation
- `Error HTTP 401` → Verificar credenciales del service account

## ✅ Estado Actual

- [x] EmailService implementado
- [x] Integración automática con señales
- [x] Endpoint REST funcional
- [x] Template HTML de email
- [x] Logging y manejo de errores
- [ ] Variables de entorno configuradas (pendiente)
- [ ] Service Account creado (pendiente)

**El código está listo, solo falta la configuración de Google Cloud.**
