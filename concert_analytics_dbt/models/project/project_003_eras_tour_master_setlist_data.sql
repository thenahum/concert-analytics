with eras_setlist_history_cte as (
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
    from
        {{ ref('mart_setlist_history') }} as msh
    where true
        and msh.artist_name_hint = 'TaylorSwift'
        and lower(coalesce(msh.event_tour, '')) like '%eras tour%'
)
, taylor_tracks_cte as (
    select
        mat.artist_name_hint
        , mat.album_id
        , mat.album_url
        , mat.album_uri
        , mat.album_type
        , mat.album_name
        , mat.album_total_tracks
        , mat.album_release_date
        , mat.album_image_url
        , mat.album_popularity
        , mat.track_id
        , mat.track_url
        , mat.track_uri
        , mat.track_disk_number
        , mat.track_duration_seconds
        , mat.track_name
        , trim(
            regexp_replace(
                regexp_replace(
                    lower(mat.track_name)
                    , '\s*\(taylor.?s version\)'
                    , ''
                    , 'gi'
                )
                , '\s+'
                , ' '
                , 'g'
            )
        ) as track_match_name
        , case
            when lower(mat.track_name) ~ 'taylor.?s version'
                or lower(mat.album_name) ~ 'taylor.?s version'
                then true
            else false
        end as is_taylors_version
        , mat.track_number
        , mat.track_popularity
        , mat.track_irsc
    from
        {{ ref('mart_all_tracks') }} as mat
    where true
        and mat.artist_name_hint = 'TaylorSwift'
)
, manual_track_link_override_cte(event_set_song_id, track_id) as (
    values
        ('d819c206f9305cae84edf2ba03d0ae31', '71BqAINEnezjQfxE4VuJfq')
        , ('69a9899c82cbfcc0535814a00f184a9f', '2RJnNdu4pb3MypbBroHU0T')
)
, track_link_base_candidates_cte as (
    select
        mtsss.artist_name_hint
        , mtsss.song_name
        , mtsss.track_name
        , tt.track_match_name
        , tt.is_taylors_version
        , false as manual_override_flag
        , mtsss.event_set_song_id
        , mtsss.track_id
        , mtsss.similarity_score
        , mtsss.similarity_rank
    from
        eras_setlist_history_cte as esh
        join {{ ref('mart_track_setlist_similarity_scores') }} as mtsss
            on esh.event_set_song_id = mtsss.event_set_song_id
        join taylor_tracks_cte as tt
            on mtsss.track_id = tt.track_id
    where true
        and esh.song_cover_flag = false

    union all

    select
        esh.artist_name_hint
        , esh.song_name
        , tt.track_name
        , tt.track_match_name
        , tt.is_taylors_version
        , true as manual_override_flag
        , esh.event_set_song_id
        , tt.track_id
        , 1.0 as similarity_score
        , 1 as similarity_rank
    from
        eras_setlist_history_cte as esh
        join manual_track_link_override_cte as mtlo
            on esh.event_set_song_id = mtlo.event_set_song_id
        join taylor_tracks_cte as tt
            on mtlo.track_id = tt.track_id
    where true
        and esh.song_cover_flag = false
)
, track_link_candidates_cte as (
    select
        tlbc.artist_name_hint
        , tlbc.song_name
        , tlbc.track_name
        , tlbc.track_match_name
        , tlbc.is_taylors_version
        , bool_or(tt.is_taylors_version) over (
            partition by
                tlbc.event_set_song_id
        ) as has_taylors_version_candidate
        , tlbc.event_set_song_id
        , tlbc.track_id
        , tlbc.similarity_score
        , tlbc.similarity_rank
        , row_number() over (
            partition by
                tlbc.event_set_song_id
            order by
                case
                    when tlbc.manual_override_flag then 0
                    else 1
                end
                , case
                    when tlbc.is_taylors_version then 0
                    else 1
                end
                , tlbc.similarity_rank
                , tlbc.similarity_score desc
                , tt.track_popularity desc nulls last
        ) as project_similarity_rank
    from
        track_link_base_candidates_cte as tlbc
        join taylor_tracks_cte as tt
            on tlbc.track_id = tt.track_id
)
, track_link_selected_cte as (
    select
        *
    from
        track_link_candidates_cte
    where true
        and project_similarity_rank = 1
)
, popularity_override_song_cte(song_match_name) as (
    values
        ('bad blood')
        , ('blank space')
        , ('shake it off')
        , ('style')
)
, popularity_source_candidates_cte as (
    select
        pos.song_match_name
        , tt.track_id as popularity_source_track_id
        , tt.track_name as popularity_source_track_name
        , tt.is_taylors_version as popularity_source_is_taylors_version
        , tt.track_popularity as popularity_source_track_popularity
        , row_number() over (
            partition by
                pos.song_match_name
            order by
                tt.track_popularity desc nulls last
        ) as popularity_source_rank
    from
        popularity_override_song_cte as pos
        join taylor_tracks_cte as tt
            on pos.song_match_name = tt.track_match_name
)
, popularity_source_selected_cte as (
    select
        *
    from
        popularity_source_candidates_cte
    where true
        and popularity_source_rank = 1
)
select
    esh.*
    , 'Taylor Swift' as artist_display_name
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
    , coalesce(pso.popularity_source_track_popularity, tr.track_popularity) as track_popularity
    , tr.track_popularity as selected_track_popularity
    , tr.track_irsc
    , tls.track_match_name
    , tls.is_taylors_version
    , tls.has_taylors_version_candidate
    , tls.similarity_score
    , tls.similarity_rank as mart_similarity_rank
    , tls.project_similarity_rank
    , case
        when pso.popularity_source_track_id = tr.track_id then 'selected_track'
        when pso.popularity_source_is_taylors_version then 'taylors_version_family_override'
        when pso.popularity_source_track_id is not null then 'original_recording_override'
        when tls.track_id is not null then 'selected_track'
    end as track_popularity_source
    , pso.popularity_source_track_id
    , pso.popularity_source_track_name
    , pso.popularity_source_is_taylors_version
    , pso.popularity_source_track_popularity
    , es.event_total_songs
    , es.event_total_sets
    , es.event_total_encore_songs
    , es.event_total_non_encore_songs
    , coalesce(tr.track_name, esh.song_name, 'Unknown') as track_song_name
    , selected_matps.track_duration_minutes
    , coalesce(
        popularity_source_matps.track_popularity_mid_rank_cdf
        , selected_matps.track_popularity_mid_rank_cdf
    ) as track_popularity_mid_rank_cdf
    , coalesce(
        popularity_source_matps.track_weighted_popularity_mid_rank_cdf
        , selected_matps.track_weighted_popularity_mid_rank_cdf
    ) as track_weighted_popularity_mid_rank_cdf
from
    eras_setlist_history_cte as esh
    left join track_link_selected_cte as tls
        on esh.event_set_song_id = tls.event_set_song_id
    left join taylor_tracks_cte as tr
        on tls.track_id = tr.track_id
    left join popularity_source_selected_cte as pso
        on tls.track_match_name = pso.song_match_name
        and tls.is_taylors_version
    left join {{ ref('mart_event_summary') }} as es
        on esh.event_id = es.event_id
    left join {{ ref('mart_all_tracks_popularity_scores') }} as selected_matps
        on tr.track_id = selected_matps.track_id
    left join {{ ref('mart_all_tracks_popularity_scores') }} as popularity_source_matps
        on pso.popularity_source_track_id = popularity_source_matps.track_id
