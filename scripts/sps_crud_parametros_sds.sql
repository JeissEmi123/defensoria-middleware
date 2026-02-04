-- CRUD stored procedures for SDS parametros (based on docker DB schema)
BEGIN;

SET search_path TO sds;

-- ================================
-- categoria_analisis_senal
-- ================================
CREATE OR REPLACE FUNCTION sds.sp_categoria_analisis_senal_create(
    p_id_categoria_analisis_senal smallint,
    p_nombre_categoria_analisis text,
    p_descripcion_categoria_analisis text DEFAULT NULL
)
RETURNS sds.categoria_analisis_senal
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.categoria_analisis_senal;
BEGIN
    INSERT INTO sds.categoria_analisis_senal (
        id_categoria_analisis_senal,
        nombre_categoria_analisis,
        descripcion_categoria_analisis
    ) VALUES (
        p_id_categoria_analisis_senal,
        p_nombre_categoria_analisis,
        p_descripcion_categoria_analisis
    )
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_categoria_analisis_senal_update(
    p_id_categoria_analisis_senal smallint,
    p_nombre_categoria_analisis text DEFAULT NULL,
    p_descripcion_categoria_analisis text DEFAULT NULL
)
RETURNS sds.categoria_analisis_senal
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.categoria_analisis_senal;
BEGIN
    UPDATE sds.categoria_analisis_senal
    SET
        nombre_categoria_analisis = COALESCE(p_nombre_categoria_analisis, nombre_categoria_analisis),
        descripcion_categoria_analisis = COALESCE(p_descripcion_categoria_analisis, descripcion_categoria_analisis)
    WHERE id_categoria_analisis_senal = p_id_categoria_analisis_senal
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_categoria_analisis_senal_get(
    p_id_categoria_analisis_senal smallint
)
RETURNS sds.categoria_analisis_senal
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.categoria_analisis_senal;
BEGIN
    SELECT * INTO v_row
    FROM sds.categoria_analisis_senal
    WHERE id_categoria_analisis_senal = p_id_categoria_analisis_senal;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_categoria_analisis_senal_list()
RETURNS SETOF sds.categoria_analisis_senal
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM sds.categoria_analisis_senal
    ORDER BY id_categoria_analisis_senal;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_categoria_analisis_senal_delete(
    p_id_categoria_analisis_senal smallint
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted integer;
BEGIN
    DELETE FROM sds.categoria_analisis_senal
    WHERE id_categoria_analisis_senal = p_id_categoria_analisis_senal;

    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$;

-- ================================
-- conducta_vulneratoria
-- ================================
CREATE OR REPLACE FUNCTION sds.sp_conducta_vulneratoria_create(
    p_id_conducta_vulneratorias smallint,
    p_nombre_conducta text,
    p_id_categoria_analisis_senal smallint,
    p_descripcion_conducta text DEFAULT NULL,
    p_codigo_conducta text DEFAULT NULL,
    p_peso_conducta numeric DEFAULT NULL,
    p_activo boolean DEFAULT true
)
RETURNS sds.conducta_vulneratoria
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.conducta_vulneratoria;
BEGIN
    INSERT INTO sds.conducta_vulneratoria (
        id_conducta_vulneratorias,
        nombre_conducta,
        descripcion_conducta,
        codigo_conducta,
        peso_conducta,
        id_categoria_analisis_senal,
        activo
    ) VALUES (
        p_id_conducta_vulneratorias,
        p_nombre_conducta,
        p_descripcion_conducta,
        p_codigo_conducta,
        p_peso_conducta,
        p_id_categoria_analisis_senal,
        p_activo
    )
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_conducta_vulneratoria_update(
    p_id_conducta_vulneratorias smallint,
    p_nombre_conducta text DEFAULT NULL,
    p_descripcion_conducta text DEFAULT NULL,
    p_codigo_conducta text DEFAULT NULL,
    p_peso_conducta numeric DEFAULT NULL,
    p_id_categoria_analisis_senal smallint DEFAULT NULL,
    p_activo boolean DEFAULT NULL
)
RETURNS sds.conducta_vulneratoria
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.conducta_vulneratoria;
BEGIN
    UPDATE sds.conducta_vulneratoria
    SET
        nombre_conducta = COALESCE(p_nombre_conducta, nombre_conducta),
        descripcion_conducta = COALESCE(p_descripcion_conducta, descripcion_conducta),
        codigo_conducta = COALESCE(p_codigo_conducta, codigo_conducta),
        peso_conducta = COALESCE(p_peso_conducta, peso_conducta),
        id_categoria_analisis_senal = COALESCE(p_id_categoria_analisis_senal, id_categoria_analisis_senal),
        activo = COALESCE(p_activo, activo)
    WHERE id_conducta_vulneratorias = p_id_conducta_vulneratorias
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_conducta_vulneratoria_get(
    p_id_conducta_vulneratorias smallint
)
RETURNS sds.conducta_vulneratoria
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.conducta_vulneratoria;
BEGIN
    SELECT * INTO v_row
    FROM sds.conducta_vulneratoria
    WHERE id_conducta_vulneratorias = p_id_conducta_vulneratorias;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_conducta_vulneratoria_list(
    p_id_categoria_analisis_senal smallint DEFAULT NULL,
    p_activo boolean DEFAULT NULL
)
RETURNS SETOF sds.conducta_vulneratoria
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM sds.conducta_vulneratoria
    WHERE (p_id_categoria_analisis_senal IS NULL OR id_categoria_analisis_senal = p_id_categoria_analisis_senal)
      AND (p_activo IS NULL OR activo = p_activo)
    ORDER BY id_conducta_vulneratorias;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_conducta_vulneratoria_delete(
    p_id_conducta_vulneratorias smallint
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted integer;
BEGIN
    DELETE FROM sds.conducta_vulneratoria
    WHERE id_conducta_vulneratorias = p_id_conducta_vulneratorias;

    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$;

-- ================================
-- palabra_clave
-- ================================
CREATE OR REPLACE FUNCTION sds.sp_palabra_clave_create(
    p_id_palabra_clave smallint,
    p_palabra_clave text,
    p_id_categoria_analisis_senal smallint,
    p_contexto text DEFAULT NULL,
    p_activo boolean DEFAULT true
)
RETURNS sds.palabra_clave
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.palabra_clave;
BEGIN
    INSERT INTO sds.palabra_clave (
        id_palabra_clave,
        palabra_clave,
        contexto,
        id_categoria_analisis_senal,
        activo
    ) VALUES (
        p_id_palabra_clave,
        p_palabra_clave,
        p_contexto,
        p_id_categoria_analisis_senal,
        p_activo
    )
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_palabra_clave_update(
    p_id_palabra_clave smallint,
    p_palabra_clave text DEFAULT NULL,
    p_contexto text DEFAULT NULL,
    p_id_categoria_analisis_senal smallint DEFAULT NULL,
    p_activo boolean DEFAULT NULL
)
RETURNS sds.palabra_clave
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.palabra_clave;
BEGIN
    UPDATE sds.palabra_clave
    SET
        palabra_clave = COALESCE(p_palabra_clave, palabra_clave),
        contexto = COALESCE(p_contexto, contexto),
        id_categoria_analisis_senal = COALESCE(p_id_categoria_analisis_senal, id_categoria_analisis_senal),
        activo = COALESCE(p_activo, activo)
    WHERE id_palabra_clave = p_id_palabra_clave
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_palabra_clave_get(
    p_id_palabra_clave smallint
)
RETURNS sds.palabra_clave
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.palabra_clave;
BEGIN
    SELECT * INTO v_row
    FROM sds.palabra_clave
    WHERE id_palabra_clave = p_id_palabra_clave;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_palabra_clave_list(
    p_id_categoria_analisis_senal smallint DEFAULT NULL,
    p_activo boolean DEFAULT NULL
)
RETURNS SETOF sds.palabra_clave
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM sds.palabra_clave
    WHERE (p_id_categoria_analisis_senal IS NULL OR id_categoria_analisis_senal = p_id_categoria_analisis_senal)
      AND (p_activo IS NULL OR activo = p_activo)
    ORDER BY id_palabra_clave;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_palabra_clave_delete(
    p_id_palabra_clave smallint
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted integer;
BEGIN
    DELETE FROM sds.palabra_clave
    WHERE id_palabra_clave = p_id_palabra_clave;

    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$;

-- ================================
-- emoticon
-- ================================
CREATE OR REPLACE FUNCTION sds.sp_emoticon_create(
    p_id_emoticon smallint,
    p_codigo_emoticon text,
    p_id_categoria_analisis_senal smallint,
    p_descripcion_emoticon text DEFAULT NULL,
    p_activo boolean DEFAULT true
)
RETURNS sds.emoticon
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.emoticon;
BEGIN
    INSERT INTO sds.emoticon (
        id_emoticon,
        codigo_emoticon,
        descripcion_emoticon,
        id_categoria_analisis_senal,
        activo
    ) VALUES (
        p_id_emoticon,
        p_codigo_emoticon,
        p_descripcion_emoticon,
        p_id_categoria_analisis_senal,
        p_activo
    )
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_emoticon_update(
    p_id_emoticon smallint,
    p_codigo_emoticon text DEFAULT NULL,
    p_descripcion_emoticon text DEFAULT NULL,
    p_id_categoria_analisis_senal smallint DEFAULT NULL,
    p_activo boolean DEFAULT NULL
)
RETURNS sds.emoticon
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.emoticon;
BEGIN
    UPDATE sds.emoticon
    SET
        codigo_emoticon = COALESCE(p_codigo_emoticon, codigo_emoticon),
        descripcion_emoticon = COALESCE(p_descripcion_emoticon, descripcion_emoticon),
        id_categoria_analisis_senal = COALESCE(p_id_categoria_analisis_senal, id_categoria_analisis_senal),
        activo = COALESCE(p_activo, activo)
    WHERE id_emoticon = p_id_emoticon
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_emoticon_get(
    p_id_emoticon smallint
)
RETURNS sds.emoticon
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.emoticon;
BEGIN
    SELECT * INTO v_row
    FROM sds.emoticon
    WHERE id_emoticon = p_id_emoticon;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_emoticon_list(
    p_id_categoria_analisis_senal smallint DEFAULT NULL,
    p_activo boolean DEFAULT NULL
)
RETURNS SETOF sds.emoticon
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM sds.emoticon
    WHERE (p_id_categoria_analisis_senal IS NULL OR id_categoria_analisis_senal = p_id_categoria_analisis_senal)
      AND (p_activo IS NULL OR activo = p_activo)
    ORDER BY id_emoticon;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_emoticon_delete(
    p_id_emoticon smallint
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted integer;
BEGIN
    DELETE FROM sds.emoticon
    WHERE id_emoticon = p_id_emoticon;

    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$;

-- ================================
-- frase_clave
-- ================================
CREATE OR REPLACE FUNCTION sds.sp_frase_clave_create(
    p_id_frase_clave smallint,
    p_frase text,
    p_id_categoria_analisis_senal smallint,
    p_contexto text DEFAULT NULL,
    p_activo boolean DEFAULT true
)
RETURNS sds.frase_clave
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.frase_clave;
BEGIN
    INSERT INTO sds.frase_clave (
        id_frase_clave,
        frase,
        contexto,
        id_categoria_analisis_senal,
        activo
    ) VALUES (
        p_id_frase_clave,
        p_frase,
        p_contexto,
        p_id_categoria_analisis_senal,
        p_activo
    )
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_frase_clave_update(
    p_id_frase_clave smallint,
    p_frase text DEFAULT NULL,
    p_contexto text DEFAULT NULL,
    p_id_categoria_analisis_senal smallint DEFAULT NULL,
    p_activo boolean DEFAULT NULL
)
RETURNS sds.frase_clave
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.frase_clave;
BEGIN
    UPDATE sds.frase_clave
    SET
        frase = COALESCE(p_frase, frase),
        contexto = COALESCE(p_contexto, contexto),
        id_categoria_analisis_senal = COALESCE(p_id_categoria_analisis_senal, id_categoria_analisis_senal),
        activo = COALESCE(p_activo, activo)
    WHERE id_frase_clave = p_id_frase_clave
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_frase_clave_get(
    p_id_frase_clave smallint
)
RETURNS sds.frase_clave
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.frase_clave;
BEGIN
    SELECT * INTO v_row
    FROM sds.frase_clave
    WHERE id_frase_clave = p_id_frase_clave;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_frase_clave_list(
    p_id_categoria_analisis_senal smallint DEFAULT NULL,
    p_activo boolean DEFAULT NULL
)
RETURNS SETOF sds.frase_clave
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM sds.frase_clave
    WHERE (p_id_categoria_analisis_senal IS NULL OR id_categoria_analisis_senal = p_id_categoria_analisis_senal)
      AND (p_activo IS NULL OR activo = p_activo)
    ORDER BY id_frase_clave;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_frase_clave_delete(
    p_id_frase_clave smallint
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted integer;
BEGIN
    DELETE FROM sds.frase_clave
    WHERE id_frase_clave = p_id_frase_clave;

    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$;

-- ================================
-- categoria_senal
-- ================================
CREATE OR REPLACE FUNCTION sds.sp_categoria_senal_create(
    p_id_categoria_senal smallint,
    p_nombre_categoria_senal text,
    p_nivel smallint,
    p_parent_categoria_senal_id smallint DEFAULT NULL,
    p_descripcion text DEFAULT NULL,
    p_color text DEFAULT NULL,
    p_activo boolean DEFAULT true,
    p_fecha_creacion timestamptz DEFAULT NULL,
    p_fecha_actualizacion timestamptz DEFAULT NULL
)
RETURNS sds.categoria_senal
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.categoria_senal;
BEGIN
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
    ) VALUES (
        p_id_categoria_senal,
        p_parent_categoria_senal_id,
        p_nombre_categoria_senal,
        p_descripcion,
        p_color,
        p_nivel,
        p_activo,
        COALESCE(p_fecha_creacion, now()),
        COALESCE(p_fecha_actualizacion, now())
    )
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_categoria_senal_update(
    p_id_categoria_senal smallint,
    p_parent_categoria_senal_id smallint DEFAULT NULL,
    p_nombre_categoria_senal text DEFAULT NULL,
    p_descripcion text DEFAULT NULL,
    p_color text DEFAULT NULL,
    p_nivel smallint DEFAULT NULL,
    p_activo boolean DEFAULT NULL,
    p_fecha_actualizacion timestamptz DEFAULT NULL
)
RETURNS sds.categoria_senal
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.categoria_senal;
BEGIN
    UPDATE sds.categoria_senal
    SET
        parent_categoria_senal_id = COALESCE(p_parent_categoria_senal_id, parent_categoria_senal_id),
        nombre_categoria_senal = COALESCE(p_nombre_categoria_senal, nombre_categoria_senal),
        descripcion = COALESCE(p_descripcion, descripcion),
        color = COALESCE(p_color, color),
        nivel = COALESCE(p_nivel, nivel),
        activo = COALESCE(p_activo, activo),
        fecha_actualizacion = COALESCE(p_fecha_actualizacion, now())
    WHERE id_categoria_senal = p_id_categoria_senal
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_categoria_senal_get(
    p_id_categoria_senal smallint
)
RETURNS sds.categoria_senal
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.categoria_senal;
BEGIN
    SELECT * INTO v_row
    FROM sds.categoria_senal
    WHERE id_categoria_senal = p_id_categoria_senal;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_categoria_senal_list(
    p_activo boolean DEFAULT NULL
)
RETURNS SETOF sds.categoria_senal
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM sds.categoria_senal
    WHERE (p_activo IS NULL OR activo = p_activo)
    ORDER BY id_categoria_senal;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_categoria_senal_delete(
    p_id_categoria_senal smallint
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted integer;
BEGIN
    DELETE FROM sds.categoria_senal
    WHERE id_categoria_senal = p_id_categoria_senal;

    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$;

-- ================================
-- categoria_observacion
-- ================================
CREATE OR REPLACE FUNCTION sds.sp_categoria_observacion_create(
    p_id_categoria_observacion smallint,
    p_codigo_categoria_observacion text,
    p_id_parent_categoria_observacion smallint DEFAULT NULL,
    p_nombre_categoria_observacion text DEFAULT NULL,
    p_descripcion_categoria_observacion text DEFAULT NULL,
    p_nivel smallint DEFAULT NULL,
    p_peso_categoria_observacion numeric DEFAULT NULL
)
RETURNS sds.categoria_observacion
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.categoria_observacion;
BEGIN
    INSERT INTO sds.categoria_observacion (
        id_categoria_observacion,
        id_parent_categoria_observacion,
        codigo_categoria_observacion,
        nombre_categoria_observacion,
        descripcion_categoria_observacion,
        nivel,
        peso_categoria_observacion
    ) VALUES (
        p_id_categoria_observacion,
        p_id_parent_categoria_observacion,
        p_codigo_categoria_observacion,
        p_nombre_categoria_observacion,
        p_descripcion_categoria_observacion,
        p_nivel,
        p_peso_categoria_observacion
    )
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_categoria_observacion_update(
    p_id_categoria_observacion smallint,
    p_id_parent_categoria_observacion smallint DEFAULT NULL,
    p_codigo_categoria_observacion text DEFAULT NULL,
    p_nombre_categoria_observacion text DEFAULT NULL,
    p_descripcion_categoria_observacion text DEFAULT NULL,
    p_nivel smallint DEFAULT NULL,
    p_peso_categoria_observacion numeric DEFAULT NULL
)
RETURNS sds.categoria_observacion
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.categoria_observacion;
BEGIN
    UPDATE sds.categoria_observacion
    SET
        id_parent_categoria_observacion = COALESCE(p_id_parent_categoria_observacion, id_parent_categoria_observacion),
        codigo_categoria_observacion = COALESCE(p_codigo_categoria_observacion, codigo_categoria_observacion),
        nombre_categoria_observacion = COALESCE(p_nombre_categoria_observacion, nombre_categoria_observacion),
        descripcion_categoria_observacion = COALESCE(p_descripcion_categoria_observacion, descripcion_categoria_observacion),
        nivel = COALESCE(p_nivel, nivel),
        peso_categoria_observacion = COALESCE(p_peso_categoria_observacion, peso_categoria_observacion)
    WHERE id_categoria_observacion = p_id_categoria_observacion
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_categoria_observacion_get(
    p_id_categoria_observacion smallint
)
RETURNS sds.categoria_observacion
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.categoria_observacion;
BEGIN
    SELECT * INTO v_row
    FROM sds.categoria_observacion
    WHERE id_categoria_observacion = p_id_categoria_observacion;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_categoria_observacion_list()
RETURNS SETOF sds.categoria_observacion
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM sds.categoria_observacion
    ORDER BY id_categoria_observacion;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_categoria_observacion_delete(
    p_id_categoria_observacion smallint
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted integer;
BEGIN
    DELETE FROM sds.categoria_observacion
    WHERE id_categoria_observacion = p_id_categoria_observacion;

    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$;

-- ================================
-- figuras_publicas
-- ================================
CREATE OR REPLACE FUNCTION sds.sp_figuras_publicas_create(
    p_id_figura_publica smallint,
    p_nombre_actor text DEFAULT NULL,
    p_peso_actor numeric DEFAULT NULL,
    p_id_categoria_observacion smallint DEFAULT NULL
)
RETURNS sds.figuras_publicas
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.figuras_publicas;
BEGIN
    INSERT INTO sds.figuras_publicas (
        id_figura_publica,
        nombre_actor,
        peso_actor,
        id_categoria_observacion
    ) VALUES (
        p_id_figura_publica,
        p_nombre_actor,
        p_peso_actor,
        p_id_categoria_observacion
    )
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_figuras_publicas_update(
    p_id_figura_publica smallint,
    p_nombre_actor text DEFAULT NULL,
    p_peso_actor numeric DEFAULT NULL,
    p_id_categoria_observacion smallint DEFAULT NULL
)
RETURNS sds.figuras_publicas
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.figuras_publicas;
BEGIN
    UPDATE sds.figuras_publicas
    SET
        nombre_actor = COALESCE(p_nombre_actor, nombre_actor),
        peso_actor = COALESCE(p_peso_actor, peso_actor),
        id_categoria_observacion = COALESCE(p_id_categoria_observacion, id_categoria_observacion)
    WHERE id_figura_publica = p_id_figura_publica
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_figuras_publicas_get(
    p_id_figura_publica smallint
)
RETURNS sds.figuras_publicas
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.figuras_publicas;
BEGIN
    SELECT * INTO v_row
    FROM sds.figuras_publicas
    WHERE id_figura_publica = p_id_figura_publica;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_figuras_publicas_list(
    p_id_categoria_observacion smallint DEFAULT NULL
)
RETURNS SETOF sds.figuras_publicas
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM sds.figuras_publicas
    WHERE (p_id_categoria_observacion IS NULL OR id_categoria_observacion = p_id_categoria_observacion)
    ORDER BY id_figura_publica;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_figuras_publicas_delete(
    p_id_figura_publica smallint
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted integer;
BEGIN
    DELETE FROM sds.figuras_publicas
    WHERE id_figura_publica = p_id_figura_publica;

    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$;

-- ================================
-- influencers
-- ================================
CREATE OR REPLACE FUNCTION sds.sp_influencers_create(
    p_id_influencer smallint,
    p_nombre_influencer text DEFAULT NULL,
    p_peso_influencer numeric DEFAULT NULL,
    p_id_categoria_observacion smallint DEFAULT NULL
)
RETURNS sds.influencers
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.influencers;
BEGIN
    INSERT INTO sds.influencers (
        id_influencer,
        nombre_influencer,
        peso_influencer,
        id_categoria_observacion
    ) VALUES (
        p_id_influencer,
        p_nombre_influencer,
        p_peso_influencer,
        p_id_categoria_observacion
    )
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_influencers_update(
    p_id_influencer smallint,
    p_nombre_influencer text DEFAULT NULL,
    p_peso_influencer numeric DEFAULT NULL,
    p_id_categoria_observacion smallint DEFAULT NULL
)
RETURNS sds.influencers
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.influencers;
BEGIN
    UPDATE sds.influencers
    SET
        nombre_influencer = COALESCE(p_nombre_influencer, nombre_influencer),
        peso_influencer = COALESCE(p_peso_influencer, peso_influencer),
        id_categoria_observacion = COALESCE(p_id_categoria_observacion, id_categoria_observacion)
    WHERE id_influencer = p_id_influencer
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_influencers_get(
    p_id_influencer smallint
)
RETURNS sds.influencers
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.influencers;
BEGIN
    SELECT * INTO v_row
    FROM sds.influencers
    WHERE id_influencer = p_id_influencer;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_influencers_list(
    p_id_categoria_observacion smallint DEFAULT NULL
)
RETURNS SETOF sds.influencers
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM sds.influencers
    WHERE (p_id_categoria_observacion IS NULL OR id_categoria_observacion = p_id_categoria_observacion)
    ORDER BY id_influencer;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_influencers_delete(
    p_id_influencer smallint
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted integer;
BEGIN
    DELETE FROM sds.influencers
    WHERE id_influencer = p_id_influencer;

    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$;

-- ================================
-- medios_digitales
-- ================================
CREATE OR REPLACE FUNCTION sds.sp_medios_digitales_create(
    p_id_medio_digital smallint,
    p_nombre_medio_digital text DEFAULT NULL,
    p_peso_medio_digital numeric DEFAULT NULL,
    p_id_categoria_observacion smallint DEFAULT NULL
)
RETURNS sds.medios_digitales
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.medios_digitales;
BEGIN
    INSERT INTO sds.medios_digitales (
        id_medio_digital,
        nombre_medio_digital,
        peso_medio_digital,
        id_categoria_observacion
    ) VALUES (
        p_id_medio_digital,
        p_nombre_medio_digital,
        p_peso_medio_digital,
        p_id_categoria_observacion
    )
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_medios_digitales_update(
    p_id_medio_digital smallint,
    p_nombre_medio_digital text DEFAULT NULL,
    p_peso_medio_digital numeric DEFAULT NULL,
    p_id_categoria_observacion smallint DEFAULT NULL
)
RETURNS sds.medios_digitales
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.medios_digitales;
BEGIN
    UPDATE sds.medios_digitales
    SET
        nombre_medio_digital = COALESCE(p_nombre_medio_digital, nombre_medio_digital),
        peso_medio_digital = COALESCE(p_peso_medio_digital, peso_medio_digital),
        id_categoria_observacion = COALESCE(p_id_categoria_observacion, id_categoria_observacion)
    WHERE id_medio_digital = p_id_medio_digital
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_medios_digitales_get(
    p_id_medio_digital smallint
)
RETURNS sds.medios_digitales
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.medios_digitales;
BEGIN
    SELECT * INTO v_row
    FROM sds.medios_digitales
    WHERE id_medio_digital = p_id_medio_digital;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_medios_digitales_list(
    p_id_categoria_observacion smallint DEFAULT NULL
)
RETURNS SETOF sds.medios_digitales
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM sds.medios_digitales
    WHERE (p_id_categoria_observacion IS NULL OR id_categoria_observacion = p_id_categoria_observacion)
    ORDER BY id_medio_digital;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_medios_digitales_delete(
    p_id_medio_digital smallint
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted integer;
BEGIN
    DELETE FROM sds.medios_digitales
    WHERE id_medio_digital = p_id_medio_digital;

    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$;

-- ================================
-- entidades
-- ================================
CREATE OR REPLACE FUNCTION sds.sp_entidades_create(
    p_id_entidades smallint,
    p_nombre_entidad text DEFAULT NULL,
    p_peso_entidad numeric DEFAULT NULL,
    p_id_categoria_observacion smallint DEFAULT NULL
)
RETURNS sds.entidades
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.entidades;
BEGIN
    INSERT INTO sds.entidades (
        id_entidades,
        nombre_entidad,
        peso_entidad,
        id_categoria_observacion
    ) VALUES (
        p_id_entidades,
        p_nombre_entidad,
        p_peso_entidad,
        p_id_categoria_observacion
    )
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_entidades_update(
    p_id_entidades smallint,
    p_nombre_entidad text DEFAULT NULL,
    p_peso_entidad numeric DEFAULT NULL,
    p_id_categoria_observacion smallint DEFAULT NULL
)
RETURNS sds.entidades
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.entidades;
BEGIN
    UPDATE sds.entidades
    SET
        nombre_entidad = COALESCE(p_nombre_entidad, nombre_entidad),
        peso_entidad = COALESCE(p_peso_entidad, peso_entidad),
        id_categoria_observacion = COALESCE(p_id_categoria_observacion, id_categoria_observacion)
    WHERE id_entidades = p_id_entidades
    RETURNING * INTO v_row;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_entidades_get(
    p_id_entidades smallint
)
RETURNS sds.entidades
LANGUAGE plpgsql
AS $$
DECLARE
    v_row sds.entidades;
BEGIN
    SELECT * INTO v_row
    FROM sds.entidades
    WHERE id_entidades = p_id_entidades;

    RETURN v_row;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_entidades_list(
    p_id_categoria_observacion smallint DEFAULT NULL
)
RETURNS SETOF sds.entidades
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM sds.entidades
    WHERE (p_id_categoria_observacion IS NULL OR id_categoria_observacion = p_id_categoria_observacion)
    ORDER BY id_entidades;
END;
$$;

CREATE OR REPLACE FUNCTION sds.sp_entidades_delete(
    p_id_entidades smallint
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted integer;
BEGIN
    DELETE FROM sds.entidades
    WHERE id_entidades = p_id_entidades;

    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$;

COMMIT;
