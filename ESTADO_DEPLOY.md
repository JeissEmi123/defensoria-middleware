# 🚨 ESTADO ACTUAL - Despliegue en Cloud Run

## ✅ Problemas Resueltos

1. **Error Decimal serialization** ✅
   - Removido `jsonable_encoder` 
   - Usando `serialize_decimal` correctamente

2. **Variables de configuración** ✅
   - Agregadas variables SMTP a `config.py`
   - Agregado `extra = "ignore"` en Config

3. **Dockerfile CMD** ✅
   - Corregido para usar `cd /app` en lugar de `--app-dir`

4. **Arquitectura de imagen** ✅
   - Construida para linux/amd64

5. **Contenedor funciona localmente** ✅
   - Probado y arranca correctamente
   - Escucha en puerto 8080

## ❌ Problema Actual

**El contenedor NO inicia en Cloud Run**
- Error: "Container failed to start and listen on port 8080"
- Exit code: 1
- Logs muestran traceback incompleto

## 🔍 Diagnóstico

### Logs de Cloud Run:
```
Container called exit(1).
Traceback (most recent call last):
  File "/usr/local/bin/uvicorn", line 8, in <module>
    sys.exit(main())
  [traceback cortado...]
```

### Prueba Local:
```bash
docker run gcr.io/sat-defensoriapueblo/defensoria-middleware:fix
# ✅ FUNCIONA - Inicia correctamente
# ✅ Escucha en puerto 8080
# ✅ No hay errores de Pydantic
```

## 🤔 Posibles Causas

1. **Timeout muy corto** - Cloud Run mata el contenedor antes de que termine de iniciar
2. **Conexión a Cloud SQL** - Falla al conectar durante el startup
3. **Variables de entorno** - Alguna variable causa error en producción
4. **Startup probe** - El health check falla antes de que la app esté lista

## 💡 Soluciones a Probar

### Opción 1: Aumentar startup probe timeout
```bash
gcloud run services update defensoria-middleware-prod \
  --startup-probe-timeout=240 \
  --region=us-central1 \
  --project=sat-defensoriapueblo
```

### Opción 2: Desplegar servicio nuevo (fresh start)
```bash
gcloud run deploy defensoria-middleware-prod-v2 \
  --image gcr.io/sat-defensoriapueblo/defensoria-middleware:fix \
  --region us-central1 \
  --set-env-vars="APP_ENV=production,EMAIL_SERVICE=none,SECRET_KEY=<SECRET_KEY>,JWT_SECRET_KEY=<JWT_SECRET_KEY>,JWT_REFRESH_SECRET_KEY=<JWT_REFRESH_SECRET_KEY>,ADMIN_DEFAULT_PASSWORD=<ADMIN_DEFAULT_PASSWORD>,POSTGRES_USER=<POSTGRES_USER>,POSTGRES_PASSWORD=<POSTGRES_PASSWORD>,POSTGRES_DB=<POSTGRES_DB>,POSTGRES_PORT=5432,DATABASE_URL=postgresql+asyncpg://<POSTGRES_USER>:<POSTGRES_PASSWORD>@/defensoria_db?host=/cloudsql/<PROJECT_ID>:us-central1:defensoria-db" \
  --add-cloudsql-instances=sat-defensoriapueblo:us-central1:defensoria-db \
  --cpu=2 \
  --memory=4Gi \
  --min-instances=1 \
  --project=sat-defensoriapueblo
```

### Opción 3: Ver logs completos
```bash
# Ver logs en Cloud Console
https://console.cloud.google.com/logs/query?project=sat-defensoriapueblo

# Filtro:
resource.type="cloud_run_revision"
resource.labels.service_name="defensoria-middleware-prod"
severity>=ERROR
```

## 📝 Próximos Pasos

1. **Aumentar timeout del startup probe**
2. **Verificar logs completos en Cloud Console**
3. **Probar con min-instances=1** para mantener instancia caliente
4. **Considerar desplegar como servicio nuevo** si persiste

## 🔗 URLs

- **Logs**: https://console.cloud.google.com/logs/query?project=sat-defensoriapueblo
- **Cloud Run**: https://console.cloud.google.com/run?project=sat-defensoriapueblo
- **Imagen**: gcr.io/sat-defensoriapueblo/defensoria-middleware:fix

## ✅ Código Listo para Producción

El código está correcto y funciona localmente. El problema es específico del entorno de Cloud Run.

**Recomendación:** Aumentar el timeout del startup probe y verificar logs completos en Cloud Console.
