# Guía de Solución de Problemas

## Diagnóstico rápido (Docker)
```bash
docker compose ps
docker compose logs -f app
curl http://localhost:9000/health
docker compose exec app alembic current
```

## Problemas comunes

### 1) La API no inicia
- Verifica si el puerto 9000 está ocupado: `lsof -i :9000`.
- Revisa el archivo `.env.docker` si estás en Docker.
- Confirma conectividad a la base de datos.

### 2) Error de conexión a PostgreSQL
```bash
docker compose logs db
# Probar conexión desde el contenedor
docker compose exec app python -c "from app.database.session import engine; print('DB OK')"
```

### 3) Migraciones pendientes
```bash
docker compose exec app alembic upgrade head
```

### 4) Autenticación falla (401)
- Verifica `SECRET_KEY`, `JWT_SECRET_KEY`, `JWT_REFRESH_SECRET_KEY`.
- Confirma que el usuario exista y no esté bloqueado.
- Revisa políticas de contraseña y bloqueo.

### 5) CORS bloqueando solicitudes
- Revisa `ALLOWED_ORIGINS` y `ALLOWED_HOSTS` en `.env.docker` o `.env`.
- Asegúrate de usar lista JSON en `ALLOWED_ORIGINS`.
- Reinicia el servicio tras cambios.

## Herramientas útiles
```bash
python scripts/validate_all.py
python scripts/health_check_db.py
python scripts/test_integration.py
```

## Logs
```bash
docker compose logs -f app
docker compose logs -f db
```
