#  Diagramas de Arquitectura - Defensoria Middleware

Esta carpeta contiene los diagramas actualizados de arquitectura del proyecto en formato **DrawIO** con diseño moderno y profesional.

##  Diagramas Disponibles

### 1.  Arquitectura Hexagonal (`01-arquitectura-hexagonal-modern.drawio`)
**Descripción:** Diagrama completo de la arquitectura hexagonal del sistema mostrando las 4 capas principales.

**Capas:**
-  **API Layer**: Endpoints FastAPI organizados por funcionalidad
-  **Application Layer**: Servicios de lógica de negocio
-  **Domain Layer**: Interfaces de repositorios (puertos de salida)
-  **Infrastructure Layer**: Implementaciones SQLAlchemy

**Características visuales:**
- Diseño moderno con gradientes y sombras
- Iconos emoji para identificación rápida
- Código de colores por capa
- Flechas que muestran el flujo de dependencias

---

### 2.  Flujo de Autenticación (`02-flujo-autenticacion-modern.drawio`)
**Descripción:** Flujo completo del proceso de autenticación multi-provider con generación de JWT.

**Componentes:**
-  Cliente (Frontend/API)
-  FastAPI Endpoint
-  AuthService
-  Providers (Local, LDAP, Azure AD)
-  Generación JWT
-  Respuesta exitosa

**Incluye:**
- Manejo de errores
- Características de seguridad (bcrypt, rate limiting, auditoría)
- Estructura de tokens JWT
- Validaciones de cada provider

---

### 3.  Repository Pattern (`03-repository-pattern-modern.drawio`)
**Descripción:** Implementación del patrón Repository siguiendo Domain Driven Design.

**Muestra:**
-  Interfaces abstractas (ABC) en la capa de dominio
-  Implementaciones concretas con SQLAlchemy
-  Inyección de dependencias en servicios
-  Beneficios del patrón (testabilidad, separación, SOLID)

**Código de ejemplo:**
- Definición de servicios con repositorios
- Interfaces abstractas con `@abstractmethod`
- Implementaciones SQLAlchemy concretas

---

### 4.  Modelo de Base de Datos (`04-modelo-datos-modern.drawio`)
**Descripción:** Schema completo de PostgreSQL con todas las tablas y relaciones.

**Tablas:**
-  **usuarios**: Datos de usuario, credenciales, estado
-  **roles**: Definición de roles del sistema
-  **permisos**: Permisos granulares
-  **usuarios_roles**: Relación N:M usuarios-roles
-  **roles_permisos**: Relación N:M roles-permisos
-  **sesiones**: Sesiones activas con JWT tokens
-  **password_reset_tokens**: Tokens de recuperación de contraseña

**Incluye:**
- Tipos de datos detallados
- Claves primarias y foráneas
- Índices y constraints
- Cardinalidades de relaciones
- Timestamps y campos de auditoría

---

##  Cómo Usar los Diagramas

### Abrir en DrawIO Desktop
1. Descargar [DrawIO Desktop](https://github.com/jgraph/drawio-desktop/releases)
2. Abrir el archivo `.drawio` deseado
3. Editar según necesidades

### Abrir en DrawIO Web
1. Ir a [app.diagrams.net](https://app.diagrams.net/)
2. File → Open From → Device
3. Seleccionar el archivo `.drawio`

### Exportar como Imagen
1. Abrir el diagrama en DrawIO
2. File → Export As → PNG/SVG/PDF
3. Configurar resolución y transparencia
4. Guardar

---

##  Guía de Colores

| Capa / Componente | Color Principal | Uso |
|-------------------|----------------|-----|
| API Layer | ![#1976d2](https://via.placeholder.com/15/1976d2/000000?text=+) Azul | Endpoints HTTP |
| Application Layer | ![#7b1fa2](https://via.placeholder.com/15/7b1fa2/000000?text=+) Púrpura | Servicios |
| Domain Layer | ![#e65100](https://via.placeholder.com/15/e65100/000000?text=+) Naranja | Interfaces |
| Infrastructure | ![#2e7d32](https://via.placeholder.com/15/2e7d32/000000?text=+) Verde | Implementaciones |
| Base de Datos | ![#336791](https://via.placeholder.com/15/336791/000000?text=+) Azul PostgreSQL | Tablas |
| Autenticación | ![#28a745](https://via.placeholder.com/15/28a745/000000?text=+) Verde éxito | Flujos exitosos |
| Errores | ![#dc3545](https://via.placeholder.com/15/dc3545/000000?text=+) Rojo | Manejo de errores |

---

##  Convenciones de Diseño

### Iconos Emoji
-  Autenticación / Claves
-  Seguridad / Protección
-  Interfaces / Contratos
-  Implementaciones / Base de Datos
-  Servicios / Lógica
-  Relaciones / Links
-  Exitoso / Validado
-  Error / Fallido

### Tipos de Flechas
- **Línea sólida**: Llamada directa / Dependencia fuerte
- **Línea punteada**: Usa interfaz / Dependencia débil
- **Grosor 3px**: Flujo principal
- **Grosor 2px**: Flujo secundario

### Sombras y Efectos
- Todos los contenedores tienen sombra para dar profundidad
- Bordes redondeados para modernidad
- Gradientes sutiles en títulos principales

---

##  Stack Tecnológico Representado

- **Backend**: FastAPI, Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **Base de Datos**: PostgreSQL 15+
- **Migraciones**: Alembic
- **Autenticación**: JWT (PyJWT), bcrypt
- **Validación**: Pydantic V2
- **Patrones**: Hexagonal Architecture, Repository Pattern, Dependency Injection

---

##  Notas de Actualización

**Versión Moderna (Noviembre 2024)**
-  Diseño visual completamente renovado
-  Paleta de colores profesional y consistente
-  Iconos emoji para mejor identificación
-  Mayor detalle en código y ejemplos
-  Diagramas más expresivos y claros
-  Nuevo diagrama de base de datos completo

**Archivos Anteriores**: Los diagramas originales se mantienen en esta carpeta con sus nombres originales para referencia.

---

##  Contribuir

Para actualizar o mejorar los diagramas:

1. Abrir el archivo `.drawio` correspondiente
2. Realizar cambios manteniendo el estilo visual
3. Usar la paleta de colores establecida
4. Incluir iconos emoji apropiados
5. Exportar versión PNG para documentación si es necesario
6. Actualizar este README si se agregan nuevos diagramas

---

##  Recursos Adicionales

- [Documentación de Arquitectura Hexagonal](../ARQUITECTURA.md)
- [Guía de Autenticación Completa](../AUTH_COMPLETE_GUIDE.md)
- [Guía de RBAC](../RBAC_GUIDE.md)
- [Guía de PostgreSQL](../POSTGRESQL_GUIDE.md)

---

**Generado para**: Defensoría del Pueblo - Middleware de Autenticación  
**Última actualización**: Noviembre 2024  
**Mantenido por**: Equipo de Desarrollo
