# Sistema de Autenticación Completo - Defensoría Middleware

## Resumen Ejecutivo

Sistema de autenticación enterprise para aplicación expuesta a internet con los más altos estándares de seguridad. Diseñado para comenzar con autenticación local contra PostgreSQL y migrar a Azure Active Directory sin cambios en la aplicación.

## Tabla de Contenidos

1. [Arquitectura](#arquitectura)
2. [Flujos de Autenticación](#flujos-de-autenticación)
3. [Endpoints API](#endpoints-api)
4. [Gestión de Usuarios](#gestión-de-usuarios)
5. [Recuperación de Contraseña](#recuperación-de-contraseña)
6. [Seguridad](#seguridad)
7. [Migración a Azure AD](#migración-a-azure-ad)
8. [Testing](#testing)

---

## Arquitectura

### Patrón de Diseño

**Strategy Pattern** para proveedores de autenticación:

```
AuthService
     AuthProviderFactory
        LocalAuthProvider (Base de Datos)
        LDAPAuthProvider (LDAP/AD local)
        AzureADAuthProvider (Azure Active Directory)
     TokenManager (JWT)
     PasswordResetService
```

### Capas de la Aplicación

```
Presentación (API)
     /api/auth              → Autenticación (login, logout, refresh)
     /api/usuarios          → Gestión de usuarios (CRUD)
     /api/password-reset    → Recuperación de contraseña
     /api/rbac              → Roles y permisos

Lógica de Negocio (Services)
     AuthService            → Orquestación de autenticación
     UserService            → CRUD y gestión de usuarios
     PasswordResetService   → Reset de contraseña
     RBACService            → Autorización

Datos (Models)
     Usuario                → Usuario (15 campos)
     Sesion                 → Sesión activa (13 campos)
     Rol                    → Rol RBAC (7 campos)
     Permiso                → Permiso RBAC (7 campos)
     EventoAuditoria        → Auditoría (10 campos)
```

---

## Flujos de Autenticación

### 1. Login con Base de Datos Local

```
Cliente → POST /api/auth/login
    ↓
    {
        "nombre_usuario": "juan.perez",
        "contrasena": "MiPassword123!"
    }
    ↓
AuthService.autenticar_usuario()
    ↓
    1. Validar entrada
    2. Buscar usuario en BD
    3. Verificar usuario activo
    4. Verificar si está bloqueado (intentos fallidos)
    5. Verificar contraseña (bcrypt)
    6. Crear sesión y tokens JWT
    7. Registrar auditoría
    ↓
    {
        "access_token": "eyJ0...",
        "refresh_token": "eyJ0...",
        "token_type": "bearer",
        "expires_in": 1800
    }
```

### 2. Login con LDAP/AD

```
Cliente → POST /api/auth/login
    ↓
AuthService.autenticar_usuario()
    ↓
    1. Usuario no existe en BD local
    2. Intentar con LDAPAuthProvider
    3. LDAP valida credenciales
    4. Crear usuario local desde datos LDAP
    5. Crear sesión y tokens
    ↓
Usuario sincronizado y autenticado
```

### 3. Login con Azure AD (Futuro)

```
Cliente → POST /api/auth/login
    ↓
AuthService.autenticar_usuario()
    ↓
    1. Usuario configurado con tipo_autenticacion = "azure_ad"
    2. AzureADAuthProvider.autenticar()
    3. MSAL valida contra Azure AD
    4. Actualizar info de usuario desde Azure
    5. Crear sesión y tokens
    ↓
Usuario autenticado con Azure AD
```

---

## Endpoints API

### Autenticación Core

#### **POST /api/auth/login**

Login de usuario.

**Rate Limit:** 5 intentos por minuto

**Request:**
```json
{
    "nombre_usuario": "juan.perez",
    "contrasena": "MiPassword123!"
}
```

**Response (200):**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
}
```

**Errores:**
- `401`: Credenciales inválidas
- `403`: Usuario inactivo o bloqueado
- `429`: Demasiados intentos

---

#### **POST /api/auth/refresh**

Refresca el access token usando refresh token.

**Request:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200):**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
}
```

---

#### **POST /api/auth/logout**

Cierra sesión del usuario actual.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
    "mensaje": "Sesión cerrada exitosamente"
}
```

---

#### **GET /api/auth/me**

Obtiene información del usuario autenticado.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
    "id": 1,
    "nombre_usuario": "juan.perez",
    "email": "juan.perez@defensoria.gov.co",
    "nombre_completo": "Juan Pérez",
    "activo": true,
    "es_superusuario": false,
    "tipo_autenticacion": "local",
    "roles": ["admin", "operador"],
    "permisos": ["usuarios.ver", "usuarios.crear", "reportes.ver"]
}
```

---

### Gestión de Usuarios

#### **POST /api/usuarios**

Crea un nuevo usuario.

**Permisos:** `usuarios.crear`

**Rate Limit:** 10/minuto

**Request:**
```json
{
    "nombre_usuario": "maria.lopez",
    "email": "maria.lopez@defensoria.gov.co",
    "nombre_completo": "María López",
    "contrasena": "Password123!@#",
    "activo": true,
    "es_superusuario": false
}
```

**Response (201):**
```json
{
    "id": 5,
    "nombre_usuario": "maria.lopez",
    "email": "maria.lopez@defensoria.gov.co",
    "nombre_completo": "María López",
    "activo": true,
    "es_superusuario": false,
    "tipo_autenticacion": "local",
    "fecha_creacion": "2024-01-15T10:30:00Z",
    "fecha_actualizacion": "2024-01-15T10:30:00Z",
    "ultimo_acceso": null
}
```

---

#### **GET /api/usuarios**

Lista usuarios con paginación.

**Permisos:** `usuarios.ver`

**Query Parameters:**
- `skip` (int): Offset para paginación (default: 0)
- `limit` (int): Cantidad de resultados (default: 100, max: 1000)
- `activo` (bool): Filtrar por estado activo

**Example:**
```
GET /api/usuarios?skip=0&limit=50&activo=true
```

**Response (200):**
```json
[
    {
        "id": 1,
        "nombre_usuario": "admin",
        "email": "admin@defensoria.gov.co",
        "nombre_completo": "Administrador",
        "activo": true,
        "es_superusuario": true,
        "tipo_autenticacion": "local",
        "fecha_creacion": "2024-01-01T00:00:00Z",
        "ultimo_acceso": "2024-01-15T09:00:00Z"
    },
    ...
]
```

---

#### **PUT /api/usuarios/{id}**

Actualiza un usuario existente.

**Permisos:** `usuarios.editar`

**Rate Limit:** 10/minuto

**Request:**
```json
{
    "email": "nuevo.email@defensoria.gov.co",
    "nombre_completo": "Juan Pérez Actualizado",
    "activo": false
}
```

**Response (200):**
```json
{
    "id": 1,
    "nombre_usuario": "juan.perez",
    "email": "nuevo.email@defensoria.gov.co",
    "nombre_completo": "Juan Pérez Actualizado",
    "activo": false,
    ...
}
```

---

#### **DELETE /api/usuarios/{id}**

Elimina un usuario (soft delete).

**Permisos:** `usuarios.eliminar`

**Rate Limit:** 5/minuto

**Response (200):**
```json
{
    "mensaje": "Usuario eliminado exitosamente"
}
```

---

#### **POST /api/usuarios/me/cambiar-contrasena**

Cambia la contraseña del usuario actual.

**Rate Limit:** 3/hora

**Request:**
```json
{
    "contrasena_actual": "OldPassword123!",
    "contrasena_nueva": "NewPassword456!@#",
    "contrasena_confirmacion": "NewPassword456!@#"
}
```

**Response (200):**
```json
{
    "mensaje": "Contraseña actualizada exitosamente"
}
```

**Errores:**
- `401`: Contraseña actual incorrecta
- `400`: Nueva contraseña no cumple requisitos
- `429`: Demasiados intentos

---

### Gestión de Sesiones

#### **GET /api/usuarios/me/sesiones**

Lista sesiones activas del usuario actual.

**Response (200):**
```json
[
    {
        "id": 123,
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 ...",
        "fecha_creacion": "2024-01-15T08:00:00Z",
        "fecha_ultimo_acceso": "2024-01-15T10:30:00Z",
        "fecha_expiracion": "2024-01-22T08:00:00Z"
    },
    ...
]
```

---

#### **DELETE /api/usuarios/me/sesiones/{sesion_id}**

Cierra una sesión específica.

**Response (200):**
```json
{
    "mensaje": "Sesión cerrada exitosamente"
}
```

---

#### **DELETE /api/usuarios/me/sesiones**

Cierra todas las sesiones excepto la actual.

**Response (200):**
```json
{
    "mensaje": "Todas las sesiones cerradas",
    "sesiones_cerradas": 3
}
```

---

### Recuperación de Contraseña

#### **POST /api/password-reset/solicitar**

Solicita un token de reset de contraseña.

**Rate Limit:** 3/hora por IP

**Request:**
```json
{
    "email": "juan.perez@defensoria.gov.co"
}
```

**Response (200):**
```json
{
    "mensaje": "Si el email existe, recibirás instrucciones para resetear tu contraseña",
    "token": "abc123..." // Solo en desarrollo
}
```

**Notas de Seguridad:**
- En producción, **siempre** retorna éxito (previene enumeración de usuarios)
- Token expira en 1 hora
- Solo funciona para usuarios con `tipo_autenticacion = "local"`

---

#### **POST /api/password-reset/resetear**

Resetea la contraseña usando un token válido.

**Rate Limit:** 5/hora por IP

**Request:**
```json
{
    "token": "abc123...",
    "nueva_contrasena": "NewSecurePassword123!@#",
    "confirmacion_contrasena": "NewSecurePassword123!@#"
}
```

**Response (200):**
```json
{
    "mensaje": "Contraseña actualizada exitosamente"
}
```

**Errores:**
- `400`: Token inválido o expirado
- `400`: Contraseña no cumple requisitos

---

## Seguridad

### Hashing de Contraseñas

**Algoritmo:** bcrypt con 12 rounds

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hash_contrasena = pwd_context.hash("password")
valido = pwd_context.verify("password", hash_contrasena)
```

### Requisitos de Contraseña

- **Longitud mínima:** 12 caracteres
- **Debe contener:**
  - Al menos 1 mayúscula
  - Al menos 1 minúscula
  - Al menos 1 número
  - Al menos 1 carácter especial
- **No puede:**
  - Contener el nombre de usuario
  - Ser igual a las últimas 3 contraseñas

**Validación:**
```python
from app.core.security import validate_password_strength

try:
    validate_password_strength("MiPassword123!@#")
    # Contraseña válida
except ValidationError as e:
    # Contraseña débil
    print(e.detail)
```

---

### Bloqueo de Cuenta

**Política:**
- **5 intentos fallidos** → Bloqueo automático
- **Duración del bloqueo:** 30 minutos
- **Reset automático:** Tras login exitoso

**Campos en modelo Usuario:**
```python
intentos_login_fallidos = Column(Integer, default=0)
fecha_bloqueo = Column(DateTime, nullable=True)
```

**Comportamiento:**
```python
if usuario.intentos_login_fallidos >= 5:
    if datetime.utcnow() - usuario.fecha_bloqueo < timedelta(minutes=30):
        raise AuthenticationError("Usuario bloqueado")
```

---

### JWT Tokens

#### Access Token

- **Duración:** 30 minutos
- **Uso:** Autenticación en cada request
- **Claims:**
  ```json
  {
      "sub": "juan.perez",
      "user_id": 1,
      "tipo_auth": "local",
      "exp": 1705315200,
      "iat": 1705313400,
      "jti": "uuid-unico"
  }
  ```

#### Refresh Token

- **Duración:** 7 días
- **Uso:** Renovar access token sin re-autenticar
- **Rotación:** Nuevo refresh token en cada refresh
- **Revocación:** Almacenado en tabla `sesiones`

---

### Rate Limiting

| Endpoint | Límite | Ventana |
|----------|--------|---------|
| POST /api/auth/login | 5 | 1 minuto |
| POST /api/auth/refresh | 10 | 1 minuto |
| POST /api/usuarios | 10 | 1 minuto |
| POST /api/usuarios/me/cambiar-contrasena | 3 | 1 hora |
| POST /api/password-reset/solicitar | 3 | 1 hora |
| POST /api/password-reset/resetear | 5 | 1 hora |

**Implementación:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
async def login(...):
    ...
```

---

### Headers de Seguridad

Configurados en `SecurityHeadersMiddleware`:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
Referrer-Policy: no-referrer
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

---

### Auditoría

Todos los eventos de autenticación se registran en `eventos_auditoria`:

```python
audit_logger.log_authentication(
    user_id=usuario.id,
    username=usuario.nombre_usuario,
    provider="local",
    result="success",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0 ...",
    reason="login_exitoso"
)
```

**Eventos auditados:**
- Login exitoso/fallido
- Logout
- Cambio de contraseña
- Reset de contraseña
- Creación/modificación de usuarios
- Asignación de roles
- Intentos de acceso no autorizado

---

## Migración a Azure AD

### Configuración Actual (Local DB)

```python
# config.py
class Settings:
    # Autenticación local por defecto
    enable_azure_ad: bool = False
    azure_ad_tenant_id: Optional[str] = None
    azure_ad_client_id: Optional[str] = None
    azure_ad_client_secret: Optional[str] = None
```

### Paso 1: Habilitar Azure AD

```bash
# .env
ENABLE_AZURE_AD=true
AZURE_AD_TENANT_ID=your-tenant-id
AZURE_AD_CLIENT_ID=your-client-id
AZURE_AD_CLIENT_SECRET=your-client-secret
```

### Paso 2: Configurar Usuario para Azure AD

**Opción A: CLI**
```bash
python scripts/manage_users.py cambiar-tipo-auth admin azure_ad --azure-id "user@tenant.onmicrosoft.com"
```

**Opción B: API**
```python
usuario = await obtener_usuario(1)
usuario.tipo_autenticacion = "azure_ad"
usuario.id_externo = "user@tenant.onmicrosoft.com"
await db.commit()
```

### Paso 3: Login con Azure AD

**Sin cambios en el cliente:**

```bash
POST /api/auth/login
{
    "nombre_usuario": "admin",
    "contrasena": "azure-ad-password"
}
```

**Backend automáticamente:**
1. Detecta `tipo_autenticacion = "azure_ad"`
2. Usa `AzureADAuthProvider`
3. Valida contra Azure AD usando MSAL
4. Crea sesión local con JWT

### Paso 4: Migración Gradual

**Escenario típico:**

1. **Fase 1:** Todos los usuarios con autenticación local
2. **Fase 2:** Usuarios administrativos migran a Azure AD
3. **Fase 3:** Usuarios operacionales migran gradualmente
4. **Fase 4:** Todos en Azure AD (opcional mantener local para emergencias)

**Script de migración en lote:**

```bash
python scripts/migrate_to_azure_ad.py --users admin,operador1,operador2
```

### Ventajas del Diseño Multi-Provider

 **Sin downtime**: Cambio en caliente sin reinicio

 **Migración gradual**: Usuario por usuario

 **Coexistencia**: Local y Azure AD simultáneamente

 **Rollback fácil**: Cambiar `tipo_autenticacion` de vuelta a `local`

 **Transparente para clientes**: Mismo endpoint `/login`

---

## Testing

### Tests Unitarios

```python
# tests/test_auth_service.py
import pytest
from app.services.auth_service import AuthService
from app.database.models import Usuario

@pytest.mark.asyncio
async def test_login_exitoso(db_session):
    auth_service = AuthService(db_session)
    
    # Crear usuario de prueba
    usuario = Usuario(
        nombre_usuario="test",
        contrasena_hash=hash_password("Test123!@#"),
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    
    # Intentar login
    tokens = await auth_service.autenticar_usuario("test", "Test123!@#")
    
    assert tokens.access_token
    assert tokens.refresh_token
    assert tokens.expires_in == 1800


@pytest.mark.asyncio
async def test_bloqueo_por_intentos_fallidos(db_session):
    auth_service = AuthService(db_session)
    
    # 5 intentos fallidos
    for _ in range(5):
        with pytest.raises(AuthenticationError):
            await auth_service.autenticar_usuario("test", "wrong")
    
    # Sexto intento debe indicar bloqueo
    with pytest.raises(AuthenticationError, match="bloqueado"):
        await auth_service.autenticar_usuario("test", "Test123!@#")
```

### Tests de Integración

```python
# tests/test_auth_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_flujo_completo_autenticacion(client: AsyncClient):
    # 1. Login
    response = await client.post("/api/auth/login", json={
        "nombre_usuario": "admin",
        "contrasena": "Admin123!@#"
    })
    assert response.status_code == 200
    tokens = response.json()
    
    # 2. Acceder a recurso protegido
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert response.status_code == 200
    
    # 3. Refresh token
    response = await client.post("/api/auth/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })
    assert response.status_code == 200
    
    # 4. Logout
    response = await client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert response.status_code == 200
```

### Tests de Seguridad

```python
# tests/test_security.py
import pytest

def test_password_hashing():
    from app.core.security import hash_password, verify_password
    
    password = "Test123!@#"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    # Hashes deben ser diferentes (salt único)
    assert hash1 != hash2
    
    # Pero ambos validan correctamente
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


def test_password_strength_validation():
    from app.core.security import validate_password_strength
    from app.core.exceptions import ValidationError
    
    # Válidas
    validate_password_strength("SecurePass123!@#")
    
    # Inválidas
    with pytest.raises(ValidationError):
        validate_password_strength("short")  # Muy corta
    
    with pytest.raises(ValidationError):
        validate_password_strength("nouppercase123!")  # Sin mayúsculas
    
    with pytest.raises(ValidationError):
        validate_password_strength("NOLOWERCASE123!")  # Sin minúsculas
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_auth_service.py

# Con coverage
pytest --cov=app --cov-report=html

# Tests de integración solamente
pytest -m integration
```

---

## Monitoreo y Observabilidad

### Logs Estructurados

```python
# Cada evento de autenticación genera logs JSON
logger.info(
    "autenticacion_exitosa",
    user_id=1,
    username="juan.perez",
    ip_address="192.168.1.100",
    provider="local"
)
```

### Métricas Recomendadas

- **Autenticaciones exitosas/fallidas por minuto**
- **Latencia de autenticación (p50, p95, p99)**
- **Usuarios bloqueados por intentos fallidos**
- **Tokens expirados vs refrescados**
- **Sesiones activas por usuario**

### Alertas Recomendadas

 **Crítico:**
- > 10 intentos de login fallidos desde misma IP en 1 minuto
- > 5 usuarios bloqueados en 5 minutos
- Rate limit excedido > 100 veces en 1 minuto

 **Advertencia:**
- Latencia de login > 2 segundos (p95)
- > 100 tokens expirados sin refresh en 1 hora
- > 50 sesiones activas por usuario

---

## Checklist de Producción

### Antes del Deployment

- [ ] `APP_ENV=production` en `.env`
- [ ] `DEBUG=false`
- [ ] `SECRET_KEY` generado con `openssl rand -hex 32`
- [ ] `DATABASE_URL` apunta a PostgreSQL de producción
- [ ] Certificado SSL/TLS configurado
- [ ] Rate limiting habilitado
- [ ] CORS configurado con orígenes permitidos
- [ ] Logs centralizados (ELK, Splunk, etc.)
- [ ] Backups automáticos de BD configurados
- [ ] Migración de Alembic ejecutada
- [ ] Health checks configurados en load balancer

### Post-Deployment

- [ ] Verificar `/health` endpoint
- [ ] Crear usuario admin inicial
- [ ] Probar login/logout
- [ ] Verificar logs de auditoría
- [ ] Configurar alertas de monitoreo
- [ ] Documentar credenciales en vault

---

## Soporte y Mantenimiento

### Comandos Útiles

```bash
# Crear usuario admin
python scripts/manage_users.py crear-admin admin admin@defensoria.gov.co --password "SecurePass123!@#"

# Listar usuarios
python scripts/manage_users.py listar

# Asignar rol
python scripts/manage_users.py asignar-rol admin administrador

# Cambiar contraseña
python scripts/manage_users.py cambiar-contrasena admin

# Backup de BD
python scripts/backup_db.py crear --compress

# Health check de BD
python scripts/health_check_db.py

# Optimizar BD
python scripts/optimize_db.py
```

### Troubleshooting

**Problema:** Usuario bloqueado

```sql
-- Ver intentos fallidos
SELECT nombre_usuario, intentos_login_fallidos, fecha_bloqueo 
FROM usuarios WHERE nombre_usuario = 'juan.perez';

-- Desbloquear manualmente
UPDATE usuarios 
SET intentos_login_fallidos = 0, fecha_bloqueo = NULL 
WHERE nombre_usuario = 'juan.perez';
```

**Problema:** Token expirado

```python
# Cliente debe usar refresh token
POST /api/auth/refresh
{
    "refresh_token": "..."
}
```

**Problema:** Sesiones huérfanas

```sql
-- Limpiar sesiones expiradas
DELETE FROM sesiones 
WHERE fecha_expiracion < NOW() OR (revocada = true AND fecha_expiracion < NOW() - INTERVAL '30 days');
```

---

## Contacto

**Equipo de Desarrollo**
- Email: dev@defensoria.gov.co
- Jira: https://jira.defensoria.gov.co/projects/AUTH
- Confluence: https://wiki.defensoria.gov.co/auth

---

## Changelog

### v1.0.0 (2024-01-15)

 **Nuevas Funcionalidades:**
- Autenticación multi-provider (Local, LDAP, Azure AD)
- Sistema RBAC completo
- Gestión completa de usuarios (CRUD)
- Recuperación de contraseña
- Gestión de sesiones activas
- Bloqueo automático por intentos fallidos
- Rate limiting por endpoint
- Auditoría completa de eventos

 **Seguridad:**
- Bcrypt (12 rounds) para hashing
- JWT con refresh token rotation
- Security headers configurados
- CORS restrictivo
- Validación de contraseña fuerte

 **Observabilidad:**
- Logs estructurados con structlog
- Auditoría en base de datos
- Health checks

 **Base de Datos:**
- PostgreSQL optimizado
- Migraciones con Alembic
- Backups automáticos
- Connection pooling con PgBouncer

---

**Documento generado:** 2024-01-15  
**Versión:** 1.0.0  
**Estado:**  Sistema Completo de Autenticación
