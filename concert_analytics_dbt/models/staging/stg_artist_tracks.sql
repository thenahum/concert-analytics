select 
	name_hint as artist_name_hint
	,track_id as track_id
	,track_url as track_url
	,track_uri as track_uri
	,album_id as album_id
	,track_disk_number as track_disk_number
	,track_duration_ms / 1000 as track_duration_seconds
	,track_name as track_name
	,track_number as track_number
from 
	{{ source('raw', 'artist_tracks') }}