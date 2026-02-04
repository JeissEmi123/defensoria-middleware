-- Reset schemas for full replace (let dump recreate sds)
DROP SCHEMA IF EXISTS sds CASCADE;
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
