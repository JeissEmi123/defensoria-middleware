"""
Revision ID: 011_add_sds_parameter_tables
Revises: 010_add_ultimo_usuario_categoria_senal
Create Date: 2026-01-05

Agregar tablas faltantes del módulo SDS y columnas de umbrales para categoria_senal
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "011_add_sds_parameter_tables"
down_revision = "010_add_ultimo_usuario_categoria_senal"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "categoria_senal",
        sa.Column("umbral_bajo", sa.Numeric(5, 2), nullable=True),
        schema="sds",
    )
    op.add_column(
        "categoria_senal",
        sa.Column("umbral_alto", sa.Numeric(5, 2), nullable=True),
        schema="sds",
    )
    op.execute(
        """
        UPDATE sds.categoria_senal
        SET
            umbral_bajo = CASE
                WHEN LOWER(nombre_categoria_senal) = 'crisis' THEN 90.00
                WHEN LOWER(nombre_categoria_senal) = 'paracrisis' THEN 31.00
                WHEN LOWER(nombre_categoria_senal) = 'ruido' THEN 0.00
                WHEN LOWER(nombre_categoria_senal) = 'rojo' THEN 61.00
                WHEN LOWER(nombre_categoria_senal) = 'amarillo' THEN 31.00
                WHEN LOWER(nombre_categoria_senal) = 'verde' THEN 11.00
                ELSE umbral_bajo
            END,
            umbral_alto = CASE
                WHEN LOWER(nombre_categoria_senal) = 'crisis' THEN 100.00
                WHEN LOWER(nombre_categoria_senal) = 'paracrisis' THEN 89.00
                WHEN LOWER(nombre_categoria_senal) = 'ruido' THEN 10.00
                WHEN LOWER(nombre_categoria_senal) = 'rojo' THEN 89.00
                WHEN LOWER(nombre_categoria_senal) = 'amarillo' THEN 60.00
                WHEN LOWER(nombre_categoria_senal) = 'verde' THEN 30.00
                ELSE umbral_alto
            END
        WHERE LOWER(nombre_categoria_senal) IN ('crisis', 'paracrisis', 'ruido', 'rojo', 'amarillo', 'verde')
        """
    )

    op.create_table(
        "categoria_observacion",
        sa.Column("id_categoria_observacion", sa.SmallInteger(), nullable=False),
        sa.Column("id_parent_categoria_observacion", sa.SmallInteger(), nullable=True),
        sa.Column("codigo_categoria_observacion", sa.Text(), nullable=False),
        sa.Column("nombre_categoria_observacion", sa.Text(), nullable=True),
        sa.Column("descripcion_categoria_observacion", sa.Text(), nullable=True),
        sa.Column("nivel", sa.SmallInteger(), nullable=False),
        sa.Column("peso_categoria_observacion", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(
            ["id_parent_categoria_observacion"],
            ["sds.categoria_observacion.id_categoria_observacion"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id_categoria_observacion"),
        sa.UniqueConstraint("codigo_categoria_observacion"),
        schema="sds",
    )

    op.create_table(
        "resultado_observacion_senal",
        sa.Column("id_resultado_observacion_senal", sa.SmallInteger(), nullable=False, autoincrement=True),
        sa.Column("id_senal_detectada", sa.Integer(), nullable=False),
        sa.Column("id_categoria_observacion", sa.SmallInteger(), nullable=False),
        sa.Column("resultado_observacion_categoria", sa.Numeric(5, 2), nullable=False),
        sa.Column("codigo_categoria_observacion", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id_senal_detectada"],
            ["sds.senal_detectada.id_senal_detectada"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["id_categoria_observacion"],
            ["sds.categoria_observacion.id_categoria_observacion"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id_resultado_observacion_senal"),
        schema="sds",
    )

    op.create_table(
        "conducta_vulneratoria",
        sa.Column("id_conducta_vulneratorias", sa.SmallInteger(), nullable=False, autoincrement=True),
        sa.Column("nombre_conducta", sa.Text(), nullable=False),
        sa.Column("descripcion_conducta", sa.Text(), nullable=True),
        sa.Column("codigo_conducta", sa.Text(), nullable=True),
        sa.Column("peso_conducta", sa.Numeric(5, 2), nullable=True),
        sa.Column("id_categoria_analisis_senal", sa.SmallInteger(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(
            ["id_categoria_analisis_senal"],
            ["sds.categoria_analisis_senal.id_categoria_analisis_senal"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id_conducta_vulneratorias"),
        schema="sds",
    )

    op.create_table(
        "palabra_clave",
        sa.Column("id_palabra_clave", sa.SmallInteger(), nullable=False, autoincrement=True),
        sa.Column("palabra_clave", sa.Text(), nullable=False),
        sa.Column("contexto", sa.Text(), nullable=True),
        sa.Column("id_categoria_analisis_senal", sa.SmallInteger(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(
            ["id_categoria_analisis_senal"],
            ["sds.categoria_analisis_senal.id_categoria_analisis_senal"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id_palabra_clave"),
        schema="sds",
    )

    op.create_table(
        "emoticon",
        sa.Column("id_emoticon", sa.SmallInteger(), nullable=False, autoincrement=True),
        sa.Column("codigo_emoticon", sa.Text(), nullable=False),
        sa.Column("descripcion_emoticon", sa.Text(), nullable=True),
        sa.Column("id_categoria_analisis_senal", sa.SmallInteger(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(
            ["id_categoria_analisis_senal"],
            ["sds.categoria_analisis_senal.id_categoria_analisis_senal"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id_emoticon"),
        schema="sds",
    )

    op.create_table(
        "frase_clave",
        sa.Column("id_frase_clave", sa.SmallInteger(), nullable=False, autoincrement=True),
        sa.Column("frase", sa.Text(), nullable=False),
        sa.Column("contexto", sa.Text(), nullable=True),
        sa.Column("id_categoria_analisis_senal", sa.SmallInteger(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(
            ["id_categoria_analisis_senal"],
            ["sds.categoria_analisis_senal.id_categoria_analisis_senal"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id_frase_clave"),
        schema="sds",
    )

    op.execute(
        """
        INSERT INTO sds.categoria_observacion (
            id_categoria_observacion, id_parent_categoria_observacion, codigo_categoria_observacion,
            nombre_categoria_observacion, descripcion_categoria_observacion, nivel, peso_categoria_observacion
        )
        VALUES
            (11, NULL, 'OBS_FIGURAS_PUBLICAS', 'Figuras públicas', 'Actores públicos tradicionales y políticos', 1, 75.00),
            (12, NULL, 'OBS_INFLUENCERS', 'Influencers', 'Creadores de contenidos digitales con impacto social', 1, 68.00),
            (14, NULL, 'OBS_MEDIOS_DIGITALES', 'Medios digitales', 'Medios tradicionales y digitales monitorizados', 1, 82.00),
            (31, NULL, 'OBS_ENTIDADES', 'Entidades y organizaciones', 'Organizaciones públicas y privadas relevantes al monitoreo', 1, 88.00)
        """
    )

    op.create_table(
        "figuras_publicas",
        sa.Column("id_figura_publica", sa.SmallInteger(), nullable=False),
        sa.Column("nombre_actor", sa.Text(), nullable=True),
        sa.Column("peso_actor", sa.Numeric(5, 2), nullable=True),
        sa.Column("id_categoria_observacion", sa.SmallInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id_categoria_observacion"],
            ["sds.categoria_observacion.id_categoria_observacion"],
            ondelete="NO ACTION",
            onupdate="NO ACTION",
        ),
        sa.PrimaryKeyConstraint("id_figura_publica"),
        schema="sds",
    )

    op.create_table(
        "influencers",
        sa.Column("id_influencer", sa.SmallInteger(), nullable=False),
        sa.Column("nombre_influencer", sa.Text(), nullable=True),
        sa.Column("peso_influencer", sa.Numeric(5, 2), nullable=True),
        sa.Column("id_categoria_observacion", sa.SmallInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id_categoria_observacion"],
            ["sds.categoria_observacion.id_categoria_observacion"],
            ondelete="NO ACTION",
            onupdate="NO ACTION",
        ),
        sa.PrimaryKeyConstraint("id_influencer"),
        schema="sds",
    )

    op.create_table(
        "medios_digitales",
        sa.Column("id_medio_digital", sa.SmallInteger(), nullable=False),
        sa.Column("nombre_medio_digital", sa.Text(), nullable=True),
        sa.Column("peso_medio_digital", sa.Numeric(5, 2), nullable=True),
        sa.Column("id_categoria_observacion", sa.SmallInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id_categoria_observacion"],
            ["sds.categoria_observacion.id_categoria_observacion"],
            ondelete="NO ACTION",
            onupdate="NO ACTION",
        ),
        sa.PrimaryKeyConstraint("id_medio_digital"),
        schema="sds",
    )

    op.create_table(
        "entidades",
        sa.Column("id_entidades", sa.SmallInteger(), nullable=False),
        sa.Column("nombre_entidad", sa.Text(), nullable=True),
        sa.Column("peso_entidad", sa.Numeric(5, 2), nullable=True),
        sa.Column("id_categoria_observacion", sa.SmallInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id_categoria_observacion"],
            ["sds.categoria_observacion.id_categoria_observacion"],
            ondelete="NO ACTION",
            onupdate="NO ACTION",
        ),
        sa.PrimaryKeyConstraint("id_entidades"),
        schema="sds",
    )

    op.execute(
        """
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
        """
    )

    op.execute(
        """
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
        """
    )

    op.execute(
        """
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
        """
    )

    op.execute(
        """
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
        """
    )


def downgrade():
    op.execute("DELETE FROM sds.entidades")
    op.execute("DELETE FROM sds.medios_digitales")
    op.execute("DELETE FROM sds.influencers")
    op.execute("DELETE FROM sds.figuras_publicas")
    op.drop_table("entidades", schema="sds")
    op.drop_table("medios_digitales", schema="sds")
    op.drop_table("influencers", schema="sds")
    op.drop_table("figuras_publicas", schema="sds")
    op.drop_table("frase_clave", schema="sds")
    op.drop_table("emoticon", schema="sds")
    op.drop_table("palabra_clave", schema="sds")
    op.drop_table("conducta_vulneratoria", schema="sds")
    op.drop_table("resultado_observacion_senal", schema="sds")
    op.drop_table("categoria_observacion", schema="sds")
    op.drop_column("categoria_senal", "umbral_alto", schema="sds")
    op.drop_column("categoria_senal", "umbral_bajo", schema="sds")
