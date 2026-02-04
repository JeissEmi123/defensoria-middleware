-- =========================================
-- SCRIPT 1: OTORGAR PERMISOS AL USUARIO app_user
-- =========================================
-- Ejecutar en Google Cloud Console > SQL > defensoria-db > Consultas

-- Verificar usuarios existentes
SELECT usename as usuario_existente FROM pg_user ORDER BY usename;

-- Verificar si el usuario app_user existe (debería existir)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'app_user') THEN
        RAISE EXCEPTION 'El usuario app_user no existe. Debe crearse primero en Cloud SQL.';
    ELSE
        RAISE NOTICE 'Usuario app_user encontrado correctamente';
    END IF;
END $$;

-- Otorgar permisos al schema sds
GRANT USAGE ON SCHEMA sds TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sds TO app_user;
GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA sds TO app_user;

-- Otorgar permisos por defecto para futuras tablas
ALTER DEFAULT PRIVILEGES IN SCHEMA sds GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA sds GRANT SELECT, USAGE ON SEQUENCES TO app_user;

-- Verificar que se aplicaron los permisos
SELECT 
    'Permisos otorgados correctamente al usuario app_user' as resultado;

-- Verificar acceso a la tabla categoria_senal
SELECT COUNT(*) as total_categorias FROM sds.categoria_senal;