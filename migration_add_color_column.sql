
-- Migración: Agregar columna color a categoria_senal
-- Fecha: 2026-01-19

-- Agregar la columna color si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'categoria_senal' 
        AND table_schema = 'sds' 
        AND column_name = 'color'
    ) THEN
        ALTER TABLE sds.categoria_senal ADD COLUMN color VARCHAR(50);
        RAISE NOTICE 'Columna color agregada a sds.categoria_senal';
    ELSE
        RAISE NOTICE 'La columna color ya existe en sds.categoria_senal';
    END IF;
END $$;

-- Actualizar los colores por defecto
UPDATE sds.categoria_senal 
SET color = CASE 
    WHEN nombre_categoria_senal ILIKE '%menor%' OR nombre_categoria_senal ILIKE '%ruido%' THEN '#808080'
    WHEN nombre_categoria_senal ILIKE '%riesgo%' OR nombre_categoria_senal ILIKE '%paracrisis%' THEN '#FFA500' 
    WHEN nombre_categoria_senal ILIKE '%amenaza%' OR nombre_categoria_senal ILIKE '%crisis%' OR nombre_categoria_senal ILIKE '%críti%' THEN '#FF0000'
    WHEN nombre_categoria_senal ILIKE '%rojo%' THEN '#FF0000'
    WHEN nombre_categoria_senal ILIKE '%amarillo%' THEN '#FFFF00'
    WHEN nombre_categoria_senal ILIKE '%verde%' THEN '#00FF00'
    ELSE COALESCE(color, '#CCCCCC')
END
WHERE color IS NULL OR color = '' OR LENGTH(TRIM(color)) = 0;

-- Mostrar el resultado
SELECT 'Migración completada. Categorías actualizadas:' as mensaje;
SELECT id_categoria_senales, nombre_categoria_senal, color, nivel 
FROM sds.categoria_senal 
ORDER BY nivel, id_categoria_senales;
