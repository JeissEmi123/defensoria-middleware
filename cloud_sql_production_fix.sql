-- =========================================================
-- SCRIPT SQL PARA CLOUD SQL PRODUCCIÓN
-- =========================================================
-- Este script debe ejecutarse en Cloud SQL como usuario postgres
-- para solucionar el DATABASE_ERROR en /api/v2/senales/home/dashboard

-- 1. Otorgar permisos básicos al schema
GRANT USAGE ON SCHEMA sds TO app_user;

-- 2. Permisos en todas las tablas existentes
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sds TO app_user;

-- 3. Permisos en secuencias (para auto-increment)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA sds TO app_user;

-- 4. Permisos por defecto para tablas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA sds 
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

-- 5. Permisos por defecto para secuencias futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA sds 
GRANT USAGE, SELECT ON SEQUENCES TO app_user;

-- 6. VERIFICACIÓN - estas consultas deben devolver TRUE
SELECT 
    'Verificación de permisos:' as mensaje,
    has_schema_privilege('app_user', 'sds', 'USAGE') as schema_usage_ok,
    has_table_privilege('app_user', 'sds.senal_detectada', 'SELECT') as table_select_ok,
    has_table_privilege('app_user', 'sds.categoria_senal', 'SELECT') as categoria_select_ok;

-- 7. PRUEBA DE LA CONSULTA QUE ESTABA FALLANDO
-- (ejecutar como app_user después de aplicar permisos)
/*
SELECT 
    sd.id_senal_detectada,
    sd.fecha_deteccion,
    sd.score_riesgo,
    cs.nombre_categoria_senal
FROM sds.senal_detectada sd
JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales
WHERE sd.score_riesgo >= 80
ORDER BY sd.fecha_deteccion DESC
LIMIT 5;
*/

-- =========================================================
-- INSTRUCCIONES DE EJECUCIÓN
-- =========================================================
-- 1. Conectar a Cloud SQL como postgres:
--    gcloud sql connect defensoria-db --user=postgres
--
-- 2. Seleccionar la base de datos:
--    \c defensoria_db;
--
-- 3. Ejecutar este script completo
--
-- 4. Reiniciar Cloud Run:
--    gcloud run services update defensoria-middleware-prod --region=us-central1
-- =========================================================