{{ config(materialized='table') }}

WITH shots AS (
    SELECT *
    FROM {{ ref('fct_events') }}
    WHERE event_type_name = 'Shot'
),

final AS (
    SELECT
        event_id,
        match_id,
        team_id,
        player_id,

        event_period,
        event_minute,
        event_second,

        location_x,
        location_y,
        (event_json -> 'shot' -> 'end_location' ->> 0)::numeric AS end_location_x,
        (event_json -> 'shot' -> 'end_location' ->> 1)::numeric AS end_location_y,

        (event_json -> 'shot' ->> 'statsbomb_xg')::numeric AS statsbomb_xg,
        event_json -> 'shot' -> 'outcome' ->> 'name' AS shot_outcome,
        event_json -> 'shot' -> 'body_part' ->> 'name' AS body_part,
        event_json -> 'shot' -> 'technique' ->> 'name' AS technique,
        event_json -> 'shot' -> 'type'      ->> 'name' AS shot_type,

        (event_json -> 'shot' -> 'outcome' ->> 'name') = 'Goal' AS is_goal,

        event_json -> 'shot' ->> 'key_pass_id' AS key_pass_id
    
    FROM shots
)

SELECT * FROM final