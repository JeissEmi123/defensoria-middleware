BEGIN;

SET search_path TO sds;

-- Limpieza en orden de dependencias
DELETE FROM sds.resultado_observacion_senal;
DELETE FROM sds.senal_detectada;
DELETE FROM sds.figuras_publicas;
DELETE FROM sds.influencers;
DELETE FROM sds.medios_digitales;
DELETE FROM sds.entidades;
DELETE FROM sds.conducta_vulneratoria;
DELETE FROM sds.palabra_clave;
DELETE FROM sds.emoticon;
DELETE FROM sds.frase_clave;
DELETE FROM sds.categoria_observacion;
DELETE FROM sds.categoria_senal;
DELETE FROM sds.categoria_analisis_senal;

-- =====================
-- Catalogos base
-- =====================
INSERT INTO sds.categoria_analisis_senal VALUES
(1, 'Reclutamiento NNA', 'Vulneraciones contra NNA en conflicto'),
(2, 'Violencia politica', 'Violencia por motivaciones politico-sociales'),
(3, 'Violencias digitales de genero', 'Violencias contra mujeres en entornos digitales');

INSERT INTO sds.categoria_senal (
    id_categoria_senal,
    parent_categoria_senal_id,
    nombre_categoria_senal,
    descripcion,
    color,
    nivel,
    activo,
    fecha_creacion,
    fecha_actualizacion
) VALUES
(1, NULL, 'Ruido', 'Interacciones que no constituyen amenaza', '#808080', 1, true, NOW(), NOW()),
(2, NULL, 'Paracrisis', 'Riesgo emergente de vulneracion', '#FFA500', 1, true, NOW(), NOW()),
(3, NULL, 'Crisis', 'Amenaza inmediata a derechos', '#FF0000', 1, true, NOW(), NOW()),
(4, 2, 'Rojo', 'Amenaza alta', '#FF0000', 2, true, NOW(), NOW()),
(5, 2, 'Amarillo', 'Riesgo medio', '#FFFF00', 2, true, NOW(), NOW()),
(6, 2, 'Verde', 'Riesgo bajo', '#00FF00', 2, true, NOW(), NOW());

INSERT INTO sds.categoria_observacion VALUES
(1, NULL, 'Actores', 'Actores', 'Cuentas involucradas', 1, 20.00),
(2, NULL, 'Dinamica', 'Dinamica', 'Evolucion en el tiempo', 1, 20.00),
(3, NULL, 'Contenido', 'Contenido', 'Narrativas e impacto', 1, 20.00),
(4, NULL, 'Expansion', 'Expansion', 'Movimiento de discursos', 1, 20.00),
(5, NULL, 'Impacto', 'Impacto', 'Consecuencias', 1, 20.00),
(11, 1, 'Actores_1', 'Figuras publicas', 'Participacion de figuras', 2, 100.00),
(12, 1, 'Actores_2', 'Influencers', 'Participacion de influencers', 2, 100.00),
(13, 1, 'Actores_3', 'Audiencias neutrales', 'Cambio en audiencias', 2, 100.00),
(14, 1, 'Actores_4', 'Medios', 'Cubrimiento en medios', 2, 100.00),
(21, 2, 'Dinamica_1', 'Duracion', 'Tiempo activo', 2, 100.00),
(22, 2, 'Dinamica_2', 'Crecimiento', 'Patron de crecimiento', 2, 100.00),
(23, 2, 'Dinamica_3', 'Coordinacion', 'Senales de coordinacion', 2, 100.00),
(31, 3, 'Contenido_1', 'Tipo', 'Naturaleza del contenido', 2, 100.00),
(32, 3, 'Contenido_2', 'Intencionalidad', 'Objetivo del discurso', 2, 100.00),
(41, 4, 'Expansion_1', 'Amplificacion', 'Como se expande', 2, 100.00),
(42, 4, 'Expansion_2', 'Alcance', 'Alcance de la conversacion', 2, 100.00),
(43, 4, 'Expansion_3', 'Plataformas', 'Numero de plataformas', 2, 100.00),
(51, 5, 'Impacto_1', 'Danio', 'Potencial de dano', 2, 100.00),
(52, 5, 'Impacto_2', 'Intensidad', 'Interacciones negativas', 2, 100.00),
(53, 5, 'Impacto_3', 'Datos personales', 'Divulgacion de datos', 2, 100.00),
(54, 5, 'Impacto_4', 'Movilizacion', 'Capacidad de movilizacion', 2, 100.00);

-- =====================
-- Parametros
-- =====================
INSERT INTO sds.conducta_vulneratoria VALUES
(1, 'Reclutamiento', 'Captacion de menores', 'CV-001', 85.00, 1, true),
(2, 'Amenazas', 'Amenazas directas', 'CV-002', 90.00, 2, true),
(3, 'Acoso digital', 'Acoso y hostigamiento', 'CV-003', 70.00, 3, true);

INSERT INTO sds.palabra_clave VALUES
(1, 'reclutar', 'Contenido de reclutamiento', 1, true),
(2, 'amenaza', 'Amenaza directa', 2, true),
(3, 'acoso', 'Acoso digital', 3, true);

INSERT INTO sds.emoticon VALUES
(1, ':skull:', 'Riesgo alto', 2, true),
(2, ':warning:', 'Alerta', 1, true),
(3, ':no_entry:', 'Bloqueo', 3, true);

INSERT INTO sds.frase_clave VALUES
(1, 'te vamos a encontrar', 'Amenaza directa', 2, true),
(2, 'trabajo facil', 'Engano a menores', 1, true),
(3, 'te vamos a exponer', 'Acoso digital', 3, true);

-- =====================
-- Figuras y entidades
-- =====================
INSERT INTO sds.figuras_publicas (id_figura_publica, nombre_actor, peso_actor, id_categoria_observacion) VALUES
(1, 'Gustavo Petro', 85.00, 11),
(2, 'Claudia Lopez', 80.00, 11),
(3, 'Alvaro Uribe', 90.00, 11);

INSERT INTO sds.influencers (id_influencer, nombre_influencer, peso_influencer, id_categoria_observacion) VALUES
(1, 'Influencer 1', 75.00, 12),
(2, 'Influencer 2', 70.00, 12),
(3, 'Influencer 3', 65.00, 12);

INSERT INTO sds.medios_digitales (id_medio_digital, nombre_medio_digital, peso_medio_digital, id_categoria_observacion) VALUES
(1, 'El Tiempo', 95.00, 14),
(2, 'Semana', 85.00, 14),
(3, 'Caracol Radio', 90.00, 14);

INSERT INTO sds.entidades (id_entidades, nombre_entidad, peso_entidad, id_categoria_observacion) VALUES
(1, 'Defensoria del Pueblo', 90.00, 31),
(2, 'Fiscalia', 85.00, 31),
(3, 'Policia Nacional', 80.00, 31);

-- =====================
-- Senales y resultados
-- =====================
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
(1, 3, NOW() - INTERVAL '2 hours', 1, 92.00, NOW() - INTERVAL '1 hours', NULL, NULL, 'Senal prueba 1', NULL, 'DETECTADA', NULL, NULL, NULL, NULL),
(2, 3, NOW() - INTERVAL '3 hours', 2, 88.50, NOW() - INTERVAL '2 hours', NULL, NULL, 'Senal prueba 2', NULL, 'EN_REVISION', NULL, NULL, NULL, NULL),
(3, 2, NOW() - INTERVAL '4 hours', 3, 76.20, NOW() - INTERVAL '3 hours', NULL, NULL, 'Senal prueba 3', NULL, 'DETECTADA', NULL, NULL, NULL, NULL),
(4, 2, NOW() - INTERVAL '5 hours', 1, 69.10, NOW() - INTERVAL '4 hours', NULL, NULL, 'Senal prueba 4', NULL, 'VALIDADA', NULL, NULL, NULL, NULL),
(5, 3, NOW() - INTERVAL '6 hours', 2, 95.00, NOW() - INTERVAL '5 hours', NULL, NULL, 'Senal prueba 5', NULL, 'DETECTADA', NULL, NULL, NULL, NULL),
(6, 1, NOW() - INTERVAL '7 hours', 2, 40.00, NOW() - INTERVAL '6 hours', NULL, NULL, 'Senal prueba 6', NULL, 'RECHAZADA', NULL, NULL, NULL, NULL),
(7, 2, NOW() - INTERVAL '8 hours', 3, 81.30, NOW() - INTERVAL '7 hours', NULL, NULL, 'Senal prueba 7', NULL, 'EN_REVISION', NULL, NULL, NULL, NULL),
(8, 3, NOW() - INTERVAL '9 hours', 1, 89.90, NOW() - INTERVAL '8 hours', NULL, NULL, 'Senal prueba 8', NULL, 'DETECTADA', NULL, NULL, NULL, NULL),
(9, 2, NOW() - INTERVAL '10 hours', 3, 73.40, NOW() - INTERVAL '9 hours', NULL, NULL, 'Senal prueba 9', NULL, 'VALIDADA', NULL, NULL, NULL, NULL),
(10, 1, NOW() - INTERVAL '11 hours', 1, 35.00, NOW() - INTERVAL '10 hours', NULL, NULL, 'Senal prueba 10', NULL, 'RECHAZADA', NULL, NULL, NULL, NULL);

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
