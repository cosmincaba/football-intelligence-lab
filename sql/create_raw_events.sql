CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.events_json (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    source_file_path TEXT NOT NULL UNIQUE,
    match_id INT NOT NULL,

    payload JSONB NOT NULL,
    content_hash VARCHAR(64) NOT NULL,

    source_commit_sha TEXT,

    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_raw_events_match_id
        UNIQUE (match_id),

    CONSTRAINT chk_events_content_hash_format
        CHECK (content_hash ~ '^[0-9a-f]{64}$')
);
