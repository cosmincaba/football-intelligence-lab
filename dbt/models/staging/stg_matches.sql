
WITH source AS (
    SELECT *
    FROM {{ source('raw', 'matches_json') }}
),

staged AS (
    SELECT
        (payload->>'match_id')::INTEGER AS match_id,
        (payload->>'match_date')::DATE AS match_date,
        (payload->>'kick_off')::TIME AS kick_off,

        (payload->'competition'->>'competition_id')::INTEGER AS competition_id,
        (payload->'season'->>'season_id')::INTEGER AS season_id,

        (payload->'home_team'->>'home_team_id')::INTEGER AS home_team_id,
        payload->'home_team'->>'home_team_name' AS home_team_name,

        (payload->'away_team'->>'away_team_id')::INTEGER AS away_team_id,
        payload->'away_team'->>'away_team_name' AS away_team_name,

        (payload->>'home_score')::INTEGER AS home_score,
        (payload->>'away_score')::INTEGER AS away_score,

        payload->>'match_status' AS match_status,

        (payload->>'last_updated')::TIMESTAMP AS source_last_updated,
        (payload->>'last_updated_360')::TIMESTAMP AS source_last_updated_360,

        source_file_path,
        content_hash,
        ingested_at,
        updated_at AS raw_updated_at

    FROM source
)

SELECT *
FROM staged
