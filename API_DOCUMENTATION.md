#  Documentación de la API

## Defensoría del Pueblo - Middleware API v1.0.0

Esta documentación describe todos los endpoints disponibles en el middleware de la Defensoría del Pueblo.

---

## 🔗 Información General

### Base URL
- **Desarrollo**: `http://localhost:8000`
- **Producción**: `https://api.defensoria.gob.pe`

### Autenticación
La API utiliza **JWT (JSON Web Tokens)** para autenticación. Incluir el token en el header:
```
Authorization: Bearer <token>
```

### Formato de Respuesta
Todas las respuestas están en formato JSON con charset UTF-8.

### Códigos de Estado HTTP
- `200` - Éxito
- `201` - Creado exitosamente
- `400` - Error en la solicitud
- `401` - No autorizado
- `403` - Prohibido
- `404` - No encontrado
- `422` - Error de validación
- `429` - Demasiadas solicitudes
- `500` - Error interno del servidor

---

##  Autenticación

### POST /auth/login
Iniciar sesión en el sistema.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@defensoria.gob.pe",
    "full_name": "Administrador",
    "is_active": true,
    "roles": ["admin"]
  }
}
```

### POST /auth/refresh
Renovar token de acceso.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### POST /auth/logout
Cerrar sesión (invalidar tokens).

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Sesión cerrada exitosamente"
}
```

### GET /auth/me
Obtener información del usuario actual.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@defensoria.gob.pe",
  "full_name": "Administrador",
  "is_active": true,
  "roles": ["admin"],
  "last_login": "2024-01-23T10:30:00Z"
}
```

---

## 👥 Gestión de Usuarios

### GET /usuarios
Listar usuarios con paginación.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip` (int, default: 0) - Número de registros a omitir
- `limit` (int, default: 100, max: 1000) - Número de registros a retornar
- `search` (string, optional) - Buscar por nombre o email
- `is_active` (bool, optional) - Filtrar por estado activo

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@defensoria.gob.pe",
      "full_name": "Administrador",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "roles": ["admin"]
    }
  ],
  "total": 1,
  "page": 1,
  "pages": 1,
  "per_page": 100
}
```

### POST /usuarios
Crear nuevo usuario.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "username": "nuevo_usuario",
  "email": "usuario@defensoria.gob.pe",
  "password": "password123",
  "full_name": "Nombre Completo",
  "is_active": true,
  "roles": ["user"]
}
```

**Response (201):**
```json
{
  "id": 2,
  "username": "nuevo_usuario",
  "email": "usuario@defensoria.gob.pe",
  "full_name": "Nombre Completo",
  "is_active": true,
  "created_at": "2024-01-23T10:30:00Z",
  "roles": ["user"]
}
```

### GET /usuarios/{user_id}
Obtener usuario por ID.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@defensoria.gob.pe",
  "full_name": "Administrador",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-23T10:30:00Z",
  "roles": ["admin"]
}
```

### PUT /usuarios/{user_id}
Actualizar usuario.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "email": "nuevo_email@defensoria.gob.pe",
  "full_name": "Nuevo Nombre",
  "is_active": true,
  "roles": ["user", "moderator"]
}
```

### DELETE /usuarios/{user_id}
Eliminar usuario (soft delete).

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Usuario eliminado exitosamente"
}
```

---

##  Señales de Detección (SDS)

### GET /api/v2/senales
Listar señales con filtros avanzados.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip` (int, default: 0) - Paginación
- `limit` (int, default: 100) - Límite de resultados
- `fecha_inicio` (date, optional) - Filtrar desde fecha (YYYY-MM-DD)
- `fecha_fin` (date, optional) - Filtrar hasta fecha (YYYY-MM-DD)
- `categoria_id` (int, optional) - Filtrar por categoría
- `estado` (string, optional) - Filtrar por estado
- `search` (string, optional) - Búsqueda en título y descripción

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "titulo": "Señal de Prueba",
      "descripcion": "Descripción de la señal",
      "fecha_deteccion": "2024-01-23T10:30:00Z",
      "estado": "activa",
      "categoria": {
        "id": 1,
        "nombre": "Categoría A",
        "color": "#FF5733"
      },
      "usuario_creador": {
        "id": 1,
        "username": "admin",
        "full_name": "Administrador"
      },
      "entidades_relacionadas": [
        {
          "id": 1,
          "nombre": "Entidad Ejemplo",
          "peso": 0.85
        }
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "pages": 1,
  "per_page": 100
}
```

### POST /api/v2/senales
Crear nueva señal.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "titulo": "Nueva Señal",
  "descripcion": "Descripción detallada de la señal",
  "categoria_id": 1,
  "entidades_ids": [1, 2, 3],
  "figuras_publicas_ids": [1],
  "influencers_ids": [1],
  "medios_digitales_ids": [1],
  "metadata": {
    "fuente": "Twitter",
    "confiabilidad": 0.9
  }
}
```

**Response (201):**
```json
{
  "id": 2,
  "titulo": "Nueva Señal",
  "descripcion": "Descripción detallada de la señal",
  "fecha_deteccion": "2024-01-23T10:30:00Z",
  "estado": "activa",
  "categoria_id": 1,
  "usuario_creador_id": 1,
  "created_at": "2024-01-23T10:30:00Z"
}
```

### GET /api/v2/senales/{senal_id}
Obtener señal por ID con detalles completos.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "titulo": "Señal de Prueba",
  "descripcion": "Descripción de la señal",
  "fecha_deteccion": "2024-01-23T10:30:00Z",
  "estado": "activa",
  "categoria": {
    "id": 1,
    "nombre": "Categoría A",
    "descripcion": "Descripción de la categoría",
    "color": "#FF5733"
  },
  "usuario_creador": {
    "id": 1,
    "username": "admin",
    "full_name": "Administrador"
  },
  "entidades_relacionadas": [
    {
      "id": 1,
      "nombre": "Entidad Ejemplo",
      "peso": 0.85,
      "categoria_observacion_id": 1
    }
  ],
  "figuras_publicas": [
    {
      "id": 1,
      "nombre": "Figura Pública",
      "peso": 0.75
    }
  ],
  "influencers": [
    {
      "id": 1,
      "nombre": "Influencer",
      "peso": 0.65
    }
  ],
  "medios_digitales": [
    {
      "id": 1,
      "nombre": "Medio Digital",
      "peso": 0.80
    }
  ],
  "historial": [
    {
      "id": 1,
      "accion": "creada",
      "fecha": "2024-01-23T10:30:00Z",
      "usuario": "admin",
      "detalles": "Señal creada inicialmente"
    }
  ]
}
```

### PUT /api/v2/senales/{senal_id}
Actualizar señal existente.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "titulo": "Título Actualizado",
  "descripcion": "Nueva descripción",
  "estado": "revisada",
  "categoria_id": 2,
  "entidades_ids": [1, 3],
  "metadata": {
    "actualizada_por": "sistema",
    "razon": "Revisión periódica"
  }
}
```

### DELETE /api/v2/senales/{senal_id}
Eliminar señal (soft delete).

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Señal eliminada exitosamente"
}
```

---

##  Parámetros del Sistema

### GET /api/v2/parametros/crud/entidades
Listar todas las entidades.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `categoria_observacion_id` (int, optional) - Filtrar por categoría

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "nombre": "Entidad Ejemplo",
      "peso": 0.85,
      "categoria_observacion_id": 1,
      "categoria_observacion": {
        "id": 1,
        "nombre": "Categoría A"
      }
    }
  ],
  "total": 1,
  "page": 1,
  "pages": 1,
  "per_page": 100
}
```

### POST /api/v2/parametros/crud/entidades
Crear nueva entidad.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "nombre": "Nueva Entidad",
  "peso": 0.75,
  "categoria_observacion_id": 1
}
```

### GET /api/v2/parametros/crud/categorias-observacion
Listar categorías de observación.

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "nombre": "Categoría A",
      "descripcion": "Descripción de la categoría",
      "color": "#FF5733",
      "activa": true
    }
  ],
  "total": 1
}
```

### GET /api/v2/parametros/crud/categorias-observacion/completo
Obtener categorías con todas sus relaciones.

**Response (200):**
```json
[
  {
    "id": 1,
    "nombre": "Categoría A",
    "descripcion": "Descripción completa",
    "color": "#FF5733",
    "activa": true,
    "entidades": [
      {
        "id": 1,
        "nombre": "Entidad 1",
        "peso": 0.85
      }
    ],
    "figuras_publicas": [
      {
        "id": 1,
        "nombre": "Figura Pública 1",
        "peso": 0.75
      }
    ],
    "influencers": [
      {
        "id": 1,
        "nombre": "Influencer 1",
        "peso": 0.65
      }
    ],
    "medios_digitales": [
      {
        "id": 1,
        "nombre": "Medio Digital 1",
        "peso": 0.80
      }
    ]
  }
]
```

### GET /api/v2/parametros/crud/figuras-publicas
Listar figuras públicas.

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `categoria_observacion_id` (int, optional)

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "nombre": "Figura Pública",
      "peso": 0.75,
      "categoria_observacion_id": 1
    }
  ],
  "total": 1
}
```

### GET /api/v2/parametros/crud/influencers
Listar influencers.

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "nombre": "Influencer",
      "peso": 0.65,
      "categoria_observacion_id": 1
    }
  ],
  "total": 1
}
```

### GET /api/v2/parametros/crud/medios-digitales
Listar medios digitales.

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "nombre": "Medio Digital",
      "peso": 0.80,
      "categoria_observacion_id": 1
    }
  ],
  "total": 1
}
```

---

##  RBAC (Control de Acceso)

### GET /rbac/roles
Listar todos los roles disponibles.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "admin",
    "description": "Administrador del sistema",
    "permissions": [
      "users:read",
      "users:write",
      "users:delete",
      "senales:read",
      "senales:write",
      "senales:delete"
    ]
  },
  {
    "id": 2,
    "name": "user",
    "description": "Usuario estándar",
    "permissions": [
      "senales:read",
      "senales:write"
    ]
  }
]
```

### GET /rbac/permissions
Listar todos los permisos disponibles.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "users:read",
    "description": "Leer usuarios"
  },
  {
    "id": 2,
    "name": "users:write",
    "description": "Crear y modificar usuarios"
  },
  {
    "id": 3,
    "name": "senales:read",
    "description": "Leer señales"
  }
]
```

---

##  Recuperación de Contraseña

### POST /password/request-reset
Solicitar restablecimiento de contraseña.

**Request Body:**
```json
{
  "email": "usuario@defensoria.gob.pe"
}
```

**Response (200):**
```json
{
  "message": "Si el email existe, se ha enviado un enlace de restablecimiento"
}
```

### POST /password/reset
Restablecer contraseña con token.

**Request Body:**
```json
{
  "token": "reset_token_here",
  "new_password": "nueva_password123"
}
```

**Response (200):**
```json
{
  "message": "Contraseña restablecida exitosamente"
}
```

---

##  Endpoints de Sistema

### GET /
Información básica de la API.

**Response (200):**
```json
{
  "message": "Defensoria Middleware API",
  "version": "1.0.0",
  "status": "operational"
}
```

### GET /health
Health check del sistema.

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-23T10:30:00Z",
  "version": "1.0.0",
  "database": "connected",
  "uptime": "2 days, 3 hours, 45 minutes"
}
```

### GET /docs
Documentación interactiva Swagger UI.

### GET /redoc
Documentación interactiva ReDoc.

---

##  Modelos de Datos

### Usuario
```json
{
  "id": "integer",
  "username": "string (unique)",
  "email": "string (unique)",
  "full_name": "string",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_login": "datetime",
  "roles": ["string"]
}
```

### Señal
```json
{
  "id": "integer",
  "titulo": "string",
  "descripcion": "text",
  "fecha_deteccion": "datetime",
  "estado": "string (activa|revisada|archivada)",
  "categoria_id": "integer",
  "usuario_creador_id": "integer",
  "metadata": "json",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Categoría de Observación
```json
{
  "id": "integer",
  "nombre": "string",
  "descripcion": "text",
  "color": "string (hex color)",
  "activa": "boolean",
  "created_at": "datetime"
}
```

### Entidad
```json
{
  "id": "integer",
  "nombre": "string",
  "peso": "decimal (0.0-1.0)",
  "categoria_observacion_id": "integer"
}
```

---

## Códigos de Error

### Errores de Autenticación
```json
{
  "error": "INVALID_CREDENTIALS",
  "message": "Credenciales inválidas",
  "details": null
}
```

### Errores de Validación
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Error de validación",
  "details": {
    "field": "email",
    "message": "Formato de email inválido"
  }
}
```

### Errores de Permisos
```json
{
  "error": "INSUFFICIENT_PERMISSIONS",
  "message": "Permisos insuficientes",
  "details": {
    "required_permission": "users:write"
  }
}
```

### Rate Limiting
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Límite de solicitudes excedido",
  "details": {
    "retry_after": 60
  }
}
```

---

## 📊 Ejemplos de Uso

### Flujo Completo de Autenticación
```bash
# 1. Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2. Usar token en requests
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# 3. Refresh token
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "refresh_token_here"}'
```

### Crear y Gestionar Señal
```bash
# 1. Crear señal
curl -X POST "http://localhost:8000/api/v2/senales" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Nueva Señal de Prueba",
    "descripcion": "Descripción detallada",
    "categoria_id": 1,
    "entidades_ids": [1, 2]
  }'

# 2. Listar señales
curl -X GET "http://localhost:8000/api/v2/senales?limit=10&skip=0" \
  -H "Authorization: Bearer $TOKEN"

# 3. Obtener señal específica
curl -X GET "http://localhost:8000/api/v2/senales/1" \
  -H "Authorization: Bearer $TOKEN"
```

---

##  Configuración de Cliente

### Headers Recomendados
```
Content-Type: application/json
Authorization: Bearer <token>
Accept: application/json
User-Agent: DefensoriaClient/1.0.0
```

### Manejo de Errores
```javascript
// Ejemplo en JavaScript
async function apiCall(endpoint, options = {}) {
  try {
    const response = await fetch(endpoint, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Error en la API');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error en API:', error);
    throw error;
  }
}
```
