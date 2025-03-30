select 
	album_id
	,album_url
	,album_uri
	,album_type
	,album_name
	,album_total_tracks
	,album_release_date
	,album_image_url
	,album_popularity
	,track_id
	,track_url
	,track_uri
	,track_disk_number
	,track_duration_seconds
	,track_name
	,track_number
	,track_popularity
	,track_irsc
from 
	{{ ref('mart_all_tracks_versions') }}
where 
	track_version_rank = 1