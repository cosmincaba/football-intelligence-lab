
{{ config(materialized='table') }}

WITH expanded AS (
    SELECT
        r.match_id,
        r.source_file_path,
        r.content_hash,
        r.ingested_at,
        r.updated_at AS raw_updated_at,
        e.event AS event_json,
        e.ordinality AS event_array_position
    FROM {{ source('raw', 'events_json') }} AS r
    CROSS JOIN LATERAL jsonb_array_elements(r.payload)
        WITH ORDINALITY AS e(event, ordinality)
),

staged AS (
    SELECT
        (event_json->>'id')::UUID AS event_id,
        match_id,
        event_array_position,
        (event_json->>'index')::INTEGER AS event_index,
        (event_json->>'period')::INTEGER AS event_period,
        (event_json->>'timestamp')::TIME AS event_timestamp,
        (event_json->>'minute')::INTEGER AS event_minute,
        (event_json->>'second')::INTEGER AS event_second,

        (event_json->'type'->>'id')::INTEGER AS event_type_id,
        event_json->'type'->>'name' AS event_type_name,

        (event_json->'team'->>'id')::INTEGER AS team_id,
        event_json->'team'->>'name' AS team_name,

        (event_json->'player'->>'id')::INTEGER AS player_id,
        event_json->'player'->>'name' AS player_name,

        (event_json->'position'->>'id')::INTEGER AS position_id,
        event_json->'position'->>'name' AS position_name,

        (event_json->>'possession')::INTEGER AS possession,
        (event_json->'possession_team'->>'id')::INTEGER
            AS possession_team_id,
        event_json->'possession_team'->>'name'
            AS possession_team_name,

        (event_json->'play_pattern'->>'id')::INTEGER
            AS play_pattern_id,
        event_json->'play_pattern'->>'name'
            AS play_pattern_name,

        (event_json->'location'->>0)::NUMERIC AS location_x,
        (event_json->'location'->>1)::NUMERIC AS location_y,
        (event_json->>'duration')::NUMERIC AS duration,

        event_json,
        source_file_path,
        content_hash,
        ingested_at,
        raw_updated_at
    FROM expanded
)

SELECT *
FROM staged
