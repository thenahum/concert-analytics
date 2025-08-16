

with coachella_dates_cte(artist_name_hint,coachella_weekend,coachella_start_date,coachella_end_date) as (
    values 
        ('Turnstile','Weekend 1','2022-04-16'::date,'2022-04-18'::date)
        , ('BillieEilish','Weekend 1','2022-04-16'::date,'2022-04-18'::date)
        , ('JapaneseBreakfast','Weekend 1','2022-04-16'::date,'2022-04-18'::date)
        -- , ('TameImpala','Weekend 1','2019-04-12'::Date, '2019-04-14'::date)
        , ('Turnstile','Weekend 2','2022-04-23'::Date, '2022-04-25'::date)
        , ('BillieEilish','Weekend 2','2022-04-23'::Date, '2022-04-25'::date)
        , ('JapaneseBreakfast','Weekend 2','2022-04-23'::Date, '2022-04-25'::date)
        -- , ('TameImpala','Weekend 2','2019-04-19'::date, '2019-04-21'::Date)
)
, analysis_dates_cte as (
    select 
        artist_name_hint
        , min(coachella_start_date) as first_coachella_date
        , max(coachella_end_date) as last_coachella_date
        , min(coachella_start_date) - 365 as reporting_start_date
        , max(coachella_end_date) + 365 as reporting_end_date
    from 
        coachella_dates_cte
    group by 
        1
)
, glider_cte as (
    select 
        mat.* 
    from 
        {{ ref('mart_all_tracks') }} as mat
    where true 
        and artist_name_hint = 'JapaneseBreakfast'
        and lower(track_name) like '%glider%'
) 
, glider_similarity_cte as (
    select 
        msh.artist_name_hint
        , msh.song_name
        , 'Glider' as track_name
        , msh.event_set_song_id
        , g_cte.track_id
        , 1 as similarity_score
        , 1 as similarity_rank
    from 
        {{ ref('mart_setlist_history') }} as msh 
        CROSS JOIN glider_cte as g_cte
    where TRUE
        and lower(msh.song_name) like '%glider%'
        and msh.artist_name_hint = 'JapaneseBreakfast'
)
, setlisth_history_coachella_flags_cte as (
    select 
        msh.artist_name_hint
        , msh.event_set_song_id
        , msh.event_id
        , msh.event_date
        , msh.event_info
        , msh.event_url
        , msh.event_tour_id
        , msh.event_tour
        , msh.venue_id
        , msh.venue_name
        , msh.venue_city
        , msh.venue_state_code
        , msh.venue_country_code
        , msh.venue_latitude
        , msh.venue_longitude
        , msh.set_index
        , msh.set_index_reversed
        , msh.encore_index
        , msh.encore_flag
        , msh.song_index
        , msh.song_index_reversed
        , msh.song_position_in_set_index
        , msh.song_position_in_set_index_reversed
        , msh.song_name
        , msh.song_info
        , msh.song_cover_flag
        , msh.song_cover_artist_mbid
        , msh.song_cover_artist_name
        , msh.song_with_flag
        , msh.song_with_artist_mbid
        , msh.song_with_artist_name
        , msh.song_last_event_set_song_id
        , msh.song_last_event_id
        , msh.song_last_event_date
        , case 
            when cd_cte.artist_name_hint is not null then TRUE 
            else FALSE 
        end as is_coachella
        , cd_cte.coachella_weekend as coachella_weekend
        , case 
            when ad_cte.first_coachella_date > msh.event_date then  ad_cte.first_coachella_date - msh.event_date 
        end as days_before_first_coachella_date
        , case 
            when ad_cte.last_coachella_date < msh.event_date then msh.event_date - ad_cte.last_coachella_date 
        end as days_after_last_coachella_date
        , case 
            when cd_cte.artist_name_hint is not null then 'Coachella'
            when ad_cte.first_coachella_date > msh.event_date then 'Before Coachella'
            when ad_cte.last_coachella_date < msh.event_date then 'After Coachella'
        end as coachella_analytics_period
    from 
        {{ ref('mart_setlist_history') }} as msh
        join analysis_dates_cte as ad_cte
            on msh.artist_name_hint = ad_cte.artist_name_hint
            and msh.event_date between ad_cte.reporting_start_date and ad_cte.reporting_end_date 
        left join coachella_dates_cte as cd_cte
            on msh.artist_name_hint = cd_cte.artist_name_hint
            and msh.event_date between cd_cte.coachella_start_date and cd_cte.coachella_end_date
    where TRUE
)
, track_link_filtered_cte as (
    select 
        *
    from 
        {{ ref('mart_track_setlist_similarity_scores') }} as mtsss
    where TRUE
        and mtsss.similarity_rank = 1
    union 
    select 
        *
    from 
        glider_similarity_cte as gs_cte
)
select
    cs_cte.*
    , case
        when cs_cte.artist_name_hint = 'BillieEilish' then 'Billie Eilish'
        when cs_cte.artist_name_hint = 'JapaneseBreakfast' then 'Japanese Breakfast'
        when cs_cte.artist_name_hint = 'Turnstile' then 'Turnstile'
    end as artist_display_name
    , tr.album_id
    , tr.album_url
    , tr.album_uri
    , tr.album_type
    , tr.album_name
    , tr.album_total_tracks
    , tr.album_release_date
    , tr.album_image_url
    , tr.album_popularity
    , tr.track_id
    , tr.track_url
    , tr.track_uri
    , tr.track_disk_number
    , tr.track_duration_seconds
    , tr.track_name
    , tr.track_number
    , tr.track_popularity
    , tr.track_irsc
	, es.event_total_songs
	, es.event_total_sets
	, es.event_total_encore_songs
	, es.event_total_non_encore_songs
    , coalesce(tr.track_name,cs_cte.song_name,'Unknown') as track_song_name
    , matps.track_duration_minutes
    , matps.track_popularity_mid_rank_cdf
    , matps.track_weighted_popularity_mid_rank_cdf
from 
    setlisth_history_coachella_flags_cte as cs_cte
    left join track_link_filtered_cte as tl_cte
        on cs_cte.event_set_song_id = tl_cte.event_set_song_id
        and cs_cte.song_cover_flag = FALSE 
    left join {{ ref('mart_all_tracks') }} as tr
		on tl_cte.track_id = tr.track_id
    left join {{ ref('mart_event_summary') }} as es
    	on cs_cte.event_id = es.event_id
    left join {{ ref('mart_all_tracks_popularity_scores') }} as matps
        on tr.track_id = matps.track_id
