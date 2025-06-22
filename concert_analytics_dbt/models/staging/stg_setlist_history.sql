select 
	name_hint as artist_name_hint
	,md5(event_id||set_index||song_index) as event_set_song_id
	,event_id as event_id
	,TO_DATE(event_date, 'DD-MM-YYYY') as event_date 
	,event_info as event_info
	,event_url as event_url
	,md5(tour_name) as event_tour_id
	,tour_name as event_tour
	,md5(venue||venue_city||venue_state_code||venue_country_code) as venue_id
	,venue as venue_name
	,venue_city as venue_city
	,venue_state_code as venue_state_code
	,venue_country_code as venue_country_code
	,cast(nullif(venue_lat,0) as float) as venue_latitude
	,cast(nullif(venue_lon,0) as float) as venue_longitude
	,dense_rank() over (partition by event_id order by set_index asc nulls last) as set_index 
	,dense_rank() over (partition by event_id order by set_index desc nulls last) as set_index_reversed 
	,cast(encore_index as int) as encore_index
	,cast(encore_flag as bool) as encore_flag
	,row_number() over (partition by event_id order by set_index asc, song_index asc nulls last) as song_index
	,row_number() over (partition by event_id order by set_index desc, song_index desc nulls last) as song_index_reversed
	,row_number() OVER (PARTITION BY event_id, set_index ORDER BY song_index asc nulls last) AS song_position_in_set_index
	,row_number() OVER (PARTITION BY event_id, set_index ORDER BY song_index desc nulls last) AS song_position_in_set_index_reversed
	,nullif(song,'') as song_name
	,song_info as song_info
	,cast(song_cover_flag as bool) as song_cover_flag
	,song_cover_artist_mbid as song_cover_artist_mbid
	,song_cover_artist_name as song_cover_artist_name
	,cast(song_with_flag as bool) as song_with_flag
	,song_with_artist_mbid as song_with_artist_mbid
	,song_with_artist_name as song_with_artist_name
from 
	{{ source('raw', 'setlist_history') }}