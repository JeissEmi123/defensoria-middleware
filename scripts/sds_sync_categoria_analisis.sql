CREATE OR REPLACE FUNCTION sds.sync_categoria_analisis(
    p_id_categoria smallint,
    p_payload jsonb
) RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
    v_categoria jsonb;
    v_conductas jsonb;
    v_palabras jsonb;
    v_emoticones jsonb;
    v_frases jsonb;
    v_upsert_conductas integer := 0;
    v_upsert_palabras integer := 0;
    v_upsert_emoticones integer := 0;
    v_upsert_frases integer := 0;
    v_deleted_conductas integer := 0;
    v_deleted_palabras integer := 0;
    v_deleted_emoticones integer := 0;
    v_deleted_frases integer := 0;
    v_updated_categoria boolean := false;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM sds.categoria_analisis_senal
        WHERE id_categoria_analisis_senal = p_id_categoria
    ) THEN
        RAISE EXCEPTION 'Categoria de analisis no existe'
            USING ERRCODE = 'P0002';
    END IF;

    v_categoria := p_payload->'categoria';
    IF v_categoria IS NULL THEN
        RAISE EXCEPTION 'categoria requerida'
            USING ERRCODE = '22023';
    END IF;

    UPDATE sds.categoria_analisis_senal
    SET nombre_categoria_analisis = v_categoria->>'nombre_categoria_analisis',
        descripcion_categoria_analisis = v_categoria->>'descripcion_categoria_analisis'
    WHERE id_categoria_analisis_senal = p_id_categoria;
    v_updated_categoria := true;

    v_conductas := COALESCE(p_payload->'conductas', '[]'::jsonb);
    v_palabras := COALESCE(p_payload->'palabras_clave', '[]'::jsonb);
    v_emoticones := COALESCE(p_payload->'emoticones', '[]'::jsonb);
    v_frases := COALESCE(p_payload->'frases_clave', '[]'::jsonb);

    IF EXISTS (
        SELECT 1
        FROM sds.conducta_vulneratoria cv
        JOIN jsonb_to_recordset(v_conductas) AS x(id_conducta_vulneratorias smallint)
            ON cv.id_conducta_vulneratorias = x.id_conducta_vulneratorias
        WHERE cv.id_categoria_analisis_senal <> p_id_categoria
    ) THEN
        RAISE EXCEPTION 'Conflicto de categoria para conductas'
            USING ERRCODE = '23505';
    END IF;

    WITH payload AS (
        SELECT * FROM jsonb_to_recordset(v_conductas) AS x(
            id_conducta_vulneratorias smallint,
            nombre_conducta_vulneratoria text,
            definicion_conducta_vulneratoria text,
            peso_conducta_vulneratoria numeric(5, 2)
        )
    ),
    upserted AS (
        INSERT INTO sds.conducta_vulneratoria (
            id_conducta_vulneratorias,
            id_categoria_analisis_senal,
            nombre_conducta_vulneratoria,
            definicion_conducta_vulneratoria,
            peso_conducta_vulneratoria
        )
        SELECT
            x.id_conducta_vulneratorias,
            p_id_categoria,
            x.nombre_conducta_vulneratoria,
            x.definicion_conducta_vulneratoria,
            x.peso_conducta_vulneratoria
        FROM payload x
        ON CONFLICT (id_conducta_vulneratorias) DO UPDATE
        SET nombre_conducta_vulneratoria = EXCLUDED.nombre_conducta_vulneratoria,
            definicion_conducta_vulneratoria = EXCLUDED.definicion_conducta_vulneratoria,
            peso_conducta_vulneratoria = EXCLUDED.peso_conducta_vulneratoria
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_upsert_conductas FROM upserted;

    WITH deleted AS (
        DELETE FROM sds.conducta_vulneratoria
        WHERE id_categoria_analisis_senal = p_id_categoria
          AND (
            jsonb_array_length(v_conductas) = 0
            OR id_conducta_vulneratorias NOT IN (
                SELECT (elem->>'id_conducta_vulneratorias')::smallint
                FROM jsonb_array_elements(v_conductas) AS elem
            )
          )
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_deleted_conductas FROM deleted;

    IF EXISTS (
        SELECT 1
        FROM sds.palabra_clave pk
        JOIN jsonb_to_recordset(v_palabras) AS x(id_palabra_clave smallint)
            ON pk.id_palabra_clave = x.id_palabra_clave
        WHERE pk.id_categoria_analisis_senal <> p_id_categoria
    ) THEN
        RAISE EXCEPTION 'Conflicto de categoria para palabras clave'
            USING ERRCODE = '23505';
    END IF;

    WITH payload AS (
        SELECT * FROM jsonb_to_recordset(v_palabras) AS x(
            id_palabra_clave smallint,
            nombre_palabra_clave text,
            peso_palabra_clave numeric(5, 2)
        )
    ),
    upserted AS (
        INSERT INTO sds.palabra_clave (
            id_palabra_clave,
            id_categoria_analisis_senal,
            nombre_palabra_clave,
            peso_palabra_clave
        )
        SELECT
            x.id_palabra_clave,
            p_id_categoria,
            x.nombre_palabra_clave,
            x.peso_palabra_clave
        FROM payload x
        ON CONFLICT (id_palabra_clave) DO UPDATE
        SET nombre_palabra_clave = EXCLUDED.nombre_palabra_clave,
            peso_palabra_clave = EXCLUDED.peso_palabra_clave
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_upsert_palabras FROM upserted;

    WITH deleted AS (
        DELETE FROM sds.palabra_clave
        WHERE id_categoria_analisis_senal = p_id_categoria
          AND (
            jsonb_array_length(v_palabras) = 0
            OR id_palabra_clave NOT IN (
                SELECT (elem->>'id_palabra_clave')::smallint
                FROM jsonb_array_elements(v_palabras) AS elem
            )
          )
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_deleted_palabras FROM deleted;

    IF EXISTS (
        SELECT 1
        FROM sds.emoticon em
        JOIN jsonb_to_recordset(v_emoticones) AS x(id_emoticon smallint)
            ON em.id_emoticon = x.id_emoticon
        WHERE em.id_categoria_analisis_senal <> p_id_categoria
    ) THEN
        RAISE EXCEPTION 'Conflicto de categoria para emoticones'
            USING ERRCODE = '23505';
    END IF;

    WITH payload AS (
        SELECT * FROM jsonb_to_recordset(v_emoticones) AS x(
            id_emoticon smallint,
            tipo_emoticon text,
            peso_emoticon numeric(5, 2)
        )
    ),
    upserted AS (
        INSERT INTO sds.emoticon (
            id_emoticon,
            id_categoria_analisis_senal,
            tipo_emoticon,
            peso_emoticon
        )
        SELECT
            x.id_emoticon,
            p_id_categoria,
            x.tipo_emoticon,
            x.peso_emoticon
        FROM payload x
        ON CONFLICT (id_emoticon) DO UPDATE
        SET tipo_emoticon = EXCLUDED.tipo_emoticon,
            peso_emoticon = EXCLUDED.peso_emoticon
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_upsert_emoticones FROM upserted;

    WITH deleted AS (
        DELETE FROM sds.emoticon
        WHERE id_categoria_analisis_senal = p_id_categoria
          AND (
            jsonb_array_length(v_emoticones) = 0
            OR id_emoticon NOT IN (
                SELECT (elem->>'id_emoticon')::smallint
                FROM jsonb_array_elements(v_emoticones) AS elem
            )
          )
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_deleted_emoticones FROM deleted;

    IF EXISTS (
        SELECT 1
        FROM sds.frase_clave fc
        JOIN jsonb_to_recordset(v_frases) AS x(id_frase_clave smallint)
            ON fc.id_frase_clave = x.id_frase_clave
        WHERE fc.id_categoria_analisis_senal <> p_id_categoria
    ) THEN
        RAISE EXCEPTION 'Conflicto de categoria para frases clave'
            USING ERRCODE = '23505';
    END IF;

    WITH payload AS (
        SELECT * FROM jsonb_to_recordset(v_frases) AS x(
            id_frase_clave smallint,
            nombre_frase_clave text,
            peso_frase_clave numeric(5, 2)
        )
    ),
    upserted AS (
        INSERT INTO sds.frase_clave (
            id_frase_clave,
            id_categoria_analisis_senal,
            nombre_frase_clave,
            peso_frase_clave
        )
        SELECT
            x.id_frase_clave,
            p_id_categoria,
            x.nombre_frase_clave,
            x.peso_frase_clave
        FROM payload x
        ON CONFLICT (id_frase_clave) DO UPDATE
        SET nombre_frase_clave = EXCLUDED.nombre_frase_clave,
            peso_frase_clave = EXCLUDED.peso_frase_clave
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_upsert_frases FROM upserted;

    WITH deleted AS (
        DELETE FROM sds.frase_clave
        WHERE id_categoria_analisis_senal = p_id_categoria
          AND (
            jsonb_array_length(v_frases) = 0
            OR id_frase_clave NOT IN (
                SELECT (elem->>'id_frase_clave')::smallint
                FROM jsonb_array_elements(v_frases) AS elem
            )
          )
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_deleted_frases FROM deleted;

    RETURN jsonb_build_object(
        'idCategoria', p_id_categoria,
        'updatedCategoria', v_updated_categoria,
        'upserted', jsonb_build_object(
            'conductas', v_upsert_conductas,
            'palabras_clave', v_upsert_palabras,
            'emoticones', v_upsert_emoticones,
            'frases_clave', v_upsert_frases
        ),
        'deleted', jsonb_build_object(
            'conductas', v_deleted_conductas,
            'palabras_clave', v_deleted_palabras,
            'emoticones', v_deleted_emoticones,
            'frases_clave', v_deleted_frases
        )
    );
END;
$$;
