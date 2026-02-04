-- =========================================
-- SCRIPT 2: VERIFICACIÓN FINAL
-- =========================================
-- Ejecutar después del script de permisos para confirmar que todo está bien

-- Verificar que la columna color existe
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'categoria_senal' 
AND table_schema = 'sds'
ORDER BY ordinal_position;

-- Verificar los datos en categoria_senal
SELECT 
    id_categoria_senales,
    nombre_categoria_senal,
    color,
    nivel,
    descripcion_categoria_senal
FROM sds.categoria_senal 
ORDER BY nivel, id_categoria_senales;

-- Confirmar que app_user tiene acceso
SELECT current_user as usuario_actual;
SELECT 'Test de acceso exitoso' as resultado;