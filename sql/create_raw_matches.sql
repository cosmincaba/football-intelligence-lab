-- raw schema

CREATE SCHEMA IF NOT EXISTS raw;

-- table

CREATE TABLE IF NOT EXISTS raw.matches_json(
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
    ,source_file_path TEXT NOT NULL UNIQUE
    ,payload JSONB NOT NULL
    ,content_hash CHAR(64) NOT NULL
    ,ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    ,updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()  
);