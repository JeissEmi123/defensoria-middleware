-- Agregar la columna color si no existe
ALTER TABLE sds.categoria_senal ADD COLUMN IF NOT EXISTS color VARCHAR(50);

-- Actualizar los colores por defecto
UPDATE sds.categoria_senal 
SET color = CASE 
    WHEN nombre_categoria_senal = 'Problemas menores' THEN '#808080'
    WHEN nombre_categoria_senal = 'Riesgos potenciales' THEN '#FFA500' 
    WHEN nombre_categoria_senal LIKE '%Amenaza%' OR nombre_categoria_senal LIKE '%Crisis%' THEN '#FF0000'
    WHEN nombre_categoria_senal = 'Rojo' THEN '#FF0000'
    WHEN nombre_categoria_senal = 'Amarillo' THEN '#FFFF00'
    WHEN nombre_categoria_senal = 'Verde' THEN '#00FF00'
    ELSE '#CCCCCC'
END
WHERE color IS NULL OR color = '';