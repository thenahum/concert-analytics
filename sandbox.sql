with all_tracks_summary_stats_cte as (
    select
        artist_name_hint as artist_name_hint
        , min(track_popularity) as artist_min_track_popularity
        , max(track_popularity) as artist_max_track_popularity
        , avg(track_popularity::float) as artist_avg_track_popularity
        , percentile_disc(0.5) WITHIN GROUP (ORDER BY track_popularity) as artist_median_track_popularity
        , stddev_samp(track_popularity::float) as artist_stddev_track_popularity
    from
        analytics_mart.mart_all_tracks
    group by 
        1
)
, all_tracks_popularity_metrics_1_cte as (
    select 
        atss_cte.*
        , mat.track_id
        , mat.track_popularity
        , mat.track_duration_seconds
        , mat.track_duration_seconds / 60.0 as track_duration_minutes
        , mat.track_popularity / atss_cte.artist_avg_track_popularity as track_popularity_relative_score
        , ((mat.track_popularity - atss_cte.artist_avg_track_popularity) / atss_cte.artist_stddev_track_popularity) as track_popularity_z_score
    from
        analytics_mart.mart_all_tracks as mat
        join all_tracks_summary_stats_cte as atss_cte
            on mat.artist_name_hint = atss_cte.artist_name_hint
)
select 
    atpm_cte.*
    , ((atpm_cte.track_popularity_z_score + 2.5)/5.0) as track_popularity_normalized_z_score
    , ((atpm_cte.track_popularity_z_score + 2.5)/5.0) * atpm_cte.track_duration_minutes as track_weighted_popularity_normalized_z_score
from 
    all_tracks_popularity_metrics_1_cte as atpm_cte
limit 
    100
;


select 
    artist_name_hint
    , track_popularity
    , count(1)
from  
    analytics_mart.mart_all_tracks 
group by 
    1,2
limit 
    1000
;