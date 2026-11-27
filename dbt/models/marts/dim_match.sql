-- dim_match: one row per match. Primary key: match_id.

WITH matches AS (
    SELECT * FROM {{ ref('stg_matches') }}
),

final AS (
    SELECT
        match_id,
        match_date,
        kick_off,
        competition_id,
        season_id,
        home_team_id,
        away_team_id,
        home_score,
        away_score,
        CASE
            WHEN home_score > away_score THEN 'home_win'
            WHEN home_score < away_score THEN 'away_win'
            WHEN home_score = away_score THEN 'draw'
            ELSE NULL
        END AS match_result,
        match_status,
        source_last_updated
    FROM matches
)

SELECT * FROM final