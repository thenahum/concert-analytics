select 
    track_name
    ,count(1) as total_times_played
    ,max(case when is_coachella then 1 else 0 end) as played_in_coachella
from 
    analytics_project.project_002_coachella_master_setlist_data
where 
    artist_name_hint = 'Turnstile'
group by 
    1
order by 
    2 desc 
;



select 
    event_date
    ,count(1)
from 
    analytics_project.project_002_coachella_master_setlist_data
where 
    artist_name_hint = 'JapaneseBreakfast'
    -- and event_date = '2021-06-10'
group by 1
limit 2000;

with glider_cte as (
    select 
        mat.* 
    from 
        analytics_mart.mart_all_tracks as mat
    where true 
        and artist_name_hint = 'JapaneseBreakfast'
        and lower(track_name) like '%glider%'
)
select 
    msh.artist_name_hint
    , msh.song_name
    , 'Glider' as track_name
    , msh.event_set_song_id
    , g_cte.track_id
    , 1 as similarity_score
    , 1 as similarity_rank
from 
    analytics_mart.mart_setlist_history as msh 
    CROSS JOIN glider_cte as g_cte
where TRUE
    and lower(msh.song_name) like '%glider%'
    and msh.artist_name_hint = 'JapaneseBreakfast'
limit 
    100;

select * 
from 
    analytics_mart.mart_all_tracks
where true 
    and artist_name_hint = 'TameImpala'
    and lower(track_name) like '%led%'
limit 100