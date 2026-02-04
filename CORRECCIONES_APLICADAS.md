# 🔧 Correcciones Aplicadas - Despliegue Backend

## ✅ Problemas Resueltos

### 1. CORS (Cross-Origin Resource Sharing)
**Problema:** Frontend bloqueado por política CORS
```
Access to fetch from origin 'https://defensoria-frontend-jrwf7omlvq-uc.a.run.app' 
has been blocked by CORS policy
```

**Solución:**
- `ALLOWED_ORIGINS=["*"]` - Permite todos los orígenes
- `CORS_ALLOW_CREDENTIALS=true` - Permite credenciales
- Middleware CORS configurado en `app/main.py`

### 2. Rate Limiting (429 Too Many Requests)
**Problema:** Demasiadas peticiones bloqueadas
```
GET ... net::ERR_FAILED 429 (Too Many Requests)
```

**Solución:**
- `RATE_LIMIT_PER_MINUTE=300` (antes: 60)
- `AUTH_RATE_LIMIT_PER_MINUTE=20` (antes: 5)

### 3. Secretos en Cloud Run
**Problema:** Secretos montados sobrescribían el código
**Solución:** `--clear-secrets` en el despliegue

## 📋 Configuración Final

### Variables de Entorno
```bash
APP_ENV=production
EMAIL_SERVICE=none
DATABASE_URL=postgresql+asyncpg://app_user:AppUser2026!@/defensoria_db?host=/cloudsql/sat-defensoriapueblo:us-central1:defensoria-db
POSTGRES_USER=app_user
POSTGRES_PASSWORD=AppUser2026!
POSTGRES_DB=defensoria_db
POSTGRES_PORT=5432
SECRET_KEY=prod-secret-2026
JWT_SECRET_KEY=jwt-prod-2026
JWT_REFRESH_SECRET_KEY=jwt-refresh-prod-2026
ADMIN_DEFAULT_PASSWORD=Admin2026!
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true
LOCAL_AUTH_ENABLED=true
LDAP_ENABLED=false
ENABLE_HTTPS_REDIRECT=false
RATE_LIMIT_PER_MINUTE=300
AUTH_RATE_LIMIT_PER_MINUTE=20
```

### Recursos Cloud Run
```yaml
CPU: 1 core
Memoria: 2 GB
Min Instancias: 1
Max Instancias: 10
Timeout: 900s
CPU Boost: Habilitado
```

## 🚀 Despliegue Rápido

### Opción 1: Script Automático
```bash
./deploy-rapido.sh
```

### Opción 2: Manual
```bash
gcloud builds submit --config=cloudbuild-deploy.yaml
```

### Opción 3: Con Verificación
```bash
# Desplegar
gcloud builds submit --config=cloudbuild-deploy.yaml

# Verificar
URL=$(gcloud run services describe defensoria-middleware-prod --region=us-central1 --format='value(status.url)')
curl "$URL/health"
```

## 📁 Archivos Clave

### `cloudbuild-deploy.yaml`
Configuración de Cloud Build con todas las correcciones aplicadas:
- Build de imagen Docker
- Push a Container Registry
- Deploy a Cloud Run con variables correctas
- Limpieza de secretos

### `deploy-rapido.sh`
Script bash para despliegue en un solo comando:
- Configura proyecto GCP
- Ejecuta Cloud Build
- Verifica el servicio
- Muestra URL y health check

### `Dockerfile`
Imagen optimizada con:
- Python 3.11-slim
- Dependencias del sistema (LDAP, PostgreSQL)
- Puerto 8080 expuesto
- Uvicorn como servidor ASGI

## 🔍 Verificación Post-Despliegue

```bash
# URL del servicio
https://defensoria-middleware-prod-jrwf7omlvq-uc.a.run.app

# Endpoints de prueba
curl https://defensoria-middleware-prod-jrwf7omlvq-uc.a.run.app/health
curl https://defensoria-middleware-prod-jrwf7omlvq-uc.a.run.app/

# Ver logs
gcloud run services logs read defensoria-middleware-prod --region=us-central1

# Ver métricas
gcloud run services describe defensoria-middleware-prod --region=us-central1
```

## 🐛 Troubleshooting

### Si persisten errores CORS:
1. Verificar que `ALLOWED_ORIGINS=["*"]` esté configurado
2. Revisar logs: `gcloud run services logs read defensoria-middleware-prod --region=us-central1`
3. Verificar middleware CORS en `app/main.py`

### Si persisten errores 429:
1. Aumentar más los límites: `RATE_LIMIT_PER_MINUTE=600`
2. Redesplegar: `./deploy-rapido.sh`

### Si el servicio no inicia:
1. Verificar Cloud SQL está activo
2. Revisar variables de entorno
3. Ver logs de inicio: `gcloud run services logs read defensoria-middleware-prod --region=us-central1 --limit=100`

## 📊 Próximas Mejoras

1. **CORS específico**: Cambiar `["*"]` por dominios específicos en producción
2. **Monitoreo**: Configurar alertas en Cloud Monitoring
3. **Autoscaling**: Ajustar min/max instancias según carga real
4. **Dominio personalizado**: Configurar dominio propio
5. **CI/CD**: Automatizar con triggers de GitHub

## 🔐 Seguridad

⚠️ **IMPORTANTE**: En producción real:
- Cambiar `ALLOWED_ORIGINS=["*"]` por dominios específicos
- Rotar secretos y passwords
- Configurar autenticación en Cloud Run
- Habilitar Cloud Armor para protección DDoS
- Implementar API Gateway para rate limiting avanzado
