-- ===============================================
-- CORRECCIÓN DE PERMISOS PARA app_user EN PRODUCCIÓN
-- ===============================================
-- Este script soluciona el error:
-- "permission denied for schema sds"
-- que causa el error 500 en /api/v2/senales/home/dashboard

-- 1. Otorgar permisos de uso al schema sds
GRANT USAGE ON SCHEMA sds TO app_user;

-- 2. Otorgar permisos de SELECT a todas las tablas existentes
GRANT SELECT ON ALL TABLES IN SCHEMA sds TO app_user;

-- 3. Otorgar permisos de INSERT, UPDATE, DELETE (para operaciones CRUD)
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sds TO app_user;

-- 4. Otorgar permisos en secuencias (para campos auto-incrementales como IDs)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA sds TO app_user;

-- 5. Configurar permisos por defecto para tablas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA sds 
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

-- 6. Configurar permisos por defecto para secuencias futuras  
ALTER DEFAULT PRIVILEGES IN SCHEMA sds 
GRANT USAGE, SELECT ON SEQUENCES TO app_user;

-- ===============================================
-- VERIFICACIÓN DE PERMISOS (ejecutar después)
-- ===============================================

-- Verificar permisos otorgados
SELECT 
    schemaname,
    tablename,
    has_table_privilege('app_user', schemaname||'.'||tablename, 'SELECT') as can_select,
    has_table_privilege('app_user', schemaname||'.'||tablename, 'INSERT') as can_insert,
    has_table_privilege('app_user', schemaname||'.'||tablename, 'UPDATE') as can_update,
    has_table_privilege('app_user', schemaname||'.'||tablename, 'DELETE') as can_delete
FROM pg_tables 
WHERE schemaname = 'sds'
ORDER BY tablename;

-- Probar la consulta que estaba fallando
SELECT 
    sd.id_senal_detectada,
    sd.fecha_deteccion, 
    sd.score_riesgo,
    cs.nombre_categoria_senal
FROM sds.senal_detectada sd
JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales
LIMIT 3;