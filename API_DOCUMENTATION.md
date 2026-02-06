# Documentación de API (Resumen)

## Información general
- Formato: JSON (UTF-8)
- Autenticación: JWT con header `Authorization: Bearer <token>`
- Documentación interactiva: `/docs` y `/redoc`

## Base URL
- Local: `http://localhost:9000`
- Producción: `https://<tu-servicio>`

## Autenticación

### `POST /auth/login`
Inicia sesión y retorna tokens. El request acepta `username`/`password` o `nombre_usuario`/`contrasena`.

```json
{
  "username": "admin",
  "password": "admin123"
}
```

### `POST /auth/refresh`
Refresca el access token con `refresh_token`.

### `POST /auth/logout`
Cierra la sesión actual.

### `GET /auth/me`
Retorna el usuario autenticado.

### `POST /auth/validate`
Valida el token JWT enviado en el header.

## Grupos de endpoints (por prefijo)

### Señales (SDS)
- `GET /api/v2/senales/...`

### Categorías de observación
- `GET|POST|PUT|DELETE /api/v2/categorias-observacion`
- `GET /api/v2/categorias-observacion/jerarquia/arbol`

### Parámetros SDS
- `GET|POST|PUT|DELETE /api/v2/parametros/...`

### CRUD unificado
- `GET|POST|PUT|DELETE /api/v1/crud-unificado/...`

### Administración de modelo
- `GET|POST|PUT|DELETE /admin-modelo/...`

### Usuarios y RBAC
- `GET|POST|PUT|DELETE /usuarios`
- `GET|POST|PUT|DELETE /rbac/...`

### Recuperación de contraseña
- `POST /password/solicitar`
- `POST /password/cancelar/{usuario_id}`

## Health check
- `GET /health`

## Errores y respuestas
Los errores se devuelven en JSON. Para esquemas completos y ejemplos, usar `/docs`.
