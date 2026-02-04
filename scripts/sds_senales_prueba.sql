BEGIN;

SET search_path TO sds;

DELETE FROM sds.resultado_observacion_senal;
DELETE FROM sds.senal_detectada;

INSERT INTO sds.senal_detectada (
    id_senal_detectada,
    id_categoria_senal,
    fecha_deteccion,
    id_categoria_analisis,
    score_riesgo,
    fecha_actualizacion,
    categorias_observacion,
    plataformas_digitales,
    contenido_detectado,
    metadatos,
    estado,
    url_origen,
    usuario_asignado_id,
    fecha_resolucion,
    notas_resolucion
) VALUES
(1, 3, NOW() - INTERVAL '2 hours', 1, 92.00, NOW() - INTERVAL '1 hours', NULL, NULL, 'Prueba senal 1', NULL, 'DETECTADA', NULL, NULL, NULL, NULL),
(2, 3, NOW() - INTERVAL '3 hours', 2, 88.50, NOW() - INTERVAL '2 hours', NULL, NULL, 'Prueba senal 2', NULL, 'EN_REVISION', NULL, NULL, NULL, NULL),
(3, 2, NOW() - INTERVAL '4 hours', 3, 76.20, NOW() - INTERVAL '3 hours', NULL, NULL, 'Prueba senal 3', NULL, 'DETECTADA', NULL, NULL, NULL, NULL),
(4, 2, NOW() - INTERVAL '5 hours', 1, 69.10, NOW() - INTERVAL '4 hours', NULL, NULL, 'Prueba senal 4', NULL, 'VALIDADA', NULL, NULL, NULL, NULL),
(5, 3, NOW() - INTERVAL '6 hours', 2, 95.00, NOW() - INTERVAL '5 hours', NULL, NULL, 'Prueba senal 5', NULL, 'DETECTADA', NULL, NULL, NULL, NULL),
(6, 1, NOW() - INTERVAL '7 hours', 2, 40.00, NOW() - INTERVAL '6 hours', NULL, NULL, 'Prueba senal 6', NULL, 'RECHAZADA', NULL, NULL, NULL, NULL),
(7, 2, NOW() - INTERVAL '8 hours', 3, 81.30, NOW() - INTERVAL '7 hours', NULL, NULL, 'Prueba senal 7', NULL, 'EN_REVISION', NULL, NULL, NULL, NULL),
(8, 3, NOW() - INTERVAL '9 hours', 1, 89.90, NOW() - INTERVAL '8 hours', NULL, NULL, 'Prueba senal 8', NULL, 'DETECTADA', NULL, NULL, NULL, NULL),
(9, 2, NOW() - INTERVAL '10 hours', 3, 73.40, NOW() - INTERVAL '9 hours', NULL, NULL, 'Prueba senal 9', NULL, 'VALIDADA', NULL, NULL, NULL, NULL),
(10, 1, NOW() - INTERVAL '11 hours', 1, 35.00, NOW() - INTERVAL '10 hours', NULL, NULL, 'Prueba senal 10', NULL, 'RECHAZADA', NULL, NULL, NULL, NULL);

INSERT INTO sds.resultado_observacion_senal (
    id_resultado_observacion_senal,
    id_senal_detectada,
    id_categoria_observacion,
    resultado_observacion_categoria,
    codigo_categoria_observacion
) VALUES
(1, 1, 11, 85.00, 'Actores_1'),
(2, 1, 21, 70.00, 'Dinamica_1'),
(3, 1, 31, 60.00, 'Contenido_1'),
(4, 2, 12, 75.00, 'Actores_2'),
(5, 2, 22, 68.00, 'Dinamica_2'),
(6, 2, 32, 72.00, 'Contenido_2'),
(7, 3, 13, 55.00, 'Actores_3'),
(8, 3, 23, 64.00, 'Dinamica_3'),
(9, 3, 41, 58.00, 'Expansion_1'),
(10, 4, 14, 62.00, 'Actores_4'),
(11, 4, 42, 66.00, 'Expansion_2'),
(12, 4, 51, 74.00, 'Impacto_1'),
(13, 5, 11, 90.00, 'Actores_1'),
(14, 5, 43, 80.00, 'Expansion_3'),
(15, 5, 52, 88.00, 'Impacto_2');

COMMIT;
