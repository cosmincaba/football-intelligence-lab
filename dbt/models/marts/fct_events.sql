SELECT
    event_id,
    match_id,
    team_id,
    player_id,  

    event_index,
    event_period,
    event_minute,
    event_second,

    event_type_id,
    event_type_name,
    position_id,
    position_name,

    possession,
    possession_team_id,
    play_pattern_id,
    play_pattern_name,

    location_x,
    location_y,
    duration,

    event_json   
FROM {{ ref('stg_events') }}