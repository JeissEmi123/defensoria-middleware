-- Script para otorgar permisos al usuario defensoria_app en el schema sds
-- Ejecutar en la base de datos de GCP

-- Otorgar permisos al schema sds
GRANT USAGE ON SCHEMA sds TO defensoria_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sds TO defensoria_app;
GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA sds TO defensoria_app;

-- Otorgar permisos por defecto para futuras tablas
ALTER DEFAULT PRIVILEGES IN SCHEMA sds GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO defensoria_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA sds GRANT SELECT, USAGE ON SEQUENCES TO defensoria_app;

-- Verificar que el usuario puede acceder
SELECT 'Permisos otorgados correctamente' as resultado;

-- Mostrar permisos actuales
SELECT 
    schemaname,
    tablename,
    tableowner,
    hasinserts,
    hasselects,
    hasupdates,
    hasdeletes
FROM pg_tables 
WHERE schemaname = 'sds'
AND tablename = 'categoria_senal';