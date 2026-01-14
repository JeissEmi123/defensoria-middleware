# Scripts de Validación GCP/Gmail API

Este directorio contiene herramientas para validar y configurar la integración con Gmail API para el sistema de notificaciones por email de Defensoría del Pueblo.

## 📋 Scripts Disponibles

### 🔧 Configuración Automática
- **`setup_gmail_api.sh`** - **Script principal** que configura todo automáticamente
  - Crea Service Account
  - Habilita APIs necesarias
  - Configura variables de entorno
  - Genera credenciales

### 🔍 Diagnóstico y Validación
- **`basic_gcp_check.py`** - Diagnóstico básico sin dependencias
- **`diagnose_gcp_connectivity.py`** - Test completo de conectividad
- **`validate_gcp_config.py`** - Validación detallada de configuración
- **`test_gmail_setup.py`** - **NUEVO**: Verificación completa de Gmail API
- **`test_email_flow.py`** - Test del flujo completo de emails
- **`validate_all.py`** - Script maestro que ejecuta todos los tests

## 🚀 Uso Rápido

### Opción 1: Configuración Automática (RECOMENDADO)
```bash
# Ejecutar configuración completa
./scripts/setup_gmail_api.sh
```

### Opción 2: Validación Manual
```bash
# 1. Diagnóstico básico
python3 scripts/basic_gcp_check.py

# 2. Validación completa  
python3 scripts/validate_all.py

# 3. Test específico de email
python3 scripts/test_email_flow.py
```

## 📊 Interpretación de Resultados

### ✅ Todo OK
- Conectividad a Google APIs funcional
- Service Account configurado correctamente
- Variables de entorno establecidas
- Gmail API responde correctamente

### ⚠️ Problemas Parciales
- Conectividad OK pero faltan configuraciones
- Service Account existe pero permisos incorrectos
- Variables configuradas pero archivos faltantes

### ❌ Problemas Serios
- Sin conectividad a internet
- Google Cloud CLI no instalado
- Sin autenticación en GCP
- APIs no habilitadas

## 🔧 Solución de Problemas Comunes

### "gcloud not found"
```bash
# Instalar Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

### "Service Account not found"
```bash
# Crear manualmente
gcloud iam service-accounts create defensoria-gmail \
  --display-name="Defensoria Gmail Service"

# Generar credenciales
gcloud iam service-accounts keys create ~/gmail-sa.json \
  --iam-account=defensoria-gmail@PROJECT_ID.iam.gserviceaccount.com
```

### "Gmail API access denied"
1. Verificar que Gmail API esté habilitada
2. Configurar Domain-wide Delegation en Google Admin Console
3. Verificar scopes: `https://www.googleapis.com/auth/gmail.send`

### "Email not sent"
1. Verificar `COORDINADOR_EMAIL` en .env
2. Confirmar Domain-wide Delegation
3. Verificar que el usuario delegado exista
4. Revisar logs de la aplicación

## 📁 Estructura de Archivos Generados

```
defensoria-middleware/
├── config/
│   └── gmail-service-account.json  # Credenciales (NO subir a git)
├── .env                             # Variables actualizadas
├── .env.backup.YYYYMMDD_HHMMSS     # Backup automático
└── scripts/
    ├── logs/                        # Logs de validación
    └── *.py                         # Scripts de validación
```

## 🔒 Seguridad

### Archivos Sensibles (NO incluir en git)
- `config/gmail-service-account.json`
- `.env` (en producción)
- Cualquier archivo con credenciales

### Permisos Recomendados
```bash
chmod 600 config/gmail-service-account.json  # Solo propietario
chmod 644 .env                               # Lectura general
```

## 📚 Documentación Adicional

- [Configuración Completa](../docs/CONFIGURACION_EMAIL.md)
- [API de Señales](../docs/API_SENALES_FRONTEND.md)
- [Google Cloud IAM](https://cloud.google.com/iam/docs/service-accounts)
- [Gmail API](https://developers.google.com/gmail/api)

## ⚡ Comandos de Emergencia

### Regenerar Service Account
```bash
# Eliminar actual
gcloud iam service-accounts delete defensoria-gmail@PROJECT_ID.iam.gserviceaccount.com

# Recrear
./scripts/setup_gmail_api.sh
```

### Reset Completo de Configuración
```bash
# Backup de configuración actual
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Eliminar configuración Gmail
sed -i '/GMAIL_/d' .env
sed -i '/EMAIL_/d' .env
sed -i '/COORDINADOR_/d' .env

# Reconfigurar
./scripts/setup_gmail_api.sh
```

### Verificar Estado del Sistema
```bash
# Status rápido
python3 scripts/basic_gcp_check.py

# Validación completa
python3 scripts/validate_all.py

# Test en vivo (cuidado - envía email real)
python3 scripts/test_email_flow.py
```

## 📞 Soporte

Si los scripts fallan:

1. **Revisar conectividad**: `python3 scripts/basic_gcp_check.py`
2. **Verificar logs**: `docker-compose logs defensoria-middleware`
3. **Consultar documentación**: `docs/CONFIGURACION_EMAIL.md`
4. **Regenerar configuración**: `./scripts/setup_gmail_api.sh`

---
**Nota**: Estos scripts están diseñados para el entorno de Defensoría del Pueblo y requieren acceso a Google Cloud Platform y Google Workspace.