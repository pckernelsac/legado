-- ============================================================================
-- Extensiones requeridas por Legado Eterno.
-- Se ejecuta una sola vez al inicializar el volumen de datos.
-- ============================================================================

-- Búsqueda fuzzy / similitud (autocompletado de nombres de memoriales).
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Funciones criptográficas (gen_random_bytes para tokens, etc.).
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Sin acentos para búsquedas (José == Jose).
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Estadísticas de queries para tuning de performance.
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- NOTA: Los UUIDv7 se generan en la capa de aplicación (app/core/identifiers.py)
-- para garantizar compatibilidad y ordenación temporal independiente del motor.
