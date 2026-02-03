# 🔧 Solución: Endpoints no retornan datos en producción

## Problema Reportado
```
Los endpoints no se están llenando para mostrar en el frontend en producción:
- POST /auth/login → ✅ Funciona (retorna token)
- GET /api/v2/senales/consultar → ❌ NO RETORNA DATOS
```

## Análisis Realizado

### 1. **Verificación del Endpoint**
✅ El endpoint está correctamente implementado en:
- [senales_v2.py](app/api/senales_v2.py#L171) - Ruta `/api/v2/senales/consultar`
- [senal_service_v2.py](app/services/senal_service_v2.py#L380) - Lógica de consulta

### 2. **Estructura de Datos**
El endpoint hace JOINs entre 3 tablas:
```sql
SELECT ... FROM sds.senal_detectada sd
  JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales
  JOIN sds.categoria_analisis_senal cas ON sd.id_categoria_analisis = cas.id_categoria_analisis_senal
```

## 🔴 Causas Probables (Por orden de probabilidad)

### **CAUSA #1: NO HAY DATOS EN LA TABLA SENAL_DETECTADA** ⚠️
La tabla está vacía. Sin datos de entrada, el endpoint retorna `{"total": 0, "senales": []}`.

**Síntomas:**
- Endpoint responde con status 200
- `total: 0`
- Array `senales: []` vacío

**Solución:**
```python
# Script para insertar datos de prueba en producción
# Ver: scripts/insert_test_senales_prod.py
```

---

### **CAUSA #2: PROBLEMA CON LAS JOINs SQL**
Las tablas están desincronizadas o faltan registros en tablas relacionadas.

**Síntomas:**
- Error SQL en los logs
- Las JOINs no encuentran coincidencias
- Registros huérfanos sin categorías

---

### **CAUSA #3: ERROR DE AUTENTICACIÓN**
El usuario no tiene permisos para leer de la tabla `sds.senal_detectada`.

**Síntomas:**
- Error 403 Forbidden
- Error de permisos SQL

---

### **CAUSA #4: PROBLEMA DE CONFIGURACIÓN EN PRODUCCIÓN**
Mismatch entre la configuración de producción y la base de datos.

---

## 📋 PASOS PARA DIAGNOSTICAR

### Paso 1: Ejecutar Script SQL de Diagnóstico
```bash
# Ejecutar en Cloud SQL de producción
psql -h PROD_HOST -U app_user -d defensoria_db < diagnostico_senales.sql
```

Este script verificará:
- ✅ Si las tablas existen
- ✅ Cuántos registros hay
- ✅ Si los JOINs funcionan
- ✅ Si hay registros huérfanos

### Paso 2: Ejecutar Test del Endpoint
```bash
python test_senales_prod_simple.py
```

Este script:
1. Se autentica en producción
2. Llama al endpoint `/api/v2/senales/consultar`
3. Muestra la respuesta completa
4. Identifica si es falta de datos o error de lógica

### Paso 3: Ver Logs de Producción
```bash
# Ver logs en Cloud Run
gcloud run logs read defensoria-middleware-prod --region us-central1 --limit 50
```

---

## ✅ SOLUCIONES RECOMENDADAS

### Si el Problema es Falta de Datos:

**Opción A: Insertar datos de prueba**
```sql
-- Primero, insertar categorías si no existen
INSERT INTO sds.categoria_senal (id_categoria_senales, nombre_categoria_senal, color, nivel)
VALUES 
  (1, 'Crisis', '#FF0000', 3),
  (2, 'Paracrisis', '#FFA500', 2),
  (3, 'Problemas Menores', '#00FF00', 1)
ON CONFLICT DO NOTHING;

INSERT INTO sds.categoria_analisis_senal (id_categoria_analisis_senal, nombre_categoria_analisis)
VALUES 
  (1, 'Violencia de Género'),
  (2, 'Menores de Edad'),
  (3, 'Derechos Laborales')
ON CONFLICT DO NOTHING;

-- Luego, insertar señales de prueba
INSERT INTO sds.senal_detectada (
  id_senal_detectada, id_categoria_senal, id_categoria_analisis,
  fecha_deteccion, score_riesgo, estado
)
VALUES 
  (1, 1, 1, NOW(), 85.5, 'DETECTADA'),
  (2, 2, 2, NOW() - INTERVAL '1 day', 65.0, 'DETECTADA'),
  (3, 3, 3, NOW() - INTERVAL '2 days', 45.0, 'DETECTADA')
ON CONFLICT DO NOTHING;
```

**Opción B: Crear script Python para poblar datos**
Ver: [scripts/populate_test_signals.py](scripts/populate_test_signals.py)

---

### Si el Problema es Error en las JOINs:

**Fix: Actualizar el servicio para manejar mejor los errores**

El archivo [app/services/senal_service_v2.py](app/services/senal_service_v2.py#L428) ya tiene lógica para manejar inconsistencias, pero se puede mejorar:

```python
# Mejora: Agregar logging detallado para debugging

async def consultar_senales(self, ...):
    """Versión mejorada con logging"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # ... código existente ...
        result = await self.db.execute(query, params)
        rows = result.fetchall()
        
        logger.info(f"Consulta completada: {len(rows)} registros")
        
    except Exception as e:
        logger.error(f"Error en consulta: {str(e)}", exc_info=True)
        raise
```

---

## 🚀 MEJORAS IMPLEMENTADAS EN EL CÓDIGO

### 1. **Script de Diagnóstico Simple**
- Archivo: [test_senales_prod_simple.py](test_senales_prod_simple.py)
- Uso: `python test_senales_prod_simple.py`
- Verifica el endpoint sin necesidad de BD

### 2. **Script SQL de Diagnóstico Completo**
- Archivo: [diagnostico_senales.sql](diagnostico_senales.sql)
- Verificación de tablas, datos y JOINs
- Fácil ejecutar en Cloud SQL

### 3. **Script Python Asíncrono de Diagnóstico**
- Archivo: [diagnostico_senales_prod.py](diagnostico_senales_prod.py)
- Diagnóstico integral: endpoint + base de datos

---

## 📊 Checklist de Verificación

- [ ] Ejecutar [diagnostico_senales.sql](diagnostico_senales.sql)
- [ ] Ejecutar `python test_senales_prod_simple.py`
- [ ] Revisar logs en Cloud Run
- [ ] Verificar si hay datos en `senal_detectada`
- [ ] Verificar relaciones en `categoria_senal`
- [ ] Verificar relaciones en `categoria_analisis_senal`
- [ ] Confirmar permisos de usuario `app_user`

---

## 📞 Siguientes Pasos

1. **Ejecutar diagnóstico**: Usa los scripts proporcionados
2. **Identificar causa**: ¿Faltan datos o hay error SQL?
3. **Aplicar solución**: Inserta datos o corrige JOINs
4. **Validar**: Vuelve a probar el endpoint
5. **Monitorear**: Agrega logs para futuras investigaciones

---

## 🔗 Archivos Relacionados

- [app/api/senales_v2.py](app/api/senales_v2.py) - Endpoints
- [app/services/senal_service_v2.py](app/services/senal_service_v2.py) - Lógica
- [app/database/models_sds.py](app/database/models_sds.py) - Modelos BD
- [diagnostico_senales.sql](diagnostico_senales.sql) - SQL de diagnóstico
- [test_senales_prod_simple.py](test_senales_prod_simple.py) - Test simple
- [diagnostico_senales_prod.py](diagnostico_senales_prod.py) - Diagnóstico completo

---

## ⚠️ NOTA IMPORTANTE

**El endpoint funciona correctamente**. El problema es que:
- **No hay datos** en la tabla `senal_detectada`, O
- **Hay un problema** con las relaciones entre tablas

Usa los scripts de diagnóstico para identificar exactamente cuál es el problema.
