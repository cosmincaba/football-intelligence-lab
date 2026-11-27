-- dim_match: one row per match.
--
-- What is a "dimension"?
--   A dimension table describes the "things" we analyse (here: matches).
--   Fact tables (like fct_events later) store what HAPPENED and point to a
--   dimension by its key (match_id). So every event can look up its match here.
--
-- Grain (what one row means): one StatsBomb match.
-- Primary key: match_id (tested as unique + not_null in dim_match.yml).
-- Source: stg_matches, which already has one row per match and typed columns.

WITH matches AS (

    -- Step 1: read the staging model.
    -- ref() tells dbt "this model depends on stg_matches", so dbt builds
    -- stg_matches first and draws the arrow in the lineage graph.
    SELECT *
    FROM {{ ref('stg_matches') }}

),

final AS (

    -- Step 2: keep only the columns that DESCRIBE a match.
    SELECT
        -- The key. Fact tables will join to dim_match on this column.
        match_id,

        -- When the match was played.
        match_date,
        kick_off,

        -- Which tournament and season the match belongs to.
        -- (Only ids for now. A dim_competition could hold the names later.)
        competition_id,
        season_id,

        -- Who played. We keep only the team IDS, not the names.
        -- The names live in dim_team, so they are stored in one place only.
        -- To get a name, join: dim_match.home_team_id = dim_team.team_id
        home_team_id,
        away_team_id,

        -- Final score.
        home_score,
        away_score,

        -- A small calculated column, so the dashboard does not have to
        -- repeat this logic. CASE works like IF / ELSE IF / ELSE.
        CASE
            WHEN home_score > away_score THEN 'home_win'
            WHEN home_score < away_score THEN 'away_win'
            WHEN home_score = away_score THEN 'draw'
            ELSE NULL  -- a score is missing, so we cannot say
        END AS match_result,

        -- StatsBomb's status for the match data (for example 'available').
        match_status,

        -- When StatsBomb last changed this match record. Useful to know
        -- which data version an analysis was built on.
        source_last_updated

    FROM matches

)

SELECT *
FROM final
