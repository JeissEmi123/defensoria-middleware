BEGIN;

SET search_path TO sds;

-- Crear las tablas sin restricciones de clave foránea primero
DROP TABLE IF EXISTS sds.figuras_publicas CASCADE;
CREATE TABLE sds.figuras_publicas
(
    id_figura_publica smallint NOT NULL,
    nombre_actor text,
    peso_actor numeric(5, 2),
    id_categoria_observacion smallint,
    PRIMARY KEY (id_figura_publica)
);

DROP TABLE IF EXISTS sds.influencers CASCADE;
CREATE TABLE sds.influencers
(
    id_influencer smallint NOT NULL,
    nombre_influencer text,
    peso_influencer numeric(5, 2),
    id_categoria_observacion smallint,
    PRIMARY KEY (id_influencer)
);

DROP TABLE IF EXISTS sds.medios_digitales CASCADE;
CREATE TABLE sds.medios_digitales
(
    id_medio_digital smallint NOT NULL,
    nombre_medio_digital text,
    peso_medio_digital numeric(5, 2),
    id_categoria_observacion smallint,
    PRIMARY KEY (id_medio_digital)
);

DROP TABLE IF EXISTS sds.entidades CASCADE;
CREATE TABLE sds.entidades
(
    id_entidades smallint NOT NULL,
    nombre_entidad text,
    peso_entidad numeric(5, 2),
    id_categoria_observacion smallint,
    PRIMARY KEY (id_entidades)
);

-- Insertar datos
INSERT INTO sds.figuras_publicas (id_figura_publica, nombre_actor, peso_actor, id_categoria_observacion) VALUES
(1, 'Gustavo Petro', 85.00, 11),
(2, 'Álvaro Uribe Vélez', 90.00, 11),
(3, 'Iván Duque Márquez', 75.00, 11),
(4, 'Claudia López', 80.00, 11),
(5, 'Francisco Santos', 70.00, 11),
(6, 'Germán Vargas Lleras', 65.00, 11),
(7, 'María Fernanda Cabal', 85.00, 11),
(8, 'Roy Barreras', 60.00, 11),
(9, 'Piedad Córdoba', 80.00, 11),
(10, 'Jorge Enrique Robledo', 75.00, 11);

INSERT INTO sds.influencers (id_influencer, nombre_influencer, peso_influencer, id_categoria_observacion) VALUES
(1, 'Juanpis González', 90.00, 12),
(2, 'La Paisa (Marce)', 85.00, 12),
(3, 'La Tigresa del Oriente', 80.00, 12),
(4, 'Pipepunk', 75.00, 12),
(5, 'Coscu', 70.00, 12);

INSERT INTO sds.medios_digitales (id_medio_digital, nombre_medio_digital, peso_medio_digital, id_categoria_observacion) VALUES
(1, 'El Tiempo', 95.00, 14),
(2, 'El Espectador', 90.00, 14),
(3, 'Semana', 85.00, 14),
(4, 'La Silla Vacía', 80.00, 14),
(5, 'Blu Radio', 85.00, 14);

INSERT INTO sds.entidades (id_entidades, nombre_entidad, peso_entidad, id_categoria_observacion) VALUES
(1, 'Fuerzas Militares de Colombia', 95.00, 31),
(2, 'Policía Nacional de Colombia', 90.00, 31),
(3, 'Fiscalía General de la Nación', 85.00, 31),
(4, 'Procuraduría General de la Nación', 80.00, 31),
(5, 'Contraloría General de la República', 75.00, 31);

COMMIT;