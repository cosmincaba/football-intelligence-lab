
SELECT
    match_id,
    event_index,
    COUNT(*) AS duplicate_count
FROM {{ ref('stg_events') }}
GROUP BY match_id, event_index
HAVING COUNT(*) > 1
