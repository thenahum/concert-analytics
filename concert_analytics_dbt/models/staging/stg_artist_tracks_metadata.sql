select 
	name_hint as artist_name_hint
	,cast(track_id as varchar) as track_id
	,cast(track_popularity as int) as track_popularity
	,cast(track_isrc as varchar) as track_isrc
from 
	{{ source('raw', 'artist_tracks_metadata') }} 
	