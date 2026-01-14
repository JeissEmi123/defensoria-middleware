# Configuraciones de Email para Diferentes Escenarios

## 🔧 Opción 1: Gmail Personal (OAuth) - Más Fácil

### Configurar OAuth

```bash
# 1. Instalar dependencias
pip install google-auth-oauthlib

# 2. Configurar OAuth
python scripts/setup_oauth_gmail.py

# 3. Actualizar .env
GMAIL_USE_OAUTH=true
GMAIL_TOKEN_FILE=config/gmail-token.pickle
GMAIL_OAUTH_CLIENT_SECRET_FILE=config/oauth-client-secret.json
EMAIL_FROM=tu-email@gmail.com
COORDINADOR_EMAIL=coordinador@gmail.com
```

### Ventajas:
- ✅ No requiere Google Workspace
- ✅ Funciona con cualquier Gmail personal
- ✅ Configuración simple

### Desventajas:
- ⚠️ Token expira (se renueva automáticamente)
- ⚠️ Limitado por cuotas de Gmail personal

---

## 🏢 Opción 2: Servicio de Email Tercero (SendGrid)

### Configurar SendGrid

```bash
# 1. Instalar SendGrid
pip install sendgrid

# 2. Configurar .env
EMAIL_SERVICE=sendgrid
SENDGRID_API_KEY=tu_sendgrid_api_key
EMAIL_FROM=noreply@tu-dominio.com
COORDINADOR_EMAIL=coordinador@tu-dominio.com
```

### Ventajas:
- ✅ Profesional y confiable
- ✅ Altas cuotas de envío
- ✅ Funciona con cualquier dominio
- ✅ Analytics y tracking

---

## 📧 Opción 3: SMTP Tradicional

### Configurar SMTP

```bash
# Para Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
SMTP_USE_TLS=true

# Para otros proveedores (ejemplo: Outlook)
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
```

### Ventajas:
- ✅ Universal - funciona con cualquier proveedor
- ✅ Simple y directo

### Desventajas:
- ⚠️ Requiere App Passwords para Gmail
- ⚠️ Menos seguro que OAuth

---

## 🔗 Opción 4: Service Account (Ya configurado)

Tu configuración actual - ideal para Google Workspace empresarial.

---

## 🎯 Recomendación

**Para desarrollo/testing:** OAuth con Gmail personal
**Para producción:** SendGrid o Service Account

¿Cuál prefieres configurar?