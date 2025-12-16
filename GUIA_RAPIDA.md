# Guía Rápida de Despliegue

## Resumen Ejecutivo

✅ **Aplicación desplegada exitosamente en Google Cloud Platform**

**URL:** https://defensoria-middleware-411798681660.us-central1.run.app  
**Usuario:** admin  
**Password:** Admin123!

## Comandos Rápidos

### Probar la aplicación

```powershell
# Login
$body = @{nombre_usuario="admin"; contrasena="Admin123!"} | ConvertTo-Json
Invoke-RestMethod -Uri "https://defensoria-middleware-411798681660.us-central1.run.app/auth/login" -Method POST -ContentType "application/json" -Body $body
```

### Conectar a base de datos

```bash
gcloud beta sql connect defensoria-db --user=postgres --database=defensoria_db
# Password: 160ad94e587af20af57bb5fc30c9fbd0
```

> **Nota:** El comando `beta` usa el Cloud SQL Proxy interno para evitar restricciones de red organizacionales.

### Ver logs

```powershell
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=defensoria-middleware" --limit=20
```

### Redesplegar

```powershell
docker build -t gcr.io/sat-defensoriapueblo/defensoria-middleware:latest .
docker push gcr.io/sat-defensoriapueblo/defensoria-middleware:latest
gcloud run deploy defensoria-middleware --image gcr.io/sat-defensoriapueblo/defensoria-middleware:latest --region us-central1
```

## Estructura del Proyecto

```
defensoria-middleware/
├── app/                    # Código de la aplicación
│   ├── api/               # Endpoints
│   ├── core/              # Configuración y seguridad
│   ├── database/          # Modelos
│   ├── services/          # Lógica de negocio
│   └── schemas/           # Validaciones
├── alembic/               # Migraciones de BD
├── Dockerfile             # Imagen Docker
└── README.md              # Documentación completa
```

## Recursos GCP

| Servicio | Nombre | Estado |
|----------|--------|--------|
| Cloud Run | defensoria-middleware | ✅ ACTIVO |
| Cloud SQL | defensoria-db | ✅ ACTIVO |
| Secret Manager | db-password, jwt-secret | ✅ CONFIGURADO |
| Container Registry | gcr.io/.../defensoria-middleware | ✅ DESPLEGADO |

## 💰 Análisis de Costos y Arquitectura

### Componentes Desplegados

#### 1. **Cloud Run** (Backend API)
**¿Qué es?** Plataforma serverless que ejecuta contenedores Docker sin gestionar servidores.

**¿Por qué se eligió?**
- ✅ **Escalado automático:** De 0 a N instancias según demanda
- ✅ **Pago por uso:** Solo pagas cuando hay requests (no 24/7)
- ✅ **Sin gestión de servidores:** Google maneja infraestructura
- ✅ **HTTPS automático:** SSL incluido sin configuración
- ✅ **Deploys instantáneos:** Rollback en segundos

**Configuración actual:**
- CPU: 1 vCPU (durante request)
- RAM: 512 MB
- Timeout: 300 segundos
- Concurrencia: 80 requests/instancia

**Costo mensual:** ~$5-8 USD
- $0.00002400 por vCPU-segundo
- $0.00000250 por GB-segundo de memoria
- 2 millones de requests gratis/mes
- Para 10,000 requests/día: ~$6/mes

#### 2. **Cloud SQL** (Base de Datos PostgreSQL 15)
**¿Qué es?** Base de datos PostgreSQL administrada con backups automáticos.

**¿Por qué se eligió?**
- ✅ **Administrada:** Google maneja actualizaciones, parches, backups
- ✅ **Alta disponibilidad:** Opción de réplicas y failover automático
- ✅ **Seguridad:** Encriptación en reposo y tránsito
- ✅ **Backups automáticos:** Point-in-time recovery
- ✅ **Escalable:** Fácil upgrade de recursos

**Configuración actual:**
- Tier: db-f1-micro (shared CPU)
- RAM: 0.6 GB
- Storage: 10 GB SSD
- Region: us-central1

**Costo mensual:** ~$7-10 USD
- Instancia db-f1-micro: $7.67/mes
- Storage SSD: $0.17/GB/mes → $1.70 para 10GB
- Backups: Primeros 7 días gratis

**💡 Alternativas evaluadas:**
- ❌ **Compute Engine + PostgreSQL manual:** Más barato pero requiere mantenimiento
- ❌ **Cloud SQL tier mayor:** db-n1-standard-1 cuesta $70/mes (overkill)
- ✅ **db-f1-micro:** Balance perfecto para MVP/desarrollo

#### 3. **Secret Manager** (Gestión de Credenciales)
**¿Qué es?** Almacén seguro para contraseñas, tokens y secretos.

**¿Por qué se eligió?**
- ✅ **Seguridad:** Encriptación AES-256, auditoría completa
- ✅ **Versionado:** Historial de cambios de secrets
- ✅ **Rotación:** Actualización sin redeploy
- ✅ **IAM integrado:** Control granular de accesos

**Secretos almacenados:**
- `db-password`: Contraseña de PostgreSQL
- `jwt-secret`: Clave para firmar tokens JWT

**Costo mensual:** ~$0.30 USD
- $0.06 por secreto activo/mes
- 2 secretos × $0.06 = $0.12/mes
- 10,000 operaciones gratis/mes

#### 4. **Container Registry** (Almacenamiento de Imágenes)
**¿Qué es?** Repositorio privado de imágenes Docker.

**¿Por qué se eligió?**
- ✅ **Integración nativa:** Funciona directo con Cloud Run
- ✅ **Escaneo de vulnerabilidades:** Detección automática
- ✅ **Control de acceso:** IAM por imagen

**Costo mensual:** ~$0.50 USD
- Storage: $0.026/GB/mes
- Imagen actual: ~400 MB → $0.01/mes
- Egress: $0.12/GB (solo cuando se descarga)

---

### 📊 Resumen de Costos

| Servicio | Configuración | Costo Mensual | Justificación |
|----------|---------------|---------------|---------------|
| **Cloud Run** | 1 vCPU, 512MB | $5-8 USD | Serverless, pago por uso |
| **Cloud SQL** | db-f1-micro, 10GB | $7-10 USD | BD administrada, backups incluidos |
| **Secret Manager** | 2 secretos | $0.30 USD | Seguridad de credenciales |
| **Container Registry** | 400MB imagen | $0.50 USD | Repositorio privado |
| **Networking** | Egress/Ingress | $1-2 USD | Transferencia de datos |
| **Logging** | Cloud Logging | $0-1 USD | Primeros 50GB gratis |
| **TOTAL ACTUAL** | | **$14-22 USD/mes** | ✅ Ambiente de desarrollo |

---

### 🚀 Proyección de Costos por Escenario

#### Escenario 1: Desarrollo/Testing (Actual)
- **Tráfico:** 1,000 requests/día
- **Usuarios concurrentes:** 5-10
- **Costo:** $14-22 USD/mes
- ✅ **Ideal para:** MVP, pruebas, demos

#### Escenario 2: Producción Inicial
- **Tráfico:** 10,000 requests/día
- **Usuarios concurrentes:** 50-100
- **Upgrades necesarios:**
  - Cloud SQL → db-g1-small (1.7GB RAM): $35/mes
  - Cloud Run → 2GB RAM: $15/mes
- **Costo:** $60-80 USD/mes
- ✅ **Ideal para:** Lanzamiento, primeros 6 meses

#### Escenario 3: Producción Establecida
- **Tráfico:** 50,000 requests/día
- **Usuarios concurrentes:** 200-500
- **Upgrades necesarios:**
  - Cloud SQL → db-n1-standard-1 (3.75GB RAM): $70/mes
  - Cloud Run → 4GB RAM, autoscaling: $40/mes
  - Cloud CDN para assets: $10/mes
- **Costo:** $130-160 USD/mes
- ✅ **Ideal para:** Operación estable, alta disponibilidad

#### Escenario 4: Alta Disponibilidad (Enterprise)
- **Tráfico:** 200,000+ requests/día
- **Usuarios concurrentes:** 1,000+
- **Upgrades necesarios:**
  - Cloud SQL → db-n1-standard-2 + réplica: $200/mes
  - Cloud Run → Multi-region: $100/mes
  - Cloud Armor (WAF): $30/mes
  - Cloud Load Balancer: $20/mes
- **Costo:** $400-500 USD/mes
- ✅ **Ideal para:** Misión crítica, 99.95% uptime

---

### 🔍 Comparación con Alternativas

#### vs. Servidor Tradicional (VM)
| Aspecto | Cloud Run + Cloud SQL | Compute Engine VM |
|---------|----------------------|-------------------|
| **Costo inicial** | $14-22/mes | $35-50/mes |
| **Escalabilidad** | Automática | Manual |
| **Mantenimiento** | Mínimo (managed) | Alto (OS, security patches) |
| **Tiempo setup** | 10 minutos | 2-4 horas |
| **Alta disponibilidad** | Built-in | Configuración manual |
| **Backups** | Automáticos | Debes implementar |

#### vs. Hosting Tradicional (DigitalOcean, AWS EC2)
| Aspecto | GCP Cloud Run | DigitalOcean Droplet |
|---------|---------------|---------------------|
| **Precio mínimo** | $14/mes (pay-per-use) | $6/mes (512MB, siempre on) |
| **Escalado** | Automático 0→N | Manual, downtime |
| **SSL** | Incluido automático | Manual (Let's Encrypt) |
| **Deploy** | `gcloud run deploy` | SSH + Git + restart |
| **Monitoreo** | Integrado (Cloud Monitoring) | Separado (Datadog, etc) |

**Veredicto:** Cloud Run es más caro en tráfico bajo pero **mucho mejor** para producción real.

---

### 💡 Optimizaciones de Costo

#### Ahorro Inmediato (sin afectar funcionalidad)
1. **Limitar instancias mínimas a 0** (actual) → ahorra cuando no hay tráfico
2. **Reducir retención de logs** de 30 a 7 días → ahorra $5-10/mes
3. **Comprimir respuestas JSON** en FastAPI → reduce egress 60%

#### Ahorro a Mediano Plazo
1. **Cloud SQL scheduled scaling:** Apagar en horario nocturno → ahorra 40%
2. **Implementar caché Redis:** Reduce queries → menor CPU Cloud SQL
3. **Cloud CDN para assets estáticos:** Reduce requests a Cloud Run

#### Monitoreo de Costos
```bash
# Ver facturación actual
gcloud billing accounts list
gcloud beta billing budgets list --billing-account=BILLING_ACCOUNT_ID

# Crear alerta de presupuesto
gcloud beta billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Defensoria Budget Alert" \
  --budget-amount=50 \
  --threshold-rule=percent=80
```

---

### 🎯 Recomendación Actual

Para tu caso (MVP/Desarrollo):
- ✅ **Mantener configuración actual:** $14-22/mes es óptimo
- ✅ **No hacer upgrades** hasta ver métricas reales de uso
- ✅ **Monitorear latencia y errores** primero
- ✅ **Escalar solo cuando:**
  - Latencia > 2 segundos consistentemente
  - CPU > 80% por más de 5 minutos
  - Errores 5xx > 1% de requests

**Próximo upgrade sugerido:**
Cuando tengas **5,000+ requests/día**, migrar Cloud SQL a `db-g1-small` ($35/mes) para mejor performance.

## Checklist de Validación

### ✅ Completado
- [x] Aplicación desplegada en Cloud Run
- [x] Base de datos PostgreSQL creada
- [x] 10 tablas creadas correctamente
- [x] Usuario admin configurado
- [x] Secrets configurados en Secret Manager (db-password, jwt-secret)
- [x] Permisos IAM asignados
- [x] Acceso público habilitado
- [x] Login funcionando
- [x] Tokens JWT generándose correctamente
- [x] Rate limiting implementado en código
- [x] Autenticación bcrypt con 12 rounds
- [x] HTTPS habilitado (Cloud Run por defecto)

### 🔄 Pendiente para Producción

- [ ] **Dominio personalizado:** Configurar DNS y mapear a Cloud Run
- [ ] **Backups automáticos:** Programar exports diarios de Cloud SQL
- [ ] **Monitoring:** Configurar Cloud Monitoring y alertas
- [ ] **Logs estructurados:** Enviar logs a Cloud Logging con niveles
- [ ] **CORS:** Configurar orígenes permitidos según frontend
- [ ] **Firewall:** Limitar acceso por IP si es necesario (Cloud Armor)
- [ ] **Rotación de secrets:** Política de cambio periódico de contraseñas
- [ ] **Escalado:** Ajustar límites de concurrencia según carga esperada
- [ ] **2FA:** Activar autenticación de dos factores para administradores GCP

## Próximos Pasos Recomendados

### 1. Configurar Dominio Personalizado
```bash
# Mapear dominio a Cloud Run
gcloud run domain-mappings create --service defensoria-middleware --domain api.tudominio.gob --region us-central1
```

### 2. Habilitar Backups Automáticos
```bash
# Configurar backup diario a las 3 AM
gcloud sql instances patch defensoria-db --backup-start-time 03:00
```

### 3. Configurar Alertas
```bash
# Alerta si hay más de 10 errores 500 en 5 minutos
gcloud alpha monitoring policies create --notification-channels=CHANNEL_ID \
  --display-name="API Errors" \
  --condition-display-name="High error rate" \
  --condition-threshold-value=10
```

### 4. Ajustar CORS (si se conecta un frontend)
Actualizar en `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tudominio.gob"],  # Cambiar según frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

Ver **README.md** para documentación completa.
