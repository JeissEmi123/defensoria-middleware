# API de Detección de Señales - Documentación para Frontend

**Base URL:** `http://localhost:8000/api/v1/senales`  
**Autenticación:** Bearer Token (JWT) requerido en header `Authorization`

---

## 📋 Índice de Endpoints

### Listado y Búsqueda
- [GET /](#get-senales) - Listar señales con filtros
- [GET /buscar](#get-senalesbuscar) - Búsqueda full-text
- [GET /alertas/criticas](#get-senalesalertascriticas) - Top alertas críticas
- [GET /indicadores](#get-senalesindicadores) - Indicadores del sistema
- [GET /estadisticas](#get-senalesestadisticas) - Estadísticas completas

### Detalle
- [GET /{id}](#get-senalesid) - Detalle de señal
- [GET /{id}/historial](#get-senalesidhistorial) - Historial de cambios

### Creación y Actualización
- [POST /](#post-senales) - Crear señal
- [PUT /{id}](#put-senalesid) - Actualizar señal
- [PUT /{id}/categoria](#put-senalesidcategoria) - Cambiar categoría

### Operaciones Masivas
- [POST /asignacion-masiva](#post-senalesasignacion-masiva) - Asignar múltiples señales
- [POST /cambio-estado-masivo](#post-senalescambio-estado-masivo) - Cambiar estado masivo

### Catálogos
- [GET /catalogos/categorias-senal](#get-senalescatalogoscategorias-senal) - Categorías de señal
- [GET /catalogos/categorias-analisis](#get-senalescatalogoscategorias-analisis) - Categorías de análisis

---

## 🔍 Endpoints de Listado y Búsqueda

### GET /senales

Listar señales con paginación, ordenamiento y filtros.

**Query Parameters:**

| Parámetro | Tipo | Requerido | Descripción | Valores |
|-----------|------|-----------|-------------|---------|
| `skip` | integer | No | Offset para paginación | Default: 0 |
| `limit` | integer | No | Límite de resultados | Default: 100, Max: 1000 |
| `orden` | string | No | Criterio de ordenamiento | `fecha_desc`, `fecha_asc`, `score_desc`, `score_asc` |
| `estado` | string | No | Filtrar por estado | DETECTADA, EN_REVISION, VALIDADA, RECHAZADA, RESUELTA |
| `id_categoria_senal` | integer | No | Filtrar por categoría | 1=RUIDO, 2=PARACRISIS, 3=CRISIS |
| `id_categoria_analisis` | integer | No | Tipo de violencia | 1=Reclutamiento, 2=Violencia política, 3=Violencia género |
| `score_min` | decimal | No | Score mínimo | 0-100 |
| `score_max` | decimal | No | Score máximo | 0-100 |
| `fecha_desde` | datetime | No | Fecha desde | ISO 8601 format |
| `fecha_hasta` | datetime | No | Fecha hasta | ISO 8601 format |
| `plataforma` | string | No | Plataforma digital | Twitter, Facebook, Instagram, etc. |
| `usuario_asignado_id` | integer | No | Usuario asignado | ID del usuario |

**Ejemplo Request:**
```javascript
// React/Frontend
const response = await fetch(
  'http://localhost:8000/api/v1/senales?' + new URLSearchParams({
    orden: 'score_desc',
    estado: 'EN_REVISION',
    skip: 0,
    limit: 20
  }),
  {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }
);

const data = await response.json();
```

**Ejemplo Response:**
```json
{
  "items": [
    {
      "id_senal_detectada": 1,
      "fecha_deteccion": "2024-01-15T14:30:00",
      "id_categoria_senal": 3,
      "id_categoria_analisis": 1,
      "score_riesgo": 85.00,
      "categorias_observacion": {
        "categorias": [1, 2],
        "intensidad": "alta"
      },
      "plataformas_digitales": ["Twitter", "Facebook"],
      "contenido_detectado": "Publicación con llamados a reclutamiento...",
      "estado": "DETECTADA",
      "fecha_actualizacion": "2024-01-15T16:45:00"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 20,
  "has_more": true
}
```

---

### GET /senales/buscar

Búsqueda full-text en señales detectadas.

**Query Parameters:**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `q` | string | **Sí** | Término de búsqueda (mínimo 3 caracteres) |
| `skip` | integer | No | Offset |
| `limit` | integer | No | Límite |

**Ejemplo Request:**
```javascript
const searchTerm = 'reclutamiento';
const response = await fetch(
  `http://localhost:8000/api/v1/senales/buscar?q=${encodeURIComponent(searchTerm)}`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
```

---

### GET /senales/alertas/criticas

Obtener top alertas críticas del día actual.

**Query Parameters:**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `limite` | integer | No | Número de alertas (Default: 5, Max: 20) |

**Ejemplo Request:**
```javascript
const response = await fetch(
  'http://localhost:8000/api/v1/senales/alertas/criticas?limite=5',
  { headers: { 'Authorization': `Bearer ${token}` } }
);
```

**Ejemplo Response:**
```json
[
  {
    "id_senal_detectada": 6,
    "score_riesgo": 95.00,
    "estado": "RESUELTA",
    "contenido_detectado": "Amenaza directa...",
    "fecha_deteccion": "2024-01-20T21:10:00"
  }
]
```

---

### GET /senales/indicadores

Obtener indicadores del sistema.

**Ejemplo Response:**
```json
{
  "total_activas": 120,
  "en_revision": 35,
  "por_categoria": {
    "CRISIS": 15,
    "PARACRISIS": 45,
    "RUIDO": 10
  },
  "fecha_calculo": "2024-01-24T10:30:00"
}
```

---

### GET /senales/estadisticas

Obtener estadísticas completas.

**Query Parameters:**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `fecha_desde` | datetime | No | Fecha desde |
| `fecha_hasta` | datetime | No | Fecha hasta |

**Ejemplo Response:**
```json
{
  "total_senales": 250,
  "por_estado": {
    "DETECTADA": 50,
    "EN_REVISION": 80,
    "VALIDADA": 60,
    "RESUELTA": 40,
    "RECHAZADA": 20
  },
  "por_categoria_senal": {
    "CRISIS": 30,
    "PARACRISIS": 120,
    "RUIDO": 100
  },
  "por_categoria_analisis": {
    "Reclutamiento, uso y utilización de niñas, niños y adolescentes": 80,
    "Violencia política": 90,
    "Violencia digital basada en género": 80
  },
  "score_promedio": 72.5,
  "senales_ultima_semana": 45,
  "senales_ultimo_mes": 180
}
```

---

## 📄 Endpoints de Detalle

### GET /senales/{id}

Obtener detalle completo de una señal.

**Path Parameters:**
- `id`: ID de la señal (integer)

**Ejemplo Request:**
```javascript
const senalId = 1;
const response = await fetch(
  `http://localhost:8000/api/v1/senales/${senalId}`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
```

**Ejemplo Response:**
```json
{
  "id_senal_detectada": 1,
  "fecha_deteccion": "2024-01-15T14:30:00",
  "id_categoria_senal": 3,
  "id_categoria_analisis": 1,
  "score_riesgo": 85.00,
  "categorias_observacion": {
    "categorias": [1, 2],
    "intensidad": "alta",
    "frecuencia": "diaria"
  },
  "fecha_actualizacion": "2024-01-15T16:45:00",
  "plataformas_digitales": ["Twitter", "Facebook"],
  "contenido_detectado": "Publicación con llamados...",
  "metadatos": {
    "autor": "usuario_anonimo_123",
    "ubicacion": "Norte de Santander"
  },
  "estado": "DETECTADA",
  "url_origen": "https://twitter.com/example/status/123456",
  "usuario_asignado_id": null,
  "categoria_senal": {
    "id_categoria_senal": 3,
    "nombre_categoria_senal": "CRISIS",
    "color": "#FF0000",
    "nivel": 1
  },
  "categoria_analisis": {
    "id": 1,
    "nombre_categoria_analisis": "Reclutamiento, uso y utilización..."
  },
  "historial": [
    {
      "id": 1,
      "accion": "CREACION",
      "descripcion": "Señal detectada automáticamente",
      "fecha_registro": "2024-01-15T14:30:00",
      "usuario_id": null
    }
  ]
}
```

---

### GET /senales/{id}/historial

Obtener historial de cambios de una señal.

**Path Parameters:**
- `id`: ID de la señal

**Query Parameters:**
- `skip`: Offset (default: 0)
- `limit`: Límite (default: 100)

---

## ✏️ Endpoints de Creación y Actualización

### POST /senales

Crear nueva señal detectada.

**Request Body:**
```json
{
  "id_categoria_senal": 3,
  "id_categoria_analisis": 1,
  "score_riesgo": 85.00,
  "categorias_observacion": {
    "intensidad": "alta"
  },
  "plataformas_digitales": ["Twitter"],
  "contenido_detectado": "Contenido de la señal...",
  "metadatos": {
    "autor": "usuario123"
  },
  "url_origen": "https://example.com",
  "estado": "DETECTADA"
}
```

**Ejemplo Request:**
```javascript
const nuevaSenal = {
  id_categoria_senal: 3,
  score_riesgo: 85.00,
  contenido_detectado: "Texto detectado...",
  plataformas_digitales: ["Twitter"],
  estado: "DETECTADA"
};

const response = await fetch('http://localhost:8000/api/v1/senales', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(nuevaSenal)
});
```

---

### PUT /senales/{id}

Actualizar señal existente.

**Request Body (todos los campos opcionales):**
```json
{
  "score_riesgo": 90.00,
  "estado": "EN_REVISION",
  "notas_resolucion": "Señal revisada y validada"
}
```

---

### PUT /senales/{id}/categoria

Cambiar categoría de una señal (RUIDO, PARACRISIS, CRISIS).

**Query Parameters:**
- `nueva_categoria_id`: ID de la nueva categoría (required)
- `comentario`: Comentario del cambio (optional)
- `confirmo_revision`: Confirmación de revisión = **true** (required)

**Ejemplo Request:**
```javascript
const response = await fetch(
  `http://localhost:8000/api/v1/senales/${senalId}/categoria?` + new URLSearchParams({
    nueva_categoria_id: 3,  // CRISIS
    confirmo_revision: true,
    comentario: 'Escalando a crisis por gravedad'
  }),
  {
    method: 'PUT',
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
```

---

## 🔄 Endpoints de Operaciones Masivas

### POST /senales/asignacion-masiva

Asignar múltiples señales a un usuario.

**Request Body:**
```json
{
  "ids_senales": [1, 2, 3, 4, 5],
  "usuario_asignado_id": 10,
  "notas": "Asignación por especialidad"
}
```

---

### POST /senales/cambio-estado-masivo

Cambiar estado de múltiples señales.

**Request Body:**
```json
{
  "ids_senales": [1, 2, 3],
  "nuevo_estado": "VALIDADA",
  "notas": "Señales validadas tras revisión"
}
```

**Estados válidos:**
- `DETECTADA`
- `EN_REVISION`
- `VALIDADA`
- `RECHAZADA`
- `RESUELTA`

---

## 📚 Endpoints de Catálogos

### GET /senales/catalogos/categorias-senal

Listar todas las categorías de señal disponibles.

**Ejemplo Response:**
```json
[
  {
    "id_categoria_senal": 1,
    "nombre_categoria_senal": "RUIDO",
    "nivel": 1,
    "color": "#808080",
    "descripcion": "Señales sin relevancia inmediata"
  },
  {
    "id_categoria_senal": 2,
    "nombre_categoria_senal": "PARACRISIS",
    "nivel": 1,
    "color": "#FFA500",
    "descripcion": "Señales que requieren monitoreo"
  },
  {
    "id_categoria_senal": 3,
    "nombre_categoria_senal": "CRISIS",
    "nivel": 1,
    "color": "#FF0000",
    "descripcion": "Señales críticas que requieren acción inmediata"
  }
]
```

---

### GET /senales/catalogos/categorias-analisis

Listar todas las categorías de análisis (tipos de violencia).

**Ejemplo Response:**
```json
[
  {
    "id": 1,
    "nombre_categoria_analisis": "Reclutamiento, uso y utilización de niñas, niños y adolescentes",
    "palabras_clave_categoria": ["reclutamiento", "menores", "niños"],
    "hashtags_categoria": ["#Reclutamiento", "#Guerrilla"]
  },
  {
    "id": 2,
    "nombre_categoria_analisis": "Violencia política",
    "palabras_clave_categoria": ["líder social", "asesinato", "atentado"]
  },
  {
    "id": 3,
    "nombre_categoria_analisis": "Violencia digital basada en género",
    "palabras_clave_categoria": ["acoso", "ciberacoso", "deepfakes"]
  }
]
```

---

## 🔐 Autenticación

Todos los endpoints requieren autenticación mediante token JWT.

**Headers requeridos:**
```javascript
{
  'Authorization': 'Bearer <tu_token_jwt>',
  'Content-Type': 'application/json'
}
```

**Obtener token:**
```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    nombre_usuario: 'admin',
    contrasena: 'tu_password'
  })
});

const { access_token } = await loginResponse.json();
```

---

## 💡 Ejemplos de Uso Completos

### Ejemplo 1: Listar señales críticas del día

```javascript
async function obtenerAlertasCriticas() {
  const token = localStorage.getItem('token');
  
  try {
    const response = await fetch(
      'http://localhost:8000/api/v1/senales/alertas/criticas?limite=5',
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const alertas = await response.json();
    console.log('Alertas críticas:', alertas);
    return alertas;
  } catch (error) {
    console.error('Error obteniendo alertas:', error);
  }
}
```

### Ejemplo 2: Filtrar señales con múltiples criterios

```javascript
async function filtrarSenales(filtros) {
  const token = localStorage.getItem('token');
  
  const params = new URLSearchParams({
    orden: 'score_desc',
    ...filtros
  });
  
  const response = await fetch(
    `http://localhost:8000/api/v1/senales?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  return await response.json();
}

// Uso:
const senales = await filtrarSenales({
  estado: 'EN_REVISION',
  id_categoria_senal: 3,  // CRISIS
  score_min: 70,
  limit: 20
});
```

### Ejemplo 3: Hook de React con React Query

```javascript
import { useQuery } from '@tanstack/react-query';

const useSenales = (filtros = {}) => {
  return useQuery({
    queryKey: ['senales', filtros],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams(filtros);
      
      const response = await fetch(
        `http://localhost:8000/api/v1/senales?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (!response.ok) {
        throw new Error('Error cargando señales');
      }
      
      return response.json();
    },
    staleTime: 60000, // 1 minuto
    refetchOnWindowFocus: true
  });
};

// Uso en componente:
function ListaSenales() {
  const { data, isLoading, error } = useSenales({
    orden: 'fecha_desc',
    limit: 20
  });
  
  if (isLoading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      {data.items.map(senal => (
        <SenalCard key={senal.id_senal_detectada} senal={senal} />
      ))}
    </div>
  );
}
```

---

## 🎨 Colores por Categoría

Para renderizar las cards con los colores correctos:

```javascript
const getCategoriaColor = (nombreCategoria) => {
  const colores = {
    'RUIDO': '#808080',      // Gris
    'PARACRISIS': '#FFA500', // Naranja
    'CRISIS': '#FF0000'      // Rojo
  };
  return colores[nombreCategoria] || '#CCCCCC';
};

// Uso en componente:
<div 
  style={{
    borderLeft: `4px solid ${getCategoriaColor(senal.categoria_senal.nombre_categoria_senal)}`
  }}
>
  {/* Contenido de la card */}
</div>
```

---

## 📊 Documentación Interactiva (Swagger)

Para ver la documentación interactiva completa:

```
http://localhost:8000/docs
```

Aquí puedes probar todos los endpoints directamente desde el navegador.

---

## 🐛 Manejo de Errores

Todos los endpoints retornan errores en formato consistente:

```json
{
  "detail": "Señal 999 no encontrada"
}
```

**Códigos de estado HTTP:**
- `200 OK`: Operación exitosa
- `201 Created`: Recurso creado
- `400 Bad Request`: Datos inválidos
- `401 Unauthorized`: No autenticado
- `403 Forbidden`: Sin permisos
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor

---

## 📝 Notas Importantes

1. **Autenticación**: Todos los endpoints requieren token JWT válido
2. **Paginación**: Por defecto `skip=0, limit=100`
3. **Ordenamiento**: Por defecto `fecha_desc`
4. **Timestamps**: Todos en formato ISO 8601 (UTC)
5. **Decimales**: Score de riesgo con 2 decimales (0.00 - 100.00)

---

**Última actualización:** 10 de diciembre de 2025  
**Versión API:** v1  
**Puerto desarrollo:** 8000
