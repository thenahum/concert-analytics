{{ config(
	materialized= 'table'
    ,depends_on = ['analytics_mart.functions.similarity']
) }}

select 
	sh.artist_name_hint as artist_name_hint
	, sh.song_name as song_name
	, atr.track_name as track_name
	, sh.event_set_song_id as event_set_song_id
	, atr.track_id as track_id
	, analytics_mart.similarity(sh.song_name::text, atr.track_name::text) as similarity_score
	, row_number() over (
		partition by 
			sh.event_set_song_id 
		order by 
			analytics_mart.similarity(sh.song_name::text, atr.track_name::text) desc
		) as similarity_rank
from 
	{{ ref('mart_setlist_history') }} as sh
	join {{ ref('mart_all_tracks') }} as atr
		on analytics_mart.similarity(sh.song_name::text, atr.track_name::text) > 0.2
		and sh.artist_name_hint = atr.artist_name_hint
where true