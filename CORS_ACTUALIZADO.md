# ✅ CORS Actualizado para Frontend en Cloud Run

**Fecha:** 3 de diciembre de 2025  
**Frontend URL:** https://defensoria-frontend-411798681660.us-central1.run.app

---

## 🎯 Cambios Realizados

### 1. Archivo Modificado: `app/main.py`

Se agregó el origen del frontend desplegado en Cloud Run:

```python
ALLOWED_ORIGINS = [
    # Frontend en Cloud Run (Producción)
    "https://defensoria-frontend-411798681660.us-central1.run.app",
    
    # Desarrollo local (mantiene compatibilidad)
    "http://localhost:3000",
    "http://localhost:3001",
    # ... otros orígenes de desarrollo
]
```

---

## 🚀 Cómo Desplegar los Cambios

### Opción 1: Script Automático (Recomendado)

```powershell
.\actualizar-cors.ps1
```

### Opción 2: Manual

```powershell
# 1. Build imagen
docker build -t gcr.io/sat-defensoriapueblo/defensoria-middleware:latest .

# 2. Push a GCR
docker push gcr.io/sat-defensoriapueblo/defensoria-middleware:latest

# 3. Deploy a Cloud Run
gcloud run deploy defensoria-middleware `
    --image gcr.io/sat-defensoriapueblo/defensoria-middleware:latest `
    --region us-central1
```

---

## 🧪 Verificar que Funciona

### Desde el Frontend

1. Abre: https://defensoria-frontend-411798681660.us-central1.run.app
2. Intenta hacer login con:
   - Usuario: `admin`
   - Password: `Admin123!`
3. Verifica en DevTools (F12) → Network que no hay errores CORS

### Desde PowerShell (Test Manual)

```powershell
# Test preflight CORS
$headers = @{
    "Origin" = "https://defensoria-frontend-411798681660.us-central1.run.app"
    "Access-Control-Request-Method" = "POST"
    "Access-Control-Request-Headers" = "Content-Type,Authorization"
}

Invoke-WebRequest `
    -Uri "https://defensoria-middleware-411798681660.us-central1.run.app/auth/login" `
    -Method OPTIONS `
    -Headers $headers
```

Deberías ver en la respuesta:
```
Access-Control-Allow-Origin: https://defensoria-frontend-411798681660.us-central1.run.app
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

---

## 📋 Configuración CORS Actual

| Parámetro | Valor |
|-----------|-------|
| **allow_origins** | Frontend Cloud Run + localhost |
| **allow_credentials** | `True` (permite JWT) |
| **allow_methods** | `["*"]` (todos los métodos) |
| **allow_headers** | `["*"]` (todos los headers) |
| **max_age** | `3600` (1 hora cache) |

---

## 🔐 Ejemplo de Uso desde Frontend

### JavaScript/Fetch

```javascript
const API_URL = 'https://defensoria-middleware-411798681660.us-central1.run.app';

// Login
const login = async () => {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      nombre_usuario: 'admin',
      contrasena: 'Admin123!'
    })
  });
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  return data;
};

// Request autenticado
const getProfile = async () => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`${API_URL}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};
```

### React/Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://defensoria-middleware-411798681660.us-central1.run.app',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para agregar token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

---

## 🐛 Troubleshooting

### Error: "CORS policy blocked"

**Causa:** Backend no desplegado con nueva configuración

**Solución:**
```powershell
.\actualizar-cors.ps1
```

### Error: "No Access-Control-Allow-Origin header"

**Causa:** URL del frontend no coincide exactamente

**Verificar:**
- URL debe ser exacta (con/sin trailing slash)
- Protocolo correcto (https vs http)
- Dominio completo

**Solución:** Revisar `app/main.py` línea 19

### Error: "Credentials flag is true but header missing"

**Causa:** Frontend no envía credentials

**Solución en Frontend:**
```javascript
fetch(url, {
  credentials: 'include',  // Agregar esta línea
  // ... resto de config
})
```

---

## 📊 Checklist de Despliegue

- [x] Actualizar `app/main.py` con URL del frontend
- [ ] Ejecutar `.\actualizar-cors.ps1`
- [ ] Esperar 1-2 minutos a que Cloud Run actualice
- [ ] Probar login desde frontend
- [ ] Verificar en DevTools que no hay errores CORS
- [ ] Probar endpoints protegidos (GET /auth/me)
- [ ] Documentar en README principal

---

## 📞 Información de Contacto

**Backend API:** https://defensoria-middleware-411798681660.us-central1.run.app  
**Frontend:** https://defensoria-frontend-411798681660.us-central1.run.app  
**Proyecto GCP:** sat-defensoriapueblo  
**Región:** us-central1

---

**Próximos pasos:**
1. Ejecutar `.\actualizar-cors.ps1`
2. Probar login desde el frontend
3. Reportar cualquier error CORS que persista
