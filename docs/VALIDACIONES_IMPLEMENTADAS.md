# Validaciones Implementadas - Sistema de Autenticación

##  Resumen

Este documento detalla todas las validaciones de seguridad y negocio implementadas en el sistema de autenticación de la Defensoría del Pueblo.

---

##  1. Validaciones de Usuario

### 1.1 Nombre de Usuario
 **Implementado**

- Mínimo 3 caracteres, máximo 50
- Solo letras, números, guiones y guiones bajos
- No puede ser un email (no contener @ o .)
- No puede empezar con número
- No puede ser palabra reservada: admin, root, system, administrator, superuser, user, test, demo, guest, public, api, null, undefined, default, config, settings
- Validación contra inyección SQL y XSS
- Conversión automática a minúsculas

### 1.2 Email
 **Implementado**

- Formato RFC 5322 válido
- Máximo 254 caracteres
- No puede contener caracteres peligrosos: < > " ' \ ; ( )
- No permite dominios temporales/desechables: tempmail.com, 10minutemail.com, guerrillamail.com, mailinator.com, throwaway.email, temp-mail.org
- Conversión automática a minúsculas
- Sanitización de espacios
- Validación de unicidad en base de datos

### 1.3 Nombre Completo
 **Implementado**

- Mínimo 3 caracteres, máximo 100
- No puede contener números
- Solo letras, espacios, acentos y caracteres especiales permitidos: ' -
- No permite múltiples espacios consecutivos
- Validación contra inyección SQL y XSS

---

##  2. Validaciones de Contraseña

### 2.1 Fortaleza de Contraseña
**Implementado**

- Mínimo 12 caracteres, máximo 128
- Al menos 1 letra mayúscula
- Al menos 1 letra minúscula
- Al menos 1 número
- Al menos 1 carácter especial: ! @ # $ % ^ & * ( ) _ + - = [ ] { } ; ' : " \ | , . < > / ?
- No puede contener el nombre de usuario
- No puede contener partes del email
- No puede contener secuencias comunes: abcd, 1234, qwer, asdf, zxcv
- No puede contener patrones débiles: 123456, password, qwerty, abc123, letmein, welcome, monkey, dragon, master, sunshine
- No más de 3 caracteres repetidos consecutivos

### 2.2 Historial de Contraseñas
 **Implementado**

- No permite reutilizar las últimas 5 contraseñas (configurable)
- Almacenamiento seguro con bcrypt
- Limpieza automática de historial antiguo
- Configurable mediante `ENFORCE_PASSWORD_HISTORY=true`
- Número de contraseñas a recordar: `PASSWORD_HISTORY_COUNT=5`

### 2.3 Expiración de Contraseña
 **Implementado** (Deshabilitado por defecto)

- Cambio obligatorio cada 90 días (configurable)
- Configurable mediante `ENFORCE_PASSWORD_EXPIRATION=true`
- Días de expiración: `PASSWORD_EXPIRATION_DAYS=90`

---

##  3. Validaciones de Negocio

### 3.1 Límite de Usuarios
 **Implementado** (Deshabilitado por defecto)

- Límite máximo de usuarios en el sistema: 1000 (configurable)
- Configurable mediante `ENFORCE_USER_LIMIT=true`
- Límite: `MAX_USERS_LIMIT=1000`

### 3.2 Protección de Administradores
 **Implementado**

- No se puede eliminar el último administrador del sistema
- Validación automática al intentar eliminar usuario con rol de superusuario
- Cuenta administradores activos antes de permitir eliminación

### 3.3 Auto-protección
 **Implementado**

- Un usuario no puede eliminarse a sí mismo
- Validación en endpoint de eliminación

---

##  4. Validaciones de Sesión

### 4.1 Límite de Sesiones Activas
 **Implementado**

- Máximo 5 sesiones activas por usuario (configurable)
- Cierre automático de sesión más antigua al exceder límite
- Configurable mediante `MAX_ACTIVE_SESSIONS_PER_USER=5`

### 4.2 Timeout de Inactividad
 **Configurado** (Pendiente implementación completa)

- Tiempo de inactividad: 60 minutos (configurable)
- Configurable mediante `SESSION_INACTIVITY_TIMEOUT_MINUTES=60`

---

##  5. Validaciones de Seguridad

### 5.1 Inyección SQL
 **Implementado**

- Detección de patrones SQL maliciosos
- Validación en todos los inputs de texto
- Patrones detectados: ', --, ;, ||, *, union, select, insert, update, delete, drop, create, alter, exec, execute, or, and

### 5.2 Cross-Site Scripting (XSS)
 **Implementado**

- Detección de patrones XSS
- Validación en todos los inputs de texto
- Patrones detectados: <script>, javascript:, on*=, <iframe>, <object>, <embed>

### 5.3 Caracteres de Control
 **Implementado**

- Remoción de caracteres de control no permitidos
- Permite solo: \n, \r, \t
- Validación en sanitización de inputs

### 5.4 Rate Limiting
 **Implementado**

- Login: 5 intentos por minuto
- Crear usuario: 10 por minuto
- Actualizar usuario: 10 por minuto
- Eliminar usuario: 5 por minuto
- Cambiar contraseña: 3 por hora
- Cerrar todas las sesiones: 3 por hora

### 5.5 Account Lockout
 **Implementado**

- Bloqueo automático tras 5 intentos fallidos (configurable)
- Duración del bloqueo: 30 minutos (configurable)
- Desbloqueo automático después del tiempo
- Desbloqueo manual por administrador
- Configurable mediante `MAX_LOGIN_ATTEMPTS=5` y `ACCOUNT_LOCKOUT_MINUTES=30`

---

##  6. Validaciones de Entrada

### 6.1 Sanitización General
**Implementado**

- Truncado a longitud máxima (255 caracteres por defecto)
- Remoción de caracteres no imprimibles
- Trim de espacios en blanco
- Aplicado a todos los inputs de texto

### 6.2 Validación de Longitud
 **Implementado**

| Campo | Mínimo | Máximo |
|-------|--------|--------|
| Nombre de usuario | 3 | 50 |
| Email | - | 254 |
| Nombre completo | 3 | 100 |
| Contraseña | 12 | 128 |

---

##  7. Configuración

### Variables de Entorno

```bash
# Límites de Sesión
MAX_ACTIVE_SESSIONS_PER_USER=5
SESSION_INACTIVITY_TIMEOUT_MINUTES=60

# Política de Contraseñas
PASSWORD_HISTORY_COUNT=5
PASSWORD_EXPIRATION_DAYS=90
ENFORCE_PASSWORD_HISTORY=true
ENFORCE_PASSWORD_EXPIRATION=false

# Límites de Usuarios
MAX_USERS_LIMIT=1000
ENFORCE_USER_LIMIT=false

# Account Lockout
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_MINUTES=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
AUTH_RATE_LIMIT_PER_MINUTE=5
```

---

## 8. Testing

### Probar Validaciones de Usuario

```bash
# Nombre de usuario inválido (email)
curl -X POST http://localhost:8000/usuarios/create \
  -H "Content-Type: application/json" \
  -d '{"nombre_usuario":"test@email.com","email":"test@test.com","contrasena":"TestPassword123!","activo":true}'

# Nombre de usuario reservado
curl -X POST http://localhost:8000/usuarios/create \
  -H "Content-Type: application/json" \
  -d '{"nombre_usuario":"admin","email":"test@test.com","contrasena":"TestPassword123!","activo":true}'

# Email temporal
curl -X POST http://localhost:8000/usuarios/create \
  -H "Content-Type: application/json" \
  -d '{"nombre_usuario":"testuser","email":"test@tempmail.com","contrasena":"TestPassword123!","activo":true}'
```

### Probar Validaciones de Contraseña

```bash
# Contraseña débil (sin mayúsculas)
curl -X POST http://localhost:8000/usuarios/create \
  -H "Content-Type: application/json" \
  -d '{"nombre_usuario":"testuser","email":"test@test.com","contrasena":"testpassword123!","activo":true}'

# Contraseña con nombre de usuario
curl -X POST http://localhost:8000/usuarios/create \
  -H "Content-Type: application/json" \
  -d '{"nombre_usuario":"testuser","email":"test@test.com","contrasena":"Testuser123!","activo":true}'

# Contraseña con patrón débil
curl -X POST http://localhost:8000/usuarios/create \
  -H "Content-Type: application/json" \
  -d '{"nombre_usuario":"testuser","email":"test@test.com","contrasena":"Password123!","activo":true}'
```

---

##  9. Mensajes de Error

Todos los errores de validación retornan:

```json
{
  "error": "VAL_001",
  "message": "Descripción del error específico",
  "details": {}
}
```

**Código HTTP:** 422 Unprocessable Entity

---

##  10. Próximas Mejoras

- [ ] Validación de dominio de email (DNS lookup)
- [ ] Integración con Have I Been Pwned API
- [ ] Detección de patrones de uso anormales
- [ ] Validación de cambio de user agent en sesión
- [ ] Validación de cambio de IP en sesión
- [ ] Notificaciones por email de eventos de seguridad
- [ ] Dashboard de métricas de seguridad

---

**Última actualización:** 1 de diciembre de 2025  
**Versión:** 2.0.0
