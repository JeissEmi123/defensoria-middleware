# Documentación Técnica - Defensoria Middleware

## 5. BACK-END CONFIGURADO PARA EL CONSUMO DE DATOS

### 5.1 Servicios y endpoints desarrollados

El sistema expone una API REST construida con FastAPI que maneja cuatro áreas principales de funcionalidad. Cada endpoint fue diseñado pensando en la seguridad y escalabilidad del sistema.

**Módulo de Autenticación (/auth)**

El módulo de autenticación es el punto de entrada principal del sistema. Implementamos cinco endpoints que cubren todo el ciclo de vida de una sesión de usuario:

- POST /auth/login: Recibe credenciales del usuario y valida contra múltiples proveedores (local, LDAP, Azure AD). Retorna un par de tokens JWT: uno de acceso con 30 minutos de validez y otro de refresco válido por 7 días. Durante el desarrollo tuvimos que ajustar los tiempos de expiración varias veces hasta encontrar el balance correcto entre seguridad y experiencia de usuario.

- POST /auth/logout: Invalida la sesión actual marcándola como inactiva en la base de datos. Esto fue importante porque inicialmente solo confiábamos en la expiración del token, pero necesitábamos una forma de revocar acceso inmediatamente.

- POST /auth/refresh: Permite obtener un nuevo token de acceso usando el token de refresco. Este endpoint es crítico para mantener sesiones activas sin que el usuario tenga que volver a autenticarse constantemente.

- GET /auth/me: Retorna la información completa del usuario autenticado, incluyendo sus roles y permisos. Los clientes frontend usan este endpoint para personalizar la interfaz según los permisos del usuario.

- GET /auth/providers: Lista los proveedores de autenticación disponibles y activos en el sistema. Útil para interfaces que necesitan mostrar opciones de login dinámicamente.

**Módulo RBAC (/rbac)**

El control de acceso basado en roles fue uno de los componentes más complejos de implementar. Terminamos con 13 endpoints que permiten gestionar roles, permisos y sus asignaciones:

Para roles tenemos operaciones CRUD completas: crear, listar, obtener por ID, actualizar y eliminar (soft delete). Cada rol puede tener múltiples permisos asociados y un usuario puede tener múltiples roles.

Los permisos se gestionan de forma similar pero son más estáticos. Definimos permisos granulares como "usuarios.crear", "usuarios.leer", "roles.actualizar", etc. Esto nos da flexibilidad para controlar acceso a nivel de operación específica.

Los endpoints de asignación permiten vincular roles a usuarios y verificar si un usuario tiene un permiso o rol específico. Estos últimos son especialmente útiles para validaciones en tiempo real desde el frontend.

**Módulo de Usuarios (/usuarios)**

Este módulo maneja todo el ciclo de vida de los usuarios en el sistema:

- POST /usuarios: Crea nuevos usuarios. Incluye validación de fortaleza de contraseña (mínimo 12 caracteres) y verifica que el nombre de usuario y email sean únicos.

- GET /usuarios: Lista usuarios con paginación. Soporta filtros por estado activo/inactivo. Implementamos paginación porque en pruebas con datos de ejemplo nos dimos cuenta que sin límites la respuesta era muy pesada.

- GET /usuarios/{id}: Obtiene detalles de un usuario específico. Retorna toda la información excepto la contraseña hash.

- PUT /usuarios/{id}: Actualiza información del usuario. No permite cambiar la contraseña por este endpoint, eso se hace por un flujo separado más seguro.

- DELETE /usuarios/{id}: Desactiva el usuario (soft delete). No eliminamos físicamente registros para mantener integridad referencial y auditoría.

También incluimos endpoints para gestión de sesiones del usuario actual y cambio de contraseña con validación de contraseña anterior.

**Módulo de Recuperación de Contraseña (/password)**

Implementamos un flujo seguro de recuperación de contraseña en dos pasos:

- POST /password/solicitar: Genera un token único de recuperación válido por 1 hora. En desarrollo retorna el token directamente, pero en producción solo envía email (cuando tengamos SMTP configurado).

- POST /password/cancelar: Permite a un administrador cancelar tokens de recuperación activos. Útil si un usuario reporta que no solicitó el cambio.

El sistema incluye protección anti-enumeración: siempre retorna éxito aunque el email no exista, para evitar que atacantes descubran emails válidos en el sistema.

### 5.2 Arquitectura lógica del back-end

Adoptamos arquitectura hexagonal (también conocida como puertos y adaptadores) porque necesitábamos un sistema mantenible a largo plazo y que pudiera evolucionar sin romper todo.

**Capa de API (Presentación)**

Esta es la capa más externa. Aquí viven los routers de FastAPI que reciben las peticiones HTTP. Su única responsabilidad es:
- Validar el formato de entrada usando schemas de Pydantic
- Extraer el usuario autenticado del token JWT
- Llamar al servicio correspondiente
- Formatear la respuesta

No hay lógica de negocio aquí. Si necesitamos cambiar de FastAPI a otro framework, solo tocamos esta capa.

**Capa de Aplicación (Servicios)**

Los servicios orquestan la lógica de negocio. Por ejemplo, AuthService maneja todo el flujo de autenticación:
1. Busca el usuario en la base de datos
2. Determina qué proveedor usar (local, LDAP, etc)
3. Valida las credenciales contra ese proveedor
4. Genera los tokens JWT
5. Registra la sesión
6. Registra el evento en auditoría

Cada servicio recibe repositorios por inyección de dependencias. Esto hace que sean fáciles de testear porque podemos inyectar mocks.

**Capa de Dominio (Interfaces)**

Aquí definimos las interfaces (clases abstractas) que los repositorios deben implementar. Por ejemplo, IUsuarioRepository define métodos como:
- obtener_por_nombre_usuario()
- crear()
- actualizar()
- listar()

Esta capa es pura lógica de negocio, sin dependencias de frameworks o bases de datos. Es el corazón del sistema.

**Capa de Infraestructura (Implementaciones)**

Aquí viven las implementaciones concretas:
- Repositorios con SQLAlchemy que hablan con PostgreSQL
- Proveedores de autenticación (LocalAuthProvider, LDAPAuthProvider)
- Integraciones con servicios externos

Si mañana queremos cambiar de PostgreSQL a MongoDB, solo reescribimos los repositorios en esta capa. El resto del sistema no se entera.

**Flujo de una petición típica**

Cuando llega POST /auth/login:
1. El router auth.py valida el JSON con LoginRequest schema
2. Llama a auth_service.autenticar_usuario()
3. El servicio usa usuario_repository.obtener_por_nombre_usuario()
4. El repositorio ejecuta la query SQL con SQLAlchemy
5. El servicio valida la contraseña con el provider correspondiente
6. Genera tokens JWT usando funciones de core/security.py
7. Guarda la sesión usando sesion_repository.crear()
8. Retorna TokenResponse al router
9. El router serializa a JSON y envía al cliente

Esta separación nos salvó varias veces durante el desarrollo. Cuando cambiamos la estructura de la tabla de sesiones, solo tocamos el modelo y el repositorio. Los servicios y la API siguieron funcionando sin cambios.

### 5.3 Gestión de autenticación y seguridad

La seguridad fue prioridad desde el día uno. Implementamos múltiples capas de protección.

**Autenticación Multi-Proveedor**

El sistema soporta tres tipos de autenticación:

Local: Usuario y contraseña almacenados en nuestra base de datos. Las contraseñas se hashean con bcrypt usando factor de trabajo 12. Nunca almacenamos contraseñas en texto plano. Cuando un usuario se registra, bcrypt genera un salt aleatorio y lo incluye en el hash. Esto significa que dos usuarios con la misma contraseña tendrán hashes completamente diferentes.

LDAP/Active Directory: Para organizaciones que ya tienen un directorio corporativo. El sistema valida credenciales contra el servidor LDAP pero mantiene una copia local del usuario para gestionar roles y permisos. Esto fue un requisito porque no todos los atributos que necesitamos están en LDAP.

Azure AD (en desarrollo): Usará OAuth2/OpenID Connect. Ya tenemos la estructura preparada pero falta la implementación completa.

**Tokens JWT**

Usamos JSON Web Tokens para mantener sesiones sin estado. Cada token incluye:
- sub: nombre de usuario
- user_id: ID numérico del usuario
- tipo_auth: proveedor usado (local, ldap, azure_ad)
- exp: timestamp de expiración
- type: "access" o "refresh"

Los tokens se firman con HS256 usando una clave secreta que debe ser única por ambiente. En desarrollo usamos una clave fija pero en producción debe generarse con openssl rand -hex 32.

Implementamos un sistema de dos tokens: access token de corta duración (30 min) y refresh token de larga duración (7 días). Esto limita la ventana de exposición si un token es comprometido.

**Control de Acceso (RBAC)**

El sistema de roles y permisos funciona así:

Un permiso es la unidad mínima de acceso. Tiene un código único como "usuarios.crear" y está asociado a un recurso y una acción.

Un rol agrupa múltiples permisos. Por ejemplo, el rol "Administrador" tiene todos los permisos, mientras que "Usuario" solo tiene permisos de lectura.

Un usuario puede tener múltiples roles. Sus permisos efectivos son la unión de todos los permisos de sus roles.

Implementamos dos formas de validar permisos:

1. Decorador requiere_permisos(): Se aplica a nivel de endpoint. FastAPI lo ejecuta antes de llamar a la función del endpoint.

2. Verificación programática: Los servicios pueden llamar a rbac_service.usuario_tiene_permiso() para validaciones más complejas.

Los superusuarios tienen un bypass: se les permite todo sin verificar permisos específicos. Esto simplifica la administración inicial del sistema.

**Protecciones de Seguridad**

Rate Limiting: Usamos slowapi para limitar peticiones por IP. Los endpoints de autenticación tienen límites más estrictos (10 por minuto) que los de consulta (100 por minuto). Esto previene ataques de fuerza bruta.

Account Lockout: Después de 5 intentos fallidos de login, la cuenta se bloquea automáticamente. Un administrador debe desbloquearla manualmente. Registramos cada intento fallido con timestamp e IP.

Validación de Entrada: Todos los datos de entrada pasan por schemas de Pydantic que validan tipos, longitudes y formatos. Por ejemplo, los nombres de usuario solo permiten caracteres alfanuméricos, guiones y guiones bajos.

CORS: Configurado para aceptar solo orígenes específicos. En desarrollo permitimos localhost, pero en producción debe configurarse con los dominios reales.

Auditoría: Cada operación importante (login, logout, cambio de permisos, etc) se registra en logs estructurados con formato JSON. Incluimos timestamp, usuario, acción, IP y resultado.

HTTPS: En producción el sistema debe correr detrás de un proxy reverso (nginx) que maneje TLS. Incluimos configuración para forzar HTTPS en las cookies de sesión.

**Gestión de Sesiones**

Cada vez que un usuario hace login, creamos un registro en la tabla sesiones con:
- Token de acceso (hasheado)
- Token de refresco (hasheado)
- IP del cliente
- User agent
- Timestamps de creación y expiración

Esto nos permite:
- Ver todas las sesiones activas de un usuario
- Cerrar sesiones específicas remotamente
- Invalidar todos los tokens de un usuario si su cuenta es comprometida
- Auditar desde dónde se conectan los usuarios

Implementamos un script de limpieza (cleanup_expired_tokens.py) que debe ejecutarse periódicamente para eliminar sesiones expiradas y mantener la tabla limpia.

**Recuperación de Contraseña**

El flujo de recuperación usa tokens de un solo uso con expiración de 1 hora:
1. Usuario solicita reset ingresando su email
2. Sistema genera token aleatorio de 32 bytes
3. Token se hashea y guarda en password_reset_tokens
4. Se envía email con link que incluye el token en texto plano
5. Usuario hace click y envía nueva contraseña junto con el token
6. Sistema valida token, verifica que no haya expirado
7. Actualiza contraseña y marca token como usado
8. Invalida todas las sesiones activas del usuario

El sistema incluye protección anti-enumeración: siempre retorna éxito aunque el email no exista. Esto previene que atacantes descubran qué emails están registrados.

## 6. INTEGRACIONES Y COMPONENTES COMPLEMENTARIOS

### 6.1 APIs y servicios externos

El sistema está diseñado para integrarse con servicios externos, aunque algunas integraciones están pendientes de configuración.

**Active Directory / LDAP**

La integración con LDAP permite autenticar usuarios contra un directorio corporativo existente. Usamos la librería python-ldap para conectarnos al servidor.

Configuración requerida en variables de entorno:
- LDAP_SERVER: URL del servidor (ldap://servidor.dominio.com)
- LDAP_PORT: Puerto (389 para LDAP, 636 para LDAPS)
- LDAP_BASE_DN: Base DN para búsquedas (dc=empresa,dc=com)
- LDAP_USER_DN_TEMPLATE: Template para construir el DN del usuario
- LDAP_BIND_USER: Usuario para bind inicial (opcional)
- LDAP_BIND_PASSWORD: Contraseña del usuario de bind

El flujo de autenticación LDAP:
1. Usuario ingresa credenciales
2. Sistema construye el DN usando el template
3. Intenta bind con ese DN y la contraseña
4. Si bind es exitoso, busca atributos del usuario (email, nombre completo)
5. Sincroniza o crea el usuario en la base de datos local
6. Genera tokens JWT normalmente

Decidimos mantener una copia local de usuarios LDAP porque necesitamos gestionar roles y permisos que no existen en el directorio. También nos permite que el sistema siga funcionando si el servidor LDAP está caído (los usuarios no podrán autenticarse pero las sesiones activas siguen válidas).

**Azure AD / OAuth2 (Pendiente)**

Tenemos la estructura preparada para integración con Azure AD usando OAuth2/OpenID Connect. La implementación está en app/auth/providers/azure_ad_provider.py pero aún no está completa.

El flujo planeado:
1. Usuario hace click en "Login con Microsoft"
2. Sistema redirige a Azure AD con client_id y redirect_uri
3. Usuario autentica en Microsoft
4. Azure AD redirige de vuelta con authorization code
5. Sistema intercambia code por access token
6. Obtiene información del usuario del endpoint /me de Microsoft Graph
7. Crea o actualiza usuario local
8. Genera tokens JWT propios

Configuración que se necesitará:
- AZURE_AD_CLIENT_ID: ID de la aplicación registrada en Azure
- AZURE_AD_CLIENT_SECRET: Secret de la aplicación
- AZURE_AD_TENANT_ID: ID del tenant de Azure AD
- AZURE_AD_REDIRECT_URI: URL de callback

**Servidor SMTP (Pendiente)**

Para recuperación de contraseña necesitamos enviar emails. Tenemos el código preparado pero falta configurar el servidor SMTP.

Variables de entorno necesarias:
- SMTP_HOST: Servidor SMTP (smtp.gmail.com, smtp.office365.com, etc)
- SMTP_PORT: Puerto (587 para TLS, 465 para SSL)
- SMTP_USER: Usuario para autenticación
- SMTP_PASSWORD: Contraseña o app password
- SMTP_FROM_EMAIL: Email remitente
- SMTP_FROM_NAME: Nombre del remitente

El sistema usa la librería aiosmtplib para envío asíncrono de emails. Los templates de email están en app/integrations/email_templates.py.

Mientras no esté configurado SMTP, el sistema en modo desarrollo retorna el token de recuperación directamente en la respuesta JSON. Esto es solo para testing, en producción debe deshabilitarse.

**PostgreSQL**

La base de datos es PostgreSQL 15+. Elegimos PostgreSQL por:
- Robustez y confiabilidad probada
- Soporte excelente para JSON (útil para auditoría)
- Índices avanzados (GIN, GIST)
- Transacciones ACID completas
- Comunidad grande y documentación extensa

Usamos SQLAlchemy 2.0 como ORM con el driver asyncpg para operaciones asíncronas. Esto nos da mejor performance que el driver psycopg2 tradicional.

Las migraciones se manejan con Alembic. Cada cambio de schema genera un archivo de migración versionado. Esto nos permite:
- Aplicar cambios de forma controlada
- Revertir cambios si algo sale mal
- Mantener historial de evolución del schema
- Sincronizar múltiples ambientes (dev, staging, prod)

Configuramos índices en columnas frecuentemente consultadas:
- usuarios.nombre_usuario (único)
- usuarios.email (único)
- sesiones.usuario_id
- sesiones.access_token_hash
- password_reset_tokens.token_hash

También tenemos índices compuestos para queries comunes como buscar sesiones activas de un usuario.

### 6.2 Herramientas de despliegue y automatización

**Docker y Docker Compose**

El sistema está completamente dockerizado. Tenemos dos contenedores:

Contenedor de aplicación (app):
- Imagen base: python:3.11-slim
- Instala dependencias de requirements.txt
- Copia código de la aplicación
- Expone puerto 8000
- Ejecuta uvicorn con reload en desarrollo

Contenedor de base de datos (db):
- Imagen: postgres:15-alpine
- Volumen persistente para datos
- Configuración de usuario y base de datos por variables de entorno
- Expone puerto 5432 (solo para desarrollo)

El docker-compose.yml orquesta ambos contenedores:
- Define red interna para comunicación
- Monta volúmenes para persistencia
- Configura variables de entorno
- Establece dependencias (app espera a db)

Para iniciar todo el stack:
```bash
docker-compose up -d
```

El contenedor de aplicación incluye un script de inicio (start-docker.sh) que:
1. Espera a que PostgreSQL esté listo
2. Ejecuta migraciones de Alembic
3. Inicia el servidor uvicorn

Esto asegura que la base de datos esté lista antes de que la aplicación intente conectarse.

**Scripts de Gestión**

Desarrollamos varios scripts para tareas administrativas comunes:

init_db.py: Inicializa la base de datos desde cero. Crea todas las tablas, inserta permisos base y crea el usuario administrador inicial. Debe ejecutarse una sola vez después del primer despliegue.

manage_users.py: CLI interactiva para gestionar usuarios. Permite crear, listar, actualizar, eliminar y desbloquear usuarios sin necesidad de usar la API. Útil para administración inicial o recuperación de emergencia.

backup_db.py: Crea backups de la base de datos usando pg_dump. Genera archivos SQL comprimidos con timestamp. Soporta backup completo o solo schema.

cleanup_expired_tokens.py: Limpia tokens de sesión y recuperación expirados. Debe ejecutarse periódicamente (recomendamos diario) para mantener la base de datos limpia.

health_check_db.py: Verifica conectividad y estado de la base de datos. Útil para monitoreo y troubleshooting.

validate_config.py: Valida que todas las variables de entorno requeridas estén configuradas correctamente antes de desplegar a producción. Verifica que las secret keys sean únicas y suficientemente largas.

Todos estos scripts están en la carpeta scripts/ y pueden ejecutarse directamente con Python o dentro del contenedor Docker.

**Migraciones con Alembic**

Alembic maneja la evolución del schema de base de datos. El flujo típico:

1. Modificar modelos en app/database/models.py
2. Generar migración: `alembic revision --autogenerate -m "descripción"`
3. Revisar el archivo generado en alembic/versions/
4. Aplicar migración: `alembic upgrade head`

Alembic detecta automáticamente cambios en los modelos y genera el código SQL necesario. Siempre revisamos las migraciones generadas porque a veces necesitan ajustes manuales.

Para revertir una migración: `alembic downgrade -1`

Mantenemos el historial completo de migraciones en control de versiones. Esto nos permite reconstruir el schema desde cero aplicando todas las migraciones en orden.

**Variables de Entorno**

Usamos archivos .env para configuración. Tenemos tres archivos:

.env.example: Template con todas las variables y valores de ejemplo. Está en el repositorio como referencia.

.env.docker: Configuración para desarrollo local con Docker. Usa valores seguros para desarrollo pero no para producción.

.env: Archivo real con configuración del ambiente. No está en el repositorio (está en .gitignore). Cada ambiente (dev, staging, prod) tiene su propio .env.

Variables críticas que deben ser únicas por ambiente:
- SECRET_KEY: Para firmar cookies y sesiones
- JWT_SECRET_KEY: Para firmar tokens de acceso
- JWT_REFRESH_SECRET_KEY: Para firmar tokens de refresco
- DATABASE_URL: Conexión a PostgreSQL

Generamos las secret keys con: `openssl rand -hex 32`

**Despliegue a Producción**

Para producción recomendamos:

1. Servidor con Docker y Docker Compose instalados
2. Nginx como proxy reverso para:
   - Terminar TLS/SSL
   - Servir archivos estáticos (si los hay)
   - Rate limiting adicional
   - Balanceo de carga (si hay múltiples instancias)

3. PostgreSQL en servidor separado o servicio administrado (AWS RDS, Azure Database, etc)

4. Variables de entorno configuradas en archivo .env seguro con permisos restrictivos (chmod 600)

5. Logs centralizados en servicio externo (CloudWatch, Datadog, etc)

6. Backups automáticos de base de datos (diarios con retención de 30 días)

7. Monitoreo de salud del servicio

El proceso de despliegue:
1. Clonar repositorio en servidor
2. Copiar .env de producción
3. Construir imágenes: `docker-compose build`
4. Iniciar servicios: `docker-compose up -d`
5. Ejecutar migraciones: `docker-compose exec app alembic upgrade head`
6. Inicializar datos: `docker-compose exec app python scripts/init_db.py`
7. Verificar salud: `curl http://localhost:8000/health`

Para actualizaciones:
1. Pull de cambios del repositorio
2. Reconstruir imágenes si hay cambios en dependencias
3. Aplicar migraciones
4. Reiniciar contenedores: `docker-compose restart app`

Implementamos rolling updates para minimizar downtime: levantamos una nueva instancia, esperamos que esté healthy, redirigimos tráfico, apagamos la instancia vieja.

### 6.3 Monitoreo del sistema

El monitoreo es esencial para detectar problemas antes de que afecten a usuarios.

**Logs Estructurados**

Todos los logs usan formato JSON estructurado. Cada entrada incluye:
- timestamp: ISO 8601 con timezone
- level: DEBUG, INFO, WARNING, ERROR, CRITICAL
- logger: Nombre del módulo que generó el log
- event: Tipo de evento (login_exitoso, error_base_datos, etc)
- Campos adicionales según el evento (user_id, ip_address, error, etc)

Ejemplo de log de login exitoso:
```json
{
  "timestamp": "2025-01-15T10:30:45.123456-05:00",
  "level": "info",
  "logger": "app.services.auth_service",
  "event": "login_exitoso",
  "username": "jperez",
  "user_id": 42,
  "ip_address": "192.168.1.100",
  "provider": "local"
}
```

Los logs estructurados son fáciles de parsear y buscar. Podemos enviarlos a sistemas como Elasticsearch para análisis avanzado.

**Endpoints de Salud**

Implementamos dos endpoints para monitoreo:

GET /health: Retorna 200 OK si el servicio está corriendo. Es un health check básico que solo verifica que el proceso esté vivo.

GET /: Retorna información del sistema (versión, estado). Útil para verificar qué versión está desplegada.

Estos endpoints no requieren autenticación para que sistemas de monitoreo externos puedan consultarlos.

**Métricas Importantes**

Recomendamos monitorear:

Disponibilidad:
- Uptime del servicio
- Tasa de respuestas 5xx
- Latencia de endpoints (p50, p95, p99)

Autenticación:
- Intentos de login (exitosos vs fallidos)
- Cuentas bloqueadas
- Tokens generados por minuto
- Sesiones activas

Base de Datos:
- Conexiones activas
- Queries lentas (> 1 segundo)
- Tamaño de tablas principales
- Tasa de crecimiento

Recursos:
- CPU usage
- Memoria RAM
- Espacio en disco
- Conexiones de red

**Alertas Sugeridas**

Configurar alertas para:
- Servicio caído (health check falla por > 2 minutos)
- Tasa de errores > 5% en 5 minutos
- Latencia p95 > 2 segundos
- Más de 10 intentos fallidos de login desde misma IP en 1 minuto
- Uso de CPU > 80% por > 5 minutos
- Uso de memoria > 90%
- Espacio en disco < 10% libre
- Conexiones a base de datos > 80% del pool

**Auditoría**

El sistema registra eventos de auditoría para:
- Todos los logins (exitosos y fallidos)
- Cambios en usuarios (crear, actualizar, eliminar)
- Cambios en roles y permisos
- Asignación de roles a usuarios
- Cambios de contraseña
- Recuperación de contraseña
- Cierre de sesiones

Los logs de auditoría incluyen:
- Quién hizo la acción (usuario autenticado)
- Qué acción se realizó
- Sobre qué recurso (ID del usuario afectado, rol modificado, etc)
- Cuándo (timestamp preciso)
- Desde dónde (IP address)
- Resultado (éxito o error)

Estos logs deben retenerse por al menos 1 año para cumplir con requisitos de auditoría y seguridad.

**Troubleshooting**

Para diagnosticar problemas comunes:

Servicio no inicia:
1. Verificar logs: `docker-compose logs app`
2. Verificar que PostgreSQL esté corriendo: `docker-compose ps`
3. Verificar variables de entorno: `docker-compose exec app env | grep DATABASE_URL`
4. Verificar conectividad a DB: `docker-compose exec app python scripts/health_check_db.py`

Login falla:
1. Verificar que el usuario existe: `docker-compose exec app python scripts/manage_users.py`
2. Verificar que la cuenta no esté bloqueada
3. Revisar logs de autenticación
4. Verificar configuración del proveedor (LDAP, etc)

Performance lento:
1. Revisar queries lentas en PostgreSQL
2. Verificar índices en tablas grandes
3. Revisar uso de CPU y memoria
4. Verificar conexiones activas a DB

Tokens inválidos:
1. Verificar que JWT_SECRET_KEY no haya cambiado
2. Verificar que el token no haya expirado
3. Verificar que la sesión no haya sido cerrada
4. Revisar logs de validación de tokens

---

**Notas Finales**

Esta documentación refleja el estado actual del sistema. Algunas integraciones (Azure AD, SMTP) están preparadas pero pendientes de configuración final. El sistema es funcional y seguro para uso en producción con las integraciones actuales (autenticación local y LDAP).

Para preguntas o soporte técnico, consultar el README.md principal o contactar al equipo de desarrollo.
