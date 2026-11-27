select home_team_id as team_id,
       home_team_name as team_name
from {{ ref('stg_matches') }}

union

select away_team_id,
       away_team_name
from {{ ref('stg_matches') }}