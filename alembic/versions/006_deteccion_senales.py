"""
Revision ID: 006_deteccion_senales
Revises: 005_add_password_history
Create Date: 2025-12-10

Sistema de Detección de Señales - Derechos Digitales
Tablas: categoria_analisis_senal, categoria_senal, senal_detectada, historial_senal
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '006_deteccion_senales'
down_revision = '005_add_password_history'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Tabla: categoria_analisis_senal
    op.create_table(
        'categoria_analisis_senal',
        sa.Column('id', sa.SmallInteger(), nullable=False, autoincrement=True),
        sa.Column('nombre_categoria_analisis', sa.String(150), nullable=False),
        sa.Column('propiedades_conductas_vulneratorias', JSONB, nullable=True),
        sa.Column('palabras_clave_categoria', JSONB, nullable=True),
        sa.Column('hashtags_categoria', JSONB, nullable=True),
        sa.Column('emoticones_categoria', JSONB, nullable=True),
        sa.Column('frases_categoria', JSONB, nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    
    # Índices para categoria_analisis_senal
    op.create_index('ix_categoria_analisis_senal_id', 'categoria_analisis_senal', ['id'])
    op.create_index('ix_categoria_analisis_senal_nombre', 'categoria_analisis_senal', ['nombre_categoria_analisis'])
    op.create_index('ix_categoria_analisis_senal_activo', 'categoria_analisis_senal', ['activo'])

    # 2. Tabla: categoria_senal (jerárquica)
    op.create_table(
        'categoria_senal',
        sa.Column('id_categoria_senal', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('nombre_categoria_senal', sa.String(100), nullable=False),
        sa.Column('parent_categoria_senal_id', sa.SmallInteger(), nullable=True),
        sa.Column('nivel', sa.SmallInteger(), nullable=False),
        sa.Column('color', sa.String(50), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id_categoria_senal'),
        sa.ForeignKeyConstraint(['parent_categoria_senal_id'], ['categoria_senal.id_categoria_senal'], ondelete='SET NULL'),
        sa.UniqueConstraint('id_categoria_senal')
    )
    
    # Índices para categoria_senal
    op.create_index('ix_categoria_senal_id', 'categoria_senal', ['id_categoria_senal'])
    op.create_index('ix_categoria_senal_nombre', 'categoria_senal', ['nombre_categoria_senal'])
    op.create_index('ix_categoria_senal_parent', 'categoria_senal', ['parent_categoria_senal_id'])
    op.create_index('ix_categoria_senal_nivel', 'categoria_senal', ['nivel'])
    op.create_index('ix_categoria_senal_activo', 'categoria_senal', ['activo'])

    # 3. Tabla: senal_detectada (principal)
    op.create_table(
        'senal_detectada',
        sa.Column('id_senal_detectada', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('fecha_deteccion', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('id_categoria_senal', sa.SmallInteger(), nullable=True),
        sa.Column('id_categoria_analisis', sa.SmallInteger(), nullable=True),
        sa.Column('score_riesgo', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('categorias_observacion', JSONB, nullable=True),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('plataformas_digitales', JSONB, nullable=True),
        sa.Column('contenido_detectado', sa.Text(), nullable=True),
        sa.Column('metadatos', JSONB, nullable=True),
        sa.Column('estado', sa.String(50), nullable=False, server_default='DETECTADA'),
        sa.Column('url_origen', sa.String(500), nullable=True),
        sa.Column('usuario_asignado_id', sa.Integer(), nullable=True),
        sa.Column('fecha_resolucion', sa.DateTime(), nullable=True),
        sa.Column('notas_resolucion', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id_senal_detectada'),
        sa.ForeignKeyConstraint(['id_categoria_senal'], ['categoria_senal.id_categoria_senal'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['id_categoria_analisis'], ['categoria_analisis_senal.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['usuario_asignado_id'], ['usuarios.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('id_senal_detectada')
    )
    
    # Índices para senal_detectada
    op.create_index('ix_senal_detectada_id', 'senal_detectada', ['id_senal_detectada'])
    op.create_index('ix_senal_detectada_fecha_deteccion', 'senal_detectada', ['fecha_deteccion'])
    op.create_index('ix_senal_detectada_categoria_senal', 'senal_detectada', ['id_categoria_senal'])
    op.create_index('ix_senal_detectada_categoria_analisis', 'senal_detectada', ['id_categoria_analisis'])
    op.create_index('ix_senal_detectada_score_riesgo', 'senal_detectada', ['score_riesgo'])
    op.create_index('ix_senal_detectada_estado', 'senal_detectada', ['estado'])
    op.create_index('ix_senal_detectada_usuario_asignado', 'senal_detectada', ['usuario_asignado_id'])

    # 4. Tabla: historial_senal (trazabilidad)
    op.create_table(
        'historial_senal',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('id_senal_detectada', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('accion', sa.String(100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('estado_anterior', sa.String(50), nullable=True),
        sa.Column('estado_nuevo', sa.String(50), nullable=True),
        sa.Column('datos_adicionales', JSONB, nullable=True),
        sa.Column('fecha_registro', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['id_senal_detectada'], ['senal_detectada.id_senal_detectada'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='SET NULL')
    )
    
    # Índices para historial_senal
    op.create_index('ix_historial_senal_id', 'historial_senal', ['id'])
    op.create_index('ix_historial_senal_senal_id', 'historial_senal', ['id_senal_detectada'])
    op.create_index('ix_historial_senal_usuario_id', 'historial_senal', ['usuario_id'])
    op.create_index('ix_historial_senal_fecha_registro', 'historial_senal', ['fecha_registro'])
    op.create_index('ix_historial_senal_accion', 'historial_senal', ['accion'])

    # 5. Insertar datos iniciales - Categorías de Análisis de Señales
    op.execute("""
        INSERT INTO categoria_analisis_senal 
            (nombre_categoria_analisis, propiedades_conductas_vulneratorias, palabras_clave_categoria, 
             hashtags_categoria, emoticones_categoria, frases_categoria)
        VALUES
            (
                'Reclutamiento, uso y utilización de niñas, niños y adolescentes',
                '{ "Uso": "Comprende todas aquellas prácticas o comportamientos de quienes promuevan, induzcan, faciliten, financien o colaboren para que los niños, niñas y adolescentes participen en cualquier actividad ilegal de los grupos armados organizados o grupos delictivos organizados; recurriendo a cualquier forma de violencia, amenaza, coerción o engaño que conlleve a la vulneración o falta de garantía de sus derechos, con el propósito de obtener provecho económico o cualquier otro beneficio. El Código Penal en su artículo 188 D tipifica esta conducta como uso de menores [de edad] para la comisión de delitos. (CPDHAI, 2019)", "Utilización": "Participación indirecta de niños, niñas y adolescentes en toda forma de vinculación, permanente u ocasional, con grupos armados organizados o grupos delincuenciales sin necesariamente ser separados de su entorno familiar y comunitario. Todas ellas, actividades con fines diferentes de carácter ilegal o informal. De otra parte, la utilización no se encuentra tipificada como un delito del Código Penal. (CPDHAI, 2019)", "Vinculación": "Cualquier forma de relacionamiento, acercamiento, aproximación a los niños, niñas y adolescentes para cumplir cualquier tipo de rol dentro o a favor de un GAO, GDO o GAOR. (CPDHAI, 2019)", "Reclutamiento": "Separación física de los niños, niñas y adolescentes de su entorno familiar y comunitario para que participen de manera directa en actividades bélicas, militares, tácticas, de sustento o para que desempeñen cualquier tipo de rol dentro de los grupos armados organizados o grupos delictivos organizados. En el Auto 251 de 2008 la Corte Constitucional señaló que todo reclutamiento es un acto de carácter coercitivo, del cual, son víctimas los niños, niñas y adolescentes. El Código Penal en su artículo 162 tipifica esta conducta como el delito de reclutamiento ilícito. (CPDHAI, 2019)"}',
                '["grupos armados organizados (GAO)", "grupos delictivos organizados (GDO)", "reclutamiento", "uso", "utilización", "niñas", "niños", "adolescentes", "niñez",  "menores", "jóvenes", "juventud", "conflicto", "conflicto armado", "guerra", "disidencias", "Estado Mayor Central", "ELN", "Segunda Marquetalia", "crimen organizado", "guerrilla", "guerrillas", "cultivos ilícitos", "porte de armas", "enfrentamientos", "redes sociales"]',
                '["#Reclutamiento", "#Guerrilla", "#Milicias", "#PrivacidadDigital"]',
                '["🔓", "📢", "🆘", "🚫"]',
                '["aquí está su dirección", "publico sus datos", "esto es lo que hace"]'
            ),
            (
                'Violencia política',
                '{ "Violencia Política": "Aquella ejercida como medio de lucha políticosocial, ya sea con el fin de mantener, modificar, substituir o destruir un modelo de Estado o de sociedad, o también para destruir o reprimir a un grupo humano con identidad dentro de la sociedad por su afinidad social, política, gremial, étnica, racial, religiosa, cultural o ideológica, esté o no organizado. Puede ser perpetrada por (1) agentes estatales o por particulares que actúan con el apoyo, tolerancia o aquiescencia de las autoridades del Estado y en este caso se tipifica como Violación de Derechos Humanos; (2) actores insurgentes y en este caso esa violencia se ajusta a las leyes o costumbres de la guerra y entonces se tipifica como acciones bélicas, o se aparta de las normas que regulan los conflictos armados y entonces se tipifica como Infracción al Derecho Internacional Humanitario;(3) grupos o individuos no vinculados al Estado ni a la insurgencia que actúan por motivaciones político-ideológicas contra personas u organizaciones con identidades o posiciones distintas. Estas acciones, identificadas principalmente por su móvil, se consideran Violencia Político-Social, e incluyen prácticas como secuestros o limpieza social con finalidad política.", "Violencia político-social": "Aquella ejercida por terceros motivados por fines político-ideológicospersonas, organizaciones o grupos particulares o no determinados, motivados por la lucha en torno al poder político o por la intolerancia frente a otras ideologías, razas, etnias, religiones, culturas o sectores sociales, estén o no organizados."}',
                '["líder social", "líderes sociales", "líderes indígenas", "defensor de derechos humanos", "defensora de derechos humanos", "asesinato", "asesinatos", "desaparición", "atentado", "atentados", "candidato", "candidatos", "candidata", "candidatas", "precandidato", "precandidatos", "precandidata", "precandidatas", "líderes políticos", "partidos políticos", "movimientos políticos"]',
                '["#Presidente", "#Congreso", "#Petro", "#Corrupción"]',
                '["🤬", "👹", "💩", "🚩"]',
                '["fuera corrupto", "político mediocre", "ladrón de corbata"]'
            ),
            (
                'Violencia digital basada en género',
                '{ "Violencia digital contra las mujeres (VDCM)": "La violencia digital contra las mujeres constituye una violación de los derechos humanos y un acto de discriminación de carácter estructural. Se inscribe en un continuum de violencia que abarca tanto los espacios en línea, como fuera de ella, donde las agresiones digitales pueden manifestarse como una extensión o un precedente de la violencia física, sexual, el acoso o el acecho.", "Violencia basada en género": "Acción causada por un ejercicio del poder que se fundamenta en estereotipos sobre lo femenino y lo masculino y en las relaciones desiguales entre hombres y mujeres en la sociedad. Así mismo, se sustenta en las construcciones realizadas de forma social y favorece a los grupos que han ejercido el poder a través del miedo y la violencia. Esto afecta no solo a mujeres, sino también a segmentos de la población que no encajan en los parámetros de género y sexualidad dominantes como lo son hombres gay, personas transgénero y lesbianas.", "Violencia sociopolítica de género": "Es aquella violencia ejercida como medio de lucha político– social, con el fin destruir o reprimir a un grupo humano con identidad dentro de la sociedad. En el caso de las lideresas y defensoras, su labor las hace susceptibles de sufrir persecuciones y ataques múltiples, reiterados y escalonados en razón de su labor", "Violencia facilitada por tecnologías específicas y dispositivos (Categoría VDCM)": "Formas de acoso, violencia o abuso que se producen mediante herramientas tecnológicas específicas. Incluye el acecho con programas espía, control remoto de dispositivos, geolocalización sin consentimiento", "Abuso amplificado en línea (Categoría VDCM)": "Abusos que ocurren en internet y se intensifican por la naturaleza viral y masiva del entorno digital. Incluye la difusión no consentida de imágenes íntimas, campañas de desprestigio, ciberacoso.", "Nuevas formas de abuso generadas por la tecnología (Categoría VDCM)": "Formas de violencia que surgen a partir de innovaciones tecnológicas que permiten nuevas modalidades de daño. Incluye material sexualmente explícito falso (deepfakes), suplantación de identidad en el metaverso, manipulación de avatares.", "Uso del entorno en línea para facilitar violencia y abuso (Categoría VDCM)": "Cuando el espacio digital se convierte. en medio para facilitar o posibilitar otros tipos de violencia. Incluye la captación de víctimas por redes de trata en redes sociales, grooming, reclutamiento para explotación." }',
                '["acoso", "acecho", "abuso", "candidatas", "lideresas", "defensoras", "ciberacoso", "desprestigio", "video íntimo", "deepfakes", "pornografía", "grooming", "trata", "explotación sexual", "prostitución"]',
                '["#Explotacion", "#Acoso", "#ViolenciaSexual", "#Gay", "#Homosexual"]',
                '["🔓", "📢", "🆘", "🚫", "👁️", "📍", "🕵️", "📡"]',
                '["tenías que ser gay", "publico sus datos", "por ser lesbiana"]'
            )
    """)

    # 6. Insertar datos iniciales - Categorías de Señales (jerárquicas)
    op.execute("""
        INSERT INTO categoria_senal (nombre_categoria_senal, parent_categoria_senal_id, nivel, color, descripcion) 
        VALUES
            -- Nivel 1: Categorías principales
            ('RUIDO', NULL, 1, '#808080', 'Señales sin relevancia inmediata'),
            ('PARACRISIS', NULL, 1, '#FFA500', 'Señales que requieren monitoreo'),
            ('CRISIS', NULL, 1, '#FF0000', 'Señales críticas que requieren acción inmediata'),
            
            -- Nivel 2: Subcategorías de señales
            ('ROJO', 1, 2, '#FF0000', 'Nivel de riesgo alto'),
            ('AMARILLO', 2, 2, '#FFFF00', 'Nivel de riesgo medio'),
            ('VERDE', 1, 2, '#00FF00', 'Nivel de riesgo bajo')
    """)


def downgrade():
    # Eliminar tablas en orden inverso
    op.drop_index('ix_historial_senal_accion', 'historial_senal')
    op.drop_index('ix_historial_senal_fecha_registro', 'historial_senal')
    op.drop_index('ix_historial_senal_usuario_id', 'historial_senal')
    op.drop_index('ix_historial_senal_senal_id', 'historial_senal')
    op.drop_index('ix_historial_senal_id', 'historial_senal')
    op.drop_table('historial_senal')

    op.drop_index('ix_senal_detectada_usuario_asignado', 'senal_detectada')
    op.drop_index('ix_senal_detectada_estado', 'senal_detectada')
    op.drop_index('ix_senal_detectada_score_riesgo', 'senal_detectada')
    op.drop_index('ix_senal_detectada_categoria_analisis', 'senal_detectada')
    op.drop_index('ix_senal_detectada_categoria_senal', 'senal_detectada')
    op.drop_index('ix_senal_detectada_fecha_deteccion', 'senal_detectada')
    op.drop_index('ix_senal_detectada_id', 'senal_detectada')
    op.drop_table('senal_detectada')

    op.drop_index('ix_categoria_senal_activo', 'categoria_senal')
    op.drop_index('ix_categoria_senal_nivel', 'categoria_senal')
    op.drop_index('ix_categoria_senal_parent', 'categoria_senal')
    op.drop_index('ix_categoria_senal_nombre', 'categoria_senal')
    op.drop_index('ix_categoria_senal_id', 'categoria_senal')
    op.drop_table('categoria_senal')

    op.drop_index('ix_categoria_analisis_senal_activo', 'categoria_analisis_senal')
    op.drop_index('ix_categoria_analisis_senal_nombre', 'categoria_analisis_senal')
    op.drop_index('ix_categoria_analisis_senal_id', 'categoria_analisis_senal')
    op.drop_table('categoria_analisis_senal')
