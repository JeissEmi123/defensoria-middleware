#  Guía de Seguridad - Defensoria Middleware

##  CHECKLIST OBLIGATORIO ANTES DE PRODUCCIÓN

###  1. Configuración de Secrets (CRÍTICO)

#### Generar Secret Keys Seguros
```bash
# Generar SECRET_KEY
openssl rand -hex 32

# Generar JWT_SECRET_KEY
openssl rand -hex 32

# Generar JWT_REFRESH_SECRET_KEY
openssl rand -hex 32
```

#### Archivo .env (NUNCA COMMITEAR)
Crear archivo `.env` con los valores generados:

```dotenv
# ============================================
# SEGURIDAD - VALORES OBLIGATORIOS
# ============================================
SECRET_KEY=<tu-secret-key-de-64-caracteres>
JWT_SECRET_KEY=<tu-jwt-secret-key-de-64-caracteres>
JWT_REFRESH_SECRET_KEY=<tu-jwt-refresh-secret-key-de-64-caracteres>

# ============================================
# BASE DE DATOS
# ============================================
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/db
POSTGRES_USER=defensoria_prod
POSTGRES_PASSWORD=<contraseña-fuerte-generada>
POSTGRES_DB=defensoria_db

# ============================================
# USUARIO ADMINISTRADOR INICIAL
# ============================================
ADMIN_DEFAULT_PASSWORD=<contraseña-temporal-fuerte>
```

** Verificar:**
- [ ] SECRET_KEY tiene mínimo 64 caracteres
- [ ] JWT_SECRET_KEY es diferente de SECRET_KEY
- [ ] JWT_REFRESH_SECRET_KEY es diferente de los anteriores
- [ ] Contraseñas de base de datos son únicas y fuertes
- [ ] `.env` está en `.gitignore`

---

###  2. Base de Datos

#### PostgreSQL en Producción
```bash
# Crear usuario de base de datos CON contraseña fuerte
CREATE USER defensoria_prod WITH PASSWORD 'your-strong-password-here';
CREATE DATABASE defensoria_db OWNER defensoria_prod;
GRANT ALL PRIVILEGES ON DATABASE defensoria_db TO defensoria_prod;
```

** Verificar:**
- [ ] Usuario de BD NO es `postgres`
- [ ] Contraseña NO es `postgres`, `admin`, `123456`, etc.
- [ ] BD está en red privada (no expuesta públicamente)
- [ ] Backups automáticos configurados
- [ ] SSL/TLS habilitado para conexiones

---

###  3. CORS y Dominios

#### Configurar Dominios Permitidos
```dotenv
# Solo dominios de producción
ALLOWED_ORIGINS=["https://app.defensoria.gob.pe","https://api.defensoria.gob.pe"]
ALLOWED_HOSTS=["app.defensoria.gob.pe","api.defensoria.gob.pe"]
```

** Verificar:**
- [ ] NO hay `localhost` en ALLOWED_ORIGINS
- [ ] NO hay `*` (wildcard) en producción
- [ ] Usar HTTPS exclusivamente
- [ ] Protocolo `http://` removido

---

###  4. Autenticación y Autorización

#### Tokens JWT
```dotenv
ACCESS_TOKEN_EXPIRE_MINUTES=15    # Reducir en producción
REFRESH_TOKEN_EXPIRE_DAYS=7       # Máximo recomendado
```

#### Bloqueo de Cuentas
```dotenv
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_MINUTES=30
```

** Verificar:**
- [ ] Tokens de acceso expiran en máximo 30 minutos
- [ ] Refresh tokens expiran en máximo 7 días
- [ ] Rate limiting configurado
- [ ] Bloqueo de cuentas activo

---

###  5. HTTPS y Certificados SSL

#### Habilitar HTTPS Obligatorio
```dotenv
ENABLE_HTTPS_REDIRECT=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=strict
```

** Verificar:**
- [ ] Certificado SSL válido instalado
- [ ] Redirección HTTP → HTTPS activa
- [ ] Cookies marcadas como `Secure`
- [ ] HSTS (HTTP Strict Transport Security) habilitado

---

###  6. Logging y Auditoría

```dotenv
LOG_LEVEL=WARNING          # En producción, NO usar DEBUG
ENABLE_AUDIT_LOG=true      # Obligatorio
LOG_FORMAT=json            # Mejor para análisis
```

** Verificar:**
- [ ] DEBUG deshabilitado (`DEBUG=false`)
- [ ] Logs de auditoría activos
- [ ] Logs se guardan en sistema externo
- [ ] Rotación de logs configurada
- [ ] NO se loguean contraseñas ni tokens

---

###  7. Docker en Producción

#### Variables de Entorno Docker
```bash
# Crear archivo .env.prod
cp .env.example .env.prod
# Editar .env.prod con valores de producción

# Iniciar con archivo específico
docker-compose --env-file .env.prod up -d
```

** Verificar:**
- [ ] Contenedores NO corren como root
- [ ] Volúmenes persistentes configurados
- [ ] Red privada entre servicios
- [ ] Límites de recursos establecidos
- [ ] Health checks configurados

---

###  8. Usuario Administrador

#### Primer Login
```bash
# 1. Inicializar BD con contraseña temporal
ADMIN_DEFAULT_PASSWORD="Temporal123!@#" python scripts/init_db.py

# 2. Inmediatamente cambiar contraseña
# Login → Perfil → Cambiar Contraseña
```

** Verificar:**
- [ ] Contraseña temporal cambiada inmediatamente
- [ ] Usuario `admin` renombrado si es posible
- [ ] MFA (autenticación multifactor) habilitado
- [ ] Permisos de superusuario restringidos

---

###  9. LDAP / Azure AD (Opcional)

#### Configuración LDAP Seguro
```dotenv
LDAP_ENABLED=true
LDAP_SERVER=ldaps://ldap.domain.com  # Usar LDAPS (puerto 636)
LDAP_USE_SSL=true
LDAP_BIND_PASSWORD=<service-account-password>
```

** Verificar:**
- [ ] Usar LDAPS (no LDAP sin cifrar)
- [ ] Cuenta de servicio con permisos mínimos
- [ ] Certificado SSL del servidor LDAP validado
- [ ] Timeout configurado (max 10 segundos)

---

###  10. Checklist Final de Producción

#### Antes de Deploy
- [ ] `.env` creado con valores únicos
- [ ] Todas las SECRET_KEY generadas con `openssl`
- [ ] Contraseñas de BD cambiadas
- [ ] CORS configurado solo para dominios reales
- [ ] HTTPS habilitado y forzado
- [ ] DEBUG=false
- [ ] Logs de auditoría activos
- [ ] Rate limiting configurado
- [ ] Backups automáticos configurados
- [ ] Plan de respuesta a incidentes documentado

#### Después de Deploy
- [ ] Cambiar contraseña de admin
- [ ] Verificar logs de acceso
- [ ] Prueba de penetración realizada
- [ ] Monitoreo activo configurado
- [ ] Alertas de seguridad configuradas

---

##  Valores NUNCA Usar en Producción

```bash
#  PROHIBIDO
admin / admin
postgres / postgres
root / root
admin / 123456
admin / password

#  PROHIBIDO - Secret Keys
"CHANGE-THIS-IN-PRODUCTION"
"secret"
"development"
"test"
```

---

##  Contacto de Seguridad

En caso de encontrar vulnerabilidades:
- Email: security@defensoria.gob.pe
- No publicar vulnerabilidades públicamente
- Esperar respuesta antes de divulgar

---

##  Referencias

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

**Última actualización:** 24 de noviembre de 2025  
**Versión:** 1.0.0
