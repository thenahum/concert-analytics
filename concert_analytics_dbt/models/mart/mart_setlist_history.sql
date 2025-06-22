-- models/mart/mart_setlist_history.sql

select 
	artist_name_hint
	,event_set_song_id
	,event_id
	,event_date
	,event_info
	,event_url
	,event_tour_id
	,event_tour
	,venue_id
	,venue_name
	,venue_city
	,venue_state_code
	,venue_country_code
	,venue_latitude
	,venue_longitude
	,set_index
	,set_index_reversed
	,encore_index
	,encore_flag
	,song_index
	,song_index_reversed
	,song_position_in_set_index
	,song_position_in_set_index_reversed
	,song_name
	,song_info
	,song_cover_flag
	,song_cover_artist_mbid
	,song_cover_artist_name
	,song_with_flag
	,song_with_artist_mbid
	,song_with_artist_name  
	,lag(event_set_song_id) over (partition by artist_name_hint,song_name order by event_date desc) as song_last_event_set_song_id	
	,lag(event_id) over (partition by artist_name_hint,song_name order by event_date desc) as song_last_event_id
	,lag(event_date) over (partition by artist_name_hint,song_name order by event_date desc) as song_last_event_date
from 
	{{ ref('stg_setlist_history') }}