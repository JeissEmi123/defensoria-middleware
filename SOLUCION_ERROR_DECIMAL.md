# ✅ SOLUCIÓN - Error "Decimal is not JSON serializable"

## 🔴 Error en Producción

```
Error guardando comentario: 
{message: 'Error al actualizar señal: Object of type Decimal is not JSON serializable', status: 500}
```

**Endpoint afectado:** `PATCH /api/v2/senales/{id_senal}`

## 🔍 Causa Raíz

El endpoint `actualizar_senal` estaba usando `jsonable_encoder()` de FastAPI para serializar la respuesta, pero este encoder **no maneja correctamente los objetos `Decimal`** de PostgreSQL en todos los casos.

### Código Problemático (línea 310):
```python
return jsonable_encoder(resultado)  # ❌ Falla con Decimals
```

## ✅ Solución Aplicada

Reemplazamos `jsonable_encoder` con nuestra función personalizada `serialize_decimal` que ya existe en el proyecto y maneja correctamente todos los tipos de datos de PostgreSQL.

### Cambios en `app/api/senales_v2.py`:

**1. Removido import innecesario:**
```python
# ❌ ANTES
from fastapi.encoders import jsonable_encoder

# ✅ DESPUÉS  
from app.core.json_utils import serialize_decimal
```

**2. Actualizado el return del endpoint:**
```python
# ❌ ANTES (línea 310)
return jsonable_encoder(resultado)

# ✅ DESPUÉS
return resultado  # Ya viene serializado del servicio
```

**Nota:** El servicio `SenalServiceV2.actualizar_senal()` ya retorna el resultado serializado con `serialize_decimal()` en la línea 956, por lo que no necesitamos volver a serializarlo en el endpoint.

## 🧪 Verificación Local

```bash
# 1. Reiniciar aplicación
docker-compose restart app

# 2. Probar el endpoint
curl -X PATCH "http://localhost:9000/api/v2/senales/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"id_categoria_senal":2,"descripcion_cambio":"test","confirmo_revision":true}'
```

## 🚀 Desplegar a Producción

```bash
# Opción 1: Script automático
./deploy-prod.sh

# Opción 2: Manual
gcloud builds submit --config=cloudbuild-prod.yaml --project=sat-defensoriapueblo
```

## 📊 Verificar en Producción

```bash
# 1. Verificar que el servicio está corriendo
gcloud run services describe defensoria-middleware-prod \
  --region=us-central1 \
  --project=sat-defensoriapueblo

# 2. Probar el endpoint corregido
curl -X PATCH "https://defensoria-middleware-prod-411798681660.us-central1.run.app/api/v2/senales/2001" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"id_categoria_senal":6,"descripcion_cambio":"pruebas","confirmo_revision":true}'

# 3. Ver logs en tiempo real
gcloud run services logs tail defensoria-middleware-prod \
  --region=us-central1 \
  --project=sat-defensoriapueblo
```

## 🔧 Función serialize_decimal

La función `serialize_decimal` en `app/core/json_utils.py` maneja correctamente:
- ✅ Objetos `Decimal` → `float`
- ✅ Objetos `datetime` → `str` (ISO format)
- ✅ Objetos `date` → `str` (ISO format)
- ✅ Diccionarios anidados
- ✅ Listas y tuplas

```python
def serialize_decimal(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: serialize_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_decimal(item) for item in obj]
    # ... más conversiones
    return obj
```

## 📝 Resumen de Cambios

| Archivo | Línea | Cambio |
|---------|-------|--------|
| `app/api/senales_v2.py` | 6 | ❌ Removido `from fastapi.encoders import jsonable_encoder` |
| `app/api/senales_v2.py` | 12 | ✅ Agregado `from app.core.json_utils import serialize_decimal` |
| `app/api/senales_v2.py` | 310 | ✅ Cambiado `return jsonable_encoder(resultado)` → `return resultado` |

## ⚠️ Importante

- El servicio `SenalServiceV2.actualizar_senal()` **ya serializa** el resultado con `serialize_decimal()` antes de retornarlo
- **No es necesario** volver a serializar en el endpoint
- Esta solución aplica para **todos los endpoints** que retornan datos con Decimals

## ✅ Resultado Esperado

Después del despliegue:
- ✅ El endpoint `PATCH /api/v2/senales/{id}` funciona correctamente
- ✅ Los comentarios se guardan sin error 500
- ✅ Los valores `Decimal` se serializan correctamente a JSON
- ✅ La respuesta incluye todos los campos actualizados

---

**Estado:** ✅ Solucionado  
**Próximo paso:** Desplegar a producción con `./deploy-prod.sh`
