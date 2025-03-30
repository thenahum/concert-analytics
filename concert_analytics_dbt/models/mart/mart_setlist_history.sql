-- models/mart/mart_setlist_history.sql

select 
	event_set_song_id
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
	,encore_index
	,encore_flag
	,song_index
	,song_position_in_set_index
	,song_name
	,song_info
	,song_cover_flag
	,song_cover_artist_mbid
	,song_cover_artist_name
	,song_with_flag
	,song_with_artist_mbid
	,song_with_artist_name  
from 
	{{ ref('stg_setlist_history') }}