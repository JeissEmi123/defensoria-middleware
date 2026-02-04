BEGIN;

SET search_path TO sds;

DROP TABLE IF EXISTS "sds.figuras_publicas";
CREATE TABLE IF NOT EXISTS sds.figuras_publicas
(
    id_figura_publica smallint NOT NULL,
    nombre_actor text,
    peso_actor numeric(5, 2),
    id_categoria_observacion smallint,
    PRIMARY KEY (id_figura_publica),
	CONSTRAINT fk_fig_publica_cat_observacion FOREIGN KEY (id_categoria_observacion)
    REFERENCES sds.categoria_observacion (id_categoria_observacion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
);

DROP TABLE IF EXISTS "sds.influencers";
CREATE TABLE IF NOT EXISTS sds.influencers
(
    id_influencer smallint NOT NULL,
    nombre_influencer text,
    peso_influencer numeric(5, 2),
    id_categoria_observacion smallint,
    PRIMARY KEY (id_influencer),
	CONSTRAINT fk_influencers_cat_observacion FOREIGN KEY (id_categoria_observacion)
    REFERENCES sds.categoria_observacion (id_categoria_observacion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
);

DROP TABLE IF EXISTS "sds.medios_digitales";
CREATE TABLE IF NOT EXISTS sds.medios_digitales
(
    id_medio_digital smallint NOT NULL,
    nombre_medio_digital text,
    peso_medio_digital numeric(5, 2),
    id_categoria_observacion smallint,
    PRIMARY KEY (id_medio_digital),
	CONSTRAINT fk_medios_digitales_cat_observacion FOREIGN KEY (id_categoria_observacion)
    REFERENCES sds.categoria_observacion (id_categoria_observacion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
);

DROP TABLE IF EXISTS "sds.entidades";
CREATE TABLE IF NOT EXISTS sds.entidades
(
    id_entidades smallint NOT NULL,
    nombre_entidad text,
    peso_entidad numeric(5, 2),
    id_categoria_observacion smallint,
    PRIMARY KEY (id_entidades),
	CONSTRAINT fk_entidades_cat_observacion FOREIGN KEY (id_categoria_observacion)
    REFERENCES sds.categoria_observacion (id_categoria_observacion) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
);

-- ============================================
-- POBLAR TABLA SDS.FIGURAS_PUBLICAS (50 registros)
-- Figuras públicas tradicionales colombianas
-- ============================================
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
(10, 'Jorge Enrique Robledo', 75.00, 11),
(11, 'Sergio Fajardo', 70.00, 11),
(12, 'Antonio Sanguino', 55.00, 11),
(13, 'Juan Manuel Galán', 65.00, 11),
(14, 'Catherine Juvinao', 60.00, 11),
(15, 'David Racero', 50.00, 11),
(16, 'Alexander López', 55.00, 11),
(17, 'Benedicta de los Ángeles', 45.00, 11),
(18, 'Harold Guerrero', 40.00, 11),
(19, 'Myriam A. de Rueda', 35.00, 11),
(20, 'José A. Ocampo', 80.00, 11),
(21, 'Armando Benedetti', 75.00, 11),
(22, 'Paloma Valencia', 85.00, 11),
(23, 'Humberto de la Calle', 70.00, 11),
(24, 'César Gaviria', 75.00, 11),
(25, 'Andrés Pastrana', 70.00, 11),
(26, 'Ernesto Samper', 65.00, 11),
(27, 'Nohemí Sanín', 60.00, 11),
(28, 'Antanas Mockus', 80.00, 11),
(29, 'Enrique Peñalosa', 75.00, 11),
(30, 'Carlos Fernando Galán', 70.00, 11),
(31, 'Gustavo Bolívar', 85.00, 11),
(32, 'Iván Cepeda', 80.00, 11),
(33, 'María José Pizarro', 75.00, 11),
(34, 'Jota Pe Hernández', 65.00, 11),
(35, 'Jorge Iván Ospina', 60.00, 11),
(36, 'Daniel Quintero', 70.00, 11),
(37, 'Federico Gutiérrez', 75.00, 11),
(38, 'Luis Pérez', 55.00, 11),
(39, 'Jorge Bedoya', 50.00, 11),
(40, 'Cielo Rusinque', 45.00, 11),
(41, 'Ana María Castañeda', 40.00, 11),
(42, 'Diego Molano', 65.00, 11),
(43, 'Angela María Robledo', 70.00, 11),
(44, 'Juan Carlos Losada', 60.00, 11),
(45, 'David Luna', 55.00, 11),
(46, 'Sandra Ortiz', 50.00, 11),
(47, 'Julian Rodríguez', 45.00, 11),
(48, 'Nicolás Ramos', 40.00, 11),
(49, 'Viviane Morales', 75.00, 11),
(50, 'Álvaro Leyva', 70.00, 11);

-- ============================================
-- POBLAR TABLA SDS.INFLUENCERS (20 registros)
-- Influencers digitales colombianos
-- ============================================
INSERT INTO sds.influencers (id_influencer, nombre_influencer, peso_influencer, id_categoria_observacion) VALUES
(1, 'Juanpis González', 90.00, 12),
(2, 'La Paisa (Marce)', 85.00, 12),
(3, 'La Tigresa del Oriente', 80.00, 12),
(4, 'Pipepunk', 75.00, 12),
(5, 'Coscu', 70.00, 12),
(6, 'Luisito Comunica', 85.00, 12),
(7, 'German Garmendia', 80.00, 12),
(8, 'Yuya', 75.00, 12),
(9, 'Juan Guarnizo', 80.00, 12),
(10, 'AuronPlay', 85.00, 12),
(11, 'El Rubius', 80.00, 12),
(12, 'Migue Granados', 70.00, 12),
(13, 'Dalas Review', 75.00, 12),
(14, 'Mikecrack', 65.00, 12),
(15, 'Vegetta777', 70.00, 12),
(16, 'Willyrex', 65.00, 12),
(17, 'Mangel', 60.00, 12),
(18, 'Alexby', 55.00, 12),
(19, 'Jordi Wild', 70.00, 12),
(20, 'Luis Ángel Arango', 45.00, 12);

-- ============================================
-- POBLAR TABLA SDS.MEDIOS_DIGITALES (30 registros)
-- Medios tradicionales y digitales colombianos
-- ============================================
INSERT INTO sds.medios_digitales (id_medio_digital, nombre_medio_digital, peso_medio_digital, id_categoria_observacion) VALUES
(1, 'El Tiempo', 95.00, 14),
(2, 'El Espectador', 90.00, 14),
(3, 'Semana', 85.00, 14),
(4, 'La Silla Vacía', 80.00, 14),
(5, 'Blu Radio', 85.00, 14),
(6, 'Caracol Radio', 90.00, 14),
(7, 'RCN Radio', 85.00, 14),
(8, 'W Radio', 80.00, 14),
(9, 'Caracol Televisión', 95.00, 14),
(10, 'RCN Televisión', 90.00, 14),
(11, 'Canal Uno', 70.00, 14),
(12, 'Señal Colombia', 65.00, 14),
(13, 'Telemedellín', 60.00, 14),
(14, 'Teleantioquia', 55.00, 14),
(15, 'Canal Capital', 70.00, 14),
(16, 'CityTV', 60.00, 14),
(17, 'NTN24', 75.00, 14),
(18, 'CNN en Español', 85.00, 14),
(19, 'DW Español', 70.00, 14),
(20, 'BBC Mundo', 80.00, 14),
(21, 'France 24 Español', 65.00, 14),
(22, 'RT en Español', 75.00, 14),
(23, 'Telesur', 70.00, 14),
(24, 'Venezolana de Televisión', 60.00, 14),
(25, 'Panamericana Televisión', 55.00, 14),
(26, 'América Televisión', 50.00, 14),
(27, 'TV Perú', 45.00, 14),
(28, 'Ecuavisa', 40.00, 14),
(29, 'Teleamazonas', 35.00, 14),
(30, 'Canal 10 Uruguay', 30.00, 14);

-- ============================================
-- POBLAR TABLA SDS.ENTIDADES (25 registros)
-- Entidades, colectivos y organizaciones colombianas
-- ============================================
INSERT INTO sds.entidades (id_entidades, nombre_entidad, peso_entidad, id_categoria_observacion) VALUES
(1, 'Fuerzas Militares de Colombia', 95.00, 31),
(2, 'Policía Nacional de Colombia', 90.00, 31),
(3, 'Fiscalía General de la Nación', 85.00, 31),
(4, 'Procuraduría General de la Nación', 80.00, 31),
(5, 'Contraloría General de la República', 75.00, 31),
(6, 'Defensoría del Pueblo', 90.00, 31),
(7, 'Ejército de Liberación Nacional (ELN)', 85.00, 31),
(8, 'Disidencias de las FARC', 80.00, 31),
(9, 'Clan del Golfo', 75.00, 31),
(10, 'Los Pelusos', 70.00, 31),
(11, 'Los Pachenca', 65.00, 31),
(12, 'Los Rastrojos', 60.00, 31),
(13, 'Los Urabeños', 55.00, 31),
(14, 'Águilas Negras', 50.00, 31),
(15, 'Autodefensas Gaitanistas', 45.00, 31),
(16, 'Bandas Criminales (BACRIM)', 40.00, 31),
(17, 'Cartel de Sinaloa', 35.00, 31),
(18, 'Cartel de Jalisco Nueva Generación', 30.00, 31),
(19, 'Cartel del Norte del Valle', 25.00, 31),
(20, 'Cartel de Cali', 20.00, 31),
(21, 'Cartel de Medellín', 15.00, 31),
(22, 'Tren de Aragua', 10.00, 31),
(23, 'Mafia Mexicana', 5.00, 31),
(24, 'Mafia Peruana', 0.00, 31),
(25, 'Mafia Ecuatoriana', 0.00, 31);

COMMIT;