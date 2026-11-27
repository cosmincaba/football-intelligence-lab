WITH events AS (
    SELECT event_json
    FROM {{ ref('stg_events') }}
    WHERE event_json -> 'player' IS NOT NULL
),

final AS (
    SELECT DISTINCT
        (event_json -> 'player' ->> 'id')::int AS player_id,
        event_json -> 'player' ->> 'name' AS player_name
    FROM events
)

SELECT * FROM final