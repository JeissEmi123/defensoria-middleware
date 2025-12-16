# Documento Técnico - Despliegue en Google Cloud Platform

**Proyecto:** Sistema de Autenticación y Middleware - Defensoría del Pueblo  
**Ambiente:** Desarrollo (Cloud)  
**Fecha:** 9 de diciembre de 2025  
**Estado:** Preliminar

---

## 1. Resumen Ejecutivo

Este documento describe la **infraestructura desplegada en Google Cloud Platform (GCP)** para el sistema de autenticación de la Defensoría del Pueblo, incluyendo el backend (middleware) y frontend.

### 1.1 Información del Despliegue en Nube

- **Proyecto GCP:** sat-defensoriapueblo
- **Región:** us-central1
- **Servicios Desplegados en Cloud Run:**
  - **Backend (Middleware):** https://defensoria-middleware-411798681660.us-central1.run.app
  - **Frontend:** https://defensoria-frontend-411798681660.us-central1.run.app
- **Base de Datos:** Cloud SQL (PostgreSQL 15)
- **Último Deploy:** 4 de diciembre de 2025

---

## 2. Stack Tecnológico

### 2.1 Backend (Middleware)

#### Framework y Lenguaje

- **Python:** 3.11-slim
- **Framework Web:** FastAPI 0.109.0
- **ASGI Server:** Uvicorn 0.27.0
- **ORM:** SQLAlchemy 2.0.25 (con soporte async)
- **Migraciones:** Alembic 1.13.1

### 2.2 Frontend

#### Framework y Lenguaje

- **Node.js:** 20+ (requerido)
- **Framework:** React 19.2.0
- **Build Tool:** Vite 6.2.0
- **Lenguaje:** TypeScript 5.8.2
- **Router:** React Router DOM 7.9.6

#### Librerías Principales

- **Estado Global:** Zustand 5.0.8
- **Data Fetching:** TanStack React Query 5.90.11
- **Charts:** Recharts 3.5.0
- **Estilos:** Tailwind CSS 4.1.17

#### Herramientas de Desarrollo

- **Testing:** Jest 30.2.0, Testing Library 16.3.0
- **Linting:** ESLint 9.39.1 + TypeScript ESLint 8.48.0
- **Formateo:** Prettier 3.6.2
- **Git Hooks:** Husky 8.0.0 + lint-staged 16.2.7
- **TypeScript Compiler:** tsc 5.8.2

#### Configuración

- **Puerto Desarrollo:** 3001
- **Host:** 0.0.0.0 (accesible externamente)
- **Hot Module Replacement:** Habilitado
- **API Key:** Integración con Gemini API

### 2.3 Base de Datos

- **Motor:** PostgreSQL 15
- **Driver Async:** asyncpg 0.29.0
- **Driver Sync:** psycopg2-binary 2.9.9

---

## 3. Componentes de Google Cloud Platform

### 3.1 Cloud Run - Servicios Desplegados

**Región:** us-central1

#### Servicio 1: defensoria-middleware (Backend)

**URL:** https://defensoria-middleware-411798681660.us-central1.run.app  
**Último Deploy:** 2025-12-04 00:49:53 UTC  
**Deploy por:** jcamargom@agatadata.com

**Configuración:**
- **Tipo:** Managed (Serverless)
- **Memoria:** 512 MB
- **CPU:** 1 vCPU
- **Instancias Mínimas:** 0 (auto-escala desde cero)
- **Instancias Máximas:** 10
- **Puerto:** 8080
- **Autenticación:** Público (allow-unauthenticated)
- **Startup CPU Boost:** Habilitado
- **Cloud SQL:** Conectado via proxy

#### Servicio 2: defensoria-frontend (Frontend)

**URL Principal:** https://defensoria-frontend-411798681660.us-central1.run.app  
**URL Alternativa:** https://defensoria-frontend-jrwf7omlvq-uc.a.run.app  
**Último Deploy:** 2025-12-03 23:48:23 UTC  
**Deploy por:** jcamargom@agatadata.com  
**Imagen:** us-central1-docker.pkg.dev/sat-defensoriapueblo/defensoria-frontend/defensoria-frontend:latest

**Configuración:**
- **Tipo:** Managed (Serverless)
- **Framework:** React 19.2.0 + Vite 6.2.0
- **Lenguaje:** TypeScript 5.8.2
- **Memoria:** 512 MB
- **CPU:** 1000m (1 vCPU)
- **Puerto:** 8080
- **Container Concurrency:** 80 requests simultáneos
- **Instancias Mínimas:** 0 (auto-escala desde cero)
- **Instancias Máximas:** 10
- **Timeout:** 300 segundos
- **Startup CPU Boost:** Habilitado
- **Service Account:** 411798681660-compute@developer.gserviceaccount.com

**Health Checks:**
- **Tipo:** TCP Socket (puerto 8080)
- **Failure Threshold:** 1
- **Period:** 240 segundos
- **Timeout:** 240 segundos

**Variables de Entorno:**
- No se configuraron variables de entorno adicionales
- La aplicación utiliza configuración embebida en el build

**Tecnologías:**
- React Router DOM 7.9.6
- Zustand (estado global)
- TanStack Query (data fetching)
- Tailwind CSS 4.1.17
- Recharts (gráficos)
- Jest + Testing Library (testing)

**Características Comunes de los Servicios:**
- Auto-escalamiento horizontal (0-10 instancias)
- Facturación por uso (pay-per-request)
- HTTPS integrado automáticamente
- Logs integrados con Cloud Logging
- Healthchecks automáticos TCP Socket
- Región: us-central1
- Timeout: 300 segundos

### 3.2 Cloud SQL

**Instancia:** defensoria-db

**Configuración:**
- **Motor:** PostgreSQL 15
- **Tier:** db-f1-micro (desarrollo)
- **Zona:** us-central1-c
- **IP Pública:** 34.170.229.237
- **SSL:** Permitido pero no requerido
- **Connection:** Unix Socket via Cloud SQL Proxy

**Bases de Datos:**
- `postgres` - Base de datos sistema (UTF8, en_US.UTF8)
- `defensoria_db` - Base de datos principal (UTF8, en_US.UTF8)

**Usuarios:**
- `postgres` - Usuario root (utilizado en producción actual)

**Alta Disponibilidad y Backups:**
- **Backups automáticos:** Habilitados a las 03:00 AM
- **Retención de backups:** 7 días
- **Transaction logs:** 7 días de retención
- **Point-in-time recovery:** Disponible
- **Backup tier:** STANDARD

### 3.3 Secret Manager

**Secrets Almacenados:**

| Secret | Propósito | Fecha Creación |
|--------|-----------|----------------|
| `SECRET_KEY` | Clave maestra de la aplicación | 2025-12-03 |
| `JWT_SECRET_KEY` | Firma de tokens de acceso | 2025-12-03 |
| `JWT_REFRESH_SECRET_KEY` | Firma de tokens de refresh | 2025-12-03 |
| `ADMIN_DEFAULT_PASSWORD` | Password del usuario admin | 2025-12-03 |
| `POSTGRES_PASSWORD` | Password de PostgreSQL | 2025-12-03 |
| `db-password` | Password alternativo de DB | 2025-12-03 |
| `jwt-secret` | Secret JWT alternativo | 2025-12-03 |

**Configuración:**
- **Replicación:** Automática (multi-región)
- **Versionamiento:** Automático
- **Acceso:** Mediante IAM
- **Rotación:** Soportada
- **Auditoría:** Integrada con Cloud Logging

### 3.4 Artifact Registry

**Repositorios Configurados:**

#### 1. defensoria-repo (Middleware Backend)
- **Formato:** Docker
- **Ubicación:** us-central1
- **Tamaño:** 1.37 GB
- **Creado:** 2025-12-03
- **Encriptación:** Google-managed key
- **Propósito:** Imágenes del middleware backend

#### 2. defensoria-frontend (Frontend)
- **Formato:** Docker
- **Ubicación:** us-central1
- **Tamaño:** 22 MB
- **Creado:** 2025-12-03
- **Propósito:** Imágenes del frontend

**Imágenes Principales:**
- Backend: `us-central1-docker.pkg.dev/sat-defensoriapueblo/defensoria-repo/middleware:latest`
- Frontend: `us-central1-docker.pkg.dev/sat-defensoriapueblo/defensoria-frontend/defensoria-frontend:latest`

### 3.5 Cloud Build

**Propósito:** CI/CD automatizado

**Proceso:**
1. Build de imagen Docker
2. Push a Artifact Registry
3. Deploy automático a Cloud Run

**Archivo de configuración:** `cloudbuild.yaml`

**Triggers:**
- Manual via CLI
- Posibilidad de integración con repositorio Git

### 3.6 Cloud Logging

**Características:**
- Logs centralizados de Cloud Run
- Logs de aplicación (structlog)
- Logs de auditoría
- Retención configurable
- Búsqueda y filtrado avanzado

---

## 4. Arquitectura de Despliegue en GCP

```
┌──────────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                          │
│                    sat-defensoriapueblo                          │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                  Cloud Run (us-central1)                     │ │
│  │                                                               │ │
│  │  ┌────────────────────┐            ┌────────────────────┐   │ │
│  │  │    Frontend        │            │    Backend         │   │ │
│  │  │    React 19 +      │   ◄─────►  │    FastAPI        │   │ │
│  │  │    Vite 6          │    HTTPS   │    Python 3.11    │   │ │
│  │  │    TypeScript      │            │    Uvicorn        │   │ │
│  │  │    Port 8080       │            │    Port 8080      │   │ │
│  │  │    512 MB, 1 vCPU  │            │    512 MB, 1 vCPU │   │ │
│  │  │    0-10 instances  │            │    0-10 instances │   │ │
│  │  └────────────────────┘            └──────────┬─────────┘   │ │
│  │                                               │              │ │
│  └───────────────────────────────────────────────┼──────────────┘ │
│                                                  │                │
│                                                  ▼                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │               Cloud SQL Proxy (Unix Socket)                │  │
│  │      /cloudsql/sat-defensoriapueblo:us-central1:          │  │
│  │                    defensoria-db                           │  │
│  └────────────────────────────┬───────────────────────────────┘  │
│                               ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Cloud SQL                             │    │
│  │  Instance: defensoria-db                                 │    │
│  │  - PostgreSQL 15                                         │    │
│  │  - db-f1-micro (us-central1-c)                          │    │
│  │  - IP Pública: 34.170.229.237                           │    │
│  │  - Backups: 7 días @ 03:00 AM                           │    │
│  │  - DBs: postgres, defensoria_db                         │    │
│  │  - Usuario: postgres                                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│              ▲                                                   │
│              │                                                   │
│  ┌───────────┴──────────┐         ┌──────────────────────────┐ │
│  │   Secret Manager     │         │  Artifact Registry       │ │
│  │  - 7 secrets activos │         │  - defensoria-repo       │ │
│  │  - JWT keys          │         │    (1.37 GB)             │ │
│  │  - DB passwords      │         │  - defensoria-frontend   │ │
│  │  - Admin creds       │         │    (22 MB)               │ │
│  └──────────────────────┘         └──────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────┐         ┌──────────────────────────┐ │
│  │   Cloud Logging      │         │  Cloud Monitoring        │ │
│  │  - App logs          │         │  - Métricas              │ │
│  │  - Audit logs        │         │  - Alertas (disponible)  │ │
│  └──────────────────────┘         └──────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. Proceso de Despliegue

### 5.1 Herramientas de Despliegue en Nube

1. **gcloud CLI** (Google Cloud SDK)
   - Gestión de servicios GCP
   - Deploy de aplicaciones a Cloud Run
   - Configuración de infraestructura

2. **Docker**
   - Construcción de imágenes de contenedores
   - Push a Artifact Registry

3. **Cloud Build**
   - Build automático de imágenes
   - CI/CD integrado

### 5.2 Comandos de Despliegue en Cloud Run

#### Despliegue del Backend (Middleware)
```powershell
# Build con Cloud Build
gcloud builds submit --tag us-central1-docker.pkg.dev/sat-defensoriapueblo/defensoria-repo/middleware:latest

# Deploy a Cloud Run
gcloud run deploy defensoria-middleware `
    --image us-central1-docker.pkg.dev/sat-defensoriapueblo/defensoria-repo/middleware:latest `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated
```

#### Migraciones de Base de Datos
```powershell
.\run-migrations-simple.ps1
```

#### Despliegue del Frontend

```powershell
# Build con Cloud Build
gcloud builds submit --tag us-central1-docker.pkg.dev/sat-defensoriapueblo/defensoria-frontend/defensoria-frontend:latest

# Deploy a Cloud Run
gcloud run deploy defensoria-frontend `
    --image us-central1-docker.pkg.dev/sat-defensoriapueblo/defensoria-frontend/defensoria-frontend:latest `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --port 8080 `
    --memory 512Mi `
    --cpu 1 `
    --max-instances 10
```

---

## 6. Configuración en Cloud Run

### 6.1 Backend - Variables de Entorno

**Variables Configuradas en Cloud Run:**

```bash
# Variables directas
DATABASE_URL=postgresql+asyncpg://postgres:160ad94e587af20af57bb5fc30c9fbd0@/defensoria_db?host=/cloudsql/sat-defensoriapueblo:us-central1:defensoria-db
POSTGRES_USER=postgres
POSTGRES_DB=defensoria_db
POSTGRES_PORT=5432
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ENVIRONMENT=production
```

**Secrets desde Secret Manager:**
```bash
POSTGRES_PASSWORD → db-password:latest
JWT_SECRET_KEY → jwt-secret:latest
JWT_REFRESH_SECRET_KEY → jwt-secret:latest
ADMIN_DEFAULT_PASSWORD → db-password:latest
```

**Anotaciones Cloud Run:**
```yaml
autoscaling.knative.dev/maxScale: '10'
run.googleapis.com/client-name: gcloud
run.googleapis.com/client-version: 548.0.0
run.googleapis.com/cloudsql-instances: sat-defensoriapueblo:us-central1:defensoria-db
run.googleapis.com/startup-cpu-boost: 'true'
```

### 6.2 Frontend - Configuración en Cloud Run

**Variables de Entorno:**
- El frontend NO tiene variables de entorno configuradas en Cloud Run
- La configuración está embebida durante el build de la aplicación

**Anotaciones Cloud Run:**
```yaml
autoscaling.knative.dev/maxScale: '10'
run.googleapis.com/startup-cpu-boost: 'true'
containerConcurrency: 80
```

**Service Account:**
```
411798681660-compute@developer.gserviceaccount.com
```

### 6.3 CORS Configurado en Backend

**Orígenes Permitidos:**
```python
ALLOWED_ORIGINS = [
    "https://defensoria-frontend-411798681660.us-central1.run.app",
    # ... otros orígenes de desarrollo local
]
```

---

## 7. Monitoreo y Logs en GCP

### 7.1 Cloud Logging

**Consulta de Logs Backend:**
```powershell
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=defensoria-middleware" --limit=20
```

**Consulta de Logs Frontend:**
```powershell
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=defensoria-frontend" --limit=20
```

**Tipos de Logs:**
- Logs de aplicación
- Logs de sistema (Cloud Run)
- Logs de acceso HTTP
- Logs de errores

### 7.2 Health Checks

**Endpoints Desplegados:**
- Backend: https://defensoria-middleware-411798681660.us-central1.run.app/health
- Frontend: https://defensoria-frontend-411798681660.us-central1.run.app

**Métricas disponibles en Cloud Monitoring:**
- Request count
- Request latency
- Instance count
- CPU utilization
- Memory utilization
- Error rate

---

## 8. Costos Estimados en GCP

### 8.1 Cloud Run

#### Backend (defensoria-middleware)
- **Modelo:** Pay-per-use (facturación por request)
- **Recursos:** 512 MB RAM, 1 vCPU
- **Auto-escalado:** 0-10 instancias
- **Tier gratuito:** 2M requests/mes, 360,000 GB-segundos
- **Costo estimado:** ~$3-6 USD/mes

#### Frontend (defensoria-frontend)
- **Modelo:** Pay-per-use (facturación por request)
- **Recursos:** 512 MB RAM, 1 vCPU
- **Auto-escalado:** 0-10 instancias
- **Tier gratuito:** Compartido con backend
- **Costo estimado:** ~$2-4 USD/mes

**Subtotal Cloud Run:** ~$5-10 USD/mes

### 8.2 Cloud SQL (Backend)
- **Instancia:** defensoria-db
- **Tier:** db-f1-micro (compartido, 0.6 GB RAM)
- **Motor:** PostgreSQL 15
- **Storage:** 10 GB incluidos
- **Backups automáticos:** 7 días retención (3 AM diario)
- **Costo base:** ~$10 USD/mes
- **Costo total:** ~$10-12 USD/mes

### 8.3 Artifact Registry

#### Backend Repository (defensoria-repo)
- **Storage:** 1.37 GB
- **Costo:** $0.10/GB/mes
- **Subtotal:** ~$1.40 USD/mes

#### Frontend Repository (defensoria-frontend)
- **Storage:** 22 MB (0.022 GB)
- **Costo:** $0.10/GB/mes
- **Subtotal:** < $0.10 USD/mes

**Subtotal Artifact Registry:** ~$1.50 USD/mes

### 8.4 Secret Manager (Backend)
- **Secrets activos:** 7
- **Accesos estimados:** < 10,000/mes
- **Costo:** $0.06 por secret version + $0.06 por 10,000 accesos
- **Costo estimado:** < $1 USD/mes

### 8.5 Cloud Logging y Monitoring (Ambos)
- **Logs generados:** Backend (alto) + Frontend (bajo)
- **Tier gratuito:** 50 GB/mes
- **Uso estimado:** < 10 GB/mes
- **Costo estimado:** < $1 USD/mes

---

### 8.6 Resumen de Costos

| Servicio | Componente | Costo Mensual |
|----------|------------|---------------|
| **Cloud Run** | Backend (defensoria-middleware) | $3-6 USD |
| **Cloud Run** | Frontend (defensoria-frontend) | $2-4 USD |
| **Cloud SQL** | Backend (defensoria-db) | $10-12 USD |
| **Artifact Registry** | Backend (defensoria-repo: 1.37 GB) | $1.40 USD |
| **Artifact Registry** | Frontend (defensoria-frontend: 22 MB) | < $0.10 USD |
| **Secret Manager** | Backend (7 secrets) | < $1 USD |
| **Logging & Monitoring** | Backend + Frontend | < $1 USD |
| **TOTAL ESTIMADO** | | **$18-25 USD/mes** |

**Nota:** Los costos reales pueden variar según el tráfico y uso. El tier gratuito de GCP cubre parte significativa de Cloud Run en ambientes de desarrollo.

---

## 9. Comandos Útiles de Gestión

```powershell
# Ver estado de los servicios
gcloud run services list --region us-central1

# Ver detalles del backend
gcloud run services describe defensoria-middleware --region us-central1

# Ver detalles del frontend
gcloud run services describe defensoria-frontend --region us-central1

# Ver logs en tiempo real
gcloud logging tail "resource.type=cloud_run_revision" --format=json

# Conectar a Cloud SQL
gcloud sql connect defensoria-db --user=postgres

# Ver secrets
gcloud secrets list

# Ver métricas
gcloud monitoring dashboards list
```

---

## Apéndices

### A. APIs de Google Cloud Habilitadas

- `run.googleapis.com` - Cloud Run
- `sql-component.googleapis.com` - Cloud SQL
- `sqladmin.googleapis.com` - Cloud SQL Admin
- `artifactregistry.googleapis.com` - Artifact Registry
- `cloudbuild.googleapis.com` - Cloud Build
- `secretmanager.googleapis.com` - Secret Manager
- `logging.googleapis.com` - Cloud Logging
- `monitoring.googleapis.com` - Cloud Monitoring

### B. URLs de Servicios Desplegados

| Servicio | URL | Estado |
|----------|-----|--------|
| Backend | https://defensoria-middleware-411798681660.us-central1.run.app | ✅ Activo |
| Frontend | https://defensoria-frontend-411798681660.us-central1.run.app | ✅ Activo |
| Frontend (Knative) | https://defensoria-frontend-jrwf7omlvq-uc.a.run.app | ✅ Activo |

### C. Recursos de Cloud SQL

| Recurso | Detalle |
|---------|---------|
| Instancia | defensoria-db |
| Motor | PostgreSQL 15 |
| Tier | db-f1-micro |
| Zona | us-central1-c |
| IP Pública | 34.170.229.237 |
| Backups | Diarios @ 03:00 AM (7 días retención) |

---

**Documento Técnico**  
**Versión:** 1.0  
**Última actualización:** 9 de diciembre de 2025  
**Scope:** Infraestructura desplegada en Google Cloud Platform
