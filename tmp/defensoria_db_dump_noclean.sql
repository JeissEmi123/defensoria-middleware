--
-- PostgreSQL database dump
--

\restrict HSbW9pmMczipLmXjanGd2FAG0xd0tXHRfzFNzdxyxNmoE6xdS7kaj3YDH1Jhv7n

-- Dumped from database version 15.15
-- Dumped by pg_dump version 15.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: sds; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA sds;


--
-- Name: tipo_autenticacion; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.tipo_autenticacion AS ENUM (
    'local',
    'ldap',
    'azure_ad'
);


--
-- Name: create_categoria_analisis_full(smallint, jsonb); Type: FUNCTION; Schema: sds; Owner: -
--

CREATE FUNCTION sds.create_categoria_analisis_full(p_id_categoria smallint, p_payload jsonb) RETURNS jsonb
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_categoria jsonb;
    v_conductas jsonb;
    v_palabras jsonb;
    v_emoticones jsonb;
    v_frases jsonb;
    v_id_categoria smallint;
    v_base_conductas integer := 0;
    v_base_palabras integer := 0;
    v_base_emoticones integer := 0;
    v_base_frases integer := 0;
    v_ins_conductas integer := 0;
    v_ins_palabras integer := 0;
    v_ins_emoticones integer := 0;
    v_ins_frases integer := 0;
BEGIN
    v_categoria := p_payload->'categoria';
    IF v_categoria IS NULL THEN
        RAISE EXCEPTION 'categoria requerida'
            USING ERRCODE = '22023';
    END IF;

    IF p_id_categoria IS NULL THEN
        SELECT COALESCE(MAX(id_categoria_analisis_senal), 0) + 1
        INTO v_id_categoria
        FROM sds.categoria_analisis_senal;
    ELSE
        v_id_categoria := p_id_categoria;
    END IF;

    INSERT INTO sds.categoria_analisis_senal (
        id_categoria_analisis_senal,
        nombre_categoria_analisis,
        descripcion_categoria_analisis
    ) VALUES (
        v_id_categoria,
        v_categoria->>'nombre_categoria_analisis',
        v_categoria->>'descripcion_categoria_analisis'
    );

    v_conductas := COALESCE(p_payload->'conductas', '[]'::jsonb);
    v_palabras := COALESCE(p_payload->'palabras_clave', '[]'::jsonb);
    v_emoticones := COALESCE(p_payload->'emoticones', '[]'::jsonb);
    v_frases := COALESCE(p_payload->'frases_clave', '[]'::jsonb);

    SELECT COALESCE(MAX(id_conducta_vulneratorias), 0) INTO v_base_conductas FROM sds.conducta_vulneratoria;
    SELECT COALESCE(MAX(id_palabra_clave), 0) INTO v_base_palabras FROM sds.palabra_clave;
    SELECT COALESCE(MAX(id_emoticon), 0) INTO v_base_emoticones FROM sds.emoticon;
    SELECT COALESCE(MAX(id_frase_clave), 0) INTO v_base_frases FROM sds.frase_clave;

    WITH payload AS (
        SELECT
            COALESCE(x.id_conducta_vulneratorias, v_base_conductas + ROW_NUMBER() OVER ())::smallint AS id_conducta_vulneratorias,
            x.nombre_conducta_vulneratoria,
            x.definicion_conducta_vulneratoria,
            x.peso_conducta_vulneratoria
        FROM jsonb_to_recordset(v_conductas) AS x(
            id_conducta_vulneratorias smallint,
            nombre_conducta_vulneratoria text,
            definicion_conducta_vulneratoria text,
            peso_conducta_vulneratoria numeric(5, 2)
        )
    ),
    inserted AS (
        INSERT INTO sds.conducta_vulneratoria (
            id_conducta_vulneratorias,
            id_categoria_analisis_senal,
            nombre_conducta_vulneratoria,
            definicion_conducta_vulneratoria,
            peso_conducta_vulneratoria
        )
        SELECT
            x.id_conducta_vulneratorias,
            v_id_categoria,
            x.nombre_conducta_vulneratoria,
            x.definicion_conducta_vulneratoria,
            x.peso_conducta_vulneratoria
        FROM payload x
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_ins_conductas FROM inserted;

    WITH payload AS (
        SELECT
            COALESCE(x.id_palabra_clave, v_base_palabras + ROW_NUMBER() OVER ())::smallint AS id_palabra_clave,
            x.nombre_palabra_clave,
            x.peso_palabra_clave
        FROM jsonb_to_recordset(v_palabras) AS x(
            id_palabra_clave smallint,
            nombre_palabra_clave text,
            peso_palabra_clave numeric(5, 2)
        )
    ),
    inserted AS (
        INSERT INTO sds.palabra_clave (
            id_palabra_clave,
            id_categoria_analisis_senal,
            nombre_palabra_clave,
            peso_palabra_clave
        )
        SELECT
            x.id_palabra_clave,
            v_id_categoria,
            x.nombre_palabra_clave,
            x.peso_palabra_clave
        FROM payload x
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_ins_palabras FROM inserted;

    WITH payload AS (
        SELECT
            COALESCE(x.id_emoticon, v_base_emoticones + ROW_NUMBER() OVER ())::smallint AS id_emoticon,
            x.tipo_emoticon,
            x.peso_emoticon
        FROM jsonb_to_recordset(v_emoticones) AS x(
            id_emoticon smallint,
            tipo_emoticon text,
            peso_emoticon numeric(5, 2)
        )
    ),
    inserted AS (
        INSERT INTO sds.emoticon (
            id_emoticon,
            id_categoria_analisis_senal,
            tipo_emoticon,
            peso_emoticon
        )
        SELECT
            x.id_emoticon,
            v_id_categoria,
            x.tipo_emoticon,
            x.peso_emoticon
        FROM payload x
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_ins_emoticones FROM inserted;

    WITH payload AS (
        SELECT
            COALESCE(x.id_frase_clave, v_base_frases + ROW_NUMBER() OVER ())::smallint AS id_frase_clave,
            x.nombre_frase_clave,
            x.peso_frase_clave
        FROM jsonb_to_recordset(v_frases) AS x(
            id_frase_clave smallint,
            nombre_frase_clave text,
            peso_frase_clave numeric(5, 2)
        )
    ),
    inserted AS (
        INSERT INTO sds.frase_clave (
            id_frase_clave,
            id_categoria_analisis_senal,
            nombre_frase_clave,
            peso_frase_clave
        )
        SELECT
            x.id_frase_clave,
            v_id_categoria,
            x.nombre_frase_clave,
            x.peso_frase_clave
        FROM payload x
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_ins_frases FROM inserted;

    RETURN jsonb_build_object(
        'idCategoria', v_id_categoria,
        'inserted', jsonb_build_object(
            'conductas', v_ins_conductas,
            'palabras_clave', v_ins_palabras,
            'emoticones', v_ins_emoticones,
            'frases_clave', v_ins_frases
        )
    );
END;
$$;


--
-- Name: delete_categoria_analisis(smallint); Type: FUNCTION; Schema: sds; Owner: -
--

CREATE FUNCTION sds.delete_categoria_analisis(p_id_categoria smallint) RETURNS jsonb
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_deleted_conductas integer := 0;
    v_deleted_palabras integer := 0;
    v_deleted_emoticones integer := 0;
    v_deleted_frases integer := 0;
    v_deleted_categoria integer := 0;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM sds.categoria_analisis_senal
        WHERE id_categoria_analisis_senal = p_id_categoria
    ) THEN
        RAISE EXCEPTION 'Categoria de analisis no existe'
            USING ERRCODE = 'P0002';
    END IF;

    WITH deleted AS (
        DELETE FROM sds.conducta_vulneratoria
        WHERE id_categoria_analisis_senal = p_id_categoria
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_deleted_conductas FROM deleted;

    WITH deleted AS (
        DELETE FROM sds.palabra_clave
        WHERE id_categoria_analisis_senal = p_id_categoria
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_deleted_palabras FROM deleted;

    WITH deleted AS (
        DELETE FROM sds.emoticon
        WHERE id_categoria_analisis_senal = p_id_categoria
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_deleted_emoticones FROM deleted;

    WITH deleted AS (
        DELETE FROM sds.frase_clave
        WHERE id_categoria_analisis_senal = p_id_categoria
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_deleted_frases FROM deleted;

    WITH deleted AS (
        DELETE FROM sds.categoria_analisis_senal
        WHERE id_categoria_analisis_senal = p_id_categoria
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_deleted_categoria FROM deleted;

    RETURN jsonb_build_object(
        'idCategoria', p_id_categoria,
        'deleted', true,
        'deleted_counts', jsonb_build_object(
            'conductas', v_deleted_conductas,
            'palabras_clave', v_deleted_palabras,
            'emoticones', v_deleted_emoticones,
            'frases_clave', v_deleted_frases,
            'categoria', v_deleted_categoria
        )
    );
END;
$$;


--
-- Name: sync_categoria_analisis(smallint, jsonb); Type: FUNCTION; Schema: sds; Owner: -
--

CREATE FUNCTION sds.sync_categoria_analisis(p_id_categoria smallint, p_payload jsonb) RETURNS jsonb
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
        WHERE sds.conducta_vulneratoria.id_categoria_analisis_senal = p_id_categoria
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
        WHERE sds.palabra_clave.id_categoria_analisis_senal = p_id_categoria
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
        WHERE sds.emoticon.id_categoria_analisis_senal = p_id_categoria
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
        WHERE sds.frase_clave.id_categoria_analisis_senal = p_id_categoria
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


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: configuracion_sistema; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.configuracion_sistema (
    id integer NOT NULL,
    clave character varying(100) NOT NULL,
    valor text,
    tipo_dato character varying(20) DEFAULT 'string'::character varying NOT NULL,
    descripcion character varying(255),
    categoria character varying(50),
    es_sensible boolean DEFAULT false NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT now() NOT NULL,
    fecha_actualizacion timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: configuracion_sistema_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.configuracion_sistema_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: configuracion_sistema_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.configuracion_sistema_id_seq OWNED BY public.configuracion_sistema.id;


--
-- Name: eventos_auditoria; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.eventos_auditoria (
    id integer NOT NULL,
    usuario_id integer,
    tipo_evento character varying(50) NOT NULL,
    recurso character varying(100),
    accion character varying(50),
    resultado character varying(20) NOT NULL,
    ip_address character varying(45),
    user_agent character varying(500),
    detalles json,
    fecha_evento timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: eventos_auditoria_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.eventos_auditoria_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: eventos_auditoria_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.eventos_auditoria_id_seq OWNED BY public.eventos_auditoria.id;


--
-- Name: password_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.password_history (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    contrasena_hash character varying(255) NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: password_history_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.password_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: password_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.password_history_id_seq OWNED BY public.password_history.id;


--
-- Name: permisos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.permisos (
    id integer NOT NULL,
    codigo character varying(100) NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion character varying(255),
    recurso character varying(50) NOT NULL,
    accion character varying(50) NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: permisos_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.permisos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: permisos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.permisos_id_seq OWNED BY public.permisos.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    nombre character varying(50) NOT NULL,
    descripcion character varying(255),
    activo boolean DEFAULT true NOT NULL,
    es_sistema boolean DEFAULT false NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT now() NOT NULL,
    fecha_actualizacion timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: roles_permisos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.roles_permisos (
    rol_id integer NOT NULL,
    permiso_id integer NOT NULL,
    fecha_asignacion timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: sesiones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sesiones (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    token_acceso text NOT NULL,
    token_refresco text NOT NULL,
    fecha_expiracion timestamp without time zone NOT NULL,
    fecha_expiracion_refresco timestamp without time zone NOT NULL,
    valida boolean DEFAULT true NOT NULL,
    direccion_ip character varying(45),
    user_agent character varying(500),
    fecha_creacion timestamp without time zone DEFAULT now() NOT NULL,
    fecha_ultimo_acceso timestamp without time zone,
    fecha_invalidacion timestamp without time zone,
    razon_invalidacion character varying(255),
    access_token text
);


--
-- Name: sesiones_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sesiones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sesiones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sesiones_id_seq OWNED BY public.sesiones.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    nombre_usuario character varying(50) NOT NULL,
    email character varying(255),
    nombre_completo character varying(255),
    contrasena_hash character varying(255),
    tipo_autenticacion public.tipo_autenticacion DEFAULT 'local'::public.tipo_autenticacion NOT NULL,
    id_externo character varying(255),
    activo boolean DEFAULT true NOT NULL,
    es_superusuario boolean DEFAULT false NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT now() NOT NULL,
    fecha_actualizacion timestamp without time zone DEFAULT now() NOT NULL,
    ultimo_acceso timestamp without time zone,
    ultimo_cambio_contrasena timestamp without time zone,
    intentos_login_fallidos integer DEFAULT 0 NOT NULL,
    fecha_bloqueo timestamp without time zone,
    requiere_cambio_contrasena boolean DEFAULT false NOT NULL,
    telefono character varying(20),
    departamento character varying(100),
    cargo character varying(100),
    reset_token character varying(255),
    reset_token_expira timestamp without time zone
);


--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: usuarios_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuarios_roles (
    usuario_id integer NOT NULL,
    rol_id integer NOT NULL,
    fecha_asignacion timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: categoria_analisis_senal; Type: TABLE; Schema: sds; Owner: -
--

CREATE TABLE sds.categoria_analisis_senal (
    id_categoria_analisis_senal smallint NOT NULL,
    nombre_categoria_analisis text NOT NULL,
    descripcion_categoria_analisis text
);


--
-- Name: categoria_observacion; Type: TABLE; Schema: sds; Owner: -
--

CREATE TABLE sds.categoria_observacion (
    id_categoria_observacion smallint NOT NULL,
    id_parent_categoria_observacion smallint,
    codigo_categoria_observacion text NOT NULL,
    nombre_categoria_observacion text,
    descripcion_categoria_observacion text,
    nivel smallint,
    peso_categoria_observacion numeric(5,2)
);


--
-- Name: categoria_senal; Type: TABLE; Schema: sds; Owner: -
--

CREATE TABLE sds.categoria_senal (
    id_categoria_senales smallint NOT NULL,
    id_parent_categoria_senales smallint,
    nombre_categoria_senal text,
    descripcion_categoria_senal text,
    nivel smallint
);


--
-- Name: conducta_vulneratoria; Type: TABLE; Schema: sds; Owner: -
--

CREATE TABLE sds.conducta_vulneratoria (
    id_conducta_vulneratorias smallint NOT NULL,
    id_categoria_analisis_senal smallint NOT NULL,
    nombre_conducta_vulneratoria text NOT NULL,
    definicion_conducta_vulneratoria text NOT NULL,
    peso_conducta_vulneratoria numeric(5,2)
);


--
-- Name: emoticon; Type: TABLE; Schema: sds; Owner: -
--

CREATE TABLE sds.emoticon (
    id_emoticon smallint NOT NULL,
    id_categoria_analisis_senal smallint NOT NULL,
    tipo_emoticon text,
    peso_emoticon numeric(5,2)
);


--
-- Name: entidades; Type: TABLE; Schema: sds; Owner: -
--

CREATE TABLE sds.entidades (
    id_entidades smallint NOT NULL,
    nombre_entidad text,
    peso_entidad numeric(5,2),
    id_categoria_observacion smallint
);


--
-- Name: figuras_publicas; Type: TABLE; Schema: sds; Owner: -
--

CREATE TABLE sds.figuras_publicas (
    id_figura_publica smallint NOT NULL,
    nombre_actor text,
    peso_actor numeric(5,2),
    id_categoria_observacion smallint
);


--
-- Name: frase_clave; Type: TABLE; Schema: sds; Owner: -
--

CREATE TABLE sds.frase_clave (
    id_frase_clave smallint NOT NULL,
    id_categoria_analisis_senal smallint NOT NULL,
    nombre_frase_clave text,
    peso_frase_clave numeric(5,2)
);


--
-- Name: influencers; Type: TABLE; Schema: sds; Owner: -
--

CREATE TABLE sds.influencers (
    id_influencer smallint NOT NULL,
    nombre_influencer text,
    peso_influencer numeric(5,2),
    id_categoria_observacion smallint
);


--
-- Name: medios_digitales; Type: TABLE; Schema: sds; Owner: -
--

CREATE TABLE sds.medios_digitales (
    id_medio_digital smallint NOT NULL,
    nombre_medio_digital text,
    peso_medio_digital numeric(5,2),
    id_categoria_observacion smallint
);


--
-- Name: palabra_clave; Type: TABLE; Schema: sds; Owner: -
--

CREATE TABLE sds.palabra_clave (
    id_palabra_clave smallint NOT NULL,
    id_categoria_analisis_senal smallint NOT NULL,
    nombre_palabra_clave text,
    peso_palabra_clave numeric(5,2)
);


--
-- Name: resultado_observacion_senal; Type: TABLE; Schema: sds; Owner: -
--

CREATE TABLE sds.resultado_observacion_senal (
    id_resultado_observacion_senal smallint NOT NULL,
    id_senal_detectada smallint NOT NULL,
    id_categoria_observacion smallint NOT NULL,
    resultado_observacion_categoria numeric(5,2),
    codigo_categoria_observacion text
);


--
-- Name: senal_detectada; Type: TABLE; Schema: sds; Owner: -
--

CREATE TABLE sds.senal_detectada (
    id_senal_detectada smallint NOT NULL,
    id_categoria_senal smallint NOT NULL,
    fecha_deteccion timestamp with time zone,
    id_categoria_analisis_senal smallint NOT NULL,
    score_riesgo numeric(5,2),
    fecha_actualizacion timestamp with time zone
);


--
-- Name: configuracion_sistema id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configuracion_sistema ALTER COLUMN id SET DEFAULT nextval('public.configuracion_sistema_id_seq'::regclass);


--
-- Name: eventos_auditoria id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eventos_auditoria ALTER COLUMN id SET DEFAULT nextval('public.eventos_auditoria_id_seq'::regclass);


--
-- Name: password_history id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_history ALTER COLUMN id SET DEFAULT nextval('public.password_history_id_seq'::regclass);


--
-- Name: permisos id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permisos ALTER COLUMN id SET DEFAULT nextval('public.permisos_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: sesiones id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sesiones ALTER COLUMN id SET DEFAULT nextval('public.sesiones_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
008_create_historial_senal_sds
\.


--
-- Data for Name: configuracion_sistema; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.configuracion_sistema (id, clave, valor, tipo_dato, descripcion, categoria, es_sensible, fecha_creacion, fecha_actualizacion) FROM stdin;
\.


--
-- Data for Name: eventos_auditoria; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.eventos_auditoria (id, usuario_id, tipo_evento, recurso, accion, resultado, ip_address, user_agent, detalles, fecha_evento) FROM stdin;
1	2	actualizacion_categoria_senal	categoria_senal	actualizar_categoria	exito	192.168.65.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	{"id_categoria_senal": 2, "color_nuevo": "#FFA500", "descripcion_nueva": "Amenaza inmediata a derechos", "usuario_nombre": "admin"}	2026-01-15 21:51:26.198149
2	2	actualizacion_categoria_senal	categoria_senal	actualizar_categoria	exito	192.168.65.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	{"id_categoria_senal": 2, "color_nuevo": "#FFA500", "descripcion_nueva": "Amenaza inmediata a derechos", "usuario_nombre": "admin"}	2026-01-15 21:54:22.039262
3	2	actualizacion_categoria_senal	categoria_senal	actualizar_categoria	exito	192.168.65.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	{"id_categoria_senal": 2, "color_nuevo": "#FFA500", "descripcion_nueva": "Amenaza inmediata a derechos", "usuario_nombre": "admin"}	2026-01-15 21:55:22.444711
4	2	actualizacion_categoria_senal	categoria_senal	actualizar_categoria	exito	192.168.65.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	{"id_categoria_senal": 2, "color_nuevo": "#FFA500", "descripcion_nueva": "Amenaza inmediata a derechos", "usuario_nombre": "admin"}	2026-01-15 21:59:51.274069
5	2	actualizacion_categoria_senal	categoria_senal	actualizar_categoria	exito	192.168.65.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	{"id_categoria_senal": 1, "color_nuevo": "#808080", "descripcion_nueva": "Amenaza inmediata a derechos", "usuario_nombre": "admin"}	2026-01-15 22:02:29.786164
6	2	actualizacion_categoria_senal	categoria_senal	actualizar_categoria	exito	192.168.65.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	{"id_categoria_senal": 2, "color_nuevo": "#FFA500", "descripcion_nueva": "Amenaza inmediata a derechos", "usuario_nombre": "admin"}	2026-01-15 22:08:19.532236
7	2	actualizacion_categoria_senal	categoria_senal	actualizar_categoria	exito	192.168.65.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	{"id_categoria_senal": 2, "color_nuevo": "#FFA500", "descripcion_nueva": "Amenaza inmediata a derechos", "usuario_nombre": "admin"}	2026-01-15 22:08:53.453601
8	2	actualizacion_categoria_senal	categoria_senal	actualizar_categoria	exito	192.168.65.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	{"id_categoria_senal": 2, "color_nuevo": "#FFA500", "descripcion_nueva": "Amenaza inmediata a derechos", "usuario_nombre": "admin"}	2026-01-15 22:09:43.523445
9	2	actualizacion_categoria_senal	categoria_senal	actualizar_categoria	exito	192.168.65.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	{"id_categoria_senal": 2, "color_nuevo": "#FFA500", "descripcion_nueva": "Amenaza inmediata a derechos", "usuario_nombre": "admin"}	2026-01-15 22:15:53.503315
10	2	actualizacion_categoria_senal	categoria_senal	actualizar_categoria	exito	192.168.65.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	{"id_categoria_senal": 2, "color_nuevo": "#FFA500", "descripcion_nueva": "Amenaza inmediata a derechos", "usuario_nombre": "admin"}	2026-01-15 22:17:09.833137
11	2	actualizacion_categoria_senal	categoria_senal	actualizar_categoria	exito	142.251.133.106	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.2 Safari/605.1.15	{"id_categoria_senal": 3, "color_nuevo": "#FF0000", "descripcion_nueva": "Amenaza inmediata a derechos", "usuario_nombre": "admin"}	2026-01-16 02:20:50.883297
\.


--
-- Data for Name: password_history; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.password_history (id, usuario_id, contrasena_hash, fecha_creacion) FROM stdin;
\.


--
-- Data for Name: permisos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.permisos (id, codigo, nombre, descripcion, recurso, accion, fecha_creacion) FROM stdin;
1	usuarios.leer	Leer Usuarios	Ver información de usuarios	usuarios	leer	2026-01-15 19:59:12.735749
2	usuarios.crear	Crear Usuarios	Crear nuevos usuarios	usuarios	crear	2026-01-15 19:59:12.735751
3	usuarios.actualizar	Actualizar Usuarios	Modificar usuarios existentes	usuarios	actualizar	2026-01-15 19:59:12.735751
4	usuarios.eliminar	Eliminar Usuarios	Eliminar usuarios	usuarios	eliminar	2026-01-15 19:59:12.735752
5	roles.leer	Leer Roles	Ver roles del sistema	roles	leer	2026-01-15 19:59:12.735753
6	roles.crear	Crear Roles	Crear nuevos roles	roles	crear	2026-01-15 19:59:12.735753
7	roles.actualizar	Actualizar Roles	Modificar roles existentes	roles	actualizar	2026-01-15 19:59:12.735754
8	roles.eliminar	Eliminar Roles	Eliminar roles	roles	eliminar	2026-01-15 19:59:12.735754
9	alertas.leer	Leer Alertas	Ver alertas del sistema	alertas	leer	2026-01-15 19:59:12.735754
10	alertas.crear	Crear Alertas	Crear nuevas alertas	alertas	crear	2026-01-15 19:59:12.735754
11	alertas.actualizar	Actualizar Alertas	Modificar alertas	alertas	actualizar	2026-01-15 19:59:12.735754
12	alertas.eliminar	Eliminar Alertas	Eliminar alertas	alertas	eliminar	2026-01-15 19:59:12.735755
13	alertas.clasificar	Clasificar Alertas	Clasificar y categorizar alertas	alertas	clasificar	2026-01-15 19:59:12.735755
14	reportes.leer	Leer Reportes	Ver reportes del sistema	reportes	leer	2026-01-15 19:59:12.735755
15	reportes.generar	Generar Reportes	Generar nuevos reportes	reportes	generar	2026-01-15 19:59:12.735755
16	auditoria.leer	Leer Auditoría	Ver logs de auditoría	auditoria	leer	2026-01-15 19:59:12.735755
17	configuracion.leer	Leer Configuración	Ver configuración del sistema	configuracion	leer	2026-01-15 19:59:12.735756
18	configuracion.actualizar	Actualizar Configuración	Modificar configuración	configuracion	actualizar	2026-01-15 19:59:12.735756
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.roles (id, nombre, descripcion, activo, es_sistema, fecha_creacion, fecha_actualizacion) FROM stdin;
1	Administrador	Acceso completo al sistema	t	t	2026-01-15 19:59:12.738594	2026-01-15 19:59:12.738595
2	Analista	Analista de alertas y reportes	t	t	2026-01-15 19:59:12.745627	2026-01-15 19:59:12.745628
3	Operador	Operador básico del sistema	t	t	2026-01-15 19:59:12.748447	2026-01-15 19:59:12.748448
4	Auditor	Auditor del sistema	t	t	2026-01-15 19:59:12.750012	2026-01-15 19:59:12.750013
\.


--
-- Data for Name: roles_permisos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.roles_permisos (rol_id, permiso_id, fecha_asignacion) FROM stdin;
1	1	2026-01-15 19:59:12.739253
1	2	2026-01-15 19:59:12.740242
1	3	2026-01-15 19:59:12.740654
1	4	2026-01-15 19:59:12.740947
1	5	2026-01-15 19:59:12.741248
1	6	2026-01-15 19:59:12.741551
1	7	2026-01-15 19:59:12.741821
1	8	2026-01-15 19:59:12.742177
1	9	2026-01-15 19:59:12.742495
1	10	2026-01-15 19:59:12.742751
1	11	2026-01-15 19:59:12.743078
1	12	2026-01-15 19:59:12.743452
1	13	2026-01-15 19:59:12.743729
1	14	2026-01-15 19:59:12.743992
1	15	2026-01-15 19:59:12.744271
1	16	2026-01-15 19:59:12.744547
1	17	2026-01-15 19:59:12.744793
1	18	2026-01-15 19:59:12.745056
2	9	2026-01-15 19:59:12.745961
2	10	2026-01-15 19:59:12.746367
2	11	2026-01-15 19:59:12.746682
2	13	2026-01-15 19:59:12.746989
2	14	2026-01-15 19:59:12.747312
2	15	2026-01-15 19:59:12.747616
2	1	2026-01-15 19:59:12.747933
3	9	2026-01-15 19:59:12.748763
3	10	2026-01-15 19:59:12.749119
3	14	2026-01-15 19:59:12.749434
4	1	2026-01-15 19:59:12.750396
4	5	2026-01-15 19:59:12.750744
4	9	2026-01-15 19:59:12.751102
4	14	2026-01-15 19:59:12.751465
4	16	2026-01-15 19:59:12.751789
\.


--
-- Data for Name: sesiones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sesiones (id, usuario_id, token_acceso, token_refresco, fecha_expiracion, fecha_expiracion_refresco, valida, direccion_ip, user_agent, fecha_creacion, fecha_ultimo_acceso, fecha_invalidacion, razon_invalidacion, access_token) FROM stdin;
1	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTA5MDUxLCJpYXQiOjE3Njg1MDcyNTEsInR5cGUiOiJhY2Nlc3MifQ.ShWC2IWcKVRNXxRzHEO5WqhJhuOzilMCdxlHQX0gG_8	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTEyMDUxLCJpYXQiOjE3Njg1MDcyNTEsInR5cGUiOiJyZWZyZXNoIn0.HLAVAylHeTipsyBNCYtPmSEjapv1-JZxdCNH-AC89pY	2026-01-15 20:30:51.8135	2026-01-22 20:00:51.813502	f	\N	\N	2026-01-15 20:00:51.815738	\N	\N	\N	\N
2	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTA5MDU4LCJpYXQiOjE3Njg1MDcyNTgsInR5cGUiOiJhY2Nlc3MifQ.7O9r4QxaJOYlaShIA_2pzhhidWt6fI0GrJSy7TxVJdE	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTEyMDU4LCJpYXQiOjE3Njg1MDcyNTgsInR5cGUiOiJyZWZyZXNoIn0.E0WU4Sq5Gomq0A0znCp9HBMhTVni-YMK-1Drh_PDcyk	2026-01-15 20:30:58.284145	2026-01-22 20:00:58.284147	f	\N	\N	2026-01-15 20:00:58.284393	\N	\N	\N	\N
3	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTA5MDk4LCJpYXQiOjE3Njg1MDcyOTgsInR5cGUiOiJhY2Nlc3MifQ.5DU6FSrWFIKWa7QbK-DIckMTTeJZORLpt93gMyuviR4	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTEyMDk4LCJpYXQiOjE3Njg1MDcyOTgsInR5cGUiOiJyZWZyZXNoIn0.bac02HcDM8gybZ6h6P1u4o4LFaJCitQ5Fy7LV9K4cZM	2026-01-15 20:31:38.42121	2026-01-22 20:01:38.421211	f	\N	\N	2026-01-15 20:01:38.421569	\N	\N	\N	\N
4	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTA5NzUyLCJpYXQiOjE3Njg1MDc5NTIsInR5cGUiOiJhY2Nlc3MifQ.bCb8JGEuJCnJv1dbwvGWrjvnGf7jCZfQzaKKXfk5u_c	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTEyNzUyLCJpYXQiOjE3Njg1MDc5NTIsInR5cGUiOiJyZWZyZXNoIn0.YqPEAGWWGCXo7wrcy5Ajdd1LYIVCUSKfPIXI8-FRfMg	2026-01-15 20:42:32.320516	2026-01-22 20:12:32.320519	f	\N	\N	2026-01-15 20:12:32.321482	\N	\N	\N	\N
5	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTA5Nzk4LCJpYXQiOjE3Njg1MDc5OTgsInR5cGUiOiJhY2Nlc3MifQ.oBrCTvrwjWos7DB-VMBO1o1_8G1qo5v2oEXWeMoZWMQ	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTEyNzk4LCJpYXQiOjE3Njg1MDc5OTgsInR5cGUiOiJyZWZyZXNoIn0.CTANicEiYWT-jI7VAqYaf9oA8zeJIgN1AWaOkso3vWA	2026-01-15 20:43:18.689098	2026-01-22 20:13:18.689099	f	\N	\N	2026-01-15 20:13:18.689643	\N	\N	\N	\N
6	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTExMTE5LCJpYXQiOjE3Njg1MDkzMTksInR5cGUiOiJhY2Nlc3MifQ.okHO3TCfMhy8AtswCQhbnOBvAB1hAFI9PXKB_EFxwlY	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE0MTE5LCJpYXQiOjE3Njg1MDkzMTksInR5cGUiOiJyZWZyZXNoIn0.7dpULLisdZYDakiwdIf4BPw4xMzayC94GGhDwg9oXlA	2026-01-15 21:05:19.322566	2026-01-22 20:35:19.322568	f	\N	\N	2026-01-15 20:35:19.323477	\N	\N	\N	\N
7	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTExMjMxLCJpYXQiOjE3Njg1MDk0MzEsInR5cGUiOiJhY2Nlc3MifQ.4MiotdGa5Tyf24KhuYkZNbU6nazrPEYKRDN8JMicmpQ	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE0MjMxLCJpYXQiOjE3Njg1MDk0MzEsInR5cGUiOiJyZWZyZXNoIn0.RXa1ei-HdwSbl9vDRzcK1fu5OajiGCCSjQZD0m-iL08	2026-01-15 21:07:11.421657	2026-01-22 20:37:11.421658	f	\N	\N	2026-01-15 20:37:11.422024	\N	\N	\N	\N
8	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTExMjYxLCJpYXQiOjE3Njg1MDk0NjEsInR5cGUiOiJhY2Nlc3MifQ.5896i_LKnpNQGRm9A33fclMca39RataCyqv_iMEnbKI	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE0MjYxLCJpYXQiOjE3Njg1MDk0NjEsInR5cGUiOiJyZWZyZXNoIn0.-y6BBao54LgOwgQF863vF4Cijf0VLc_5CLoa1gScxK8	2026-01-15 21:07:41.546085	2026-01-22 20:37:41.546087	f	\N	\N	2026-01-15 20:37:41.5471	\N	\N	\N	\N
9	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTExMzU3LCJpYXQiOjE3Njg1MDk1NTcsInR5cGUiOiJhY2Nlc3MifQ.FBPlXpt2gGk5tQKfXawt037xps9RO3GLEr75j5PfIM8	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE0MzU3LCJpYXQiOjE3Njg1MDk1NTcsInR5cGUiOiJyZWZyZXNoIn0.kiJWa8vtg-vh1q52ranHpz3MuG9Lt4IP_pfp7oV9AqE	2026-01-15 21:09:17.350422	2026-01-22 20:39:17.350423	f	\N	\N	2026-01-15 20:39:17.350928	\N	\N	\N	\N
10	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTExNTUwLCJpYXQiOjE3Njg1MDk3NTAsInR5cGUiOiJhY2Nlc3MifQ.sOhcNTOCQMDFEbmO8MpItuZMv4Q9ruda9UYqN3LFO4g	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE0NTUwLCJpYXQiOjE3Njg1MDk3NTAsInR5cGUiOiJyZWZyZXNoIn0.iDYsLzmpbrtCBxWx8_0qYcgrlVUuI-4TJ_HgVLNIaTY	2026-01-15 21:12:30.256845	2026-01-22 20:42:30.256846	f	\N	\N	2026-01-15 20:42:30.257748	\N	\N	\N	\N
11	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTExNTU1LCJpYXQiOjE3Njg1MDk3NTUsInR5cGUiOiJhY2Nlc3MifQ.oMG7YOIupVGo5XbQ-bJP9o2npvBKiQGnsjr-DNeLEhw	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE0NTU1LCJpYXQiOjE3Njg1MDk3NTUsInR5cGUiOiJyZWZyZXNoIn0.jiunW5ookAJJaeB0Rj3rSgNRboXBTmEMmohlTK-up9I	2026-01-15 21:12:35.781074	2026-01-22 20:42:35.781076	f	\N	\N	2026-01-15 20:42:35.781478	\N	\N	\N	\N
13	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTExODg1LCJpYXQiOjE3Njg1MTAwODUsInR5cGUiOiJhY2Nlc3MifQ.c6wLyVyUboBwq30fMp1tQLBCDBMgjEz2KHJVe_7VsOU	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE0ODg1LCJpYXQiOjE3Njg1MTAwODUsInR5cGUiOiJyZWZyZXNoIn0.J8F97ys9DP1tDyGyvpivzosR9WpsyHXIh7MZZxL-LPo	2026-01-15 21:18:05.184073	2026-01-22 20:48:05.184075	f	\N	\N	2026-01-15 20:48:05.185095	\N	\N	\N	\N
14	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTEyMDk0LCJpYXQiOjE3Njg1MTAyOTQsInR5cGUiOiJhY2Nlc3MifQ.uiY-nZRPL4DIHs5jK4im7YOZ9xX7l18djEoCmsfl2bk	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE1MDk0LCJpYXQiOjE3Njg1MTAyOTQsInR5cGUiOiJyZWZyZXNoIn0.Q91RKBSu9snxX5yezR1w9881wsizte6vMkAbDoXOIwE	2026-01-15 21:21:34.046845	2026-01-22 20:51:34.046847	f	\N	\N	2026-01-15 20:51:34.047187	\N	\N	\N	\N
15	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTEyMTc4LCJpYXQiOjE3Njg1MTAzNzgsInR5cGUiOiJhY2Nlc3MifQ.z8cy8a_6u6TlIvLxk_xEIweP767My_F1Umva6teM_8M	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE1MTc4LCJpYXQiOjE3Njg1MTAzNzgsInR5cGUiOiJyZWZyZXNoIn0.x-MZGQAvQ6qcxjsvB-NP7lthkiQ6n6RM2P5M43avD8k	2026-01-15 21:22:58.975808	2026-01-22 20:52:58.97581	f	\N	\N	2026-01-15 20:52:58.976152	\N	\N	\N	\N
12	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTExNTY5LCJpYXQiOjE3Njg1MDk3NjksInR5cGUiOiJhY2Nlc3MifQ.i6fPAmRMUJtqo2GrnJ-VPp8Y2cxbnbJg7bfwubEhMa4	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE0NTY5LCJpYXQiOjE3Njg1MDk3NjksInR5cGUiOiJyZWZyZXNoIn0.QTruYopO9AG0XZMjU-Sy0dhipwf1ZkZLpOV7o68fy4Y	2026-01-15 21:12:49.670084	2026-01-22 20:42:49.670085	f	\N	\N	2026-01-15 20:42:49.671645	\N	\N	\N	\N
16	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTEyNzUyLCJpYXQiOjE3Njg1MTA5NTIsInR5cGUiOiJhY2Nlc3MifQ.CCbumWNLKyI0d5ajeCYu-kWLtas2KeHY6AWEei-_Gpw	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE1NzUyLCJpYXQiOjE3Njg1MTA5NTIsInR5cGUiOiJyZWZyZXNoIn0.gyMxPoZTkkx7_QLH-FtwV4mw9NYMkuFp6YXeSBPrOPA	2026-01-15 21:32:32.15082	2026-01-22 21:02:32.150823	f	\N	\N	2026-01-15 21:02:32.151525	\N	\N	\N	\N
17	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTEyODM5LCJpYXQiOjE3Njg1MTEwMzksInR5cGUiOiJhY2Nlc3MifQ.xAqDAe1-VFmquDvtTmIdMr5JGKcXNbqNa8ByCPwOx90	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE1ODM5LCJpYXQiOjE3Njg1MTEwMzksInR5cGUiOiJyZWZyZXNoIn0.sgLam-aVvDz7OB2pGJWLNJGyAlOLpg749iJxS8msXsA	2026-01-15 21:33:59.741275	2026-01-22 21:03:59.741277	f	\N	\N	2026-01-15 21:03:59.742348	\N	\N	\N	\N
18	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTEyOTU0LCJpYXQiOjE3Njg1MTExNTQsInR5cGUiOiJhY2Nlc3MifQ.0TDvXWAvv_hXNTUj6onTncOnuOJNtgO9oQkPMu2-5zA	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE1OTU0LCJpYXQiOjE3Njg1MTExNTQsInR5cGUiOiJyZWZyZXNoIn0.piKTsOtKwHMVvZ9wu7ImHRODVoP0jWpmqLlVXA4YhMs	2026-01-15 21:35:54.734185	2026-01-22 21:05:54.734187	f	\N	\N	2026-01-15 21:05:54.734836	\N	\N	\N	\N
23	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTE1NjQ3LCJpYXQiOjE3Njg1MTM4NDcsInR5cGUiOiJhY2Nlc3MifQ.weQxcti4xR_daKTXAgw-MEj3EVYQt2BS8HRvkpu36Q4	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE4NjQ3LCJpYXQiOjE3Njg1MTM4NDcsInR5cGUiOiJyZWZyZXNoIn0.--02_xloiN97Cr-vjwSmzh41AJRT7b-0OaP4o6_Ll6o	2026-01-15 22:20:47.747609	2026-01-22 21:50:47.74761	f	\N	\N	2026-01-15 21:50:47.748025	\N	\N	\N	\N
24	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTE2NDU5LCJpYXQiOjE3Njg1MTQ2NTksInR5cGUiOiJhY2Nlc3MifQ.Mh204INcvvpLZV0Wsb3JgV31sl3BjyDi_UUTxxyxCpo	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE5NDU5LCJpYXQiOjE3Njg1MTQ2NTksInR5cGUiOiJyZWZyZXNoIn0.FgBmea4ef2jxNwRpO0eyXWn16spQM9sK7tJlL3tX2vk	2026-01-15 22:34:19.307824	2026-01-22 22:04:19.307826	f	\N	\N	2026-01-15 22:04:19.308024	\N	\N	\N	\N
19	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTEzMDAyLCJpYXQiOjE3Njg1MTEyMDIsInR5cGUiOiJhY2Nlc3MifQ.Lhj9sgn-gedfJjPfHZfEBW637zTkH5YRtLMtlCpP4a0	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE2MDAyLCJpYXQiOjE3Njg1MTEyMDIsInR5cGUiOiJyZWZyZXNoIn0.ore5qzKGnoJ-ME94ft4FIGELr61hozCnpE2M4rWEit4	2026-01-15 21:36:42.246937	2026-01-22 21:06:42.246939	f	\N	\N	2026-01-15 21:06:42.247891	\N	\N	\N	\N
20	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTEzMDM5LCJpYXQiOjE3Njg1MTEyMzksInR5cGUiOiJhY2Nlc3MifQ.ulJM3afcoJYM_gRKl0bxMMN5RoZm6w97Pf6TwSZ3UOU	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE2MDM5LCJpYXQiOjE3Njg1MTEyMzksInR5cGUiOiJyZWZyZXNoIn0.f2N-8LWvf7iSQeZKJwXQI7keLThKtGTZ4aFIaVEwbYw	2026-01-15 21:37:19.390936	2026-01-22 21:07:19.390939	f	\N	\N	2026-01-15 21:07:19.391722	\N	\N	\N	\N
21	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTEzMjgxLCJpYXQiOjE3Njg1MTE0ODEsInR5cGUiOiJhY2Nlc3MifQ.7cTcm3-Z82bMbrvbc8V2GWspoh11QoiGGCoZ6rMp_SM	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE2MjgxLCJpYXQiOjE3Njg1MTE0ODEsInR5cGUiOiJyZWZyZXNoIn0.SY829M6kwebt1EIkmvSBfaE7IkIJ3zU1zDABBqIpgHc	2026-01-15 21:41:21.997903	2026-01-22 21:11:21.997906	f	\N	\N	2026-01-15 21:11:21.998421	\N	\N	\N	\N
22	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTE1MTc4LCJpYXQiOjE3Njg1MTMzNzgsInR5cGUiOiJhY2Nlc3MifQ.a_V8uxaJBVWJT76F7MRVVpDDwbBV0qyKhYUsZzcDSbE	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE4MTc4LCJpYXQiOjE3Njg1MTMzNzgsInR5cGUiOiJyZWZyZXNoIn0.idbwVrTUOvjtofIhAFPgs2widVmwUKt4DmkBsslEKlc	2026-01-15 22:12:58.034374	2026-01-22 21:42:58.034377	f	\N	\N	2026-01-15 21:42:58.034806	\N	\N	\N	\N
25	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTE2NTMzLCJpYXQiOjE3Njg1MTQ3MzMsInR5cGUiOiJhY2Nlc3MifQ.lEHrk2FUfGau8-viEHDyIgX-tqbzY80UqbegWActess	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE5NTMzLCJpYXQiOjE3Njg1MTQ3MzMsInR5cGUiOiJyZWZyZXNoIn0.bgQhkDtrb64kYCf0k-iitAmDQrjlBrzmK0RsM4whC00	2026-01-15 22:35:33.65629	2026-01-22 22:05:33.656291	f	\N	\N	2026-01-15 22:05:33.656624	\N	\N	\N	\N
26	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTE2OTYyLCJpYXQiOjE3Njg1MTUxNjIsInR5cGUiOiJhY2Nlc3MifQ.3F8C73zBasLlYmmeabWVZ_aNvv1zBCy9OwIuosSN-cY	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTE5OTYyLCJpYXQiOjE3Njg1MTUxNjIsInR5cGUiOiJyZWZyZXNoIn0.Z5gWn8kbOHSzSfy75D1w4uF9jE5Ldg1M8XMe22Kwb1Y	2026-01-15 22:42:42.470947	2026-01-22 22:12:42.470949	f	\N	\N	2026-01-15 22:12:42.472063	\N	\N	\N	\N
28	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTE3MjA2LCJpYXQiOjE3Njg1MTU0MDYsInR5cGUiOiJhY2Nlc3MifQ.gv3F84a3fAT9iEMCwmheGowk-baG1EENNO9UC3L81XY	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTIwMjA2LCJpYXQiOjE3Njg1MTU0MDYsInR5cGUiOiJyZWZyZXNoIn0.RRwebaEiP6LitkAGPTnxPwE0EcHdxq0LGSODDQAqWjw	2026-01-15 22:46:46.91115	2026-01-22 22:16:46.911152	f	\N	\N	2026-01-15 22:16:46.911898	\N	\N	\N	\N
29	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTE3MjUzLCJpYXQiOjE3Njg1MTU0NTMsInR5cGUiOiJhY2Nlc3MifQ.SBaaylIlVsV5U_kcdFn6MLbruGkNNwllGZCcDUw8EGM	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTIwMjUzLCJpYXQiOjE3Njg1MTU0NTMsInR5cGUiOiJyZWZyZXNoIn0.fO8n9wtR9SG2yvWXvCW4EdR7KeUkxf2qnFM-zN3tZiI	2026-01-15 22:47:33.113587	2026-01-22 22:17:33.113589	f	\N	\N	2026-01-15 22:17:33.114381	\N	\N	\N	\N
30	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTI3ODA4LCJpYXQiOjE3Njg1MjYwMDgsInR5cGUiOiJhY2Nlc3MifQ.Pp1aXbRja32kVFv5lVvv57I2ZYa-j0EY8e2_EV4d7ro	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTMwODA4LCJpYXQiOjE3Njg1MjYwMDgsInR5cGUiOiJyZWZyZXNoIn0.OZ5qdZBmnRmlJfrwYsPIfot7nZRm5RnobmimkG7mym8	2026-01-16 01:43:28.86665	2026-01-23 01:13:28.866652	f	\N	\N	2026-01-16 01:13:28.867585	\N	\N	\N	\N
31	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTI4NzgwLCJpYXQiOjE3Njg1MjY5ODAsInR5cGUiOiJhY2Nlc3MifQ.9RAXUvl3TBDRpTmrvV2ko1CgrvdJ3vyEcanE4a8pxLw	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTMxNzgwLCJpYXQiOjE3Njg1MjY5ODAsInR5cGUiOiJyZWZyZXNoIn0._EyZjFubQyUxRtPjonr07N4-qAKEDAMFgmXewn97iYo	2026-01-16 01:59:40.506092	2026-01-23 01:29:40.506095	f	\N	\N	2026-01-16 01:29:40.506362	\N	\N	\N	\N
27	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTE3MDMyLCJpYXQiOjE3Njg1MTUyMzIsInR5cGUiOiJhY2Nlc3MifQ.O3g9sGdMUkaTMJjyX7Hj_bMdplDZSQmDAO5cuWgp4vU	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTIwMDMyLCJpYXQiOjE3Njg1MTUyMzIsInR5cGUiOiJyZWZyZXNoIn0.ikSsR6BOTB5yxnER-ddMkkcJEt182PYA58JzvXbSCls	2026-01-15 22:43:52.475626	2026-01-22 22:13:52.475628	f	\N	\N	2026-01-15 22:13:52.476457	\N	\N	\N	\N
32	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTI5NDAwLCJpYXQiOjE3Njg1Mjc2MDAsInR5cGUiOiJhY2Nlc3MifQ.JxXg_7iGRsgV-9RSkRD3fTDIn5piZoFoTA7axMgLe3M	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTMyNDAwLCJpYXQiOjE3Njg1Mjc2MDAsInR5cGUiOiJyZWZyZXNoIn0.ssw8c3K2wqc6DI649LT6TcWHBpo8-0a7EGQyNZ8PK3I	2026-01-16 02:10:00.387274	2026-01-23 01:40:00.387275	f	\N	\N	2026-01-16 01:40:00.388096	\N	\N	\N	\N
33	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTMwMzI1LCJpYXQiOjE3Njg1Mjg1MjUsInR5cGUiOiJhY2Nlc3MifQ.tfjLAe3rr3t0biIe0BfZjuIP6gJMQHE47cWuC-hF-F0	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTMzMzI1LCJpYXQiOjE3Njg1Mjg1MjUsInR5cGUiOiJyZWZyZXNoIn0.58zsY7Ngqoo35ETO7Dui6Ra4UL-OdTeKGW-my1sxMfA	2026-01-16 02:25:25.251411	2026-01-23 01:55:25.251414	f	\N	\N	2026-01-16 01:55:25.251775	\N	\N	\N	\N
34	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTMxMjE3LCJpYXQiOjE3Njg1Mjk0MTcsInR5cGUiOiJhY2Nlc3MifQ.iWCjQiEggDZ5b6UI-HrK5oCYu5dvxfY4VdZFcxQpkkk	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTM0MjE3LCJpYXQiOjE3Njg1Mjk0MTcsInR5cGUiOiJyZWZyZXNoIn0.8sn-hoinhHltL0dqWIj_g8A2wW1G6ba8zZeX9Y1jL9g	2026-01-16 02:40:17.869916	2026-01-23 02:10:17.869919	f	\N	\N	2026-01-16 02:10:17.87009	\N	\N	\N	\N
35	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTMxNjg0LCJpYXQiOjE3Njg1Mjk4ODQsInR5cGUiOiJhY2Nlc3MifQ.af6fey2uFkCWN0IyelfbnL-RcDcEgO_KTP1Uv2BFWwo	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTM0Njg0LCJpYXQiOjE3Njg1Mjk4ODQsInR5cGUiOiJyZWZyZXNoIn0.XiCyEX7E-r7YowhKD_HtEXvLJoBi8IwkZxTR9KhBBAM	2026-01-16 02:48:04.347555	2026-01-23 02:18:04.347557	f	\N	\N	2026-01-16 02:18:04.34795	\N	\N	\N	\N
36	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTMyMDY2LCJpYXQiOjE3Njg1MzAyNjYsInR5cGUiOiJhY2Nlc3MifQ.RSidSueYQgRsUywDxIa8NpM7fqDgFnBcyxHJLnCDqsk	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTM1MDY2LCJpYXQiOjE3Njg1MzAyNjYsInR5cGUiOiJyZWZyZXNoIn0.ARvRmRu2-Twv3HoKv9XfDYVR8ceuK8ANWWPhGZgZWuA	2026-01-16 02:54:26.597323	2026-01-23 02:24:26.597326	f	\N	\N	2026-01-16 02:24:26.599204	\N	\N	\N	\N
37	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTM0NTUxLCJpYXQiOjE3Njg1MzI3NTEsInR5cGUiOiJhY2Nlc3MifQ.vYDsT9Dc1YzWAXs-qnQ9BFK0RHhoil1G3yPii0PHX10	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTM3NTUxLCJpYXQiOjE3Njg1MzI3NTEsInR5cGUiOiJyZWZyZXNoIn0.SFpGWZDdPz8JpIsqM1VAjyDyCK2Xc22AWFrJOXgLThQ	2026-01-16 03:35:51.488584	2026-01-23 03:05:51.488585	f	\N	\N	2026-01-16 03:05:51.488929	\N	\N	\N	\N
38	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTM0NzUwLCJpYXQiOjE3Njg1MzI5NTAsInR5cGUiOiJhY2Nlc3MifQ.bYWqkGyTsPJMfy-5AgF9_4Cv9gQ1-j2AHfE9dExRqxU	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTM3NzUwLCJpYXQiOjE3Njg1MzI5NTAsInR5cGUiOiJyZWZyZXNoIn0.9gs5v8NAjfbwA7OiAl5CvW29-GwbvaBRefs801ZOh4M	2026-01-16 03:39:10.77214	2026-01-23 03:09:10.772142	f	\N	\N	2026-01-16 03:09:10.772493	\N	\N	\N	\N
39	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTM0OTM4LCJpYXQiOjE3Njg1MzMxMzgsInR5cGUiOiJhY2Nlc3MifQ.rHc51v_mRkgy5L42EetY6WE7ONzx9LsLtay6xOk0lz0	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTM3OTM4LCJpYXQiOjE3Njg1MzMxMzgsInR5cGUiOiJyZWZyZXNoIn0.N7g8xyDbDn0xqcnQjkBrABgFv0tjveHSDFcZEX1lbNA	2026-01-16 03:42:18.197284	2026-01-23 03:12:18.197286	f	\N	\N	2026-01-16 03:12:18.197641	\N	\N	\N	\N
40	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTM0OTgzLCJpYXQiOjE3Njg1MzMxODMsInR5cGUiOiJhY2Nlc3MifQ.3hSxVm6HiSzJX1xCayWkyJVLVEpLo_RbcIBj4WRY2pw	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTM3OTgzLCJpYXQiOjE3Njg1MzMxODMsInR5cGUiOiJyZWZyZXNoIn0.UFRZlfm6Rg9pp-PbRwHnqugdvBoLok49Hn6vsnP3BPQ	2026-01-16 03:43:03.88169	2026-01-23 03:13:03.881691	f	\N	\N	2026-01-16 03:13:03.882031	\N	\N	\N	\N
42	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTkzNDkwLCJpYXQiOjE3Njg1OTE2OTAsInR5cGUiOiJhY2Nlc3MifQ.p2yAPuvSe4KGHYYHGyn54AYXvqFVisT7we-8uUqJ8wc	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTk2NDkwLCJpYXQiOjE3Njg1OTE2OTAsInR5cGUiOiJyZWZyZXNoIn0.FjzRghTtBlY_jQtug_2CiUCQojm3aU-ZeTe_G2-wQvs	2026-01-16 19:58:10.416621	2026-01-23 19:28:10.416623	f	\N	\N	2026-01-16 19:28:10.417475	\N	\N	\N	\N
43	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTk0MzE4LCJpYXQiOjE3Njg1OTI1MTgsInR5cGUiOiJhY2Nlc3MifQ.1gZIPLWYUR-eRegGkPz8uLX7r5rIc5_mWlgJXRkdy8k	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTk3MzE4LCJpYXQiOjE3Njg1OTI1MTgsInR5cGUiOiJyZWZyZXNoIn0.UtfsaI54Wh9_BZRjqWB6oFyn2AoDTX47jwzIDIrs-og	2026-01-16 20:11:58.437319	2026-01-23 19:41:58.43732	f	\N	\N	2026-01-16 19:41:58.437724	\N	\N	\N	\N
44	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTk1MzU0LCJpYXQiOjE3Njg1OTM1NTQsInR5cGUiOiJhY2Nlc3MifQ.ZmYK2bENb1fW5aMoStMY80Rojg5Ei6eCl6QbLqiGFj4	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTk4MzU0LCJpYXQiOjE3Njg1OTM1NTQsInR5cGUiOiJyZWZyZXNoIn0.uXmaCpi4FLADaYwJIjL8-c_48M5CmIr8yKHZDKfbS1w	2026-01-16 20:29:14.364874	2026-01-23 19:59:14.364875	f	\N	\N	2026-01-16 19:59:14.365806	\N	\N	\N	\N
41	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTkxNzQ5LCJpYXQiOjE3Njg1ODk5NDksInR5cGUiOiJhY2Nlc3MifQ.1mzc9VRhsDjJki-etUwkxYpICWv13kgNzA6796zhf0g	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTk0NzQ5LCJpYXQiOjE3Njg1ODk5NDksInR5cGUiOiJyZWZyZXNoIn0.tG6CcSNhFTuOcwdcRZbv9z1MzAxdxdh9gLxnHd7KTV4	2026-01-16 19:29:09.869895	2026-01-23 18:59:09.869898	f	\N	\N	2026-01-16 18:59:09.870636	\N	\N	\N	\N
45	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NTk2NTkwLCJpYXQiOjE3Njg1OTQ3OTAsInR5cGUiOiJhY2Nlc3MifQ.OO4pJASDXCvWSc2mkp3faV9Hobjy-_BiMtP9_IPcqOA	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MTk5NTkwLCJpYXQiOjE3Njg1OTQ3OTAsInR5cGUiOiJyZWZyZXNoIn0.jg0_Uj2u1VSSwoqGiHCSDeOcXW6kooUOpV9exPcZths	2026-01-16 20:49:50.557042	2026-01-23 20:19:50.557046	f	\N	\N	2026-01-16 20:19:50.557755	\N	\N	\N	\N
49	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjA4NTIwLCJpYXQiOjE3Njg2MDY3MjAsInR5cGUiOiJhY2Nlc3MifQ.QXxcUL5e8ULABAMqKfrWYRyLmT1bGagUzo3IaQkBOUQ	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjExNTIwLCJpYXQiOjE3Njg2MDY3MjAsInR5cGUiOiJyZWZyZXNoIn0.pP0PQbqKU49-DhDLw8s99E-kv6DqcEx1IDceMH0mHEY	2026-01-17 00:08:40.662545	2026-01-23 23:38:40.662546	f	\N	\N	2026-01-16 23:38:40.663536	\N	\N	\N	\N
51	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjA5MDI2LCJpYXQiOjE3Njg2MDcyMjYsInR5cGUiOiJhY2Nlc3MifQ.RLeVUIDgCYuEC07UzleVL-yDdJ_CbiXdD3OU6__F6eM	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjEyMDI2LCJpYXQiOjE3Njg2MDcyMjYsInR5cGUiOiJyZWZyZXNoIn0.nl7z4wX0vlApCdMJvWoEtBkvWZ7bSKWbzJGtpEqRROk	2026-01-17 00:17:06.909807	2026-01-23 23:47:06.909809	f	\N	\N	2026-01-16 23:47:06.910014	\N	\N	\N	\N
52	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjA5MDY4LCJpYXQiOjE3Njg2MDcyNjgsInR5cGUiOiJhY2Nlc3MifQ.wjsNYObl_fPK9MwEP_qSREmGCa3JVx6AHnaE1joXmg8	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjEyMDY4LCJpYXQiOjE3Njg2MDcyNjgsInR5cGUiOiJyZWZyZXNoIn0._LWL-QukHI9uiYe_7oq5cY2zzF1x6Rb3Tj-xDo_SOOo	2026-01-17 00:17:48.481724	2026-01-23 23:47:48.481725	f	\N	\N	2026-01-16 23:47:48.48187	\N	\N	\N	\N
53	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjA5OTM4LCJpYXQiOjE3Njg2MDgxMzgsInR5cGUiOiJhY2Nlc3MifQ.2aHlLAhkYYXvvG_pJAhLtnKt5MS0dhZJ3TAfYu_d06U	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjEyOTM4LCJpYXQiOjE3Njg2MDgxMzgsInR5cGUiOiJyZWZyZXNoIn0.hj5DyHROfoDSkC01TU9w7IeHgPsrxiS1-pvOB9i5JxY	2026-01-17 00:32:18.882605	2026-01-24 00:02:18.882606	f	\N	\N	2026-01-17 00:02:18.883112	\N	\N	\N	\N
46	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjAwMDM3LCJpYXQiOjE3Njg1OTgyMzcsInR5cGUiOiJhY2Nlc3MifQ.WvR_5cyKkcKZqxvPy4cvIICthNUVwztDYYXngAcChJc	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjAzMDM3LCJpYXQiOjE3Njg1OTgyMzcsInR5cGUiOiJyZWZyZXNoIn0.Gy7F7tSkWvXp-dZ8skN5h3psJkyPejSAypu9juju21g	2026-01-16 21:47:17.52279	2026-01-23 21:17:17.522792	f	\N	\N	2026-01-16 21:17:17.523579	\N	\N	\N	\N
47	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjA1Mzg0LCJpYXQiOjE3Njg2MDM1ODQsInR5cGUiOiJhY2Nlc3MifQ.E0FSUK-EeSYJddLeQeOaGvmFh0rMSzfex2YlaUqS2mE	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjA4Mzg0LCJpYXQiOjE3Njg2MDM1ODQsInR5cGUiOiJyZWZyZXNoIn0.0sG2hW_efXBGVqM8AJ-V00oLDfaZQ2hel63FSdbO_j8	2026-01-16 23:16:24.914164	2026-01-23 22:46:24.914166	f	\N	\N	2026-01-16 22:46:24.91498	\N	\N	\N	\N
48	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjA2MDE4LCJpYXQiOjE3Njg2MDQyMTgsInR5cGUiOiJhY2Nlc3MifQ.uweI1BiCQcR5ygO7gAawel_s2IFjAZbtbd9CCr-PeLk	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjA5MDE4LCJpYXQiOjE3Njg2MDQyMTgsInR5cGUiOiJyZWZyZXNoIn0.MkcXUG895BKbDbMc1JzqqQxxCziW_eSEBY11bVHNxG0	2026-01-16 23:26:58.399846	2026-01-23 22:56:58.399848	f	\N	\N	2026-01-16 22:56:58.400709	\N	\N	\N	\N
50	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjA4NjQwLCJpYXQiOjE3Njg2MDY4NDAsInR5cGUiOiJhY2Nlc3MifQ.P5nZ1YeYPTSg1wjX6gSTLbkEnLjMmtf-y-e6i---rts	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjExNjQwLCJpYXQiOjE3Njg2MDY4NDAsInR5cGUiOiJyZWZyZXNoIn0.NIzqCm74nzwgwxEyzIM0gUnTF8uVQVEh3SDAPN-x27w	2026-01-17 00:10:40.412483	2026-01-23 23:40:40.412485	f	\N	\N	2026-01-16 23:40:40.412791	\N	\N	\N	\N
54	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjEwNzY5LCJpYXQiOjE3Njg2MDg5NjksInR5cGUiOiJhY2Nlc3MifQ.MZsxghmO0IP6w_W03R9bNBu0ny_5EOmy1fcoH18eTJg	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjEzNzY5LCJpYXQiOjE3Njg2MDg5NjksInR5cGUiOiJyZWZyZXNoIn0.NfTH-rq3YpGtWQzIKoqLr1ls3G1wKtXjdvJLbAPQ1UY	2026-01-17 00:46:09.733809	2026-01-24 00:16:09.733811	f	\N	\N	2026-01-17 00:16:09.734128	\N	\N	\N	\N
56	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjE0MDU2LCJpYXQiOjE3Njg2MTIyNTYsInR5cGUiOiJhY2Nlc3MifQ.lGLm_zMI6UqsYuOouDwBXNUdRwxJWN7jJFZ76VPEWXI	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjE3MDU2LCJpYXQiOjE3Njg2MTIyNTYsInR5cGUiOiJyZWZyZXNoIn0.ceibN9znXJWju6t7FNqZwARvuRhPH63wOhoyaVK1H2c	2026-01-17 01:40:56.848793	2026-01-24 01:10:56.848795	f	\N	\N	2026-01-17 01:10:56.849185	\N	\N	\N	\N
57	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjE1MTMyLCJpYXQiOjE3Njg2MTMzMzIsInR5cGUiOiJhY2Nlc3MifQ.EK5GMbflcPaN3lQ4jrUQ4e_CGgsnWaRgHmY-cr1Dlzs	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjE4MTMyLCJpYXQiOjE3Njg2MTMzMzIsInR5cGUiOiJyZWZyZXNoIn0.m7knT5_w52bQnyxko7M5Gg5xoMR2Ul-V-S56MEPiQRc	2026-01-17 01:58:52.985587	2026-01-24 01:28:52.985589	f	\N	\N	2026-01-17 01:28:52.986295	\N	\N	\N	\N
65	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjMxMzc2LCJpYXQiOjE3Njg2Mjk1NzYsInR5cGUiOiJhY2Nlc3MifQ.u8GgUdBzjBeu3GATGeLsVmMkINJDGcnQ9vEYHmusy0c	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjM0Mzc2LCJpYXQiOjE3Njg2Mjk1NzYsInR5cGUiOiJyZWZyZXNoIn0.QFc6yT26oJcBbOhT8d1Ji5exm5rAA3z9j7P33Iyqfcc	2026-01-17 06:29:36.288125	2026-01-24 05:59:36.288126	f	\N	\N	2026-01-17 05:59:36.288884	\N	\N	\N	\N
66	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjMxNDMzLCJpYXQiOjE3Njg2Mjk2MzMsInR5cGUiOiJhY2Nlc3MifQ.uS3NvIZCXIdl-UGW8_EzFGprGTmhRHuVmB_fYLrTaOQ	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjM0NDMzLCJpYXQiOjE3Njg2Mjk2MzMsInR5cGUiOiJyZWZyZXNoIn0.3N9TgJYuk2cD6v9_1hTIF7avOpIM98pcTtZ1OPey6yA	2026-01-17 06:30:33.736407	2026-01-24 06:00:33.736409	f	\N	\N	2026-01-17 06:00:33.736776	\N	\N	\N	\N
55	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjEyNTg0LCJpYXQiOjE3Njg2MTA3ODQsInR5cGUiOiJhY2Nlc3MifQ.klnnzyG3bjv0KT3AHgpK0C66ghBJ2mM4GdtfDtVk0H8	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjE1NTg0LCJpYXQiOjE3Njg2MTA3ODQsInR5cGUiOiJyZWZyZXNoIn0.cnW6WwIBzqjg1aA22vrn_mDb1C03scyKGUSuqt3Mexc	2026-01-17 01:16:24.329428	2026-01-24 00:46:24.329429	f	\N	\N	2026-01-17 00:46:24.329623	\N	\N	\N	\N
67	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjMxNDQ5LCJpYXQiOjE3Njg2Mjk2NDksInR5cGUiOiJhY2Nlc3MifQ.L0l5jz5x0BGI1pGtFQCp4pDM9Yvrx-LD4nETgzG4xZI	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjM0NDQ5LCJpYXQiOjE3Njg2Mjk2NDksInR5cGUiOiJyZWZyZXNoIn0.mW_kDFQla4-3ZMNWt_4Q4M58mrL_v_yr1L-SMUdwStQ	2026-01-17 06:30:49.514403	2026-01-24 06:00:49.514404	f	\N	\N	2026-01-17 06:00:49.514602	\N	\N	\N	\N
68	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjMxNzEzLCJpYXQiOjE3Njg2Mjk5MTMsInR5cGUiOiJhY2Nlc3MifQ.MDnWxKZMBIF9gQ3qCUvrQD9ElUIbsfQYLQ--keRFvxw	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjM0NzEzLCJpYXQiOjE3Njg2Mjk5MTMsInR5cGUiOiJyZWZyZXNoIn0.Sq2YBU75-U9OsdvacY1HezWrIlQ_vLLpJI0DmyDv5P8	2026-01-17 06:35:13.56746	2026-01-24 06:05:13.567461	f	\N	\N	2026-01-17 06:05:13.567875	\N	\N	\N	\N
69	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjMyNjE3LCJpYXQiOjE3Njg2MzA4MTcsInR5cGUiOiJhY2Nlc3MifQ.gpHpOwTf7gsgvy2XkpqyWBAX4tHPu1S07PNEAQ64nLA	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjM1NjE3LCJpYXQiOjE3Njg2MzA4MTcsInR5cGUiOiJyZWZyZXNoIn0.-H5rC1dQJ7_D71jCIpJiTLZSXxfV8pt3VHtWiraclsU	2026-01-17 06:50:17.708161	2026-01-24 06:20:17.708162	f	\N	\N	2026-01-17 06:20:17.708493	\N	\N	\N	\N
58	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjE3MDcxLCJpYXQiOjE3Njg2MTUyNzEsInR5cGUiOiJhY2Nlc3MifQ.WaxSdUzGKZehpCP89TjJ54eFk6oe-CeYuwpj5wWDj64	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjIwMDcxLCJpYXQiOjE3Njg2MTUyNzEsInR5cGUiOiJyZWZyZXNoIn0.kLe9WSOpLFW08DOXFd8B8WG8DifzE1-rU7Gyru0-fh4	2026-01-17 02:31:11.150885	2026-01-24 02:01:11.150886	f	\N	\N	2026-01-17 02:01:11.151324	\N	\N	\N	\N
63	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjI5MTI3LCJpYXQiOjE3Njg2MjczMjcsInR5cGUiOiJhY2Nlc3MifQ.C5mjq38T7wCnBdW51-Ij9lZAIWtva_9RT7LFIsr61eQ	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjMyMTI3LCJpYXQiOjE3Njg2MjczMjcsInR5cGUiOiJyZWZyZXNoIn0.048WNuAdWtX9N5EhTNlZrYmLdJS-Xl7CaxalGGjlVfU	2026-01-17 05:52:07.619079	2026-01-24 05:22:07.619081	f	\N	\N	2026-01-17 05:22:07.620085	\N	\N	\N	\N
70	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjczMDU2LCJpYXQiOjE3Njg2NzEyNTYsInR5cGUiOiJhY2Nlc3MifQ.mvuFxtb3gRF9H2zF0hPd4hcsvbMH_FoLigsGINy9dLw	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5Mjc2MDU2LCJpYXQiOjE3Njg2NzEyNTYsInR5cGUiOiJyZWZyZXNoIn0.Xz1zjjGxdUrem1x6OkCQ5Tuve_EgXKHWaWcJgUs7KjA	2026-01-17 18:04:16.921311	2026-01-24 17:34:16.921312	f	\N	\N	2026-01-17 17:34:16.921972	\N	\N	\N	\N
59	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjE5NDYwLCJpYXQiOjE3Njg2MTc2NjAsInR5cGUiOiJhY2Nlc3MifQ.1ldpnQHHjQYArGUvoCvcS5RKJrOX7mkB0m1gIXBEQT0	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjIyNDYwLCJpYXQiOjE3Njg2MTc2NjAsInR5cGUiOiJyZWZyZXNoIn0.o1cxKjvdCXvl4YzzUMLVbPpEHVDJgMhJ6QFjLNQeqMI	2026-01-17 03:11:00.035598	2026-01-24 02:41:00.035599	f	\N	\N	2026-01-17 02:41:00.035989	\N	\N	\N	\N
60	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjIzOTg3LCJpYXQiOjE3Njg2MjIxODcsInR5cGUiOiJhY2Nlc3MifQ.F29aT1gzbo6HEQvdn7GiXDbH_4VlxiIa56JN-pInQOc	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjI2OTg3LCJpYXQiOjE3Njg2MjIxODcsInR5cGUiOiJyZWZyZXNoIn0.TMk61T0Eig2K-VbponEHpXIlBA02V50krkd6aaTexBs	2026-01-17 04:26:27.106148	2026-01-24 03:56:27.10615	f	\N	\N	2026-01-17 03:56:27.106902	\N	\N	\N	\N
61	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjI0Njk2LCJpYXQiOjE3Njg2MjI4OTYsInR5cGUiOiJhY2Nlc3MifQ.wv0A6s1f3SkEKKaUHH4bbXdNdhv2bw-QSJ6c7HtSgDg	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjI3Njk2LCJpYXQiOjE3Njg2MjI4OTYsInR5cGUiOiJyZWZyZXNoIn0.aP4dNNvW9gIyM4GrMbQrA-SKXIPE-MLK7spDRRxZASk	2026-01-17 04:38:16.602515	2026-01-24 04:08:16.602518	f	\N	\N	2026-01-17 04:08:16.602909	\N	\N	\N	\N
62	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjI2Njc4LCJpYXQiOjE3Njg2MjQ4NzgsInR5cGUiOiJhY2Nlc3MifQ.wMW8ulmMGuz5jv14I79oFegMWGibwZ1JHZwNrucguM8	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjI5Njc4LCJpYXQiOjE3Njg2MjQ4NzgsInR5cGUiOiJyZWZyZXNoIn0.9jTrHMXql7D_zBF3AQEwfI8lLqEMuenjQR3VZgqUcJE	2026-01-17 05:11:18.557982	2026-01-24 04:41:18.557984	f	\N	\N	2026-01-17 04:41:18.558706	\N	\N	\N	\N
64	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjI5Mzk0LCJpYXQiOjE3Njg2Mjc1OTQsInR5cGUiOiJhY2Nlc3MifQ.5jjo5a2XkeOv6LBgcQK_gPT7IseOoU0W4y7O8K1g_c0	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjMyMzk0LCJpYXQiOjE3Njg2Mjc1OTQsInR5cGUiOiJyZWZyZXNoIn0.E_2N4DiwZWdT5RHFeR3KeHDnMWhYDL_51hVf9Skq0go	2026-01-17 05:56:34.047053	2026-01-24 05:26:34.047055	f	\N	\N	2026-01-17 05:26:34.047422	\N	\N	\N	\N
75	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjgyMjcwLCJpYXQiOjE3Njg2ODA0NzAsInR5cGUiOiJhY2Nlc3MifQ.rdjtSl0nlkS5AaRUKJblotvFLE0HphZG3gxoO5OaR2U	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5Mjg1MjcwLCJpYXQiOjE3Njg2ODA0NzAsInR5cGUiOiJyZWZyZXNoIn0.1Mz_KrpCrzwIgJ8wEjdyWe9lWMaoEgi8m5TN3gJ8x_c	2026-01-17 20:37:50.345814	2026-01-24 20:07:50.345816	f	\N	\N	2026-01-17 20:07:50.346131	\N	\N	\N	\N
71	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4Njc2NzMyLCJpYXQiOjE3Njg2NzQ5MzIsInR5cGUiOiJhY2Nlc3MifQ.fmuIsDXvr5JlESQsobtDduqLb-oS75DMViSideSinN0	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5Mjc5NzMyLCJpYXQiOjE3Njg2NzQ5MzIsInR5cGUiOiJyZWZyZXNoIn0.yjYioaOYa_eCVBTGxveLw54gqUrFM5ZgTfcYPTHh6gk	2026-01-17 19:05:32.924007	2026-01-24 18:35:32.924009	f	\N	\N	2026-01-17 18:35:32.924291	\N	\N	\N	\N
76	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjgyOTkzLCJpYXQiOjE3Njg2ODExOTMsInR5cGUiOiJhY2Nlc3MifQ.mIKpZENOd_gorcn92pst6c-LSqcukSy9r7Y1UrEAGSE	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5Mjg1OTkzLCJpYXQiOjE3Njg2ODExOTMsInR5cGUiOiJyZWZyZXNoIn0.fd8wQpiuWxG-gveP4_ERTLryxksJgtSth4Ujshdcgvc	2026-01-17 20:49:53.492769	2026-01-24 20:19:53.49277	f	\N	\N	2026-01-17 20:19:53.493032	\N	\N	\N	\N
72	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4Njc5NTg5LCJpYXQiOjE3Njg2Nzc3ODksInR5cGUiOiJhY2Nlc3MifQ.ddt9nX-6c5iJRFlbzs3hPhVvgaqEP19xVkjbvfWTDQM	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MjgyNTg5LCJpYXQiOjE3Njg2Nzc3ODksInR5cGUiOiJyZWZyZXNoIn0.5fyxQryz55NJfQcgpzPI_hw8GurJtspNyva2Ip1GEr4	2026-01-17 19:53:09.657853	2026-01-24 19:23:09.657854	f	\N	\N	2026-01-17 19:23:09.658106	\N	\N	\N	\N
73	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjgxOTIwLCJpYXQiOjE3Njg2ODAxMjAsInR5cGUiOiJhY2Nlc3MifQ.akcNyfsO_5_KkcxaJw3BMYERgxUTBHhSqqvdoHPP_z8	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5Mjg0OTIwLCJpYXQiOjE3Njg2ODAxMjAsInR5cGUiOiJyZWZyZXNoIn0.a-6Onqm4Xozo7OWcC4inhu5702Nk-m8F-qqQ_lNg47c	2026-01-17 20:32:00.033837	2026-01-24 20:02:00.033838	f	\N	\N	2026-01-17 20:02:00.034655	\N	\N	\N	\N
74	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjgxOTU4LCJpYXQiOjE3Njg2ODAxNTgsInR5cGUiOiJhY2Nlc3MifQ.q222kTNGdcEqo6xb4j9fYUR3EX8MQEcXkHeKSu80GGM	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5Mjg0OTU4LCJpYXQiOjE3Njg2ODAxNTgsInR5cGUiOiJyZWZyZXNoIn0.wmrakJ6d1LOTFURCW6ZHy7_kcFptrhW7pzZ116F-vJw	2026-01-17 20:32:38.0484	2026-01-24 20:02:38.048403	f	\N	\N	2026-01-17 20:02:38.048561	\N	\N	\N	\N
77	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NjgzNDgyLCJpYXQiOjE3Njg2ODE2ODIsInR5cGUiOiJhY2Nlc3MifQ.xMcLAxDZIXrmaKw9BnFI_QOhY8Ml5DtJPLyUVKEfx8E	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5Mjg2NDgyLCJpYXQiOjE3Njg2ODE2ODIsInR5cGUiOiJyZWZyZXNoIn0.1xhL4qxLzV1bJCZU4jjbKBXACJqlBBJAb5NYd4M5tI8	2026-01-17 20:58:02.96024	2026-01-24 20:28:02.960242	f	\N	\N	2026-01-17 20:28:02.960817	\N	\N	\N	\N
78	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4Njg1Njk2LCJpYXQiOjE3Njg2ODM4OTYsInR5cGUiOiJhY2Nlc3MifQ.B3Zs6TKYVDNXNY7OCvL-qhIDDQbAvNiUNfIWGSkDV60	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5Mjg4Njk2LCJpYXQiOjE3Njg2ODM4OTYsInR5cGUiOiJyZWZyZXNoIn0.gi_kzLZXP3qD7Ms9KiE0GoV5M94456p57ceqja0eHOY	2026-01-17 21:34:56.352008	2026-01-24 21:04:56.352009	f	\N	\N	2026-01-17 21:04:56.352271	\N	\N	\N	\N
79	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NzE2MTcxLCJpYXQiOjE3Njg3MTQzNzEsInR5cGUiOiJhY2Nlc3MifQ.iyXD9ubvFsO0H8SRq7Zu6p22M11-4Xoru5ln_BYRJp0	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MzE5MTcxLCJpYXQiOjE3Njg3MTQzNzEsInR5cGUiOiJyZWZyZXNoIn0.iZ9JlbwjlkefHr5xeJ9Un2ggiXgIxZCxgiXDA9tprjU	2026-01-18 06:02:51.637775	2026-01-25 05:32:51.637777	f	\N	\N	2026-01-18 05:32:51.638502	\N	\N	\N	\N
80	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NzE3MDY1LCJpYXQiOjE3Njg3MTUyNjUsInR5cGUiOiJhY2Nlc3MifQ.7PLbMgN1kzcLHw7LnrXJlcEv9-s3k3KsbMGtkjyc0RM	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MzIwMDY1LCJpYXQiOjE3Njg3MTUyNjUsInR5cGUiOiJyZWZyZXNoIn0.X9WAmqKZyDe-ZAco226TjzWD5WqqMwUeI9YhPx3DCu4	2026-01-18 06:17:45.658126	2026-01-25 05:47:45.658128	f	\N	\N	2026-01-18 05:47:45.658652	\N	\N	\N	\N
81	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NzE3MjE0LCJpYXQiOjE3Njg3MTU0MTQsInR5cGUiOiJhY2Nlc3MifQ.k4R-5KFYBlGUk1aTsaSZ05vb_KWemCXDyQFNZcHfft0	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MzIwMjE0LCJpYXQiOjE3Njg3MTU0MTQsInR5cGUiOiJyZWZyZXNoIn0._4C1rEeRHKD3oYPGLZ2Wril6J9edrSrXyyNS-JQL-iE	2026-01-18 06:20:14.030918	2026-01-25 05:50:14.030919	f	\N	\N	2026-01-18 05:50:14.031092	\N	\N	\N	\N
82	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NzE3Mzk0LCJpYXQiOjE3Njg3MTU1OTQsInR5cGUiOiJhY2Nlc3MifQ.tKvtv28yqvox915HaQURuDSQIX4Jj_jKsLpt_5j499U	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MzIwMzk0LCJpYXQiOjE3Njg3MTU1OTQsInR5cGUiOiJyZWZyZXNoIn0.6DJetRHgtG_CoYqtMIfglFsLvR_6mjw9wc3Z1CJYK7Y	2026-01-18 06:23:14.667548	2026-01-25 05:53:14.667549	f	\N	\N	2026-01-18 05:53:14.667854	\N	\N	\N	\N
83	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NzE5ODEyLCJpYXQiOjE3Njg3MTgwMTIsInR5cGUiOiJhY2Nlc3MifQ.pSMgWSsdzt9xziCycmphZdRJd-dcJ0ArqqOdvHNnag4	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MzIyODEyLCJpYXQiOjE3Njg3MTgwMTIsInR5cGUiOiJyZWZyZXNoIn0.jUTDlNV0OYf8Dc34lcDZhKGaPnzfRCQVOhGdJC0Yasw	2026-01-18 07:03:32.602336	2026-01-25 06:33:32.602338	f	\N	\N	2026-01-18 06:33:32.602677	\N	\N	\N	\N
87	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NzIxMzI1LCJpYXQiOjE3Njg3MTk1MjUsInR5cGUiOiJhY2Nlc3MifQ.k6G5HQCQINVe0zWSiu7gVNP-sLAl9fQBLCofrVx9jBQ	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MzI0MzI1LCJpYXQiOjE3Njg3MTk1MjUsInR5cGUiOiJyZWZyZXNoIn0.gCSNO1sAD81AxRD8YZ754qtgLR3841fmUhHeqqyFWv4	2026-01-18 07:28:45.314988	2026-01-25 06:58:45.31499	f	\N	\N	2026-01-18 06:58:45.315227	\N	\N	\N	\N
85	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NzIwOTc4LCJpYXQiOjE3Njg3MTkxNzgsInR5cGUiOiJhY2Nlc3MifQ.J5XS74DQGVcGm9T8VYUmNIxnLCs3H8-mRSkUlqnfJ3I	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MzIzOTc4LCJpYXQiOjE3Njg3MTkxNzgsInR5cGUiOiJyZWZyZXNoIn0.m_ssDVFa_CUQgkeHnwrBF3FTWy1ujDIuiFJ5FWFKjNc	2026-01-18 07:22:58.397795	2026-01-25 06:52:58.397797	f	\N	\N	2026-01-18 06:52:58.398742	\N	\N	\N	\N
86	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NzIxMDYwLCJpYXQiOjE3Njg3MTkyNjAsInR5cGUiOiJhY2Nlc3MifQ.Tzdj2Pys-dSkZTSLVtbdqp_lLoc3FUT7CxX6tYCC-ZQ	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MzI0MDYwLCJpYXQiOjE3Njg3MTkyNjAsInR5cGUiOiJyZWZyZXNoIn0.Czxc622q214r8C5aqoOmotuoUpLIqUzNydFVo-LvLMM	2026-01-18 07:24:20.75504	2026-01-25 06:54:20.755043	f	\N	\N	2026-01-18 06:54:20.755228	\N	\N	\N	\N
89	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NzIyMzk5LCJpYXQiOjE3Njg3MjA1OTksInR5cGUiOiJhY2Nlc3MifQ.HMEao09NAHhOCaijc19FtCHNikQ4yQLXfTtV7vDjGWQ	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MzI1Mzk5LCJpYXQiOjE3Njg3MjA1OTksInR5cGUiOiJyZWZyZXNoIn0.YWShfxiv-3gKbf7UdvKMxAORmyQlAiUoiGxTSRoB32c	2026-01-18 07:46:39.470044	2026-01-25 07:16:39.470046	f	\N	\N	2026-01-18 07:16:39.470287	\N	\N	\N	\N
84	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NzE5OTEyLCJpYXQiOjE3Njg3MTgxMTIsInR5cGUiOiJhY2Nlc3MifQ.Xb-ATDvYrKDP4O64Zyr-fo_HBmr4KKPhhzewmiQlpOc	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MzIyOTEyLCJpYXQiOjE3Njg3MTgxMTIsInR5cGUiOiJyZWZyZXNoIn0.E9dER_-GTm3ypV2DI-r165DvHY6I7mvxUS20kCCvOQA	2026-01-18 07:05:12.185352	2026-01-25 06:35:12.185354	f	\N	\N	2026-01-18 06:35:12.185664	\N	\N	\N	\N
88	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NzIxODQ2LCJpYXQiOjE3Njg3MjAwNDYsInR5cGUiOiJhY2Nlc3MifQ.yN-tfqXinK2eEVTq6DMJhAsCgZvB3GrT0APrCPUqJKg	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MzI0ODQ2LCJpYXQiOjE3Njg3MjAwNDYsInR5cGUiOiJyZWZyZXNoIn0.Lx5IYO4WexQlE5mACpNLtW584xIxDpITkU-c3mjTU2U	2026-01-18 07:37:26.669678	2026-01-25 07:07:26.66968	f	\N	\N	2026-01-18 07:07:26.670146	\N	\N	\N	\N
90	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NzYzMzQ2LCJpYXQiOjE3Njg3NjE1NDYsInR5cGUiOiJhY2Nlc3MifQ.k1Fs-joQuagEK5OXO1ybyBlmJXyOgnM3R5adKNEyrio	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MzY2MzQ2LCJpYXQiOjE3Njg3NjE1NDYsInR5cGUiOiJyZWZyZXNoIn0.yHbNUTnRDIfo15PFmbSCs9mxltfvwVsPb-UseAIwHQ8	2026-01-18 19:09:06.31541	2026-01-25 18:39:06.315412	f	\N	\N	2026-01-18 18:39:06.31612	\N	\N	\N	\N
91	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NzYzNDQzLCJpYXQiOjE3Njg3NjE2NDMsInR5cGUiOiJhY2Nlc3MifQ.svS6wyHvmxAOLzqMBhXE64iKd1c7UZsBcWJqe4wNiSk	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MzY2NDQzLCJpYXQiOjE3Njg3NjE2NDMsInR5cGUiOiJyZWZyZXNoIn0.rLIzen1G-vcoVc_C1TO4gJK1cR-qCI_yOftWpp9DAJM	2026-01-18 19:10:43.816699	2026-01-25 18:40:43.816702	f	\N	\N	2026-01-18 18:40:43.817254	\N	\N	\N	\N
92	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4NzY1NjI5LCJpYXQiOjE3Njg3NjM4MjksInR5cGUiOiJhY2Nlc3MifQ.1YB8ZAmiuutT9G9VRghETAsbv6HnOivTG7lAmVFDtgg	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5MzY4NjI5LCJpYXQiOjE3Njg3NjM4MjksInR5cGUiOiJyZWZyZXNoIn0.Z7oGkzcbp_waa-XIh6Vi6tF4Mp7BKBC07qTpj6E7ydU	2026-01-18 19:47:09.910372	2026-01-25 19:17:09.910373	f	\N	\N	2026-01-18 19:17:09.91083	\N	\N	\N	\N
93	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4Nzk2MTU5LCJpYXQiOjE3Njg3OTQzNTksInR5cGUiOiJhY2Nlc3MifQ.qborbJRbAuC8R4NFYOqx61J4u8nE4a16sBoOC1SkAns	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5Mzk5MTU5LCJpYXQiOjE3Njg3OTQzNTksInR5cGUiOiJyZWZyZXNoIn0.fMA9eZaf4VmVjtQE_-1IZZWx7XqJlGlz7TN96V6YchQ	2026-01-19 04:15:59.776343	2026-01-26 03:45:59.776345	f	\N	\N	2026-01-19 03:45:59.777036	\N	\N	\N	\N
94	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4Nzk2MjcxLCJpYXQiOjE3Njg3OTQ0NzEsInR5cGUiOiJhY2Nlc3MifQ.Gfdat7JX7OEjf2_OlfUUyqv9mGbX3FKSYTD8DlyWfWE	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5Mzk5MjcxLCJpYXQiOjE3Njg3OTQ0NzEsInR5cGUiOiJyZWZyZXNoIn0.q94q6yUWJ5d1G0NZ0vfyw8wKmg0QoXWeyeGJj3KEh2I	2026-01-19 04:17:51.447171	2026-01-26 03:47:51.447173	f	\N	\N	2026-01-19 03:47:51.447461	\N	\N	\N	\N
95	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4Nzk4ODM0LCJpYXQiOjE3Njg3OTcwMzQsInR5cGUiOiJhY2Nlc3MifQ.eEBmTciwZpbXbq6c-8QqWb6bFJuv6vvGip2mt9952ws	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDAxODM0LCJpYXQiOjE3Njg3OTcwMzQsInR5cGUiOiJyZWZyZXNoIn0.HLOV8b-J6w5MeWMbPYh4gk2VQ7PXI2ZRR7-TQvNswv4	2026-01-19 05:00:34.058725	2026-01-26 04:30:34.058727	f	\N	\N	2026-01-19 04:30:34.059363	\N	\N	\N	\N
96	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4Nzk4ODg1LCJpYXQiOjE3Njg3OTcwODUsInR5cGUiOiJhY2Nlc3MifQ.S725VvPfmrLe5tZQXu3091Ys2S-1k4VH_q5A6uhdfG0	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDAxODg1LCJpYXQiOjE3Njg3OTcwODUsInR5cGUiOiJyZWZyZXNoIn0.w-PO7Pmn9NegcdAhdH1Oeaw-j3eV4mL0TfMwZGH0f9Y	2026-01-19 05:01:25.771149	2026-01-26 04:31:25.771151	f	\N	\N	2026-01-19 04:31:25.771512	\N	\N	\N	\N
97	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODAwNzk5LCJpYXQiOjE3Njg3OTg5OTksInR5cGUiOiJhY2Nlc3MifQ.zJ3vLwjfkdcDwNP7tBOpT9ZqKDxfGqIw90XJ52eDKJQ	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDAzNzk5LCJpYXQiOjE3Njg3OTg5OTksInR5cGUiOiJyZWZyZXNoIn0._polSBSfMhhnfktRXWR709Q0aHzpcFlyz5igR1g5xdM	2026-01-19 05:33:19.324545	2026-01-26 05:03:19.324547	f	\N	\N	2026-01-19 05:03:19.324809	\N	\N	\N	\N
98	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODAxNjQyLCJpYXQiOjE3Njg3OTk4NDIsInR5cGUiOiJhY2Nlc3MifQ.d_lw07S1I_0QrZc3gbBgN7hGnCfvTN9upfwD8wRKAOU	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA0NjQyLCJpYXQiOjE3Njg3OTk4NDIsInR5cGUiOiJyZWZyZXNoIn0.jPjbpiHM-tMwa1DzrcYTnt-FoS1HIveUeVqh7k0jPyw	2026-01-19 05:47:22.973299	2026-01-26 05:17:22.973301	f	\N	\N	2026-01-19 05:17:22.973989	\N	\N	\N	\N
99	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODAyNDU5LCJpYXQiOjE3Njg4MDA2NTksInR5cGUiOiJhY2Nlc3MifQ.a75GlaHmRCwNalDR_PSOA6FLJDA6N6EsfVGxSAwk4n0	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA1NDU5LCJpYXQiOjE3Njg4MDA2NTksInR5cGUiOiJyZWZyZXNoIn0.cUZxCYYR40mHOHR5SlUXj7wFH21lA_o0nusfqPah6uc	2026-01-19 06:00:59.958805	2026-01-26 05:30:59.958806	f	\N	\N	2026-01-19 05:30:59.959458	\N	\N	\N	\N
100	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODAzNDE0LCJpYXQiOjE3Njg4MDE2MTQsInR5cGUiOiJhY2Nlc3MifQ.Or5XzGcqqsxag1-IslK3Dl2NtoIFOfWxz6ZV0L1mN20	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA2NDE0LCJpYXQiOjE3Njg4MDE2MTQsInR5cGUiOiJyZWZyZXNoIn0.Jr9v38uttDQeZ9yFT1OZrsRUytqTs4WMre6V4jBiaeU	2026-01-19 06:16:54.512543	2026-01-26 05:46:54.512544	f	\N	\N	2026-01-19 05:46:54.51351	\N	\N	\N	\N
102	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODA0MDAwLCJpYXQiOjE3Njg4MDIyMDAsInR5cGUiOiJhY2Nlc3MifQ.2UaSQsGvnCQfdFeum1NU6b7jxZ9qSOAQjzdYKwU74a0	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA3MDAwLCJpYXQiOjE3Njg4MDIyMDAsInR5cGUiOiJyZWZyZXNoIn0.PtIww20vQQGOAXbH3ruZ1aRgniVmztKaoHB4rho74iY	2026-01-19 06:26:40.593887	2026-01-26 05:56:40.593889	f	\N	\N	2026-01-19 05:56:40.594222	\N	\N	\N	\N
101	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODAzNTU3LCJpYXQiOjE3Njg4MDE3NTcsInR5cGUiOiJhY2Nlc3MifQ.fPwYMilTHR2HgDn_1IEaIGIQiGDXNF5XzzFkA1SwXQU	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA2NTU3LCJpYXQiOjE3Njg4MDE3NTcsInR5cGUiOiJyZWZyZXNoIn0.U__DSvt8PU2IQLAaReQCiyVyCp6yxPJrQgbiNkgLTIU	2026-01-19 06:19:17.146105	2026-01-26 05:49:17.146106	f	\N	\N	2026-01-19 05:49:17.146493	\N	\N	\N	\N
103	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODA0MDEwLCJpYXQiOjE3Njg4MDIyMTAsInR5cGUiOiJhY2Nlc3MifQ.2KHSXdz-OSEDdp7Lhs8POolRSUjzpQtMytrDZtqRyOo	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA3MDEwLCJpYXQiOjE3Njg4MDIyMTAsInR5cGUiOiJyZWZyZXNoIn0.ztnKb5ZXUGH7yitCnelKLMdcH-rKMsNtpdZToDrmdMY	2026-01-19 06:26:50.609069	2026-01-26 05:56:50.60907	f	\N	\N	2026-01-19 05:56:50.609265	\N	\N	\N	\N
106	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODA0NDc0LCJpYXQiOjE3Njg4MDI2NzQsInR5cGUiOiJhY2Nlc3MifQ.X_Q01opECYQ42mIYYiSz2R0hKZ8-9tDEyWAbisF09VA	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA3NDc0LCJpYXQiOjE3Njg4MDI2NzQsInR5cGUiOiJyZWZyZXNoIn0.7W__RMf5F6VlFzflsF71z2JE85W0mZcg9dNPl7sLHLw	2026-01-19 06:34:34.520396	2026-01-26 06:04:34.520397	f	\N	\N	2026-01-19 06:04:34.520756	\N	\N	\N	\N
107	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODA0NTcxLCJpYXQiOjE3Njg4MDI3NzEsInR5cGUiOiJhY2Nlc3MifQ.NnkQxFzf7A5hoU2PLXGpKXtpbuILY-st14E4vCpmo6Y	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA3NTcxLCJpYXQiOjE3Njg4MDI3NzEsInR5cGUiOiJyZWZyZXNoIn0.2jihaSGVoxibzadRfBGDieaK7Xzmw5KAH5f_87Q_DDo	2026-01-19 06:36:11.535891	2026-01-26 06:06:11.535893	f	\N	\N	2026-01-19 06:06:11.536071	\N	\N	\N	\N
104	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODA0MDE4LCJpYXQiOjE3Njg4MDIyMTgsInR5cGUiOiJhY2Nlc3MifQ.4YgZzXrQWetVyRNVhJhqQ7xFI7Yr-W1fhHNVW4LF5_M	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA3MDE4LCJpYXQiOjE3Njg4MDIyMTgsInR5cGUiOiJyZWZyZXNoIn0.JK9GPmOZD49M7pM_wZu_8OUPfIuXFmTW17xA_wnlx2o	2026-01-19 06:26:58.63938	2026-01-26 05:56:58.639381	f	\N	\N	2026-01-19 05:56:58.639638	\N	\N	\N	\N
105	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODA0MzIxLCJpYXQiOjE3Njg4MDI1MjEsInR5cGUiOiJhY2Nlc3MifQ.28-3EXpvRKmU_I4wYpb6qV2AIxAaKdY-6nlkO0QvAB8	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA3MzIxLCJpYXQiOjE3Njg4MDI1MjEsInR5cGUiOiJyZWZyZXNoIn0.qMYWsI14DFj6F8ZdZu1ASAIljkR9giHnYljsGuzzrQ0	2026-01-19 06:32:01.815456	2026-01-26 06:02:01.815458	f	\N	\N	2026-01-19 06:02:01.815864	\N	\N	\N	\N
112	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODA1Nzc5LCJpYXQiOjE3Njg4MDM5NzksInR5cGUiOiJhY2Nlc3MifQ.1we51S53WWxx5B6BiQRHKN-om6ujOtUN9sNMymoWQjY	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA4Nzc5LCJpYXQiOjE3Njg4MDM5NzksInR5cGUiOiJyZWZyZXNoIn0.LkitBUHJY2opGwIzJ34_m4qs5Vt_rn_79REr_LHegyg	2026-01-19 06:56:19.04755	2026-01-26 06:26:19.047552	t	\N	\N	2026-01-19 06:26:19.04787	\N	\N	\N	\N
109	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODA0NzcwLCJpYXQiOjE3Njg4MDI5NzAsInR5cGUiOiJhY2Nlc3MifQ.GNo8rnsbsoheOZiXsveJ-p_-hAxEbHWQkZIHOLQ-G2Y	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA3NzcwLCJpYXQiOjE3Njg4MDI5NzAsInR5cGUiOiJyZWZyZXNoIn0.24estnfjPzTHz2gaSf-dhnPsCeqjLQmi4FVA5BNuA-M	2026-01-19 06:39:30.255703	2026-01-26 06:09:30.255704	t	\N	\N	2026-01-19 06:09:30.255862	\N	\N	\N	\N
111	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODA1MjgxLCJpYXQiOjE3Njg4MDM0ODEsInR5cGUiOiJhY2Nlc3MifQ.8ChVw9umj-eGpdnuvOJGMC2vKJ_jDeV04SqsTpGJcjM	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA4MjgxLCJpYXQiOjE3Njg4MDM0ODEsInR5cGUiOiJyZWZyZXNoIn0.0RhBjFNRjZI5oXLYtVw28LMJUoKmK_dGEdXYu9XICdI	2026-01-19 06:48:01.896806	2026-01-26 06:18:01.896807	t	\N	\N	2026-01-19 06:18:01.89714	\N	\N	\N	\N
110	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODA0OTg1LCJpYXQiOjE3Njg4MDMxODUsInR5cGUiOiJhY2Nlc3MifQ.2Q4du8QTd3CdoziEpPuBVDhOjE3EPGMsShL5K_EJcnM	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA3OTg1LCJpYXQiOjE3Njg4MDMxODUsInR5cGUiOiJyZWZyZXNoIn0.TF9eZ9SnFr5ElHmgZrpjLLC8wuYCbw-GbIwtsWitTnE	2026-01-19 06:43:05.885335	2026-01-26 06:13:05.885337	f	\N	\N	2026-01-19 06:13:05.885713	\N	\N	\N	\N
113	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODA2MDU0LCJpYXQiOjE3Njg4MDQyNTQsInR5cGUiOiJhY2Nlc3MifQ.zNdcoRUUx58BS4Jve3cdoc0jSr9QbXSejui23Dc7g3Y	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA5MDU0LCJpYXQiOjE3Njg4MDQyNTQsInR5cGUiOiJyZWZyZXNoIn0.8FXFvx51xlm8-QyJ0BoZCY5S7zOWDZBGC4jya61T5kI	2026-01-19 07:00:54.917005	2026-01-26 06:30:54.917007	t	\N	\N	2026-01-19 06:30:54.917383	\N	\N	\N	\N
108	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODA0NzY0LCJpYXQiOjE3Njg4MDI5NjQsInR5cGUiOiJhY2Nlc3MifQ.TnnR2jT4w2hCoXVWFcasq2s7yRFZ2q6RagwhNMde96Q	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDA3NzY0LCJpYXQiOjE3Njg4MDI5NjQsInR5cGUiOiJyZWZyZXNoIn0.tHunEKRNtDQBvEPUdHPAxcy9yDqVKLqXQvFZNLls0is	2026-01-19 06:39:24.131536	2026-01-26 06:09:24.131537	f	\N	\N	2026-01-19 06:09:24.131917	\N	\N	\N	\N
114	2	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY4ODI2MTg2LCJpYXQiOjE3Njg4MjQzODYsInR5cGUiOiJhY2Nlc3MifQ.g8heS_VQR0COtNN4ryHJz8y0mZONPeToa4qJ5hQCkIY	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjIsInRpcG9fYXV0aCI6ImxvY2FsIiwiZXhwIjoxNzY5NDI5MTg2LCJpYXQiOjE3Njg4MjQzODYsInR5cGUiOiJyZWZyZXNoIn0._uDafdXZlvOpYWL923HaTracSd81McD5rXEAiIEwBPQ	2026-01-19 12:36:26.526708	2026-01-26 12:06:26.52671	t	\N	\N	2026-01-19 12:06:26.527741	\N	\N	\N	\N
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usuarios (id, nombre_usuario, email, nombre_completo, contrasena_hash, tipo_autenticacion, id_externo, activo, es_superusuario, fecha_creacion, fecha_actualizacion, ultimo_acceso, ultimo_cambio_contrasena, intentos_login_fallidos, fecha_bloqueo, requiere_cambio_contrasena, telefono, departamento, cargo, reset_token, reset_token_expira) FROM stdin;
2	admin	jeissonjaviercm@gmail.com		$2b$12$kjOepGNVpCImjFHcgSMFNOK9lk3C/QDqfdfM0sqoYGz.zgSRZ8Svm	local	\N	t	t	2026-01-15 20:00:28.09199	2026-01-19 12:06:26.515319	2026-01-19 12:06:26.513743	\N	0	\N	f	\N	\N	\N	\N	\N
\.


--
-- Data for Name: usuarios_roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usuarios_roles (usuario_id, rol_id, fecha_asignacion) FROM stdin;
\.


--
-- Data for Name: categoria_analisis_senal; Type: TABLE DATA; Schema: sds; Owner: -
--

COPY sds.categoria_analisis_senal (id_categoria_analisis_senal, nombre_categoria_analisis, descripcion_categoria_analisis) FROM stdin;
2	Violencia política	Categoría relacionada con violencia por motivaciones político-sociales
3	Violencias digitales basadas en género	Categoría relacionada con violencias contra mujeres en entornos digitales
1	Reclutamiento, uso y utilización de niños y adolescentes s	Categoría relacionada con vulneraciones contra NNA en contexto de conflicto
\.


--
-- Data for Name: categoria_observacion; Type: TABLE DATA; Schema: sds; Owner: -
--

COPY sds.categoria_observacion (id_categoria_observacion, id_parent_categoria_observacion, codigo_categoria_observacion, nombre_categoria_observacion, descripcion_categoria_observacion, nivel, peso_categoria_observacion) FROM stdin;
1	\N	Actores	Actores	Cuentas involucradas en la conversación.	1	20.00
2	\N	Dinamica	Dinámica	Evolución de la conversación en el tiempo.	1	20.00
3	\N	Contenido	Contenido	Narrativas implicadas y su posible impacto.	1	20.00
4	\N	Expansion	Expansión	Movimiento y extensión de los discursos.	1	20.00
5	\N	Impacto	Impacto	Posibles consecuencias de la conversación.	1	20.00
11	1	Actores_1	Involucramiento de figuras públicas	Participación de figuras públicas tradicionales.	2	100.00
12	1	Actores_2	Participación de influencers	Participación de personalidades con influencia.	2	100.00
13	1	Actores_3	Participación de partes neutrales	Cambio en participación de audiencias neutrales.	2	100.00
14	1	Actores_4	Cubrimiento en medios	Presencia en medios tradicionales o digitales.	2	100.00
21	2	Dinamica_1	Duración	Tiempo que la conversación ha estado activa.	2	100.00
22	2	Dinamica_2	Patrón de crecimiento	Cómo crece o evoluciona la conversación.	2	100.00
23	2	Dinamica_3	Señales de coordinación	Esfuerzos organizados o campañas.	2	100.00
31	3	Contenido_1	Tipo de contenido	Naturaleza del contenido y narrativas.	2	100.00
32	3	Contenido_2	Intencionalidad discursiva	Objetivo o intención del discurso.	2	100.00
41	4	Expansion_1	Amplificación	Cómo los contenidos se expanden.	2	100.00
42	4	Expansion_2	Alcance	Qué tan lejos ha llegado la conversación.	2	100.00
43	4	Expansion_3	Plataformas involucradas	Número y tipo de plataformas.	2	100.00
51	5	Impacto_1	Potencial de daño	Posibilidad de daños concretos.	2	100.00
52	5	Impacto_2	Intensidad de interacciones negativas	Nivel de agresividad.	2	100.00
53	5	Impacto_3	Divulgación de datos personales	Implicaciones de divulgación.	2	100.00
54	5	Impacto_4	Capacidad de movilización	Potencial de generar acciones colectivas.	2	100.00
\.


--
-- Data for Name: categoria_senal; Type: TABLE DATA; Schema: sds; Owner: -
--

COPY sds.categoria_senal (id_categoria_senales, id_parent_categoria_senales, nombre_categoria_senal, descripcion_categoria_senal, nivel) FROM stdin;
4	2	Rojo	Amenazas significativas que requieren atención urgente.	2
5	2	Amarillo	Riesgos potenciales que pueden escalar.	2
6	2	Verde	Problemas menores que no requieren acción inmediata.	2
1	\N	Problemas menores	Entramado de interacciones digitales desafiantes o controversiales que no constituyen amenaza o riesgo de violación a DDHH.	1
2	\N	Riesgos potenciales	Señales de advertencia sobre situaciones emergentes que indican riesgo de vulneración de DDHH.	1
3	\N	Amenazas significativas	Señales de eventos de alta complejidad que constituyen amenaza inmediata contra vida, integridad, libertad o seguridad.	1
\.


--
-- Data for Name: conducta_vulneratoria; Type: TABLE DATA; Schema: sds; Owner: -
--

COPY sds.conducta_vulneratoria (id_conducta_vulneratorias, id_categoria_analisis_senal, nombre_conducta_vulneratoria, definicion_conducta_vulneratoria, peso_conducta_vulneratoria) FROM stdin;
4	1	Vinculación	Cualquier forma de relacionamiento, acercamiento, aproximación a los niños, niñas y adolescentes para cumplir cualquier tipo de rol dentro o a favor de un GAO, GDO o GAOR.	100.00
2	1	Utilizaciónes	Participación indirecta de niños, niñas y adolescentes en toda forma de vinculación, permanente u ocasional, con grupos armados organizados o grupos delincuenciales sin necesariamente ser separados de su entorno familiar y comunitario.	100.00
1	1	Reclutamientos	Comprende todas aquellas prácticas o comportamientos de quienes promuevan, induzcan, faciliten, financien o colaboren para que los niños, niñas y adolescentes participen en cualquier actividad ilegal de los grupos armados organizados o grupos delictivos organizados.	100.00
3	1	Uso	Comprende todas aquellas prácticas o comportamientos de quienes promuevan, induzcan, faciliten, financien o colaboren para que los niños, niñas y adolescentes participen en cualquier actividad ilegal de los grupos armados organizados o grupos delictivos organizados.	100.00
\.


--
-- Data for Name: emoticon; Type: TABLE DATA; Schema: sds; Owner: -
--

COPY sds.emoticon (id_emoticon, id_categoria_analisis_senal, tipo_emoticon, peso_emoticon) FROM stdin;
3	1	⚠️	100.00
4	1	💔	100.00
5	1	🗺️📍	100.00
6	1	👥🔻	100.00
7	1	💰➡️👦	100.00
8	1	📱💬	100.00
2	1	👦➡️🔫	100.00
1	1	😢😢😢😢	100.00
\.


--
-- Data for Name: entidades; Type: TABLE DATA; Schema: sds; Owner: -
--

COPY sds.entidades (id_entidades, nombre_entidad, peso_entidad, id_categoria_observacion) FROM stdin;
1	Fuerzas Militares de Colombia	95.00	31
2	Policía Nacional de Colombia	90.00	31
3	Fiscalía General de la Nación	85.00	31
4	Procuraduría General de la Nación	80.00	31
5	Contraloría General de la República	75.00	31
6	Defensoría del Pueblo	90.00	31
7	Ejército de Liberación Nacional (ELN)	85.00	31
8	Disidencias de las FARC	80.00	31
9	Clan del Golfo	75.00	31
10	Los Pelusos	70.00	31
11	Los Pachenca	65.00	31
12	Los Rastrojos	60.00	31
13	Los Urabeños	55.00	31
14	Águilas Negras	50.00	31
15	Autodefensas Gaitanistas	45.00	31
16	Bandas Criminales (BACRIM)	40.00	31
17	Cartel de Sinaloa	35.00	31
18	Cartel de Jalisco Nueva Generación	30.00	31
19	Cartel del Norte del Valle	25.00	31
20	Cartel de Cali	20.00	31
21	Cartel de Medellín	15.00	31
22	Tren de Aragua	10.00	31
23	Mafia Mexicana	5.00	31
24	Mafia Peruana	0.00	31
25	Mafia Ecuatoriana	0.00	31
\.


--
-- Data for Name: figuras_publicas; Type: TABLE DATA; Schema: sds; Owner: -
--

COPY sds.figuras_publicas (id_figura_publica, nombre_actor, peso_actor, id_categoria_observacion) FROM stdin;
1	Gustavo Petro	85.00	11
2	Álvaro Uribe Vélez	90.00	11
3	Iván Duque Márquez	75.00	11
4	Claudia López	80.00	11
5	Francisco Santos	70.00	11
6	Germán Vargas Lleras	65.00	11
7	María Fernanda Cabal	85.00	11
8	Roy Barreras	60.00	11
9	Piedad Córdoba	80.00	11
10	Jorge Enrique Robledo	75.00	11
11	Sergio Fajardo	70.00	11
12	Antonio Sanguino	55.00	11
13	Juan Manuel Galán	65.00	11
14	Catherine Juvinao	60.00	11
15	David Racero	50.00	11
16	Alexander López	55.00	11
17	Benedicta de los Ángeles	45.00	11
18	Harold Guerrero	40.00	11
19	Myriam A. de Rueda	35.00	11
20	José A. Ocampo	80.00	11
21	Armando Benedetti	75.00	11
22	Paloma Valencia	85.00	11
23	Humberto de la Calle	70.00	11
24	César Gaviria	75.00	11
25	Andrés Pastrana	70.00	11
26	Ernesto Samper	65.00	11
27	Nohemí Sanín	60.00	11
28	Antanas Mockus	80.00	11
29	Enrique Peñalosa	75.00	11
30	Carlos Fernando Galán	70.00	11
31	Gustavo Bolívar	85.00	11
32	Iván Cepeda	80.00	11
33	María José Pizarro	75.00	11
34	Jota Pe Hernández	65.00	11
35	Jorge Iván Ospina	60.00	11
36	Daniel Quintero	70.00	11
37	Federico Gutiérrez	75.00	11
38	Luis Pérez	55.00	11
39	Jorge Bedoya	50.00	11
40	Cielo Rusinque	45.00	11
41	Ana María Castañeda	40.00	11
42	Diego Molano	65.00	11
43	Angela María Robledo	70.00	11
44	Juan Carlos Losada	60.00	11
45	David Luna	55.00	11
46	Sandra Ortiz	50.00	11
47	Julian Rodríguez	45.00	11
48	Nicolás Ramos	40.00	11
49	Viviane Morales	75.00	11
50	Álvaro Leyva	70.00	11
\.


--
-- Data for Name: frase_clave; Type: TABLE DATA; Schema: sds; Owner: -
--

COPY sds.frase_clave (id_frase_clave, id_categoria_analisis_senal, nombre_frase_clave, peso_frase_clave) FROM stdin;
1	1	reclutamiento de menores para la guerra	100.00
2	1	niños utilizados por grupos armados	100.00
3	1	vinculación de adolescentes al conflicto	100.00
4	1	explotación de niñas en redes sociales	100.00
5	1	los grupos ilegales usan a los jóvenes	100.00
6	1	menores en cultivos ilícitos	100.00
7	1	adolescentes portando armas	100.00
8	1	reclutamiento forzado de estudiantes	100.00
\.


--
-- Data for Name: influencers; Type: TABLE DATA; Schema: sds; Owner: -
--

COPY sds.influencers (id_influencer, nombre_influencer, peso_influencer, id_categoria_observacion) FROM stdin;
1	Juanpis González	90.00	12
2	La Paisa (Marce)	85.00	12
3	La Tigresa del Oriente	80.00	12
4	Pipepunk	75.00	12
5	Coscu	70.00	12
6	Luisito Comunica	85.00	12
7	German Garmendia	80.00	12
8	Yuya	75.00	12
9	Juan Guarnizo	80.00	12
10	AuronPlay	85.00	12
11	El Rubius	80.00	12
12	Migue Granados	70.00	12
13	Dalas Review	75.00	12
14	Mikecrack	65.00	12
15	Vegetta777	70.00	12
16	Willyrex	65.00	12
17	Mangel	60.00	12
18	Alexby	55.00	12
19	Jordi Wild	70.00	12
20	Luis Ángel Arango	45.00	12
\.


--
-- Data for Name: medios_digitales; Type: TABLE DATA; Schema: sds; Owner: -
--

COPY sds.medios_digitales (id_medio_digital, nombre_medio_digital, peso_medio_digital, id_categoria_observacion) FROM stdin;
1	El Tiempo	95.00	14
2	El Espectador	90.00	14
3	Semana	85.00	14
4	La Silla Vacía	80.00	14
5	Blu Radio	85.00	14
6	Caracol Radio	90.00	14
7	RCN Radio	85.00	14
8	W Radio	80.00	14
9	Caracol Televisión	95.00	14
10	RCN Televisión	90.00	14
11	Canal Uno	70.00	14
12	Señal Colombia	65.00	14
13	Telemedellín	60.00	14
14	Teleantioquia	55.00	14
15	Canal Capital	70.00	14
16	CityTV	60.00	14
17	NTN24	75.00	14
18	CNN en Español	85.00	14
19	DW Español	70.00	14
20	BBC Mundo	80.00	14
21	France 24 Español	65.00	14
22	RT en Español	75.00	14
23	Telesur	70.00	14
24	Venezolana de Televisión	60.00	14
25	Panamericana Televisión	55.00	14
26	América Televisión	50.00	14
27	TV Perú	45.00	14
28	Ecuavisa	40.00	14
29	Teleamazonas	35.00	14
30	Canal 10 Uruguay	30.00	14
\.


--
-- Data for Name: palabra_clave; Type: TABLE DATA; Schema: sds; Owner: -
--

COPY sds.palabra_clave (id_palabra_clave, id_categoria_analisis_senal, nombre_palabra_clave, peso_palabra_clave) FROM stdin;
2	1	grupos delictivos organizados	100.00
3	1	reclutamiento	100.00
4	1	uso	100.00
5	1	utilización	100.00
6	1	niñas	100.00
7	1	niños	100.00
8	1	adolescentes	100.00
9	1	niñez	100.00
10	1	menores	100.00
11	1	jóvenes	100.00
12	1	juventud	100.00
13	1	conflicto	100.00
14	1	conflicto", "armado	100.00
15	1	guerra	100.00
16	1	disidencias	100.00
17	1	Estado Mayor Central	100.00
18	1	ELN	100.00
19	1	Segunda Marquetalia	100.00
20	1	crimen organizado	100.00
21	1	guerrilla	100.00
22	1	guerrillas	100.00
23	1	cultivos ilícitos	100.00
24	1	porte armas	100.00
25	1	enfrentamientos	100.00
26	1	redes", "sociales	100.00
27	1	TikTok	100.00
28	1	Facebook	100.00
29	1	Telegram	100.00
30	1	violencia	100.00
31	1	violencia sexual	100.00
32	1	explotación sexual	100.00
33	1	exploración	100.00
34	1	abuso	100.00
1	1	grupos armados organizados	100.00
\.


--
-- Data for Name: resultado_observacion_senal; Type: TABLE DATA; Schema: sds; Owner: -
--

COPY sds.resultado_observacion_senal (id_resultado_observacion_senal, id_senal_detectada, id_categoria_observacion, resultado_observacion_categoria, codigo_categoria_observacion) FROM stdin;
1	1	11	67.88	Actores_1
2	1	12	66.97	Actores_2
3	1	13	36.60	Actores_3
4	1	14	96.84	Actores_4
5	1	21	25.62	Dinamica_1
6	1	22	22.58	Dinamica_2
7	1	23	37.71	Dinamica_3
8	1	31	92.33	Contenido_1
9	1	32	82.28	Contenido_2
10	1	41	84.93	Expansion_1
11	1	42	33.91	Expansion_2
12	1	43	18.70	Expansion_3
13	1	51	26.07	Impacto_1
14	1	52	16.23	Impacto_2
15	1	53	37.60	Impacto_3
16	1	54	48.89	Impacto_4
17	2	11	72.42	Actores_1
18	2	12	91.14	Actores_2
19	2	13	90.37	Actores_3
20	2	14	57.00	Actores_4
21	2	21	77.78	Dinamica_1
22	2	22	82.14	Dinamica_2
23	2	23	72.08	Dinamica_3
24	2	31	79.46	Contenido_1
25	2	32	32.94	Contenido_2
26	2	41	93.55	Expansion_1
27	2	42	81.52	Expansion_2
28	2	43	83.98	Expansion_3
29	2	51	69.87	Impacto_1
30	2	52	37.09	Impacto_2
31	2	53	84.02	Impacto_3
32	2	54	12.16	Impacto_4
33	3	11	76.58	Actores_1
34	3	12	22.84	Actores_2
35	3	13	29.94	Actores_3
36	3	14	81.90	Actores_4
37	3	21	40.01	Dinamica_1
38	3	22	93.77	Dinamica_2
39	3	23	21.96	Dinamica_3
40	3	31	44.78	Contenido_1
41	3	32	41.90	Contenido_2
42	3	41	65.83	Expansion_1
43	3	42	89.42	Expansion_2
44	3	43	70.68	Expansion_3
45	3	51	90.61	Impacto_1
46	3	52	53.44	Impacto_2
47	3	53	46.11	Impacto_3
48	3	54	99.53	Impacto_4
49	4	11	31.20	Actores_1
50	4	12	67.36	Actores_2
51	4	13	96.01	Actores_3
52	4	14	54.62	Actores_4
53	4	21	41.00	Dinamica_1
54	4	22	34.21	Dinamica_2
55	4	23	84.28	Dinamica_3
56	4	31	87.52	Contenido_1
57	4	32	43.68	Contenido_2
58	4	41	73.21	Expansion_1
59	4	42	18.11	Expansion_2
60	4	43	30.97	Expansion_3
61	4	51	79.70	Impacto_1
62	4	52	33.72	Impacto_2
63	4	53	79.26	Impacto_3
64	4	54	29.02	Impacto_4
65	5	11	60.35	Actores_1
66	5	12	15.37	Actores_2
67	5	13	49.49	Actores_3
68	5	14	23.36	Actores_4
69	5	21	68.76	Dinamica_1
70	5	22	62.89	Dinamica_2
71	5	23	26.26	Dinamica_3
72	5	31	15.43	Contenido_1
73	5	32	55.63	Contenido_2
74	5	41	61.56	Expansion_1
75	5	42	69.44	Expansion_2
76	5	43	35.72	Expansion_3
77	5	51	76.44	Impacto_1
78	5	52	30.27	Impacto_2
79	5	53	72.96	Impacto_3
80	5	54	89.65	Impacto_4
81	6	11	75.07	Actores_1
82	6	12	25.76	Actores_2
83	6	13	33.88	Actores_3
84	6	14	21.25	Actores_4
85	6	21	20.84	Dinamica_1
86	6	22	88.78	Dinamica_2
87	6	23	52.58	Dinamica_3
88	6	31	95.79	Contenido_1
89	6	32	96.86	Contenido_2
90	6	41	32.43	Expansion_1
91	6	42	77.87	Expansion_2
92	6	43	90.37	Expansion_3
93	6	51	35.97	Impacto_1
94	6	52	58.39	Impacto_2
95	6	53	92.10	Impacto_3
96	6	54	36.49	Impacto_4
97	7	11	53.61	Actores_1
98	7	12	22.24	Actores_2
99	7	13	26.16	Actores_3
100	7	14	67.90	Actores_4
101	7	21	20.30	Dinamica_1
102	7	22	83.47	Dinamica_2
103	7	23	67.55	Dinamica_3
104	7	31	21.93	Contenido_1
105	7	32	89.05	Contenido_2
106	7	41	37.08	Expansion_1
107	7	42	64.24	Expansion_2
108	7	43	74.56	Expansion_3
109	7	51	44.22	Impacto_1
110	7	52	53.21	Impacto_2
111	7	53	30.68	Impacto_3
112	7	54	59.83	Impacto_4
113	8	11	84.48	Actores_1
114	8	12	77.14	Actores_2
115	8	13	17.96	Actores_3
116	8	14	34.93	Actores_4
117	8	21	49.40	Dinamica_1
118	8	22	44.42	Dinamica_2
119	8	23	48.48	Dinamica_3
120	8	31	47.57	Contenido_1
121	8	32	16.48	Contenido_2
122	8	41	13.80	Expansion_1
123	8	42	18.30	Expansion_2
124	8	43	91.41	Expansion_3
125	8	51	64.06	Impacto_1
126	8	52	45.25	Impacto_2
127	8	53	22.19	Impacto_3
128	8	54	41.75	Impacto_4
129	9	11	62.58	Actores_1
130	9	12	45.18	Actores_2
131	9	13	47.07	Actores_3
132	9	14	18.31	Actores_4
133	9	21	73.77	Dinamica_1
134	9	22	85.40	Dinamica_2
135	9	23	44.79	Dinamica_3
136	9	31	64.48	Contenido_1
137	9	32	66.33	Contenido_2
138	9	41	62.70	Expansion_1
139	9	42	71.48	Expansion_2
140	9	43	98.12	Expansion_3
141	9	51	21.06	Impacto_1
142	9	52	35.19	Impacto_2
143	9	53	42.38	Impacto_3
144	9	54	59.90	Impacto_4
145	10	11	68.44	Actores_1
146	10	12	75.26	Actores_2
147	10	13	39.38	Actores_3
148	10	14	55.13	Actores_4
149	10	21	23.31	Dinamica_1
150	10	22	13.08	Dinamica_2
151	10	23	50.04	Dinamica_3
152	10	31	49.72	Contenido_1
153	10	32	63.99	Contenido_2
154	10	41	13.57	Expansion_1
155	10	42	90.16	Expansion_2
156	10	43	54.44	Expansion_3
157	10	51	55.00	Impacto_1
158	10	52	74.39	Impacto_2
159	10	53	68.20	Impacto_3
160	10	54	65.26	Impacto_4
161	11	11	80.98	Actores_1
162	11	12	69.35	Actores_2
163	11	13	70.41	Actores_3
164	11	14	83.41	Actores_4
165	11	21	76.04	Dinamica_1
166	11	22	22.77	Dinamica_2
167	11	23	51.51	Dinamica_3
168	11	31	68.24	Contenido_1
169	11	32	19.16	Contenido_2
170	11	41	56.07	Expansion_1
171	11	42	38.02	Expansion_2
172	11	43	75.81	Expansion_3
173	11	51	85.16	Impacto_1
174	11	52	58.55	Impacto_2
175	11	53	72.20	Impacto_3
176	11	54	79.76	Impacto_4
177	12	11	33.82	Actores_1
178	12	12	17.39	Actores_2
179	12	13	51.02	Actores_3
180	12	14	57.35	Actores_4
181	12	21	64.92	Dinamica_1
182	12	22	50.29	Dinamica_2
183	12	23	40.19	Dinamica_3
184	12	31	44.91	Contenido_1
185	12	32	62.95	Contenido_2
186	12	41	83.05	Expansion_1
187	12	42	70.05	Expansion_2
188	12	43	50.71	Expansion_3
189	12	51	99.82	Impacto_1
190	12	52	47.71	Impacto_2
191	12	53	64.82	Impacto_3
192	12	54	75.42	Impacto_4
193	13	11	32.91	Actores_1
194	13	12	75.00	Actores_2
195	13	13	56.85	Actores_3
196	13	14	87.95	Actores_4
197	13	21	24.84	Dinamica_1
198	13	22	17.56	Dinamica_2
199	13	23	68.01	Dinamica_3
200	13	31	91.48	Contenido_1
201	13	32	55.52	Contenido_2
202	13	41	60.87	Expansion_1
203	13	42	78.41	Expansion_2
204	13	43	30.96	Expansion_3
205	13	51	96.81	Impacto_1
206	13	52	19.80	Impacto_2
207	13	53	46.17	Impacto_3
208	13	54	35.50	Impacto_4
209	14	11	25.42	Actores_1
210	14	12	20.90	Actores_2
211	14	13	70.94	Actores_3
212	14	14	81.14	Actores_4
213	14	21	32.89	Dinamica_1
214	14	22	32.70	Dinamica_2
215	14	23	88.74	Dinamica_3
216	14	31	25.12	Contenido_1
217	14	32	69.76	Contenido_2
218	14	41	79.32	Expansion_1
219	14	42	66.75	Expansion_2
220	14	43	99.09	Expansion_3
221	14	51	47.38	Impacto_1
222	14	52	84.41	Impacto_2
223	14	53	29.81	Impacto_3
224	14	54	68.53	Impacto_4
225	15	11	21.47	Actores_1
226	15	12	34.69	Actores_2
227	15	13	12.65	Actores_3
228	15	14	46.69	Actores_4
229	15	21	60.78	Dinamica_1
230	15	22	11.23	Dinamica_2
231	15	23	98.67	Dinamica_3
232	15	31	46.63	Contenido_1
233	15	32	48.86	Contenido_2
234	15	41	68.57	Expansion_1
235	15	42	94.58	Expansion_2
236	15	43	71.16	Expansion_3
237	15	51	18.81	Impacto_1
238	15	52	32.11	Impacto_2
239	15	53	51.26	Impacto_3
240	15	54	74.02	Impacto_4
241	16	11	73.13	Actores_1
242	16	12	98.06	Actores_2
243	16	13	34.50	Actores_3
244	16	14	73.65	Actores_4
245	16	21	67.37	Dinamica_1
246	16	22	95.88	Dinamica_2
247	16	23	86.96	Dinamica_3
248	16	31	44.09	Contenido_1
249	16	32	50.20	Contenido_2
250	16	41	10.74	Expansion_1
251	16	42	60.37	Expansion_2
252	16	43	96.87	Expansion_3
253	16	51	78.50	Impacto_1
254	16	52	71.31	Impacto_2
255	16	53	90.07	Impacto_3
256	16	54	53.51	Impacto_4
257	17	11	40.59	Actores_1
258	17	12	61.00	Actores_2
259	17	13	51.48	Actores_3
260	17	14	45.83	Actores_4
261	17	21	35.55	Dinamica_1
262	17	22	68.40	Dinamica_2
263	17	23	85.80	Dinamica_3
264	17	31	18.28	Contenido_1
265	17	32	24.45	Contenido_2
266	17	41	67.46	Expansion_1
267	17	42	50.50	Expansion_2
268	17	43	48.19	Expansion_3
269	17	51	61.57	Impacto_1
270	17	52	40.82	Impacto_2
271	17	53	76.52	Impacto_3
272	17	54	16.04	Impacto_4
273	18	11	61.65	Actores_1
274	18	12	24.70	Actores_2
275	18	13	46.42	Actores_3
276	18	14	54.58	Actores_4
277	18	21	75.05	Dinamica_1
278	18	22	16.51	Dinamica_2
279	18	23	84.05	Dinamica_3
280	18	31	27.58	Contenido_1
281	18	32	19.60	Contenido_2
282	18	41	20.21	Expansion_1
283	18	42	45.32	Expansion_2
284	18	43	56.89	Expansion_3
285	18	51	68.42	Impacto_1
286	18	52	70.59	Impacto_2
287	18	53	59.99	Impacto_3
288	18	54	75.92	Impacto_4
289	19	11	34.54	Actores_1
290	19	12	95.90	Actores_2
291	19	13	19.86	Actores_3
292	19	14	69.62	Actores_4
293	19	21	35.50	Dinamica_1
294	19	22	95.87	Dinamica_2
295	19	23	49.69	Dinamica_3
296	19	31	38.34	Contenido_1
297	19	32	13.10	Contenido_2
298	19	41	18.85	Expansion_1
299	19	42	95.26	Expansion_2
300	19	43	36.66	Expansion_3
301	19	51	36.28	Impacto_1
302	19	52	89.08	Impacto_2
303	19	53	25.76	Impacto_3
304	19	54	11.47	Impacto_4
305	20	11	40.33	Actores_1
306	20	12	81.09	Actores_2
307	20	13	42.21	Actores_3
308	20	14	45.91	Actores_4
309	20	21	55.79	Dinamica_1
310	20	22	95.29	Dinamica_2
311	20	23	87.25	Dinamica_3
312	20	31	31.74	Contenido_1
313	20	32	40.28	Contenido_2
314	20	41	20.72	Expansion_1
315	20	42	57.89	Expansion_2
316	20	43	27.05	Expansion_3
317	20	51	50.92	Impacto_1
318	20	52	87.26	Impacto_2
319	20	53	64.84	Impacto_3
320	20	54	18.60	Impacto_4
321	21	11	32.35	Actores_1
322	21	12	34.23	Actores_2
323	21	13	69.09	Actores_3
324	21	14	73.05	Actores_4
325	21	21	41.81	Dinamica_1
326	21	22	24.86	Dinamica_2
327	21	23	45.28	Dinamica_3
328	21	31	52.46	Contenido_1
329	21	32	42.12	Contenido_2
330	21	41	73.24	Expansion_1
331	21	42	79.90	Expansion_2
332	21	43	18.70	Expansion_3
333	21	51	95.60	Impacto_1
334	21	52	52.30	Impacto_2
335	21	53	34.22	Impacto_3
336	21	54	53.72	Impacto_4
337	22	11	41.35	Actores_1
338	22	12	68.41	Actores_2
339	22	13	18.59	Actores_3
340	22	14	23.38	Actores_4
341	22	21	77.32	Dinamica_1
342	22	22	52.12	Dinamica_2
343	22	23	16.12	Dinamica_3
344	22	31	12.89	Contenido_1
345	22	32	49.47	Contenido_2
346	22	41	25.10	Expansion_1
347	22	42	67.77	Expansion_2
348	22	43	67.46	Expansion_3
349	22	51	40.74	Impacto_1
350	22	52	49.94	Impacto_2
351	22	53	75.09	Impacto_3
352	22	54	94.89	Impacto_4
353	23	11	45.43	Actores_1
354	23	12	12.64	Actores_2
355	23	13	41.30	Actores_3
356	23	14	79.98	Actores_4
357	23	21	92.49	Dinamica_1
358	23	22	53.51	Dinamica_2
359	23	23	54.52	Dinamica_3
360	23	31	67.08	Contenido_1
361	23	32	45.03	Contenido_2
362	23	41	47.19	Expansion_1
363	23	42	58.75	Expansion_2
364	23	43	54.19	Expansion_3
365	23	51	34.56	Impacto_1
366	23	52	60.06	Impacto_2
367	23	53	10.60	Impacto_3
368	23	54	80.87	Impacto_4
369	24	11	31.78	Actores_1
370	24	12	45.76	Actores_2
371	24	13	92.46	Actores_3
372	24	14	86.82	Actores_4
373	24	21	97.96	Dinamica_1
374	24	22	83.27	Dinamica_2
375	24	23	45.78	Dinamica_3
376	24	31	85.47	Contenido_1
377	24	32	46.17	Contenido_2
378	24	41	76.57	Expansion_1
379	24	42	23.80	Expansion_2
380	24	43	57.51	Expansion_3
381	24	51	20.07	Impacto_1
382	24	52	80.43	Impacto_2
383	24	53	23.25	Impacto_3
384	24	54	30.87	Impacto_4
385	25	11	37.81	Actores_1
386	25	12	34.33	Actores_2
387	25	13	54.37	Actores_3
388	25	14	65.56	Actores_4
389	25	21	64.48	Dinamica_1
390	25	22	81.47	Dinamica_2
391	25	23	20.01	Dinamica_3
392	25	31	88.26	Contenido_1
393	25	32	48.33	Contenido_2
394	25	41	44.55	Expansion_1
395	25	42	24.78	Expansion_2
396	25	43	57.45	Expansion_3
397	25	51	79.00	Impacto_1
398	25	52	49.49	Impacto_2
399	25	53	96.10	Impacto_3
400	25	54	88.27	Impacto_4
401	26	11	61.53	Actores_1
402	26	12	46.87	Actores_2
403	26	13	29.33	Actores_3
404	26	14	11.63	Actores_4
405	26	21	26.84	Dinamica_1
406	26	22	25.79	Dinamica_2
407	26	23	68.75	Dinamica_3
408	26	31	54.99	Contenido_1
409	26	32	85.07	Contenido_2
410	26	41	85.92	Expansion_1
411	26	42	86.34	Expansion_2
412	26	43	47.18	Expansion_3
413	26	51	86.93	Impacto_1
414	26	52	72.49	Impacto_2
415	26	53	44.06	Impacto_3
416	26	54	39.28	Impacto_4
417	27	11	66.62	Actores_1
418	27	12	54.50	Actores_2
419	27	13	20.28	Actores_3
420	27	14	78.24	Actores_4
421	27	21	77.22	Dinamica_1
422	27	22	10.53	Dinamica_2
423	27	23	97.16	Dinamica_3
424	27	31	39.91	Contenido_1
425	27	32	86.81	Contenido_2
426	27	41	54.94	Expansion_1
427	27	42	59.00	Expansion_2
428	27	43	54.13	Expansion_3
429	27	51	68.26	Impacto_1
430	27	52	32.49	Impacto_2
431	27	53	99.24	Impacto_3
432	27	54	20.50	Impacto_4
433	28	11	17.23	Actores_1
434	28	12	73.02	Actores_2
435	28	13	47.52	Actores_3
436	28	14	32.78	Actores_4
437	28	21	43.15	Dinamica_1
438	28	22	72.90	Dinamica_2
439	28	23	36.00	Dinamica_3
440	28	31	56.36	Contenido_1
441	28	32	72.33	Contenido_2
442	28	41	55.17	Expansion_1
443	28	42	13.87	Expansion_2
444	28	43	75.10	Expansion_3
445	28	51	84.61	Impacto_1
446	28	52	76.07	Impacto_2
447	28	53	48.26	Impacto_3
448	28	54	38.17	Impacto_4
449	29	11	54.11	Actores_1
450	29	12	16.67	Actores_2
451	29	13	84.29	Actores_3
452	29	14	25.27	Actores_4
453	29	21	64.29	Dinamica_1
454	29	22	23.75	Dinamica_2
455	29	23	16.37	Dinamica_3
456	29	31	88.12	Contenido_1
457	29	32	78.31	Contenido_2
458	29	41	82.27	Expansion_1
459	29	42	52.39	Expansion_2
460	29	43	62.68	Expansion_3
461	29	51	66.52	Impacto_1
462	29	52	93.36	Impacto_2
463	29	53	65.46	Impacto_3
464	29	54	37.24	Impacto_4
465	30	11	81.52	Actores_1
466	30	12	39.83	Actores_2
467	30	13	19.96	Actores_3
468	30	14	96.30	Actores_4
469	30	21	51.14	Dinamica_1
470	30	22	91.91	Dinamica_2
471	30	23	58.54	Dinamica_3
472	30	31	10.24	Contenido_1
473	30	32	85.46	Contenido_2
474	30	41	14.42	Expansion_1
475	30	42	96.99	Expansion_2
476	30	43	15.94	Expansion_3
477	30	51	18.59	Impacto_1
478	30	52	44.74	Impacto_2
479	30	53	34.83	Impacto_3
480	30	54	93.63	Impacto_4
481	31	11	87.16	Actores_1
482	31	12	63.15	Actores_2
483	31	13	85.42	Actores_3
484	31	14	15.29	Actores_4
485	31	21	73.77	Dinamica_1
486	31	22	76.70	Dinamica_2
487	31	23	94.07	Dinamica_3
488	31	31	61.94	Contenido_1
489	31	32	44.25	Contenido_2
490	31	41	19.27	Expansion_1
491	31	42	94.50	Expansion_2
492	31	43	80.14	Expansion_3
493	31	51	14.85	Impacto_1
494	31	52	67.54	Impacto_2
495	31	53	82.31	Impacto_3
496	31	54	27.31	Impacto_4
497	32	11	37.48	Actores_1
498	32	12	77.76	Actores_2
499	32	13	78.24	Actores_3
500	32	14	83.21	Actores_4
501	32	21	62.03	Dinamica_1
502	32	22	30.43	Dinamica_2
503	32	23	87.84	Dinamica_3
504	32	31	20.61	Contenido_1
505	32	32	33.29	Contenido_2
506	32	41	38.11	Expansion_1
507	32	42	18.07	Expansion_2
508	32	43	59.66	Expansion_3
509	32	51	58.81	Impacto_1
510	32	52	35.61	Impacto_2
511	32	53	61.38	Impacto_3
512	32	54	21.74	Impacto_4
513	33	11	41.11	Actores_1
514	33	12	74.17	Actores_2
515	33	13	70.08	Actores_3
516	33	14	21.75	Actores_4
517	33	21	65.24	Dinamica_1
518	33	22	95.48	Dinamica_2
519	33	23	41.49	Dinamica_3
520	33	31	87.38	Contenido_1
521	33	32	42.98	Contenido_2
522	33	41	17.63	Expansion_1
523	33	42	53.37	Expansion_2
524	33	43	60.20	Expansion_3
525	33	51	11.55	Impacto_1
526	33	52	67.23	Impacto_2
527	33	53	84.63	Impacto_3
528	33	54	89.80	Impacto_4
529	34	11	26.18	Actores_1
530	34	12	18.58	Actores_2
531	34	13	76.73	Actores_3
532	34	14	38.56	Actores_4
533	34	21	96.71	Dinamica_1
534	34	22	42.01	Dinamica_2
535	34	23	25.08	Dinamica_3
536	34	31	51.11	Contenido_1
537	34	32	39.98	Contenido_2
538	34	41	19.05	Expansion_1
539	34	42	63.40	Expansion_2
540	34	43	34.50	Expansion_3
541	34	51	75.23	Impacto_1
542	34	52	36.84	Impacto_2
543	34	53	30.78	Impacto_3
544	34	54	96.12	Impacto_4
545	35	11	21.54	Actores_1
546	35	12	48.80	Actores_2
547	35	13	15.15	Actores_3
548	35	14	40.95	Actores_4
549	35	21	28.23	Dinamica_1
550	35	22	65.54	Dinamica_2
551	35	23	52.83	Dinamica_3
552	35	31	63.49	Contenido_1
553	35	32	20.95	Contenido_2
554	35	41	37.83	Expansion_1
555	35	42	91.76	Expansion_2
556	35	43	26.95	Expansion_3
557	35	51	11.46	Impacto_1
558	35	52	69.61	Impacto_2
559	35	53	16.85	Impacto_3
560	35	54	22.17	Impacto_4
561	36	11	17.19	Actores_1
562	36	12	77.48	Actores_2
563	36	13	73.26	Actores_3
564	36	14	18.86	Actores_4
565	36	21	34.56	Dinamica_1
566	36	22	12.30	Dinamica_2
567	36	23	16.66	Dinamica_3
568	36	31	71.77	Contenido_1
569	36	32	54.40	Contenido_2
570	36	41	94.54	Expansion_1
571	36	42	55.04	Expansion_2
572	36	43	54.75	Expansion_3
573	36	51	25.60	Impacto_1
574	36	52	57.03	Impacto_2
575	36	53	10.26	Impacto_3
576	36	54	81.66	Impacto_4
577	37	11	49.65	Actores_1
578	37	12	37.33	Actores_2
579	37	13	54.05	Actores_3
580	37	14	70.98	Actores_4
581	37	21	27.21	Dinamica_1
582	37	22	41.39	Dinamica_2
583	37	23	48.09	Dinamica_3
584	37	31	75.01	Contenido_1
585	37	32	36.71	Contenido_2
586	37	41	61.44	Expansion_1
587	37	42	59.86	Expansion_2
588	37	43	10.22	Expansion_3
589	37	51	86.43	Impacto_1
590	37	52	75.42	Impacto_2
591	37	53	30.12	Impacto_3
592	37	54	10.48	Impacto_4
593	38	11	34.19	Actores_1
594	38	12	10.76	Actores_2
595	38	13	43.53	Actores_3
596	38	14	88.38	Actores_4
597	38	21	19.18	Dinamica_1
598	38	22	45.35	Dinamica_2
599	38	23	16.90	Dinamica_3
600	38	31	53.68	Contenido_1
601	38	32	78.08	Contenido_2
602	38	41	26.44	Expansion_1
603	38	42	71.91	Expansion_2
604	38	43	88.13	Expansion_3
605	38	51	10.37	Impacto_1
606	38	52	96.25	Impacto_2
607	38	53	47.38	Impacto_3
608	38	54	59.12	Impacto_4
609	39	11	47.65	Actores_1
610	39	12	80.68	Actores_2
611	39	13	41.99	Actores_3
612	39	14	38.96	Actores_4
613	39	21	99.30	Dinamica_1
614	39	22	31.76	Dinamica_2
615	39	23	10.20	Dinamica_3
616	39	31	60.88	Contenido_1
617	39	32	27.07	Contenido_2
618	39	41	48.71	Expansion_1
619	39	42	71.87	Expansion_2
620	39	43	63.30	Expansion_3
621	39	51	74.44	Impacto_1
622	39	52	28.82	Impacto_2
623	39	53	58.67	Impacto_3
624	39	54	55.08	Impacto_4
625	40	11	76.72	Actores_1
626	40	12	14.97	Actores_2
627	40	13	84.58	Actores_3
628	40	14	90.17	Actores_4
629	40	21	19.71	Dinamica_1
630	40	22	46.10	Dinamica_2
631	40	23	92.86	Dinamica_3
632	40	31	31.37	Contenido_1
633	40	32	21.76	Contenido_2
634	40	41	30.92	Expansion_1
635	40	42	71.08	Expansion_2
636	40	43	62.49	Expansion_3
637	40	51	56.04	Impacto_1
638	40	52	12.35	Impacto_2
639	40	53	17.37	Impacto_3
640	40	54	23.02	Impacto_4
641	41	11	57.81	Actores_1
642	41	12	55.69	Actores_2
643	41	13	94.31	Actores_3
644	41	14	98.65	Actores_4
645	41	21	67.89	Dinamica_1
646	41	22	43.97	Dinamica_2
647	41	23	48.89	Dinamica_3
648	41	31	53.75	Contenido_1
649	41	32	35.32	Contenido_2
650	41	41	60.53	Expansion_1
651	41	42	45.17	Expansion_2
652	41	43	82.47	Expansion_3
653	41	51	79.53	Impacto_1
654	41	52	20.11	Impacto_2
655	41	53	36.62	Impacto_3
656	41	54	69.33	Impacto_4
657	42	11	72.22	Actores_1
658	42	12	88.68	Actores_2
659	42	13	19.86	Actores_3
660	42	14	98.06	Actores_4
661	42	21	43.75	Dinamica_1
662	42	22	82.85	Dinamica_2
663	42	23	75.46	Dinamica_3
664	42	31	26.94	Contenido_1
665	42	32	12.03	Contenido_2
666	42	41	76.80	Expansion_1
667	42	42	56.27	Expansion_2
668	42	43	21.98	Expansion_3
669	42	51	68.54	Impacto_1
670	42	52	86.80	Impacto_2
671	42	53	79.20	Impacto_3
672	42	54	84.76	Impacto_4
673	43	11	41.30	Actores_1
674	43	12	31.19	Actores_2
675	43	13	92.94	Actores_3
676	43	14	66.08	Actores_4
677	43	21	70.85	Dinamica_1
678	43	22	85.99	Dinamica_2
679	43	23	66.93	Dinamica_3
680	43	31	40.74	Contenido_1
681	43	32	98.95	Contenido_2
682	43	41	61.80	Expansion_1
683	43	42	24.83	Expansion_2
684	43	43	85.51	Expansion_3
685	43	51	45.55	Impacto_1
686	43	52	34.17	Impacto_2
687	43	53	11.32	Impacto_3
688	43	54	48.46	Impacto_4
689	44	11	71.07	Actores_1
690	44	12	22.93	Actores_2
691	44	13	52.64	Actores_3
692	44	14	49.15	Actores_4
693	44	21	17.80	Dinamica_1
694	44	22	69.01	Dinamica_2
695	44	23	74.60	Dinamica_3
696	44	31	12.25	Contenido_1
697	44	32	89.94	Contenido_2
698	44	41	33.91	Expansion_1
699	44	42	89.07	Expansion_2
700	44	43	50.47	Expansion_3
701	44	51	18.46	Impacto_1
702	44	52	81.70	Impacto_2
703	44	53	80.08	Impacto_3
704	44	54	66.29	Impacto_4
705	45	11	71.30	Actores_1
706	45	12	32.50	Actores_2
707	45	13	94.40	Actores_3
708	45	14	47.26	Actores_4
709	45	21	69.59	Dinamica_1
710	45	22	32.17	Dinamica_2
711	45	23	31.99	Dinamica_3
712	45	31	10.14	Contenido_1
713	45	32	88.58	Contenido_2
714	45	41	17.68	Expansion_1
715	45	42	37.61	Expansion_2
716	45	43	59.02	Expansion_3
717	45	51	42.35	Impacto_1
718	45	52	31.66	Impacto_2
719	45	53	80.39	Impacto_3
720	45	54	33.67	Impacto_4
721	46	11	50.84	Actores_1
722	46	12	28.29	Actores_2
723	46	13	62.43	Actores_3
724	46	14	70.93	Actores_4
725	46	21	89.82	Dinamica_1
726	46	22	40.76	Dinamica_2
727	46	23	70.49	Dinamica_3
728	46	31	69.51	Contenido_1
729	46	32	68.20	Contenido_2
730	46	41	24.39	Expansion_1
731	46	42	82.13	Expansion_2
732	46	43	92.72	Expansion_3
733	46	51	22.18	Impacto_1
734	46	52	80.88	Impacto_2
735	46	53	61.20	Impacto_3
736	46	54	66.39	Impacto_4
737	47	11	95.91	Actores_1
738	47	12	90.89	Actores_2
739	47	13	45.99	Actores_3
740	47	14	64.12	Actores_4
741	47	21	50.34	Dinamica_1
742	47	22	22.37	Dinamica_2
743	47	23	34.49	Dinamica_3
744	47	31	33.08	Contenido_1
745	47	32	59.02	Contenido_2
746	47	41	35.25	Expansion_1
747	47	42	56.18	Expansion_2
748	47	43	37.89	Expansion_3
749	47	51	21.34	Impacto_1
750	47	52	56.84	Impacto_2
751	47	53	33.25	Impacto_3
752	47	54	95.64	Impacto_4
753	48	11	20.47	Actores_1
754	48	12	42.37	Actores_2
755	48	13	84.94	Actores_3
756	48	14	91.09	Actores_4
757	48	21	44.02	Dinamica_1
758	48	22	76.97	Dinamica_2
759	48	23	71.23	Dinamica_3
760	48	31	78.62	Contenido_1
761	48	32	88.47	Contenido_2
762	48	41	73.10	Expansion_1
763	48	42	50.99	Expansion_2
764	48	43	39.19	Expansion_3
765	48	51	65.41	Impacto_1
766	48	52	25.46	Impacto_2
767	48	53	11.72	Impacto_3
768	48	54	98.40	Impacto_4
769	49	11	90.28	Actores_1
770	49	12	82.54	Actores_2
771	49	13	55.48	Actores_3
772	49	14	68.71	Actores_4
773	49	21	54.93	Dinamica_1
774	49	22	68.17	Dinamica_2
775	49	23	86.32	Dinamica_3
776	49	31	36.00	Contenido_1
777	49	32	81.57	Contenido_2
778	49	41	38.66	Expansion_1
779	49	42	83.59	Expansion_2
780	49	43	19.48	Expansion_3
781	49	51	99.69	Impacto_1
782	49	52	23.25	Impacto_2
783	49	53	96.53	Impacto_3
784	49	54	89.25	Impacto_4
785	50	11	91.66	Actores_1
786	50	12	34.72	Actores_2
787	50	13	19.59	Actores_3
788	50	14	13.54	Actores_4
789	50	21	89.74	Dinamica_1
790	50	22	46.57	Dinamica_2
791	50	23	15.07	Dinamica_3
792	50	31	81.25	Contenido_1
793	50	32	12.92	Contenido_2
794	50	41	52.25	Expansion_1
795	50	42	61.32	Expansion_2
796	50	43	74.84	Expansion_3
797	50	51	21.34	Impacto_1
798	50	52	33.90	Impacto_2
799	50	53	30.01	Impacto_3
800	50	54	28.27	Impacto_4
801	51	11	71.29	Actores_1
802	51	12	88.67	Actores_2
803	51	13	68.97	Actores_3
804	51	14	93.21	Actores_4
805	51	21	86.65	Dinamica_1
806	51	22	98.03	Dinamica_2
807	51	23	96.08	Dinamica_3
808	51	31	11.69	Contenido_1
809	51	32	37.42	Contenido_2
810	51	41	74.87	Expansion_1
811	51	42	60.93	Expansion_2
812	51	43	39.09	Expansion_3
813	51	51	11.94	Impacto_1
814	51	52	41.85	Impacto_2
815	51	53	12.93	Impacto_3
816	51	54	48.15	Impacto_4
817	52	11	59.58	Actores_1
818	52	12	62.81	Actores_2
819	52	13	10.51	Actores_3
820	52	14	55.97	Actores_4
821	52	21	75.87	Dinamica_1
822	52	22	98.99	Dinamica_2
823	52	23	19.35	Dinamica_3
824	52	31	91.16	Contenido_1
825	52	32	20.01	Contenido_2
826	52	41	93.02	Expansion_1
827	52	42	98.17	Expansion_2
828	52	43	18.20	Expansion_3
829	52	51	25.58	Impacto_1
830	52	52	61.08	Impacto_2
831	52	53	21.10	Impacto_3
832	52	54	45.14	Impacto_4
833	53	11	15.17	Actores_1
834	53	12	12.64	Actores_2
835	53	13	30.73	Actores_3
836	53	14	39.58	Actores_4
837	53	21	29.98	Dinamica_1
838	53	22	38.45	Dinamica_2
839	53	23	23.51	Dinamica_3
840	53	31	76.25	Contenido_1
841	53	32	95.86	Contenido_2
842	53	41	40.62	Expansion_1
843	53	42	42.70	Expansion_2
844	53	43	85.98	Expansion_3
845	53	51	16.06	Impacto_1
846	53	52	55.04	Impacto_2
847	53	53	95.31	Impacto_3
848	53	54	40.40	Impacto_4
849	54	11	77.86	Actores_1
850	54	12	95.28	Actores_2
851	54	13	89.23	Actores_3
852	54	14	14.59	Actores_4
853	54	21	21.35	Dinamica_1
854	54	22	48.94	Dinamica_2
855	54	23	94.88	Dinamica_3
856	54	31	55.51	Contenido_1
857	54	32	59.94	Contenido_2
858	54	41	78.97	Expansion_1
859	54	42	28.20	Expansion_2
860	54	43	65.48	Expansion_3
861	54	51	47.81	Impacto_1
862	54	52	85.60	Impacto_2
863	54	53	16.32	Impacto_3
864	54	54	55.92	Impacto_4
865	55	11	88.46	Actores_1
866	55	12	11.38	Actores_2
867	55	13	97.97	Actores_3
868	55	14	21.20	Actores_4
869	55	21	99.33	Dinamica_1
870	55	22	20.28	Dinamica_2
871	55	23	89.89	Dinamica_3
872	55	31	46.91	Contenido_1
873	55	32	13.96	Contenido_2
874	55	41	12.24	Expansion_1
875	55	42	23.69	Expansion_2
876	55	43	48.41	Expansion_3
877	55	51	28.09	Impacto_1
878	55	52	79.84	Impacto_2
879	55	53	63.17	Impacto_3
880	55	54	86.10	Impacto_4
881	56	11	71.82	Actores_1
882	56	12	66.20	Actores_2
883	56	13	34.46	Actores_3
884	56	14	16.69	Actores_4
885	56	21	48.83	Dinamica_1
886	56	22	44.80	Dinamica_2
887	56	23	63.52	Dinamica_3
888	56	31	89.41	Contenido_1
889	56	32	74.60	Contenido_2
890	56	41	37.72	Expansion_1
891	56	42	91.98	Expansion_2
892	56	43	99.66	Expansion_3
893	56	51	59.43	Impacto_1
894	56	52	87.29	Impacto_2
895	56	53	91.48	Impacto_3
896	56	54	63.57	Impacto_4
897	57	11	68.32	Actores_1
898	57	12	99.45	Actores_2
899	57	13	29.85	Actores_3
900	57	14	20.31	Actores_4
901	57	21	35.26	Dinamica_1
902	57	22	56.38	Dinamica_2
903	57	23	49.49	Dinamica_3
904	57	31	40.15	Contenido_1
905	57	32	17.59	Contenido_2
906	57	41	21.05	Expansion_1
907	57	42	76.65	Expansion_2
908	57	43	91.73	Expansion_3
909	57	51	49.65	Impacto_1
910	57	52	29.29	Impacto_2
911	57	53	78.32	Impacto_3
912	57	54	43.25	Impacto_4
913	58	11	92.89	Actores_1
914	58	12	59.83	Actores_2
915	58	13	40.36	Actores_3
916	58	14	43.79	Actores_4
917	58	21	57.15	Dinamica_1
918	58	22	98.46	Dinamica_2
919	58	23	95.74	Dinamica_3
920	58	31	98.22	Contenido_1
921	58	32	41.09	Contenido_2
922	58	41	35.13	Expansion_1
923	58	42	10.49	Expansion_2
924	58	43	85.77	Expansion_3
925	58	51	40.19	Impacto_1
926	58	52	58.56	Impacto_2
927	58	53	87.10	Impacto_3
928	58	54	79.37	Impacto_4
929	59	11	21.83	Actores_1
930	59	12	37.85	Actores_2
931	59	13	23.04	Actores_3
932	59	14	89.66	Actores_4
933	59	21	20.76	Dinamica_1
934	59	22	42.99	Dinamica_2
935	59	23	74.69	Dinamica_3
936	59	31	41.99	Contenido_1
937	59	32	50.48	Contenido_2
938	59	41	26.91	Expansion_1
939	59	42	85.53	Expansion_2
940	59	43	52.47	Expansion_3
941	59	51	99.45	Impacto_1
942	59	52	76.86	Impacto_2
943	59	53	69.66	Impacto_3
944	59	54	91.32	Impacto_4
945	60	11	88.23	Actores_1
946	60	12	81.50	Actores_2
947	60	13	54.45	Actores_3
948	60	14	19.70	Actores_4
949	60	21	14.45	Dinamica_1
950	60	22	59.05	Dinamica_2
951	60	23	41.73	Dinamica_3
952	60	31	92.08	Contenido_1
953	60	32	37.56	Contenido_2
954	60	41	99.55	Expansion_1
955	60	42	70.32	Expansion_2
956	60	43	27.25	Expansion_3
957	60	51	51.22	Impacto_1
958	60	52	94.19	Impacto_2
959	60	53	57.99	Impacto_3
960	60	54	43.77	Impacto_4
961	61	11	32.24	Actores_1
962	61	12	54.45	Actores_2
963	61	13	80.32	Actores_3
964	61	14	44.32	Actores_4
965	61	21	48.13	Dinamica_1
966	61	22	34.65	Dinamica_2
967	61	23	70.15	Dinamica_3
968	61	31	99.58	Contenido_1
969	61	32	13.50	Contenido_2
970	61	41	19.67	Expansion_1
971	61	42	91.25	Expansion_2
972	61	43	32.37	Expansion_3
973	61	51	68.00	Impacto_1
974	61	52	58.24	Impacto_2
975	61	53	15.04	Impacto_3
976	61	54	56.34	Impacto_4
977	62	11	82.33	Actores_1
978	62	12	52.28	Actores_2
979	62	13	59.53	Actores_3
980	62	14	10.76	Actores_4
981	62	21	73.14	Dinamica_1
982	62	22	57.17	Dinamica_2
983	62	23	85.70	Dinamica_3
984	62	31	84.47	Contenido_1
985	62	32	43.38	Contenido_2
986	62	41	77.77	Expansion_1
987	62	42	91.08	Expansion_2
988	62	43	95.14	Expansion_3
989	62	51	96.91	Impacto_1
990	62	52	90.74	Impacto_2
991	62	53	34.24	Impacto_3
992	62	54	54.24	Impacto_4
993	63	11	44.62	Actores_1
994	63	12	95.38	Actores_2
995	63	13	87.40	Actores_3
996	63	14	48.74	Actores_4
997	63	21	11.20	Dinamica_1
998	63	22	35.46	Dinamica_2
999	63	23	71.69	Dinamica_3
1000	63	31	18.78	Contenido_1
1001	63	32	40.99	Contenido_2
1002	63	41	71.89	Expansion_1
1003	63	42	88.38	Expansion_2
1004	63	43	30.65	Expansion_3
1005	63	51	45.98	Impacto_1
1006	63	52	69.59	Impacto_2
1007	63	53	96.43	Impacto_3
1008	63	54	47.59	Impacto_4
1009	64	11	81.26	Actores_1
1010	64	12	30.23	Actores_2
1011	64	13	56.58	Actores_3
1012	64	14	10.88	Actores_4
1013	64	21	28.25	Dinamica_1
1014	64	22	15.16	Dinamica_2
1015	64	23	94.74	Dinamica_3
1016	64	31	28.85	Contenido_1
1017	64	32	22.66	Contenido_2
1018	64	41	78.93	Expansion_1
1019	64	42	81.56	Expansion_2
1020	64	43	43.14	Expansion_3
1021	64	51	47.95	Impacto_1
1022	64	52	89.73	Impacto_2
1023	64	53	12.22	Impacto_3
1024	64	54	45.03	Impacto_4
1025	65	11	87.74	Actores_1
1026	65	12	42.70	Actores_2
1027	65	13	28.06	Actores_3
1028	65	14	35.23	Actores_4
1029	65	21	88.29	Dinamica_1
1030	65	22	54.39	Dinamica_2
1031	65	23	59.48	Dinamica_3
1032	65	31	38.93	Contenido_1
1033	65	32	77.02	Contenido_2
1034	65	41	52.51	Expansion_1
1035	65	42	52.93	Expansion_2
1036	65	43	27.72	Expansion_3
1037	65	51	90.81	Impacto_1
1038	65	52	49.54	Impacto_2
1039	65	53	38.13	Impacto_3
1040	65	54	32.59	Impacto_4
1041	66	11	18.17	Actores_1
1042	66	12	61.34	Actores_2
1043	66	13	84.07	Actores_3
1044	66	14	51.41	Actores_4
1045	66	21	63.26	Dinamica_1
1046	66	22	39.36	Dinamica_2
1047	66	23	72.56	Dinamica_3
1048	66	31	62.21	Contenido_1
1049	66	32	57.10	Contenido_2
1050	66	41	82.92	Expansion_1
1051	66	42	94.12	Expansion_2
1052	66	43	92.30	Expansion_3
1053	66	51	85.32	Impacto_1
1054	66	52	25.88	Impacto_2
1055	66	53	64.37	Impacto_3
1056	66	54	68.60	Impacto_4
1057	67	11	14.45	Actores_1
1058	67	12	37.81	Actores_2
1059	67	13	82.71	Actores_3
1060	67	14	70.99	Actores_4
1061	67	21	44.54	Dinamica_1
1062	67	22	16.31	Dinamica_2
1063	67	23	36.01	Dinamica_3
1064	67	31	91.87	Contenido_1
1065	67	32	32.09	Contenido_2
1066	67	41	49.90	Expansion_1
1067	67	42	31.47	Expansion_2
1068	67	43	70.15	Expansion_3
1069	67	51	53.16	Impacto_1
1070	67	52	57.76	Impacto_2
1071	67	53	22.89	Impacto_3
1072	67	54	77.64	Impacto_4
1073	68	11	74.23	Actores_1
1074	68	12	21.35	Actores_2
1075	68	13	53.60	Actores_3
1076	68	14	31.91	Actores_4
1077	68	21	59.24	Dinamica_1
1078	68	22	77.51	Dinamica_2
1079	68	23	94.94	Dinamica_3
1080	68	31	17.45	Contenido_1
1081	68	32	72.32	Contenido_2
1082	68	41	10.74	Expansion_1
1083	68	42	45.56	Expansion_2
1084	68	43	91.35	Expansion_3
1085	68	51	74.32	Impacto_1
1086	68	52	40.32	Impacto_2
1087	68	53	38.21	Impacto_3
1088	68	54	54.51	Impacto_4
1089	69	11	21.51	Actores_1
1090	69	12	11.88	Actores_2
1091	69	13	23.30	Actores_3
1092	69	14	60.48	Actores_4
1093	69	21	93.81	Dinamica_1
1094	69	22	58.22	Dinamica_2
1095	69	23	50.72	Dinamica_3
1096	69	31	16.66	Contenido_1
1097	69	32	17.89	Contenido_2
1098	69	41	72.93	Expansion_1
1099	69	42	82.89	Expansion_2
1100	69	43	51.84	Expansion_3
1101	69	51	42.41	Impacto_1
1102	69	52	59.22	Impacto_2
1103	69	53	59.69	Impacto_3
1104	69	54	49.54	Impacto_4
1105	70	11	70.48	Actores_1
1106	70	12	55.83	Actores_2
1107	70	13	23.56	Actores_3
1108	70	14	91.83	Actores_4
1109	70	21	49.53	Dinamica_1
1110	70	22	70.06	Dinamica_2
1111	70	23	84.07	Dinamica_3
1112	70	31	52.50	Contenido_1
1113	70	32	77.92	Contenido_2
1114	70	41	67.83	Expansion_1
1115	70	42	44.14	Expansion_2
1116	70	43	63.35	Expansion_3
1117	70	51	67.90	Impacto_1
1118	70	52	95.83	Impacto_2
1119	70	53	85.28	Impacto_3
1120	70	54	45.94	Impacto_4
1121	71	11	84.01	Actores_1
1122	71	12	54.56	Actores_2
1123	71	13	43.47	Actores_3
1124	71	14	28.54	Actores_4
1125	71	21	85.34	Dinamica_1
1126	71	22	84.27	Dinamica_2
1127	71	23	73.96	Dinamica_3
1128	71	31	30.90	Contenido_1
1129	71	32	18.82	Contenido_2
1130	71	41	98.45	Expansion_1
1131	71	42	72.31	Expansion_2
1132	71	43	55.39	Expansion_3
1133	71	51	74.20	Impacto_1
1134	71	52	63.27	Impacto_2
1135	71	53	76.67	Impacto_3
1136	71	54	68.97	Impacto_4
1137	72	11	90.01	Actores_1
1138	72	12	88.40	Actores_2
1139	72	13	85.06	Actores_3
1140	72	14	53.09	Actores_4
1141	72	21	71.86	Dinamica_1
1142	72	22	19.16	Dinamica_2
1143	72	23	66.19	Dinamica_3
1144	72	31	50.67	Contenido_1
1145	72	32	19.05	Contenido_2
1146	72	41	57.54	Expansion_1
1147	72	42	58.84	Expansion_2
1148	72	43	32.34	Expansion_3
1149	72	51	50.48	Impacto_1
1150	72	52	91.73	Impacto_2
1151	72	53	70.55	Impacto_3
1152	72	54	67.61	Impacto_4
1153	73	11	39.76	Actores_1
1154	73	12	91.76	Actores_2
1155	73	13	13.10	Actores_3
1156	73	14	96.89	Actores_4
1157	73	21	57.33	Dinamica_1
1158	73	22	54.21	Dinamica_2
1159	73	23	50.91	Dinamica_3
1160	73	31	76.39	Contenido_1
1161	73	32	43.62	Contenido_2
1162	73	41	93.14	Expansion_1
1163	73	42	31.07	Expansion_2
1164	73	43	55.45	Expansion_3
1165	73	51	48.42	Impacto_1
1166	73	52	70.42	Impacto_2
1167	73	53	44.03	Impacto_3
1168	73	54	98.12	Impacto_4
1169	74	11	90.72	Actores_1
1170	74	12	14.37	Actores_2
1171	74	13	22.67	Actores_3
1172	74	14	57.66	Actores_4
1173	74	21	96.35	Dinamica_1
1174	74	22	21.38	Dinamica_2
1175	74	23	16.36	Dinamica_3
1176	74	31	88.23	Contenido_1
1177	74	32	82.19	Contenido_2
1178	74	41	98.90	Expansion_1
1179	74	42	68.60	Expansion_2
1180	74	43	96.45	Expansion_3
1181	74	51	83.03	Impacto_1
1182	74	52	88.59	Impacto_2
1183	74	53	33.81	Impacto_3
1184	74	54	17.52	Impacto_4
1185	75	11	48.34	Actores_1
1186	75	12	58.16	Actores_2
1187	75	13	41.26	Actores_3
1188	75	14	12.80	Actores_4
1189	75	21	21.34	Dinamica_1
1190	75	22	17.48	Dinamica_2
1191	75	23	78.37	Dinamica_3
1192	75	31	60.65	Contenido_1
1193	75	32	56.27	Contenido_2
1194	75	41	87.93	Expansion_1
1195	75	42	71.90	Expansion_2
1196	75	43	57.91	Expansion_3
1197	75	51	97.88	Impacto_1
1198	75	52	41.40	Impacto_2
1199	75	53	94.94	Impacto_3
1200	75	54	95.15	Impacto_4
1201	76	11	65.01	Actores_1
1202	76	12	28.87	Actores_2
1203	76	13	55.66	Actores_3
1204	76	14	49.80	Actores_4
1205	76	21	96.27	Dinamica_1
1206	76	22	28.92	Dinamica_2
1207	76	23	20.83	Dinamica_3
1208	76	31	21.20	Contenido_1
1209	76	32	80.09	Contenido_2
1210	76	41	70.69	Expansion_1
1211	76	42	75.71	Expansion_2
1212	76	43	38.36	Expansion_3
1213	76	51	83.79	Impacto_1
1214	76	52	42.79	Impacto_2
1215	76	53	88.23	Impacto_3
1216	76	54	78.29	Impacto_4
1217	77	11	15.76	Actores_1
1218	77	12	18.32	Actores_2
1219	77	13	89.10	Actores_3
1220	77	14	39.24	Actores_4
1221	77	21	61.32	Dinamica_1
1222	77	22	50.66	Dinamica_2
1223	77	23	10.55	Dinamica_3
1224	77	31	96.76	Contenido_1
1225	77	32	73.00	Contenido_2
1226	77	41	59.12	Expansion_1
1227	77	42	46.41	Expansion_2
1228	77	43	45.94	Expansion_3
1229	77	51	42.15	Impacto_1
1230	77	52	57.00	Impacto_2
1231	77	53	31.51	Impacto_3
1232	77	54	52.36	Impacto_4
1233	78	11	31.86	Actores_1
1234	78	12	92.89	Actores_2
1235	78	13	62.17	Actores_3
1236	78	14	72.55	Actores_4
1237	78	21	91.49	Dinamica_1
1238	78	22	27.34	Dinamica_2
1239	78	23	16.34	Dinamica_3
1240	78	31	70.56	Contenido_1
1241	78	32	58.07	Contenido_2
1242	78	41	67.06	Expansion_1
1243	78	42	70.58	Expansion_2
1244	78	43	46.82	Expansion_3
1245	78	51	58.30	Impacto_1
1246	78	52	37.70	Impacto_2
1247	78	53	49.82	Impacto_3
1248	78	54	44.31	Impacto_4
1249	79	11	91.68	Actores_1
1250	79	12	91.81	Actores_2
1251	79	13	94.24	Actores_3
1252	79	14	10.75	Actores_4
1253	79	21	68.17	Dinamica_1
1254	79	22	54.91	Dinamica_2
1255	79	23	89.45	Dinamica_3
1256	79	31	65.12	Contenido_1
1257	79	32	74.23	Contenido_2
1258	79	41	79.60	Expansion_1
1259	79	42	90.17	Expansion_2
1260	79	43	37.04	Expansion_3
1261	79	51	78.07	Impacto_1
1262	79	52	33.58	Impacto_2
1263	79	53	94.31	Impacto_3
1264	79	54	25.73	Impacto_4
1265	80	11	10.79	Actores_1
1266	80	12	72.77	Actores_2
1267	80	13	10.18	Actores_3
1268	80	14	66.38	Actores_4
1269	80	21	48.83	Dinamica_1
1270	80	22	36.25	Dinamica_2
1271	80	23	44.82	Dinamica_3
1272	80	31	89.91	Contenido_1
1273	80	32	45.34	Contenido_2
1274	80	41	83.76	Expansion_1
1275	80	42	70.85	Expansion_2
1276	80	43	85.62	Expansion_3
1277	80	51	64.51	Impacto_1
1278	80	52	26.62	Impacto_2
1279	80	53	13.44	Impacto_3
1280	80	54	66.91	Impacto_4
1281	81	11	59.65	Actores_1
1282	81	12	99.13	Actores_2
1283	81	13	16.42	Actores_3
1284	81	14	91.00	Actores_4
1285	81	21	65.49	Dinamica_1
1286	81	22	17.14	Dinamica_2
1287	81	23	58.79	Dinamica_3
1288	81	31	54.84	Contenido_1
1289	81	32	22.80	Contenido_2
1290	81	41	54.96	Expansion_1
1291	81	42	25.22	Expansion_2
1292	81	43	72.61	Expansion_3
1293	81	51	40.12	Impacto_1
1294	81	52	21.02	Impacto_2
1295	81	53	66.10	Impacto_3
1296	81	54	36.28	Impacto_4
1297	82	11	63.43	Actores_1
1298	82	12	92.87	Actores_2
1299	82	13	85.29	Actores_3
1300	82	14	97.50	Actores_4
1301	82	21	25.05	Dinamica_1
1302	82	22	98.68	Dinamica_2
1303	82	23	47.97	Dinamica_3
1304	82	31	97.17	Contenido_1
1305	82	32	67.79	Contenido_2
1306	82	41	42.05	Expansion_1
1307	82	42	23.54	Expansion_2
1308	82	43	37.66	Expansion_3
1309	82	51	54.92	Impacto_1
1310	82	52	82.72	Impacto_2
1311	82	53	98.50	Impacto_3
1312	82	54	51.00	Impacto_4
1313	83	11	26.69	Actores_1
1314	83	12	45.75	Actores_2
1315	83	13	50.81	Actores_3
1316	83	14	68.79	Actores_4
1317	83	21	48.09	Dinamica_1
1318	83	22	13.79	Dinamica_2
1319	83	23	38.65	Dinamica_3
1320	83	31	99.18	Contenido_1
1321	83	32	35.46	Contenido_2
1322	83	41	13.45	Expansion_1
1323	83	42	35.15	Expansion_2
1324	83	43	22.87	Expansion_3
1325	83	51	86.59	Impacto_1
1326	83	52	64.43	Impacto_2
1327	83	53	56.22	Impacto_3
1328	83	54	74.58	Impacto_4
1329	84	11	70.57	Actores_1
1330	84	12	76.92	Actores_2
1331	84	13	11.21	Actores_3
1332	84	14	91.73	Actores_4
1333	84	21	19.72	Dinamica_1
1334	84	22	65.60	Dinamica_2
1335	84	23	25.38	Dinamica_3
1336	84	31	35.23	Contenido_1
1337	84	32	22.20	Contenido_2
1338	84	41	19.21	Expansion_1
1339	84	42	62.04	Expansion_2
1340	84	43	24.87	Expansion_3
1341	84	51	73.55	Impacto_1
1342	84	52	31.07	Impacto_2
1343	84	53	87.93	Impacto_3
1344	84	54	42.79	Impacto_4
1345	85	11	63.96	Actores_1
1346	85	12	62.89	Actores_2
1347	85	13	42.90	Actores_3
1348	85	14	53.84	Actores_4
1349	85	21	29.69	Dinamica_1
1350	85	22	90.46	Dinamica_2
1351	85	23	31.66	Dinamica_3
1352	85	31	88.60	Contenido_1
1353	85	32	78.47	Contenido_2
1354	85	41	84.16	Expansion_1
1355	85	42	15.95	Expansion_2
1356	85	43	64.46	Expansion_3
1357	85	51	16.61	Impacto_1
1358	85	52	68.27	Impacto_2
1359	85	53	42.12	Impacto_3
1360	85	54	44.70	Impacto_4
1361	86	11	33.74	Actores_1
1362	86	12	29.31	Actores_2
1363	86	13	31.78	Actores_3
1364	86	14	88.34	Actores_4
1365	86	21	20.44	Dinamica_1
1366	86	22	81.77	Dinamica_2
1367	86	23	93.39	Dinamica_3
1368	86	31	64.63	Contenido_1
1369	86	32	38.84	Contenido_2
1370	86	41	83.14	Expansion_1
1371	86	42	39.83	Expansion_2
1372	86	43	17.68	Expansion_3
1373	86	51	43.92	Impacto_1
1374	86	52	18.82	Impacto_2
1375	86	53	39.67	Impacto_3
1376	86	54	84.57	Impacto_4
1377	87	11	59.06	Actores_1
1378	87	12	68.66	Actores_2
1379	87	13	81.88	Actores_3
1380	87	14	88.69	Actores_4
1381	87	21	92.17	Dinamica_1
1382	87	22	42.99	Dinamica_2
1383	87	23	10.37	Dinamica_3
1384	87	31	39.80	Contenido_1
1385	87	32	62.00	Contenido_2
1386	87	41	89.72	Expansion_1
1387	87	42	15.32	Expansion_2
1388	87	43	43.78	Expansion_3
1389	87	51	12.99	Impacto_1
1390	87	52	13.60	Impacto_2
1391	87	53	99.32	Impacto_3
1392	87	54	54.37	Impacto_4
1393	88	11	47.91	Actores_1
1394	88	12	11.23	Actores_2
1395	88	13	46.62	Actores_3
1396	88	14	38.50	Actores_4
1397	88	21	89.98	Dinamica_1
1398	88	22	46.47	Dinamica_2
1399	88	23	88.71	Dinamica_3
1400	88	31	80.94	Contenido_1
1401	88	32	46.46	Contenido_2
1402	88	41	29.62	Expansion_1
1403	88	42	55.28	Expansion_2
1404	88	43	95.75	Expansion_3
1405	88	51	20.12	Impacto_1
1406	88	52	20.36	Impacto_2
1407	88	53	54.94	Impacto_3
1408	88	54	78.81	Impacto_4
1409	89	11	46.03	Actores_1
1410	89	12	11.02	Actores_2
1411	89	13	31.20	Actores_3
1412	89	14	13.04	Actores_4
1413	89	21	47.96	Dinamica_1
1414	89	22	71.24	Dinamica_2
1415	89	23	99.27	Dinamica_3
1416	89	31	26.68	Contenido_1
1417	89	32	72.51	Contenido_2
1418	89	41	46.02	Expansion_1
1419	89	42	30.81	Expansion_2
1420	89	43	69.71	Expansion_3
1421	89	51	88.36	Impacto_1
1422	89	52	77.57	Impacto_2
1423	89	53	68.13	Impacto_3
1424	89	54	60.49	Impacto_4
1425	90	11	34.18	Actores_1
1426	90	12	87.72	Actores_2
1427	90	13	61.27	Actores_3
1428	90	14	22.90	Actores_4
1429	90	21	12.79	Dinamica_1
1430	90	22	78.63	Dinamica_2
1431	90	23	65.56	Dinamica_3
1432	90	31	95.54	Contenido_1
1433	90	32	35.36	Contenido_2
1434	90	41	81.51	Expansion_1
1435	90	42	26.55	Expansion_2
1436	90	43	28.07	Expansion_3
1437	90	51	27.72	Impacto_1
1438	90	52	24.23	Impacto_2
1439	90	53	19.37	Impacto_3
1440	90	54	47.11	Impacto_4
1441	91	11	45.20	Actores_1
1442	91	12	17.41	Actores_2
1443	91	13	20.43	Actores_3
1444	91	14	85.71	Actores_4
1445	91	21	80.38	Dinamica_1
1446	91	22	99.12	Dinamica_2
1447	91	23	41.63	Dinamica_3
1448	91	31	49.94	Contenido_1
1449	91	32	36.81	Contenido_2
1450	91	41	36.26	Expansion_1
1451	91	42	52.10	Expansion_2
1452	91	43	74.41	Expansion_3
1453	91	51	36.84	Impacto_1
1454	91	52	53.65	Impacto_2
1455	91	53	84.92	Impacto_3
1456	91	54	84.24	Impacto_4
1457	92	11	18.01	Actores_1
1458	92	12	86.89	Actores_2
1459	92	13	13.87	Actores_3
1460	92	14	60.49	Actores_4
1461	92	21	13.42	Dinamica_1
1462	92	22	57.26	Dinamica_2
1463	92	23	86.38	Dinamica_3
1464	92	31	80.67	Contenido_1
1465	92	32	69.74	Contenido_2
1466	92	41	85.01	Expansion_1
1467	92	42	49.75	Expansion_2
1468	92	43	35.86	Expansion_3
1469	92	51	17.85	Impacto_1
1470	92	52	52.30	Impacto_2
1471	92	53	69.17	Impacto_3
1472	92	54	88.15	Impacto_4
1473	93	11	44.91	Actores_1
1474	93	12	45.10	Actores_2
1475	93	13	53.78	Actores_3
1476	93	14	66.60	Actores_4
1477	93	21	55.14	Dinamica_1
1478	93	22	80.98	Dinamica_2
1479	93	23	20.41	Dinamica_3
1480	93	31	59.56	Contenido_1
1481	93	32	55.65	Contenido_2
1482	93	41	57.92	Expansion_1
1483	93	42	99.37	Expansion_2
1484	93	43	81.20	Expansion_3
1485	93	51	14.06	Impacto_1
1486	93	52	27.74	Impacto_2
1487	93	53	64.86	Impacto_3
1488	93	54	34.94	Impacto_4
1489	94	11	52.33	Actores_1
1490	94	12	51.14	Actores_2
1491	94	13	74.77	Actores_3
1492	94	14	46.02	Actores_4
1493	94	21	68.10	Dinamica_1
1494	94	22	56.61	Dinamica_2
1495	94	23	15.11	Dinamica_3
1496	94	31	33.71	Contenido_1
1497	94	32	26.07	Contenido_2
1498	94	41	86.49	Expansion_1
1499	94	42	54.53	Expansion_2
1500	94	43	10.49	Expansion_3
1501	94	51	17.29	Impacto_1
1502	94	52	65.07	Impacto_2
1503	94	53	52.73	Impacto_3
1504	94	54	61.51	Impacto_4
1505	95	11	38.08	Actores_1
1506	95	12	58.95	Actores_2
1507	95	13	73.55	Actores_3
1508	95	14	66.35	Actores_4
1509	95	21	12.69	Dinamica_1
1510	95	22	58.85	Dinamica_2
1511	95	23	25.78	Dinamica_3
1512	95	31	11.48	Contenido_1
1513	95	32	12.74	Contenido_2
1514	95	41	68.39	Expansion_1
1515	95	42	94.70	Expansion_2
1516	95	43	45.23	Expansion_3
1517	95	51	82.65	Impacto_1
1518	95	52	64.07	Impacto_2
1519	95	53	68.06	Impacto_3
1520	95	54	57.91	Impacto_4
1521	96	11	99.52	Actores_1
1522	96	12	29.76	Actores_2
1523	96	13	26.06	Actores_3
1524	96	14	91.81	Actores_4
1525	96	21	29.24	Dinamica_1
1526	96	22	85.18	Dinamica_2
1527	96	23	99.10	Dinamica_3
1528	96	31	45.04	Contenido_1
1529	96	32	41.51	Contenido_2
1530	96	41	77.68	Expansion_1
1531	96	42	80.53	Expansion_2
1532	96	43	96.88	Expansion_3
1533	96	51	11.52	Impacto_1
1534	96	52	75.61	Impacto_2
1535	96	53	86.98	Impacto_3
1536	96	54	87.99	Impacto_4
1537	97	11	76.37	Actores_1
1538	97	12	39.42	Actores_2
1539	97	13	64.39	Actores_3
1540	97	14	21.86	Actores_4
1541	97	21	11.64	Dinamica_1
1542	97	22	49.51	Dinamica_2
1543	97	23	58.40	Dinamica_3
1544	97	31	26.99	Contenido_1
1545	97	32	96.15	Contenido_2
1546	97	41	39.05	Expansion_1
1547	97	42	77.47	Expansion_2
1548	97	43	85.87	Expansion_3
1549	97	51	25.48	Impacto_1
1550	97	52	77.48	Impacto_2
1551	97	53	24.71	Impacto_3
1552	97	54	25.37	Impacto_4
1553	98	11	97.80	Actores_1
1554	98	12	85.91	Actores_2
1555	98	13	95.67	Actores_3
1556	98	14	78.32	Actores_4
1557	98	21	58.03	Dinamica_1
1558	98	22	98.89	Dinamica_2
1559	98	23	59.58	Dinamica_3
1560	98	31	82.05	Contenido_1
1561	98	32	20.78	Contenido_2
1562	98	41	88.86	Expansion_1
1563	98	42	61.29	Expansion_2
1564	98	43	87.97	Expansion_3
1565	98	51	51.53	Impacto_1
1566	98	52	51.11	Impacto_2
1567	98	53	62.02	Impacto_3
1568	98	54	10.71	Impacto_4
1569	99	11	48.83	Actores_1
1570	99	12	33.97	Actores_2
1571	99	13	96.03	Actores_3
1572	99	14	27.37	Actores_4
1573	99	21	79.41	Dinamica_1
1574	99	22	21.32	Dinamica_2
1575	99	23	10.19	Dinamica_3
1576	99	31	18.31	Contenido_1
1577	99	32	56.62	Contenido_2
1578	99	41	87.60	Expansion_1
1579	99	42	82.40	Expansion_2
1580	99	43	49.97	Expansion_3
1581	99	51	85.41	Impacto_1
1582	99	52	19.16	Impacto_2
1583	99	53	95.98	Impacto_3
1584	99	54	35.62	Impacto_4
1585	100	11	60.05	Actores_1
1586	100	12	77.62	Actores_2
1587	100	13	57.08	Actores_3
1588	100	14	78.97	Actores_4
1589	100	21	95.83	Dinamica_1
1590	100	22	53.82	Dinamica_2
1591	100	23	85.11	Dinamica_3
1592	100	31	93.86	Contenido_1
1593	100	32	72.17	Contenido_2
1594	100	41	96.97	Expansion_1
1595	100	42	29.45	Expansion_2
1596	100	43	10.15	Expansion_3
1597	100	51	73.05	Impacto_1
1598	100	52	42.20	Impacto_2
1599	100	53	26.80	Impacto_3
1600	100	54	48.57	Impacto_4
\.


--
-- Data for Name: senal_detectada; Type: TABLE DATA; Schema: sds; Owner: -
--

COPY sds.senal_detectada (id_senal_detectada, id_categoria_senal, fecha_deteccion, id_categoria_analisis_senal, score_riesgo, fecha_actualizacion) FROM stdin;
2	1	2025-12-02 17:16:23.811753+00	2	50.21	2025-12-02 17:16:23.811753+00
3	1	2025-12-03 17:06:39.088268+00	1	14.37	2025-12-03 17:06:39.088268+00
5	1	2025-12-02 23:04:11.672164+00	1	66.61	2025-12-02 23:04:11.672164+00
6	1	2025-12-02 15:39:16.411814+00	1	82.51	2025-12-02 15:39:16.411814+00
13	1	2025-12-03 22:31:02.014623+00	2	82.89	2025-12-03 22:31:02.014623+00
14	1	2025-12-05 07:24:08.238244+00	2	35.80	2025-12-05 07:24:08.238244+00
15	1	2025-12-02 05:01:50.396475+00	3	98.80	2025-12-02 05:01:50.396475+00
17	1	2025-12-01 10:10:11.979889+00	2	71.60	2025-12-01 10:10:11.979889+00
19	1	2025-12-05 19:03:40.303849+00	3	36.08	2025-12-05 19:03:40.303849+00
24	1	2025-12-02 12:21:32.403371+00	2	27.48	2025-12-02 12:21:32.403371+00
26	1	2025-12-02 01:37:35.283368+00	2	89.17	2025-12-02 01:37:35.283368+00
27	1	2025-12-04 12:11:16.662758+00	2	16.58	2025-12-04 12:11:16.662758+00
29	1	2025-12-01 02:54:05.244478+00	1	27.40	2025-12-01 02:54:05.244478+00
30	1	2025-12-01 22:20:47.667079+00	2	57.47	2025-12-01 22:20:47.667079+00
32	1	2025-12-04 14:35:15.481623+00	2	97.77	2025-12-04 14:35:15.481623+00
35	1	2025-12-01 06:32:14.746046+00	2	63.36	2025-12-01 06:32:14.746046+00
37	1	2025-12-01 12:19:31.239111+00	3	90.41	2025-12-01 12:19:31.239111+00
38	1	2025-12-02 03:08:11.96895+00	2	14.49	2025-12-02 03:08:11.96895+00
42	1	2025-12-02 22:45:27.782766+00	3	67.06	2025-12-02 22:45:27.782766+00
44	1	2025-12-02 20:29:25.634863+00	2	28.94	2025-12-02 20:29:25.634863+00
45	1	2025-12-04 13:36:56.096273+00	1	42.63	2025-12-04 13:36:56.096273+00
46	1	2025-12-01 20:36:24.052846+00	3	12.41	2025-12-01 20:36:24.052846+00
48	1	2025-12-02 11:33:53.453882+00	1	40.04	2025-12-02 11:33:53.453882+00
49	1	2025-12-03 20:02:20.608862+00	2	60.68	2025-12-03 20:02:20.608862+00
51	1	2025-12-01 21:57:04.119747+00	1	71.32	2025-12-01 21:57:04.119747+00
52	1	2025-12-05 21:39:51.928432+00	2	19.61	2025-12-05 21:39:51.928432+00
53	1	2025-12-05 21:50:19.426831+00	2	77.39	2025-12-05 21:50:19.426831+00
54	1	2025-12-02 17:38:41.208947+00	1	40.37	2025-12-02 17:38:41.208947+00
55	1	2025-12-03 08:48:47.127545+00	1	96.09	2025-12-03 08:48:47.127545+00
56	1	2025-12-03 07:07:31.639724+00	2	40.63	2025-12-03 07:07:31.639724+00
57	1	2025-12-05 15:11:21.220163+00	3	79.41	2025-12-05 15:11:21.220163+00
61	1	2025-12-03 16:55:18.47604+00	1	45.08	2025-12-03 16:55:18.47604+00
67	1	2025-12-04 12:46:43.873258+00	1	94.99	2025-12-04 12:46:43.873258+00
75	1	2025-12-01 18:29:07.046296+00	2	24.62	2025-12-01 18:29:07.046296+00
76	1	2025-12-05 05:12:30.382346+00	3	29.90	2025-12-05 05:12:30.382346+00
78	1	2025-12-03 23:38:29.981287+00	2	84.46	2025-12-03 23:38:29.981287+00
79	1	2025-12-05 03:12:04.366738+00	3	19.19	2025-12-05 03:12:04.366738+00
81	1	2025-12-04 11:59:30.389493+00	2	39.60	2025-12-04 11:59:30.389493+00
87	1	2025-12-03 20:00:20.495956+00	3	67.33	2025-12-03 20:00:20.495956+00
91	1	2025-12-03 16:56:21.285103+00	3	48.55	2025-12-03 16:56:21.285103+00
95	1	2025-12-05 03:51:02.040652+00	3	22.86	2025-12-05 03:51:02.040652+00
98	1	2025-12-01 23:13:26.114052+00	1	66.29	2025-12-01 23:13:26.114052+00
100	1	2025-12-05 22:49:57.521987+00	3	26.62	2025-12-05 22:49:57.521987+00
1	3	2026-01-19 17:42:54.36548+00	2	61.01	2026-01-19 06:30:19.423596+00
4	3	2026-01-19 19:29:42.820173+00	3	47.51	2026-01-19 06:30:19.423596+00
7	3	2026-01-19 05:06:07.307882+00	1	82.17	2026-01-19 06:30:19.423596+00
8	3	2026-01-19 07:28:34.136763+00	2	65.50	2026-01-19 06:30:19.423596+00
9	2	2026-01-19 16:23:11.670635+00	3	69.71	2026-01-19 06:30:19.423596+00
10	2	2026-01-19 03:40:36.754528+00	3	79.01	2026-01-19 06:30:19.423596+00
11	2	2026-01-19 14:40:22.525699+00	1	63.50	2026-01-19 06:30:19.423596+00
12	3	2026-01-19 12:38:25.2194+00	2	21.82	2026-01-19 06:30:19.423596+00
16	3	2026-01-19 20:20:09.420091+00	2	97.64	2026-01-19 06:30:19.423596+00
18	3	2026-01-19 07:31:31.848135+00	1	89.26	2026-01-19 06:30:19.423596+00
20	3	2026-01-19 19:17:52.514996+00	3	49.93	2026-01-19 06:30:19.423596+00
21	3	2026-01-19 16:55:34.047618+00	1	22.65	2026-01-19 06:30:19.423596+00
22	2	2026-01-19 06:00:14.842438+00	1	59.27	2026-01-19 06:30:19.423596+00
23	2	2026-01-19 03:44:57.520597+00	1	96.35	2026-01-19 06:30:19.423596+00
25	2	2026-01-19 21:29:09.839461+00	2	52.78	2026-01-19 06:30:19.423596+00
28	3	2026-01-19 04:06:14.541984+00	3	12.41	2026-01-19 06:30:19.423596+00
31	2	2026-01-19 07:16:05.190865+00	1	79.58	2026-01-19 06:30:19.423596+00
33	2	2026-01-19 08:55:24.168178+00	1	93.15	2026-01-19 06:30:19.423596+00
34	2	2026-01-19 13:25:10.485723+00	2	90.05	2026-01-19 06:30:19.423596+00
36	3	2026-01-19 18:26:07.400858+00	1	53.30	2026-01-19 06:30:19.423596+00
39	2	2026-01-19 15:00:26.286183+00	2	68.97	2026-01-19 06:30:19.423596+00
40	2	2026-01-19 13:35:26.552913+00	2	84.63	2026-01-19 06:30:19.423596+00
41	3	2026-01-19 22:28:54.868087+00	2	89.50	2026-01-19 06:30:19.423596+00
43	2	2026-01-19 05:58:51.441843+00	1	14.28	2026-01-19 06:30:19.423596+00
47	2	2026-01-19 04:53:26.574798+00	1	24.89	2026-01-19 06:30:19.423596+00
50	3	2026-01-19 14:22:51.035495+00	2	80.97	2026-01-19 06:30:19.423596+00
58	2	2026-01-19 21:25:25.432425+00	3	52.26	2026-01-19 06:30:19.423596+00
59	2	2026-01-19 14:17:57.474231+00	2	60.55	2026-01-19 06:30:19.423596+00
60	3	2026-01-19 17:30:31.058061+00	1	15.83	2026-01-19 06:30:19.423596+00
62	2	2026-01-19 14:20:44.722692+00	1	96.80	2026-01-19 06:30:19.423596+00
63	3	2026-01-19 17:35:22.16342+00	3	19.81	2026-01-19 06:30:19.423596+00
64	2	2026-01-19 19:39:23.149472+00	2	39.83	2026-01-19 06:30:19.423596+00
65	2	2026-01-19 19:39:26.187419+00	1	36.93	2026-01-19 06:30:19.423596+00
66	2	2026-01-19 21:33:23.061317+00	2	86.53	2026-01-19 06:30:19.423596+00
68	3	2026-01-19 06:50:41.700457+00	2	87.32	2026-01-19 06:30:19.423596+00
69	3	2026-01-19 19:38:39.163388+00	1	54.28	2026-01-19 06:30:19.423596+00
70	3	2026-01-19 12:59:24.085799+00	2	30.00	2026-01-19 06:30:19.423596+00
71	2	2026-01-19 23:31:56.148136+00	3	89.13	2026-01-19 06:30:19.423596+00
72	2	2026-01-19 06:22:12.139589+00	1	18.59	2026-01-19 06:30:19.423596+00
73	3	2026-01-19 02:39:36.087353+00	2	81.59	2026-01-19 06:30:19.423596+00
74	3	2026-01-19 05:32:12.414915+00	3	25.56	2026-01-19 06:30:19.423596+00
77	2	2026-01-19 10:45:24.110657+00	1	23.36	2026-01-19 06:30:19.423596+00
80	3	2026-01-19 22:50:48.959874+00	1	11.59	2026-01-19 06:30:19.423596+00
82	2	2026-01-19 18:33:38.594856+00	3	12.66	2026-01-19 06:30:19.423596+00
83	2	2026-01-19 02:49:54.613077+00	3	77.98	2026-01-19 06:30:19.423596+00
84	2	2026-01-19 04:13:06.822435+00	1	80.76	2026-01-19 06:30:19.423596+00
85	2	2026-01-19 02:08:29.006284+00	2	68.66	2026-01-19 06:30:19.423596+00
86	2	2026-01-19 13:08:18.075147+00	1	35.17	2026-01-19 06:30:19.423596+00
88	2	2026-01-19 05:12:30.346164+00	2	11.42	2026-01-19 06:30:19.423596+00
89	2	2026-01-19 20:52:25.52253+00	3	79.02	2026-01-19 06:30:19.423596+00
90	2	2026-01-19 08:47:38.263424+00	1	98.74	2026-01-19 06:30:19.423596+00
92	2	2026-01-19 18:09:20.383862+00	2	41.09	2026-01-19 06:30:19.423596+00
93	2	2026-01-19 12:56:17.823559+00	1	53.82	2026-01-19 06:30:19.423596+00
94	2	2026-01-19 10:30:07.232143+00	2	20.60	2026-01-19 06:30:19.423596+00
96	3	2026-01-19 22:10:48.994857+00	2	99.60	2026-01-19 06:30:19.423596+00
97	2	2026-01-19 04:01:33.440924+00	2	87.72	2026-01-19 06:30:19.423596+00
99	2	2026-01-19 02:37:42.389354+00	2	87.65	2026-01-19 06:30:19.423596+00
\.


--
-- Name: configuracion_sistema_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.configuracion_sistema_id_seq', 1, false);


--
-- Name: eventos_auditoria_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.eventos_auditoria_id_seq', 11, true);


--
-- Name: password_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.password_history_id_seq', 1, false);


--
-- Name: permisos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.permisos_id_seq', 18, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.roles_id_seq', 4, true);


--
-- Name: sesiones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sesiones_id_seq', 114, true);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 2, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: configuracion_sistema configuracion_sistema_clave_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configuracion_sistema
    ADD CONSTRAINT configuracion_sistema_clave_key UNIQUE (clave);


--
-- Name: configuracion_sistema configuracion_sistema_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configuracion_sistema
    ADD CONSTRAINT configuracion_sistema_pkey PRIMARY KEY (id);


--
-- Name: eventos_auditoria eventos_auditoria_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eventos_auditoria
    ADD CONSTRAINT eventos_auditoria_pkey PRIMARY KEY (id);


--
-- Name: password_history password_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_history
    ADD CONSTRAINT password_history_pkey PRIMARY KEY (id);


--
-- Name: permisos permisos_codigo_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permisos
    ADD CONSTRAINT permisos_codigo_key UNIQUE (codigo);


--
-- Name: permisos permisos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permisos
    ADD CONSTRAINT permisos_pkey PRIMARY KEY (id);


--
-- Name: roles roles_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_nombre_key UNIQUE (nombre);


--
-- Name: roles_permisos roles_permisos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles_permisos
    ADD CONSTRAINT roles_permisos_pkey PRIMARY KEY (rol_id, permiso_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: sesiones sesiones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sesiones
    ADD CONSTRAINT sesiones_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- Name: usuarios usuarios_nombre_usuario_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_nombre_usuario_key UNIQUE (nombre_usuario);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: usuarios_roles usuarios_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios_roles
    ADD CONSTRAINT usuarios_roles_pkey PRIMARY KEY (usuario_id, rol_id);


--
-- Name: categoria_analisis_senal categoria_analisis_senal_pkey; Type: CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.categoria_analisis_senal
    ADD CONSTRAINT categoria_analisis_senal_pkey PRIMARY KEY (id_categoria_analisis_senal);


--
-- Name: categoria_observacion categoria_observacion_pkey; Type: CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.categoria_observacion
    ADD CONSTRAINT categoria_observacion_pkey PRIMARY KEY (id_categoria_observacion);


--
-- Name: categoria_senal categoria_senal_pkey; Type: CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.categoria_senal
    ADD CONSTRAINT categoria_senal_pkey PRIMARY KEY (id_categoria_senales);


--
-- Name: conducta_vulneratoria conducta_vulneratoria_pkey; Type: CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.conducta_vulneratoria
    ADD CONSTRAINT conducta_vulneratoria_pkey PRIMARY KEY (id_conducta_vulneratorias);


--
-- Name: emoticon emoticon_pkey; Type: CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.emoticon
    ADD CONSTRAINT emoticon_pkey PRIMARY KEY (id_emoticon);


--
-- Name: entidades entidades_pkey; Type: CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.entidades
    ADD CONSTRAINT entidades_pkey PRIMARY KEY (id_entidades);


--
-- Name: figuras_publicas figuras_publicas_pkey; Type: CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.figuras_publicas
    ADD CONSTRAINT figuras_publicas_pkey PRIMARY KEY (id_figura_publica);


--
-- Name: frase_clave frase_clave_pkey; Type: CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.frase_clave
    ADD CONSTRAINT frase_clave_pkey PRIMARY KEY (id_frase_clave);


--
-- Name: influencers influencers_pkey; Type: CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.influencers
    ADD CONSTRAINT influencers_pkey PRIMARY KEY (id_influencer);


--
-- Name: medios_digitales medios_digitales_pkey; Type: CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.medios_digitales
    ADD CONSTRAINT medios_digitales_pkey PRIMARY KEY (id_medio_digital);


--
-- Name: palabra_clave palabra_clave_pkey; Type: CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.palabra_clave
    ADD CONSTRAINT palabra_clave_pkey PRIMARY KEY (id_palabra_clave);


--
-- Name: resultado_observacion_senal resultado_observacion_senal_pkey; Type: CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.resultado_observacion_senal
    ADD CONSTRAINT resultado_observacion_senal_pkey PRIMARY KEY (id_resultado_observacion_senal);


--
-- Name: senal_detectada senal_detectada_pkey; Type: CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.senal_detectada
    ADD CONSTRAINT senal_detectada_pkey PRIMARY KEY (id_senal_detectada);


--
-- Name: idx_usuario_reset_token; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_usuario_reset_token ON public.usuarios USING btree (reset_token);


--
-- Name: ix_configuracion_sistema_categoria; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_configuracion_sistema_categoria ON public.configuracion_sistema USING btree (categoria);


--
-- Name: ix_configuracion_sistema_clave; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_configuracion_sistema_clave ON public.configuracion_sistema USING btree (clave);


--
-- Name: ix_eventos_auditoria_fecha_evento; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_eventos_auditoria_fecha_evento ON public.eventos_auditoria USING btree (fecha_evento);


--
-- Name: ix_eventos_auditoria_resultado; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_eventos_auditoria_resultado ON public.eventos_auditoria USING btree (resultado);


--
-- Name: ix_eventos_auditoria_tipo_evento; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_eventos_auditoria_tipo_evento ON public.eventos_auditoria USING btree (tipo_evento);


--
-- Name: ix_eventos_auditoria_usuario_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_eventos_auditoria_usuario_id ON public.eventos_auditoria USING btree (usuario_id);


--
-- Name: ix_password_history_fecha_creacion; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_password_history_fecha_creacion ON public.password_history USING btree (fecha_creacion);


--
-- Name: ix_password_history_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_password_history_id ON public.password_history USING btree (id);


--
-- Name: ix_password_history_usuario_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_password_history_usuario_id ON public.password_history USING btree (usuario_id);


--
-- Name: ix_permisos_codigo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_permisos_codigo ON public.permisos USING btree (codigo);


--
-- Name: ix_permisos_recurso; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_permisos_recurso ON public.permisos USING btree (recurso);


--
-- Name: ix_roles_activo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_roles_activo ON public.roles USING btree (activo);


--
-- Name: ix_roles_nombre; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_roles_nombre ON public.roles USING btree (nombre);


--
-- Name: ix_roles_permisos_permiso_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_roles_permisos_permiso_id ON public.roles_permisos USING btree (permiso_id);


--
-- Name: ix_roles_permisos_rol_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_roles_permisos_rol_id ON public.roles_permisos USING btree (rol_id);


--
-- Name: ix_sesiones_fecha_expiracion; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_sesiones_fecha_expiracion ON public.sesiones USING btree (fecha_expiracion);


--
-- Name: ix_sesiones_usuario_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_sesiones_usuario_id ON public.sesiones USING btree (usuario_id);


--
-- Name: ix_sesiones_valida; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_sesiones_valida ON public.sesiones USING btree (valida);


--
-- Name: ix_usuarios_activo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_usuarios_activo ON public.usuarios USING btree (activo);


--
-- Name: ix_usuarios_email; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_usuarios_email ON public.usuarios USING btree (email);


--
-- Name: ix_usuarios_id_externo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_usuarios_id_externo ON public.usuarios USING btree (id_externo);


--
-- Name: ix_usuarios_nombre_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_usuarios_nombre_usuario ON public.usuarios USING btree (nombre_usuario);


--
-- Name: ix_usuarios_roles_rol_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_usuarios_roles_rol_id ON public.usuarios_roles USING btree (rol_id);


--
-- Name: ix_usuarios_roles_usuario_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_usuarios_roles_usuario_id ON public.usuarios_roles USING btree (usuario_id);


--
-- Name: eventos_auditoria eventos_auditoria_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eventos_auditoria
    ADD CONSTRAINT eventos_auditoria_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: password_history password_history_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_history
    ADD CONSTRAINT password_history_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: roles_permisos roles_permisos_permiso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles_permisos
    ADD CONSTRAINT roles_permisos_permiso_id_fkey FOREIGN KEY (permiso_id) REFERENCES public.permisos(id) ON DELETE CASCADE;


--
-- Name: roles_permisos roles_permisos_rol_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles_permisos
    ADD CONSTRAINT roles_permisos_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: sesiones sesiones_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sesiones
    ADD CONSTRAINT sesiones_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: usuarios_roles usuarios_roles_rol_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios_roles
    ADD CONSTRAINT usuarios_roles_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: usuarios_roles usuarios_roles_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios_roles
    ADD CONSTRAINT usuarios_roles_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: conducta_vulneratoria fk_conducta_categoria_analisis; Type: FK CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.conducta_vulneratoria
    ADD CONSTRAINT fk_conducta_categoria_analisis FOREIGN KEY (id_categoria_analisis_senal) REFERENCES sds.categoria_analisis_senal(id_categoria_analisis_senal);


--
-- Name: emoticon fk_emoticon_categoria_analisis; Type: FK CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.emoticon
    ADD CONSTRAINT fk_emoticon_categoria_analisis FOREIGN KEY (id_categoria_analisis_senal) REFERENCES sds.categoria_analisis_senal(id_categoria_analisis_senal);


--
-- Name: entidades fk_entidades_cat_observacion; Type: FK CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.entidades
    ADD CONSTRAINT fk_entidades_cat_observacion FOREIGN KEY (id_categoria_observacion) REFERENCES sds.categoria_observacion(id_categoria_observacion);


--
-- Name: figuras_publicas fk_fig_publica_cat_observacion; Type: FK CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.figuras_publicas
    ADD CONSTRAINT fk_fig_publica_cat_observacion FOREIGN KEY (id_categoria_observacion) REFERENCES sds.categoria_observacion(id_categoria_observacion);


--
-- Name: frase_clave fk_frase_categoria_analisis; Type: FK CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.frase_clave
    ADD CONSTRAINT fk_frase_categoria_analisis FOREIGN KEY (id_categoria_analisis_senal) REFERENCES sds.categoria_analisis_senal(id_categoria_analisis_senal);


--
-- Name: influencers fk_influencers_cat_observacion; Type: FK CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.influencers
    ADD CONSTRAINT fk_influencers_cat_observacion FOREIGN KEY (id_categoria_observacion) REFERENCES sds.categoria_observacion(id_categoria_observacion);


--
-- Name: medios_digitales fk_medios_digitales_cat_observacion; Type: FK CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.medios_digitales
    ADD CONSTRAINT fk_medios_digitales_cat_observacion FOREIGN KEY (id_categoria_observacion) REFERENCES sds.categoria_observacion(id_categoria_observacion);


--
-- Name: palabra_clave fk_palabra_categoria_analisis; Type: FK CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.palabra_clave
    ADD CONSTRAINT fk_palabra_categoria_analisis FOREIGN KEY (id_categoria_analisis_senal) REFERENCES sds.categoria_analisis_senal(id_categoria_analisis_senal);


--
-- Name: resultado_observacion_senal fk_res_obs_categoria; Type: FK CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.resultado_observacion_senal
    ADD CONSTRAINT fk_res_obs_categoria FOREIGN KEY (id_categoria_observacion) REFERENCES sds.categoria_observacion(id_categoria_observacion);


--
-- Name: resultado_observacion_senal fk_res_obs_senal; Type: FK CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.resultado_observacion_senal
    ADD CONSTRAINT fk_res_obs_senal FOREIGN KEY (id_senal_detectada) REFERENCES sds.senal_detectada(id_senal_detectada);


--
-- Name: senal_detectada fk_senal_categoria_analisis; Type: FK CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.senal_detectada
    ADD CONSTRAINT fk_senal_categoria_analisis FOREIGN KEY (id_categoria_analisis_senal) REFERENCES sds.categoria_analisis_senal(id_categoria_analisis_senal);


--
-- Name: senal_detectada fk_senal_categoria_senal; Type: FK CONSTRAINT; Schema: sds; Owner: -
--

ALTER TABLE ONLY sds.senal_detectada
    ADD CONSTRAINT fk_senal_categoria_senal FOREIGN KEY (id_categoria_senal) REFERENCES sds.categoria_senal(id_categoria_senales);


--
-- PostgreSQL database dump complete
--

\unrestrict HSbW9pmMczipLmXjanGd2FAG0xd0tXHRfzFNzdxyxNmoE6xdS7kaj3YDH1Jhv7n

