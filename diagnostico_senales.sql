-- Script de diagnóstico para problema con endpoint /api/v2/senales/consultar
-- Ejecutar en la base de datos de producción para diagnosticar por qué no hay datos

-- 1. Verificar que las tablas existen
SELECT 'TABLA SENAL_DETECTADA' as verificacion, EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'sds' AND table_name = 'senal_detectada'
) as existe;

SELECT 'TABLA CATEGORIA_SENAL' as verificacion, EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'sds' AND table_name = 'categoria_senal'
) as existe;

SELECT 'TABLA CATEGORIA_ANALISIS_SENAL' as verificacion, EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'sds' AND table_name = 'categoria_analisis_senal'
) as existe;

-- 2. Contar registros en cada tabla
SELECT 'Registros en SENAL_DETECTADA' as tabla, COUNT(*) as cantidad FROM sds.senal_detectada;
SELECT 'Registros en CATEGORIA_SENAL' as tabla, COUNT(*) as cantidad FROM sds.categoria_senal;
SELECT 'Registros en CATEGORIA_ANALISIS_SENAL' as tabla, COUNT(*) as cantidad FROM sds.categoria_analisis_senal;

-- 3. Ver estructura de columnas
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'sds' AND table_name = 'senal_detectada'
ORDER BY ordinal_position;

SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'sds' AND table_name = 'categoria_senal'
ORDER BY ordinal_position;

-- 4. Si hay datos, ver ejemplos
SELECT 
    sd.id_senal_detectada,
    sd.id_categoria_senal,
    sd.id_categoria_analisis,
    sd.fecha_deteccion,
    sd.score_riesgo,
    sd.estado
FROM sds.senal_detectada sd
LIMIT 5;

-- 5. Ver categorías disponibles
SELECT 
    id_categoria_senales,
    nombre_categoria_senal,
    color
FROM sds.categoria_senal
LIMIT 10;

-- 6. Ver categorías de análisis disponibles
SELECT 
    id_categoria_analisis_senal,
    nombre_categoria_analisis
FROM sds.categoria_analisis_senal
LIMIT 10;

-- 7. Probar la query del endpoint (la que usa consultar_senales)
-- Esta es la query que debería funcionar:
SELECT 
    sd.id_senal_detectada,
    CONCAT('Señal #', sd.id_senal_detectada) as titulo,
    cs.nombre_categoria_senal,
    COALESCE(cs.color, '#CCCCCC') as color,
    sd.score_riesgo,
    sd.fecha_deteccion,
    cas.nombre_categoria_analisis,
    'Sistema' as usuario
FROM sds.senal_detectada sd
JOIN sds.categoria_senal cs ON sd.id_categoria_senal = cs.id_categoria_senales
JOIN sds.categoria_analisis_senal cas ON sd.id_categoria_analisis = cas.id_categoria_analisis_senal
ORDER BY sd.score_riesgo DESC, sd.fecha_deteccion DESC
LIMIT 10;

-- 8. Ver si hay registros huérfanos (sin relación a categorías)
SELECT 
    sd.id_senal_detectada,
    sd.id_categoria_senal,
    sd.id_categoria_analisis,
    (SELECT COUNT(*) FROM sds.categoria_senal cs WHERE cs.id_categoria_senales = sd.id_categoria_senal) as categoria_senal_existe,
    (SELECT COUNT(*) FROM sds.categoria_analisis_senal cas WHERE cas.id_categoria_analisis_senal = sd.id_categoria_analisis) as categoria_analisis_existe
FROM sds.senal_detectada sd
LIMIT 10;

-- 9. Contar registros sin relación válida
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN categoria_senal_existe = 0 THEN 1 ELSE 0 END) as sin_categoria_senal,
    SUM(CASE WHEN categoria_analisis_existe = 0 THEN 1 ELSE 0 END) as sin_categoria_analisis
FROM (
    SELECT 
        sd.id_senal_detectada,
        (SELECT COUNT(*) FROM sds.categoria_senal cs WHERE cs.id_categoria_senales = sd.id_categoria_senal) as categoria_senal_existe,
        (SELECT COUNT(*) FROM sds.categoria_analisis_senal cas WHERE cas.id_categoria_analisis_senal = sd.id_categoria_analisis) as categoria_analisis_existe
    FROM sds.senal_detectada sd
) t;
