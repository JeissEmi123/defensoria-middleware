BEGIN;

DROP SCHEMA IF EXISTS sds CASCADE;
CREATE SCHEMA sds;

SET search_path TO sds;

/*
DROP TABLE IF EXISTS "sds.categoria_analisis_senal";
DROP TABLE IF EXISTS "sds.conducta_vulneratoria";
DROP TABLE IF EXISTS "sds.palabra_clave";
DROP TABLE IF EXISTS "sds.emoticon";
DROP TABLE IF EXISTS "sds.frase_clave";
DROP TABLE IF EXISTS "sds.categoria_senal";
DROP TABLE IF EXISTS "sds.senal_detectada";
DROP TABLE IF EXISTS "sds.categoria_observacion";
DROP TABLE IF EXISTS "sds.resultado_observacion_senal";
*/

DROP TABLE IF EXISTS "sds.categoria_analisis_senal";
CREATE TABLE IF NOT EXISTS sds.categoria_analisis_senal
(
    id_categoria_analisis_senal smallint NOT NULL,
    nombre_categoria_analisis text NOT NULL,
    descripcion_categoria_analisis text,
    PRIMARY KEY (id_categoria_analisis_senal)
);

DROP TABLE IF EXISTS "sds.conducta_vulneratoria";
CREATE TABLE IF NOT EXISTS sds.conducta_vulneratoria
(
    id_conducta_vulneratorias smallint NOT NULL,
    id_categoria_analisis_senal smallint NOT NULL,
    nombre_conducta_vulneratoria text NOT NULL,
    definicion_conducta_vulneratoria text NOT NULL,
    peso_conducta_vulneratoria numeric(5, 2),
    PRIMARY KEY (id_conducta_vulneratorias),
    CONSTRAINT fk_conducta_vul_categoria_analisis_senal FOREIGN KEY (id_categoria_analisis_senal)
    REFERENCES sds.categoria_analisis_senal (id_categoria_analisis_senal) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
);

DROP TABLE IF EXISTS "sds.palabra_clave";
CREATE TABLE IF NOT EXISTS sds.palabra_clave
(
    id_palabra_clave smallint NOT NULL,
    id_categoria_analisis_senal smallint NOT NULL,
    nombre_palabra_clave text,
    peso_palabra_clave numeric(5, 2),
    PRIMARY KEY (id_palabra_clave),
	CONSTRAINT fk_palabra_clave_categoria_analisis_senal FOREIGN KEY (id_categoria_analisis_senal)
    REFERENCES sds.categoria_analisis_senal (id_categoria_analisis_senal) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
);

DROP TABLE IF EXISTS "sds.emoticon";
CREATE TABLE IF NOT EXISTS sds.emoticon
(
    id_emoticon smallint NOT NULL,
    id_categoria_analisis_senal smallint NOT NULL,
    tipo_emoticon text,
    peso_emoticon numeric(5, 2),
    PRIMARY KEY (id_emoticon),
    CONSTRAINT fk_emoticon_categoria_analisis_senal FOREIGN KEY (id_categoria_analisis_senal)
    REFERENCES sds.categoria_analisis_senal (id_categoria_analisis_senal) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
);

DROP TABLE IF EXISTS "sds.frase_clave";
CREATE TABLE IF NOT EXISTS sds.frase_clave
(
    id_frase_clave smallint NOT NULL,
    id_categoria_analisis_senal smallint NOT NULL,
    nombre_frase_clave text,
    peso_frase_clave numeric(5, 2),
    PRIMARY KEY (id_frase_clave),
    CONSTRAINT fk_frase_clave_categoria_analisis_senal FOREIGN KEY (id_categoria_analisis_senal)
    REFERENCES sds.categoria_analisis_senal (id_categoria_analisis_senal) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
);

-- Insertar Metacategorías (Categorías de Análisis)
INSERT INTO sds.categoria_analisis_senal (id_categoria_analisis_senal, nombre_categoria_analisis, descripcion_categoria_analisis) VALUES
(1, 'Reclutamiento, uso y utilización de niñas, niños y adolescentes', 'Categoría relacionada con vulneraciones contra NNA en contexto de conflicto'),
(2, 'Violencia política', 'Categoría relacionada con violencia por motivaciones político-sociales'),
(3, 'Violencias digitales basadas en género', 'Categoría relacionada con violencias contra mujeres en entornos digitales');

-- Insertar Conductas Vulneratorias para la Categoría 1
INSERT INTO sds.conducta_vulneratoria (id_conducta_vulneratorias, id_categoria_analisis_senal, nombre_conducta_vulneratoria, definicion_conducta_vulneratoria, peso_conducta_vulneratoria) VALUES
(1, 1, 'Reclutamiento', 'Separación física de los niños, niñas y adolescentes de su entorno familiar y comunitario para que participen de manera directa en actividades bélicas, militares, tácticas, de sustento o para que desempeñen cualquier tipo de rol dentro de los grupos armados organizados o grupos delictivos organizados.', 100.00),
(2, 1, 'Utilización', 'Participación indirecta de niños, niñas y adolescentes en toda forma de vinculación, permanente u ocasional, con grupos armados organizados o grupos delincuenciales sin necesariamente ser separados de su entorno familiar y comunitario.', 100.00),
(3, 1, 'Uso', 'Comprende todas aquellas prácticas o comportamientos de quienes promuevan, induzcan, faciliten, financien o colaboren para que los niños, niñas y adolescentes participen en cualquier actividad ilegal de los grupos armados organizados o grupos delictivos organizados.', 100.00),
(4, 1, 'Vinculación', 'Cualquier forma de relacionamiento, acercamiento, aproximación a los niños, niñas y adolescentes para cumplir cualquier tipo de rol dentro o a favor de un GAO, GDO o GAOR.', 100.00);

-- Insertar Conductas Vulneratorias para la Categoría 2
INSERT INTO sds.conducta_vulneratoria (id_conducta_vulneratorias, id_categoria_analisis_senal, nombre_conducta_vulneratoria, definicion_conducta_vulneratoria, peso_conducta_vulneratoria) VALUES
(5, 2, 'Violencia Política', 'Aquella ejercida como medio de lucha político-social, ya sea con el fin de mantener, modificar, substituir o destruir un modelo de Estado o de sociedad, o también para destruir o reprimir a un grupo humano con identidad dentro de la sociedad por su afinidad social, política, gremial, étnica, racial, religiosa, cultural o ideológica.', 100.00),
(6, 2, 'Violencia político-social', 'Aquella ejercida por terceros motivados por fines político-ideológicos: personas, organizaciones o grupos particulares o no determinados, motivados por la lucha en torno al poder político o por la intolerancia frente a otras ideologías, razas, etnias, religiones, culturas o sectores sociales, estén o no organizados.', 100.00);

-- Insertar Conductas Vulneratorias para la Categoría 3
INSERT INTO sds.conducta_vulneratoria (id_conducta_vulneratorias, id_categoria_analisis_senal, nombre_conducta_vulneratoria, definicion_conducta_vulneratoria, peso_conducta_vulneratoria) VALUES
(7, 3, 'Violencia digital contra las mujeres (VCDM)', 'Violación de los derechos humanos y un acto de discriminación de carácter estructural que se inscribe en un contexto de violencias que abarca tanto los espacios físicos, como el entorno digital, donde las expresiones digitales pueden manifestarse como una extensión o un procedimiento de la violencia física, sexual, el acoso o el asecho.', 100.00),
(8, 3, 'Violencia facilitada por tecnología específica y dispositivos', 'Formas de acoso, violencia o abuso que se producen mediante herramientas tecnológicas específicas. Incluye el asecho con programas espía o el control remoto de dispositivos sin consentimiento.', 100.00),
(9, 3, 'Abuso amplificado en línea', 'Abuso que ocurre en internet y se intensifica por la naturaleza virtual del entorno digital, incluye la difusión no consentida de imágenes íntimas, campañas de desprestigio, acoso.', 100.00),
(10, 3, 'Nuevas formas de abuso generadas por la tecnología', 'Formas de violencia que surgen a partir de innovaciones tecnológicas que permiten nuevas modalidades de abuso. Incluye material sexualmente explícito falso (deepfakes), suplantación de identidad en entornos digitales, manipulación de audios.', 100.00),
(11, 3, 'Uso del entorno en línea para facilitar otras violencias', 'Cuando el espacio digital se convierte en medio para facilitar y posibilitar otros tipos de violencia, incluye la captación de víctimas por redes de trata en redes sociales, grooming, reclutamiento para explotación.', 100.00);

-- Insertar Palabras Clave para la Categoría 1
INSERT INTO sds.palabra_clave (id_palabra_clave, id_categoria_analisis_senal, nombre_palabra_clave, peso_palabra_clave) VALUES
(1, 1, 'grupos armados organizados', 100.00),
(2, 1, 'grupos delictivos organizados', 100.00),
(3, 1, 'reclutamiento', 100.00),
(4, 1, 'uso', 100.00),
(5, 1, 'utilización', 100.00),
(6, 1, 'niñas', 100.00),
(7, 1, 'niños', 100.00),
(8, 1, 'adolescentes', 100.00),
(9, 1, 'niñez', 100.00),
(10, 1, 'menores', 100.00),
(11, 1, 'jóvenes', 100.00),
(12, 1, 'juventud', 100.00),
(13, 1, 'conflicto', 100.00),
(14, 1, 'conflicto", "armado', 100.00),
(15, 1, 'guerra', 100.00),
(16, 1, 'disidencias', 100.00),
(17, 1, 'Estado Mayor Central', 100.00),
(18, 1, 'ELN', 100.00),
(19, 1, 'Segunda Marquetalia', 100.00),
(20, 1, 'crimen organizado', 100.00),
(21, 1, 'guerrilla', 100.00),
(22, 1, 'guerrillas', 100.00),
(23, 1, 'cultivos ilícitos', 100.00),
(24, 1, 'porte armas', 100.00),
(25, 1, 'enfrentamientos', 100.00),
(26, 1, 'redes", "sociales', 100.00),
(27, 1, 'TikTok', 100.00),
(28, 1, 'Facebook', 100.00),
(29, 1, 'Telegram', 100.00),
(30, 1, 'violencia', 100.00),
(31, 1, 'violencia sexual', 100.00),
(32, 1, 'explotación sexual', 100.00),
(33, 1, 'exploración', 100.00),
(34, 1, 'abuso', 100.00);

-- Insertar Palabras Clave para la Categoría 2
INSERT INTO sds.palabra_clave (id_palabra_clave, id_categoria_analisis_senal, nombre_palabra_clave, peso_palabra_clave) VALUES
(35, 2, 'líder social', 100.00),
(36, 2, 'líderes sociales', 100.00),
(37, 2, 'líderes indígenas', 100.00),
(38, 2, 'defensor derechos humanos', 100.00),
(39, 2, 'defensora derechos humanos', 100.00),
(40, 2, 'asesinato', 100.00),
(41, 2, 'asesinatos', 100.00),
(42, 2, 'desaparición', 100.00),
(43, 2, 'atentado', 100.00),
(44, 2, 'atentados', 100.00),
(45, 2, 'candidato', 100.00),
(46, 2, 'candidatos', 100.00),
(47, 2, 'candidata', 100.00),
(48, 2, 'candidatas', 100.00),
(49, 2, 'precandidato', 100.00),
(50, 2, 'precandidatos', 100.00),
(51, 2, 'precandidata', 100.00),
(52, 2, 'precandidatas', 100.00),
(53, 2, 'líderes políticos', 100.00),
(54, 2, 'partidos políticos', 100.00),
(55, 2, 'movimientos políticos', 100.00);

-- Insertar Palabras Clave para la Categoría 3
INSERT INTO sds.palabra_clave (id_palabra_clave, id_categoria_analisis_senal, nombre_palabra_clave, peso_palabra_clave) VALUES
(56, 3, 'acoso', 100.00),
(57, 3, 'acoso", "en", "línea', 100.00),
(58, 3, 'abuso', 100.00),
(59, 3, 'condenas', 100.00),
(60, 3, 'lideresas', 100.00),
(61, 3, 'defensoras', 100.00),
(62, 3, 'obstaculización', 100.00),
(63, 3, 'desprestigio', 100.00),
(64, 3, 'video", "íntimo', 100.00),
(65, 3, 'deepfakes', 100.00),
(66, 3, 'pornovenganza', 100.00),
(67, 3, 'grooming', 100.00),
(68, 3, 'trata', 100.00),
(69, 3, 'explotación sexual', 100.00),
(70, 3, 'prostitución', 100.00);

-- Insertar Emoticones Generados para la Categoría 1 (Contexto de conflicto y manipulación)
INSERT INTO sds.emoticon (id_emoticon, id_categoria_analisis_senal, tipo_emoticon, peso_emoticon) VALUES
(1, 1, '😢', 100.00),  -- Llanto (dolor, separación)
(2, 1, '👦➡️🔫', 100.00), -- Niño hacia arma
(3, 1, '⚠️', 100.00),  -- Advertencia (peligro)
(4, 1, '💔', 100.00),  -- Corazón roto (familia destruida)
(5, 1, '🗺️📍', 100.00), -- Mapa con ubicación (reclutamiento en zona)
(6, 1, '👥🔻', 100.00), -- Grupo decreciendo (pérdida)
(7, 1, '💰➡️👦', 100.00), -- Dinero hacia niño (explotación económica)
(8, 1, '📱💬', 100.00); -- Teléfono con mensaje (reclutamiento digital)

-- Insertar Emoticones Generados para la Categoría 2 (Contexto de violencia política)
INSERT INTO sds.emoticon (id_emoticon, id_categoria_analisis_senal, tipo_emoticon, peso_emoticon) VALUES
(9, 2, '⚖️', 100.00),  -- Balanza (justicia/desigualdad)
(10, 2, '🗳️❌', 100.00), -- Urna tachada (obstaculización democrática)
(11, 2, '👥⚔️', 100.00), -- Grupos en conflicto
(12, 2, '🔇', 100.00),  -- Silenciado (censura)
(13, 2, '🏛️', 100.00),  -- Edificio gubernamental (Estado)
(14, 2, '✊', 100.00),  -- Puño en alto (protesta, resistencia)
(15, 2, '⚠️', 100.00),  -- Advertencia (amenaza)
(16, 2, '📢', 100.00); -- Megáfono (discurso, proclama)

-- Insertar Emoticones Generados para la Categoría 3 (Contexto de violencia digital de género)
INSERT INTO sds.emoticon (id_emoticon, id_categoria_analisis_senal, tipo_emoticon, peso_emoticon) VALUES
(17, 3, '👩💻', 100.00), -- Mujer en computador (espacio digital)
(18, 3, '📵', 100.00),  -- No teléfono (violación espacio digital)
(19, 3, '🛡️❌', 100.00), -- Escudo tachado (desprotección)
(20, 3, '📸⚠️', 100.00), -- Cámara advertencia (imágenes íntimas)
(21, 3, '🔐', 100.00),  -- Candado (seguridad, privacidad vulnerada)
(22, 3, '👤➡️👤', 100.00), -- Persona a persona (suplantación)
(23, 3, '📧💔', 100.00), -- Email corazón roto (acoso digital)
(24, 3, '🚫', 100.00);  -- Prohibido (violencia)

-- Insertar Frases Clave Generadas para la Categoría 1
INSERT INTO sds.frase_clave (id_frase_clave, id_categoria_analisis_senal, nombre_frase_clave, peso_frase_clave) VALUES
(1, 1, 'reclutamiento de menores para la guerra', 100.00),
(2, 1, 'niños utilizados por grupos armados', 100.00),
(3, 1, 'vinculación de adolescentes al conflicto', 100.00),
(4, 1, 'explotación de niñas en redes sociales', 100.00),
(5, 1, 'los grupos ilegales usan a los jóvenes', 100.00),
(6, 1, 'menores en cultivos ilícitos', 100.00),
(7, 1, 'adolescentes portando armas', 100.00),
(8, 1, 'reclutamiento forzado de estudiantes', 100.00);

-- Insertar Frases Clave Generadas para la Categoría 2
INSERT INTO sds.frase_clave (id_frase_clave, id_categoria_analisis_senal, nombre_frase_clave, peso_frase_clave) VALUES
(9, 2, 'amenazas a líderes sociales', 100.00),
(10, 2, 'asesinato de defensores de derechos humanos', 100.00),
(11, 2, 'violencia contra candidatos políticos', 100.00),
(12, 2, 'ataques a movimientos sociales', 100.00),
(13, 2, 'persecución por ideología política', 100.00),
(14, 2, 'desaparición forzada de activistas', 100.00),
(15, 2, 'ataques a sedes de partidos', 100.00),
(16, 2, 'estigmatización de líderes indígenas', 100.00);

-- Insertar Frases Clave Generadas para la Categoría 3
INSERT INTO sds.frase_clave (id_frase_clave, id_categoria_analisis_senal, nombre_frase_clave, peso_frase_clave) VALUES
(17, 3, 'acoso en línea a mujeres', 100.00),
(18, 3, 'difusión de imágenes íntimas sin consentimiento', 100.00),
(19, 3, 'suplantación de identidad digital', 100.00),
(20, 3, 'campañas de desprestigio contra lideresas', 100.00),
(21, 3, 'grooming en redes sociales', 100.00),
(22, 3, 'control remoto de dispositivos de pareja', 100.00),
(23, 3, 'deepfakes con contenido sexual', 100.00),
(24, 3, 'trata de personas mediante internet', 100.00);

DROP TABLE IF EXISTS "sds.categoria_senal";
CREATE TABLE IF NOT EXISTS sds.categoria_senal
(
    id_categoria_senales smallint NOT NULL,
    id_parent_categoria_senales smallint,
    nombre_categoria_senal text,
    descripcion_categoria_senal text,
    nivel smallint,
    PRIMARY KEY (id_categoria_senales)
);

DROP TABLE IF EXISTS "sds.senal_detectada";
CREATE TABLE IF NOT EXISTS sds.senal_detectada
(
    id_senal_detectada smallint NOT NULL,
    id_categoria_senal smallint NOT NULL,
    fecha_deteccion timestamp with time zone,
    id_categoria_analisis_senal smallint NOT NULL,
    score_riesgo numeric(5, 2),
    fecha_actualizacion timestamp with time zone,
    PRIMARY KEY (id_senal_detectada)
);

DROP TABLE IF EXISTS "sds.categoria_observacion";
CREATE TABLE IF NOT EXISTS sds.categoria_observacion
(
    id_categoria_observacion smallint NOT NULL,
    id_parent_categoria_observacion smallint,
    codigo_categoria_observacion text NOT NULL,
    nombre_categoria_observacion text,
    descripcion_categoria_observacion text,
    nivel smallint,
    peso_categoria_observacion numeric(5, 2),
    PRIMARY KEY (id_categoria_observacion)
);

DROP TABLE IF EXISTS "sds.resultado_observacion_senal";
CREATE TABLE IF NOT EXISTS sds.resultado_observacion_senal
(
    id_resultado_observacion_senal smallint NOT NULL,
    id_senal_detectada smallint NOT NULL,
    id_categoria_observacion smallint NOT NULL,
    resultado_observacion_categoria numeric(5, 2),
    codigo_categoria_observacion text,
    PRIMARY KEY (id_resultado_observacion_senal),
    CONSTRAINT fk_res_obs_senal_detectada FOREIGN KEY (id_senal_detectada)
    REFERENCES sds.senal_detectada (id_senal_detectada) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION,
	CONSTRAINT fk_res_obs_categoria_observacion FOREIGN KEY (id_categoria_observacion)
    REFERENCES sds.categoria_observacion (id_categoria_observacion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
);


-- ============================================
-- 1. POBLAR TABLA CATEGORÍA DE SEÑAL (3 tipos)
-- ============================================
INSERT INTO sds.categoria_senal (id_categoria_senales, id_parent_categoria_senales, nombre_categoria_senal, descripcion_categoria_senal, nivel) VALUES
(1, NULL, 'Ruido', 'Entramado de interacciones digitales desafiantes o controversiales que no constituyen amenaza o riesgo de violación a DDHH. Se enmarcan en ejercicio legítimo de libre expresión y debate público.', 1),
(2, NULL, 'Paracrisis', 'Señales de advertencia sobre situaciones emergentes que indican riesgo de vulneración de DDHH. Pueden generar daños psicosociales, reputacionales o afectar participación ciudadana.', 1),
(3, NULL, 'Crisis', 'Señales de eventos de alta complejidad que constituyen amenaza inmediata contra vida, integridad, libertad o seguridad. Consecuencias graves e irreversibles que requieren intervención urgente.', 1),
(4, 2, 'Rojo', 'Amenazas significativas como contenido viral negativo, problemas legales o situaciones que vulneran derechos humanos y fundamentales. Requieren atención y escalamiento urgente. Pueden señalar la existencia de una crisis', 2),
(5, 2, 'Amarillo', 'Riesgos potenciales que pueden escalar si no se manejan de manera adecuada, como tendencias negativas emergentes o temas controvertidos. Pueden señalar la existencia de una paracrisis', 2),
(6, 2, 'Verde', 'Problemas menores o comentarios generales que no requieren una acción inmediata. Pueden ser parte del ruido digital, tratarse de eventos aislados que es preferible no amplificar o de muestras legítimas y controladas de disenso.', 2);

-- ============================================
-- 2. POBLAR TABLA CATEGORÍA DE OBSERVACIÓN
-- ============================================
-- Nivel 1: Dimensiones principales (20% cada una)

INSERT INTO sds.categoria_observacion (id_categoria_observacion, id_parent_categoria_observacion, codigo_categoria_observacion, nombre_categoria_observacion, descripcion_categoria_observacion, nivel, peso_categoria_observacion) VALUES
(1, NULL, 'Actores', 'Actores', 'Cuentas involucradas en la conversación: figuras públicas, autoridades, individuos, cuentas anónimas, grupos o colectivos.', 1, 20.00),
(2, NULL, 'Dinámica', 'Dinámica', 'Evolución de la conversación en el tiempo y signos de crecimiento orgánico o manipulación.', 1, 20.00),
(3, NULL, 'Contenido', 'Contenido', 'Narrativas implicadas y su posible impacto en protección, reputación o seguridad de personas o colectivos.', 1, 20.00),
(4, NULL, 'Expansión', 'Expansión', 'Movimiento y extensión de los discursos en torno a vulneraciones de DDHH.', 1, 20.00),
(5, NULL, 'Impacto', 'Impacto', 'Posibles consecuencias de la conversación, considerando el potencial del discurso para vulnerar derechos.', 1, 20.00);

-- Subcategorías para Actores (A1-A4)
INSERT INTO sds.categoria_observacion VALUES (11, 1, 'Actores_1', 'Involucramiento de figuras públicas', 'Participación de figuras públicas tradicionales que pueden cambiar percepción pública o amplificar narrativas asociadas con vulneración de DDHH.', 2, 100.00);
INSERT INTO sds.categoria_observacion VALUES (12, 1, 'Actores_2', 'Participación de influencers o grupos reconocidos', 'Participación de personalidades con influencia que pueden cambiar percepción pública o dinámicas de conversación.', 2, 100.00);
INSERT INTO sds.categoria_observacion VALUES (13, 1, 'Actores_3', 'Participación de partes anteriormente neutrales', 'Cambio en participación de audiencias previamente neutrales hacia posiciones que podrían generar riesgos.', 2, 100.00);
INSERT INTO sds.categoria_observacion VALUES (14, 1, 'Actores_4', 'Cubrimiento en medios', 'Presencia, tratamiento y alcance que medios tradicionales o digitales dan a la conversación.', 2, 100.00);

-- Subcategorías para Dinámica (B1-B3)
INSERT INTO sds.categoria_observacion VALUES (21, 2, 'Dinamica_1', 'Duración', 'Tiempo que la conversación ha estado activa y sostenida.', 2, 100.00);
INSERT INTO sds.categoria_observacion VALUES (22, 2, 'Dinamica_2', 'Patrón de crecimiento', 'Cómo crece o evoluciona la conversación: gradual o repentina.', 2, 100.00);
INSERT INTO sds.categoria_observacion VALUES (23, 2, 'Dinamica_3', 'Señales de coordinación', 'Esfuerzos organizados o campañas que podrían estar impulsando conversación artificialmente.', 2, 100.00);

-- Subcategorías para Contenido (C1-C2)
INSERT INTO sds.categoria_observacion VALUES (31, 3, 'Contenido_1', 'Tipo de contenido', 'Naturaleza del contenido y narrativas asociadas.', 2, 100.00);
INSERT INTO sds.categoria_observacion VALUES (32, 3, 'Contenido_2', 'Intencionalidad discursiva', 'Objetivo o intención detrás del discurso en la conversación.', 2, 100.00);

-- Subcategorías para Expansión (D1-D3)
INSERT INTO sds.categoria_observacion VALUES (41, 4, 'Expansion_1', 'Amplificación', 'Cómo los contenidos se expanden más allá de su origen, alcanzando audiencia más amplia.', 2, 100.00);
INSERT INTO sds.categoria_observacion VALUES (42, 4, 'Expansion_2', 'Alcance', 'Qué tan lejos ha llegado la conversación en términos geográficos y demográficos.', 2, 100.00);
INSERT INTO sds.categoria_observacion VALUES (43, 4, 'Expansion_3', 'Plataformas involucradas', 'Número y tipo de plataformas digitales donde aparece la conversación.', 2, 100.00);

-- Subcategorías para Impacto (E1-E4)
INSERT INTO sds.categoria_observacion VALUES (51, 5, 'Impacto_1', 'Potencial de daño', 'Posibilidad de que la conversación genere daños concretos a personas o grupos.', 2, 100.00);
INSERT INTO sds.categoria_observacion VALUES (52, 5, 'Impacto_2', 'Intensidad de interacciones negativas', 'Nivel de agresividad, desinformación o expresiones de odio en la conversación.', 2, 100.00);
INSERT INTO sds.categoria_observacion VALUES (53, 5, 'Impacto_3', 'Divulgación de datos personales', 'Implicaciones de divulgación de información sensible o privada.', 2, 100.00);
INSERT INTO sds.categoria_observacion VALUES (54, 5, 'Impacto_4', 'Capacidad de movilización', 'Potencial de la conversación para generar acciones colectivas o movilizaciones.', 2, 100.00);

END;